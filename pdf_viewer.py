import streamlit as st
import base64
import requests
import re
import pandas as pd
import hashlib
import os

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Initialize session state for notes storage
if 'notes' not in st.session_state:
    st.session_state.notes = {}

# CSV file for storing user credentials
USERS_CSV = "users.csv"

def init_users_csv():
    if not os.path.exists(USERS_CSV):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USERS_CSV, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def read_users():
    init_users_csv()
    return pd.read_csv(USERS_CSV)

def write_user(username, password):
    df = read_users()
    new_user = pd.DataFrame({"username": [username], "password": [password]})
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)

def signup():
    st.subheader("Sign Up")
    new_username = st.text_input("New Username", key="signup_username")
    new_password = st.text_input("New Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    if st.button("Sign Up"):
        if new_username and new_password and confirm_password:
            if new_password == confirm_password:
                df = read_users()
                if new_username not in df["username"].values:
                    write_user(new_username, hash_password(new_password))
                    st.success("Successfully signed up! Please log in.")
                    st.rerun()
                else:
                    st.error("Username already exists.")
            else:
                st.error("Passwords do not match.")
        else:
            st.error("Please fill in all fields.")

def login():
    st.subheader("Log In")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Log In"):
        df = read_users()
        if username in df["username"].values:
            stored_password = df.loc[df["username"] == username, "password"].iloc[0]
            if stored_password == hash_password(password):
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Incorrect password.")
        else:
            st.error("Username not found.")

st.title("PDF Viewer App with Notes")

if not st.session_state.authenticated:
    auth_option = st.radio("Choose an option:", ("Log In", "Sign Up"))
    if auth_option == "Sign Up":
        signup()
    else:
        login()
else:
    st.write(f"Logged in as: **{st.session_state.current_user}**")
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.success("Logged out successfully.")
        st.rerun()

    # PDF Viewer
    st.subheader("View PDF")
    source_option = st.radio("Select PDF source:", ("Upload Local PDF", "Google Drive Link"))
    
    # Determine a key for notes storage
    pdf_key = None

    if source_option == "Upload Local PDF":
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded_file:
            bytes_data = uploaded_file.read()
            pdf_key = uploaded_file.name
            b64 = base64.b64encode(bytes_data).decode("utf-8")
            iframe = f'<iframe src="data:application/pdf;base64,{b64}" width="700" height="1000"></iframe>'
            st.markdown(iframe, unsafe_allow_html=True)
        else:
            st.info("Please upload a PDF file to view.")
    else:
        google_drive_link = st.text_input("Enter Google Drive PDF link:")
        if google_drive_link:
            def get_direct_download_link(drive_link):
                m = re.search(r'[-\w]{25,}', drive_link)
                return f"https://drive.google.com/uc?export=download&id={m.group(0)}" if m else None
            direct = get_direct_download_link(google_drive_link)
            if direct:
                try:
                    resp = requests.get(direct)
                    if resp.status_code == 200 and 'application/pdf' in resp.headers.get('content-type','').lower():
                        pdf_key = google_drive_link
                        b64 = base64.b64encode(resp.content).decode("utf-8")
                        iframe = f'<iframe src="data:application/pdf;base64,{b64}" width="700" height="1000"></iframe>'
                        st.markdown(iframe, unsafe_allow_html=True)
                    else:
                        st.error("Failed to fetch PDF. Ensure it’s publicly accessible.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Invalid Google Drive link.")
        else:
            st.info("Please enter a Google Drive link to view.")

    # Take Notes section
    if pdf_key:
        st.subheader("Take Notes")
        note_key = f"{st.session_state.current_user}__{pdf_key}"
        existing = st.session_state.notes.get(note_key, "")
        updated = st.text_area("Your notes:", value=existing, height=200)
        if st.button("Save Notes"):
            st.session_state.notes[note_key] = updated
            st.success("Notes saved!")

        # Optionally, show all your notes for this session
        if st.checkbox("Show all my notes this session"):
            for k, v in st.session_state.notes.items():
                user, key = k.split("__", 1)
                if user == st.session_state.current_user:
                    st.markdown(f"**Document:** {key}\n\n{v}\n---")
