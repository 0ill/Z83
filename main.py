import streamlit as st
import json
from datetime import date, datetime
from utils.google_sheets import connect_to_google_sheets
from utils.constants import JOB_SHEET_NAME, JOB_WORKSHEET_NAME
from utils.helpers import load_css
from components.auth import show_auth_forms
from components.jobs import show_job_listings
from components.application import job_application_assistant
from components.apply import show_apply_page


def parse_date(date_str):
    """Parse a date string into a datetime.date object, return None if invalid."""
    if not date_str or date_str == "N/A":
        return None
    # Normalize by removing extra spaces and handling time suffixes
    date_str = date_str.strip()
    # Try to strip time component (e.g., "at 16H00") and parse just the date
    if " at " in date_str:
        date_part = date_str.split(" at ")[0].strip()
    else:
        date_part = date_str
    # Try common date formats
    formats = [
        "%Y-%m-%d",           # 2025-05-13
        "%d/%m/%Y",           # 13/05/2025
        "%m/%d/%Y",           # 05/13/2025
        "%d-%m-%Y",           # 13-05-2025
        "%B %d, %Y",          # May 13, 2025
        "%d %B %Y",           # 13 May 2025
        "%d %b %Y",           # 13 May 2025 (abbreviated month)
        "%d %b %Y at %HH%M",  # 02 May 2025 at 16H00
        "%d %b %Y @ %HH%M",   # 23 May 2025 @ 16h00
        "%d %B %Y @ %Hh%M",    # 02 June 2025 @ 15h45
        "%d %B %Y @%Hh%M",      #30 May 2025, 16:00
        "%d %B %Y, %H:%M"      #30 May 2025, 16:00
    ]
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str if fmt.endswith("at %HH%M") else date_part, fmt).date()
            #st.write(f"Successfully parsed date: {date_str} as {parsed_date}")
            return parsed_date
        except ValueError:
            continue
    st.warning(f"Could not parse date: {date_str}")
    return None

@st.cache_data
def load_job_postings():
    """Load job postings from Google Sheets or fallback to JSON, returning only records with closing date greater than today."""
    today = date.today() #date(2025, 4, 30)  # Hardcoded for consistency; use date.today() for dynamic date
    sheet = connect_to_google_sheets(JOB_SHEET_NAME, JOB_WORKSHEET_NAME)
    records = []
    source = "Google Sheets"

    if sheet:
        try:
            records = sheet.get_all_records()
            #st.write(f"Loaded {len(records)} records from Google Sheets")
        except Exception as e:
            st.error(f"Failed to load job postings from Google Sheets: {str(e)}")
            source = "JSON"
    else:
        st.warning("Could not connect to Google Sheets, falling back to JSON")
        source = "JSON"

    if not records and source == "JSON":
        try:
            with open("data.json", "r") as f:
                records = json.load(f)
                st.write(f"Loaded {len(records)} records from data.json")
        except FileNotFoundError:
            st.error("data.json not found. Please ensure the file exists.")
            return []
        except json.JSONDecodeError:
            st.error("Invalid JSON format in data.json.")
            return []
        except Exception as e:
            st.error(f"Failed to load job postings from JSON: {str(e)}")
            return []

    # Filter records with valid closing dates greater than today
    filtered_records = [
        record for record in records
        if record.get("Closing Date") and parse_date(record.get("Closing Date")) and parse_date(record.get("Closing Date")) >= today
    ]
    #st.write(f"Filtered to {len(filtered_records)} records with closing date after {today}")

    # Fallback: if no records after filtering, return all records to avoid empty list
    if not filtered_records:
        st.warning("No records with future closing dates found. Displaying all records as fallback.")
        return records

    return filtered_records

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(layout="wide")
    load_css()
    
    st.title("Welcome to The Lab!")
    st.header("Introduction")
    st.write("This is a simple page created to help with Government job applications")

    # Initialize session state
    if "current_app_state" not in st.session_state:
        st.session_state.current_app_state = "Jobs"

    job_postings = load_job_postings()
    show_auth_forms()
    
    st.divider()
    
    if st.session_state.current_app_state == "Jobs":
        with st.container(border=True):
            if job_postings:
                show_job_listings(job_postings)
            else:
                st.error("No job postings available to display.")
    elif st.session_state.current_app_state == "App":
        with st.container(border=True):
            job_application_assistant()
    elif st.session_state.current_app_state == "Apply":
        with st.container(border=True):
            show_apply_page()

if __name__ == "__main__":
    main()