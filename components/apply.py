import streamlit as st
from components.application import z83

@st.dialog("Support the Application")
def show_buy_me_a_coffee_dialog(job):
    """Display a dialog with an iframe for Buy Me a Coffee."""
    st.markdown(f"Applying for **{job.get('Position Title', 'N/A')}** (Post Number: {job.get('Post Number', 'N/A')})")
    st.markdown("Please complete a donation via Buy Me a Coffee to support this service.")
    # Embed Buy Me a Coffee iframe
    iframe_code = """
    <iframe src="https://buymeacoffee.com/auxygenlabs/e/409646" 
            width="100%" 
            height="400px" 
            frameborder="0">
    </iframe>
    """
    st.components.v1.html(iframe_code, height=400)
    st.info("Note: Transaction status cannot be verified automatically. Please complete the donation and click 'Proceed' to continue with your application.")
    # Button to proceed after donation
    if st.button("Proceed with Application", key=f"proceed_{job.get('Post Number', 'N/A')}"):
        st.session_state.dialog_open = False
        st.rerun()
    if st.button("Cancel", key=f"cancel_{job.get('Post Number', 'N/A')}"):
        st.session_state.dialog_open = False
        st.rerun()

def show_apply_page():
    """Display selected jobs with Apply and Remove buttons."""
    st.title("Selected Jobs for Application")
    with st.container(border=True):
        col1, col2, col1x, col2x = st.columns(4)
        with col1:
            st.markdown("Explore Selected Jobs below.")
        with col1x:
            if st.button("Jobs", key="jobs_app", use_container_width=True):
                st.session_state.current_app_state = "Jobs"
                st.rerun()
        with col2x:
            if st.button("Application Assistant", key="z83", use_container_width=True):
                st.session_state.current_app_state = "App"
                st.rerun()
        st.divider()
    
    if st.session_state.added_jobs:
        for job in st.session_state.added_jobs:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**{job.get('Position Title', 'N/A')}** (Reference Number: {job.get('Reference Number', 'N/A')})")
                    st.markdown(f"Department: {job.get('Department', 'N/A')}")
                    st.markdown(f"Location: {job.get('Province', 'N/A')} : {job.get('City or Town', 'N/A')}")
                    st.markdown(f"Closing Date: {job.get('Closing Date', 'N/A')}")
                with col2:
                    if st.button("Apply", key=f"apply_{job.get('Post Number', 'N/A')}_{job.get('Position Title', 'N/A')}", use_container_width=True):
                        #st.session_state.dialog_open = True
                        #show_buy_me_a_coffee_dialog(job)
                        # Proceed with application (assuming donation completed)
                        z83(job)
                with col3:
                    if st.button("Remove", key=f"remove_{job.get('Post Number', 'N/A')}_{job.get('Position Title', 'N/A')}", use_container_width=True):
                        st.session_state.added_jobs = [
                            j for j in st.session_state.added_jobs if j.get("Post Number") != job.get("Post Number")
                        ]
                        st.rerun()
    else:
        st.info("You have not added any jobs yet.")
    
    if st.button("Back to Jobs", use_container_width=True):
        st.session_state.current_app_state = "Jobs"
        st.rerun()