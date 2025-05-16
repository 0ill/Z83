import streamlit as st
from datetime import datetime
from utils.google_sheets import connect_to_google_sheets, add_new_row
from utils.constants import USER_SHEET_NAME, USER_LOGIN_WORKSHEET_NAME,USER_DATA_WORKSHEET_NAME, SESSION_KEYS, BUTTON_LABELS, USER_LOGIN_HEADERS
from utils.helpers import hash_password, check_password
from utils.helpers import load_user_data
from components.application import initialize_session_state as z83_in

def initialize_session_state():
    """Ensure all required session state variables exist."""
    for key, default_value in SESSION_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def handle_logout():
    """Clear session state on logout."""
    st.session_state.clear()
    st.rerun()

def render_auth_buttons():
    """Render the signup/login button pair."""
    col1, col2 = st.columns(2)
    with col1:
        if st.button(BUTTON_LABELS["signup"][0], key=BUTTON_LABELS["signup"][1], use_container_width=True):
            st.session_state.signup_clicked = not st.session_state.signup_clicked
            st.session_state.login_clicked = False
    with col2:
        if st.button(BUTTON_LABELS["login"][0], key=BUTTON_LABELS["login"][1], use_container_width=True):
            st.session_state.login_clicked = not st.session_state.login_clicked
            st.session_state.signup_clicked = False

def render_signup_form():
    """Display and handle signup form."""
    with st.form("sign_up_form"):
        st.subheader(":material/how_to_reg: Sign Up")
        name = st.text_input("Name", key="signup_name")
        surname = st.text_input("Surname", key="signup_surname")
        email = st.text_input("Email", key="signup_email").lower()
        phone = st.text_input("Phone Number", key="signup_phone")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.form_submit_button("Submit :material/send:", type="primary"):
            if not all([name, email, password]):
                st.error("Please fill in all required fields")
                return

            sheet = connect_to_google_sheets(USER_SHEET_NAME, USER_LOGIN_WORKSHEET_NAME)
            if not sheet:
                return

            try:
                existing_emails = [row[2] for row in sheet.get_all_values()[1:]]
                if email in existing_emails:
                    st.error("Email already exists")
                    return

                hashed_password = hash_password(password)
                creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                add_new_row(sheet, [name, surname, email, phone, hashed_password, creation])

                st.session_state.signup_login = True
                st.session_state.current_user = name
                st.success("Registration successful!")
                st.rerun()

            except Exception as e:
                st.error(f"Registration failed: {str(e)}")

def render_login_form():
    """Display and handle login form."""
    with st.form("login_form"):
        st.subheader(":material/login: Login")
        email = st.text_input("Email", key="login_email").lower()
        password = st.text_input("Password", type="password", key="login_password")

        if st.form_submit_button("Submit :material/send:", type="primary"):
            if not all([email, password]):
                st.error("Please enter valid credentials")
                return

            sheet = connect_to_google_sheets(USER_SHEET_NAME, USER_LOGIN_WORKSHEET_NAME)
            if not sheet:
                return

            try:
                records = sheet.get_all_records()
                if not records:
                    st.error("No registered users")
                    return

                user_data = next((row for row in records if row["email"] == email), None)
                if not user_data:
                    st.error("Invalid credentials")
                    return

                if check_password(password, user_data["password"]):
                    st.session_state.signup_login = True
                    st.session_state.current_user = user_data["name"]
                    # Load user data and update resume_data
                    loaded_data = load_user_data(email)
                    
                    z83_in()
                    st.session_state.resume_data = loaded_data if loaded_data else st.session_state.resume_data
                    st.success("Login successful!")
                    st.rerun()
                    st.write(loaded_data)
                else:
                    st.error("Invalid credentials")

            except Exception as e:
                st.error(f"Login failed: {str(e)}")

def show_auth_forms():
    """Main authentication component."""
    initialize_session_state()

    with st.container(border=True):
        if st.session_state.signup_login:
            st.button(
                BUTTON_LABELS["logout"][0],
                key=BUTTON_LABELS["logout"][1],
                on_click=handle_logout,
                use_container_width=True,
                type="primary",
            )
            if st.session_state.current_user:
                st.markdown(f"**Welcome, {st.session_state.current_user}!**")
        else:
            render_auth_buttons()
            if st.session_state.signup_clicked:
                render_signup_form()
            elif st.session_state.login_clicked:
                render_login_form()