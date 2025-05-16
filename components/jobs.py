import streamlit as st
import pandas as pd
from utils.constants import JOB_SESSION_KEYS, PAGE_SIZE

def initialize_job_session_state():
    """Initialize session state variables for job listings."""
    for key, default_value in JOB_SESSION_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    if "added_jobs" not in st.session_state:
        st.session_state.added_jobs = []

def create_pagination_controls(total_pages):
    """Render pagination controls."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button(":material/arrow_back_ios: Previous", use_container_width=True):
            if st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.rerun()
    with col2:
        if st.session_state.current_page > total_pages:
            st.session_state.current_page = 1
            st.rerun()
        st.button(f"Page {st.session_state.current_page} of {total_pages}", use_container_width=True, disabled=True)
    with col3:
        if st.button("Next :material/arrow_forward_ios:", use_container_width=True):
            if st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.rerun()

def render_job_card(job, index):
    """Render an individual job card."""
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{job.get('Position Title', 'N/A')}**")
            col1x, col2x, col3x = st.columns(3)
            with col1x:
                st.markdown(f":material/domain: *Department: {job.get('Department', 'N/A')}*")
                st.markdown(f":material/checkbook: *Salary: {job.get('Salary', 'N/A')}*")
            with col2x:
                st.markdown(f":material/location_on: *Province: {job.get('Province', 'N/A')} : {job.get('City or Town', 'N/A')}*")
                st.markdown(f":material/event: *Closing Date: {job.get('Closing Date', 'N/A')}*")
        with col2:
            post_number = job.get("Post Number", "Unknown")
            if st.button("View Details", key=f"view_{post_number}_{index}", use_container_width=True):
                st.session_state.selected_job = job
                st.session_state.dialog_open = True
                st.rerun()
            if any(j.get("Post Number") == post_number for j in st.session_state.added_jobs):
                st.button("Added", disabled=True, key=f"add_{post_number}_{index}", use_container_width=True)
            else:
                if st.button("Add Job", key=f"add_{post_number}_{index}", use_container_width=True):
                    st.session_state.added_jobs.append(job)
                    st.rerun()

@st.dialog("Job Details")
def show_job_details(job):
    """Display job details in a dialog."""
    st.markdown(f"**Position Title:** {job.get('Position Title', 'N/A')}")
    st.markdown(f"**Reference Number:** {job.get('Reference Number', 'N/A')}")
    st.markdown(f"**Department:** {job.get('Department', 'N/A')}")
    st.markdown(f"**Location:** {job.get('Province', 'N/A')} : {job.get('City or Town', 'N/A')}")
    st.markdown(f"**Salary:** {job.get('Salary', 'N/A')}")
    st.markdown("### Requirements:")
    for requirement in job.get("Requirements", "").split("\n"):
        st.markdown(f"- {requirement}")
    st.markdown("### Duties:")
    for duty in job.get("Duties", "").split("\n"):
        st.markdown(f"- {duty}")
    st.markdown("### Application Process:")
    st.markdown(f"- Hand-delivery: {job.get('Application Hand', 'N/A')}")
    st.markdown(f"- Postal-delivery: {job.get('Application Postal', 'N/A')}")
    st.markdown(f"- Online-form: {job.get('Application Online', 'N/A')}")
    st.markdown(f"- Email to: {job.get('Application Email', 'N/A')}")
    #for method in job.get("Application Process", "").split("\n"): #, details
    #    st.markdown(f"- **{method}")
    st.markdown("### Contact Information:")
    st.markdown(f"- Name: {job.get('Contact Name', 'N/A')}")
    st.markdown(f"- Phone: {job.get('Contact Phone', 'N/A')}")
    st.markdown(f"- Email: {job.get('Contact Email', 'N/A')}")
    st.markdown(f"### Closing Date: :red[{job.get('Closing Date', 'N/A')}]")
    #st.markdown(f"**Contact Information:** {job.get('Contact Name', 'N/A')}: {job.get('Contact Phone', 'N/A')}: {job.get('Contact Email', 'N/A')}")
    st.session_state.dialog_open = False
    if st.button("Close"):
        st.session_state.dialog_open = False
        st.rerun()

#@st.dialog("Your Selected Jobs")
#def show_selection_dialog():
#    """Display selected jobs in a dialog with apply and remove functionality."""
#    if st.session_state.added_jobs:
#        for job in st.session_state.added_jobs:
#            col1, col2, col3 = st.columns([3, 1, 1])
#            with col1:
#                st.markdown(f"- {job.get('Position Title', 'N/A')} (Post Number: {job.get('Post Number', 'N/A')})")
#            with col2:
#                if st.button("Apply", key=f"apply_{job.get('Post Number', 'N/A')}_{job.get('Position Title', 'N/A')}"):
#                    st.session_state.current_app_state = "App"
#                    st.session_state.current_section = "Application Form"
#                    st.session_state.selected_job_for_application = job
#                    st.rerun()
#            with col3:
#                if st.button("Remove", key=f"remove_{job.get('Post Number', 'N/A')}_{job.get('Position Title', 'N/A')}"):
#                    st.session_state.added_jobs = [
#                        j for j in st.session_state.added_jobs if j.get("Post Number") != job.get("Post Number")
#                    ]
#                    st.rerun()
#    else:
#        st.write("You have not added any jobs yet.")
#    if st.button("Close"):
#        st.session_state.selection_dialog_open = False
#        st.rerun()

def extract_lat_lon(coord):
    """Extract latitude and longitude from coordinates string."""
    try:
        if coord and "," in coord:
            lat_str, lon_str = coord.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return pd.Series({"lat": lat, "lon": lon})
        return pd.Series({"lat": None, "lon": None})
    except Exception:
        return pd.Series({"lat": None, "lon": None})

def show_job_listings(job_postings):
    """Main job listings component with filters and added job functionality."""
    initialize_job_session_state()
    st.title(":material/work: Job Postings")

    with st.container(border=True):
        col1, col2, col1x, col2x = st.columns(4)
        with col1:
            st.markdown("Explore job opportunities below.")
        with col1x:
            if st.button("Application Assistant", key="z83", use_container_width=True):
                st.session_state.current_app_state = "App"
                st.rerun()
        with col2x:
            if st.button("View/Apply selecctions", key="apply", use_container_width=True):
                st.session_state.current_app_state = "Apply"
                st.rerun()
        #with col3x:
        #    if st.button("Apply", key="apply", use_container_width=True):
        #        st.session_state.current_app_state = "Apply"
        #        st.rerun()

        st.markdown("#### Filters")
        filtered_jobs = job_postings
        col1, col2, col3 = st.columns(3)
        with col1:
            departments = sorted(set(str(job.get("Department", "N/A")) for job in filtered_jobs))
            selected_department = st.selectbox("Department", ["All"] + departments, key="filter_department")
            if selected_department != "All":
                filtered_jobs = [job for job in filtered_jobs if job.get("Department") == selected_department]
        with col2:
            provinces = sorted(set(str(job.get("Province", "N/A")) for job in filtered_jobs))
            selected_province = st.selectbox("Province", ["All"] + provinces, key="filter_province")
            if selected_province != "All":
                filtered_jobs = [job for job in filtered_jobs if job.get("Province") == selected_province]
        with col3:
            cities = sorted(set(str(job.get("City or Town", "N/A")) for job in filtered_jobs))
            selected_city = st.selectbox("City or Town", ["All"] + cities, key="filter_city")
            if selected_city != "All":
                filtered_jobs = [job for job in filtered_jobs if job.get("City or Town") == selected_city]

        st.session_state.filtered_jobs = filtered_jobs
        st.divider()

        total_pages = (len(filtered_jobs) + PAGE_SIZE - 1) // PAGE_SIZE or 1
        start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
        current_jobs = filtered_jobs[start_idx:start_idx + PAGE_SIZE]

        for idx, job in enumerate(current_jobs):
            render_job_card(job, start_idx + idx)

        create_pagination_controls(total_pages)
        st.divider()

        df = pd.DataFrame(filtered_jobs)
        if "Coordinates" in df.columns:
            df[["lat", "lon"]] = df["Coordinates"].apply(extract_lat_lon)
            df_clean = df.dropna(subset=["lat", "lon"])
            if not df_clean.empty:
                st.title("Job Postings Map")
                st.write("Below is a map of the job postings based on the provided coordinates:")
                st.map(df_clean[["lat", "lon"]], size=20)
            else:
                st.write("No valid coordinates found for mapping.")
        else:
            st.write("Coordinates data is missing for mapping.")

        if st.session_state.dialog_open and st.session_state.selected_job:
            show_job_details(st.session_state.selected_job)

        if st.session_state.selection_dialog_open:
            show_selection_dialog()