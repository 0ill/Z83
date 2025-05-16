import bcrypt
import streamlit as st
from datetime import datetime
from utils.google_sheets import connect_to_google_sheets
from utils.constants import USER_SHEET_NAME, USER_LOGIN_WORKSHEET_NAME, USER_DATA_WORKSHEET_NAME 
from datetime import date, datetime

def safe_strptime(date_str, format):
    if date_str in ["", "N/A"]:  # Handle empty strings and 'N/A'
        return None
    try:
        return datetime.strptime(date_str, format).date()
    except ValueError:
        return None  # Return None for any other invalid date string

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Check if a password matches its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def load_css():
    """Load custom CSS styles."""
    try:
        with open("styles.css") as f:
            st.html(f"<style>{f.read()}</style>")
    except FileNotFoundError:
        st.warning("styles.css not found. Proceeding without custom styles.")

def parse_user_data(row):
    """Parse the flat row data into the nested resume_data structure."""
    resume_data = {}

    # Personal Information
    resume_data["personal_info"] = {
        "full_name": row.get("Full Name", ""),
        "surname": row.get("Surname", ""),
        "email": row.get("Email", ""),
        "phone": row.get("Phone", ""),
        "id_num": row.get("ID Number", ""),
        "pas_num": row.get("Passport Number", ""),
        "birth_date": safe_strptime(row.get("Birth Date", ""), "%Y-%m-%d"),
        "sa_citi": row.get("SA Citizen", ""),
        "nationality": row.get("Nationality", ""),
        "gender": row.get("Gender", ""),
        "race": row.get("Race", ""),
        "disability": row.get("Disability", ""),
        "p_location": row.get("Location", ""),
        "linkedin": row.get("LinkedIn", ""),
        "other_profiles": row.get("Other Profiles", ""),
    }

    # Additional Personal Information
    resume_data["personal_add_info"] = {
        "convicted": row.get("Convicted", ""),
        "convicted_text": row.get("Convicted Details", ""),
        "case": row.get("Pending Case", ""),
        "case_text": row.get("Case Details", ""),
        "dismissed": row.get("Dismissed", ""),
        "dismissed_text": row.get("Dismissed Details", ""),
        "disciplinary": row.get("Disciplinary", ""),
        "disciplinary_text": row.get("Disciplinary Details", ""),
        "resigned": row.get("Resigned", ""),
        "resigned_text": row.get("Resigned Details", ""),
        "discharged": row.get("Discharged", ""),
        "pub_pri": row.get("Business with State", ""),
        "pub_pri_text": row.get("Business Details", ""),
        "pub_ser": row.get("Relinquish Business", ""),
        "pri_sec": row.get("Private Sector Exp", ""),
        "pub_sec": row.get("Public Sector Exp", ""),
        "reg_date": safe_strptime(row.get("Registration Date", ""), "%Y-%m-%d"),
        "reg_num": row.get("Registration Number", ""),
    }

    # Correspondence Preferences
    resume_data["corr_prefs"] = {
        "lang_pref": row.get("Language Preference", ""),
        "method": row.get("Method", ""),
        "contact_text": row.get("Contact Details", ""),
    }

    # Languages (up to 5)
    resume_data["languages"] = []
    for i in range(1, 6):
        lang = {
            "name": row.get(f"Language{i}_Name", ""),
            "speak": row.get(f"Language{i}_Speak", ""),
            "read": row.get(f"Language{i}_Read", ""),
        }
        if lang["name"]:
            resume_data["languages"].append(lang)

    # Education (up to 4)
    resume_data["education"] = []
    for i in range(1, 5):
        edu = {
            "institution": row.get(f"Education{i}_Institution", ""),
            "degree": row.get(f"Education{i}_Degree", ""),
            "field": row.get(f"Education{i}_Field", ""),
            "location": row.get(f"Education{i}_Location", ""),
            "graduation_date": row.get(f"Education{i}_Graduation", ""),
        }
        if edu["institution"]:
            resume_data["education"].append(edu)

    # Current Qualification
    resume_data["current_qual"] = {
        "current_qual": row.get("Current Qualification", ""),
    }

    # Work Experience (up to 3)
    resume_data["work_experience"] = []
    for i in range(1, 4):
        exp = {
            "job_title": row.get(f"Work{i}_JobTitle", ""),
            "company": row.get(f"Work{i}_Company", ""),
            "dates_start": safe_strptime(row.get(f"Work{i}_StartDate", ""), "%Y-%m-%d"),
            "dates_end": safe_strptime(row.get(f"Work{i}_EndDate", ""), "%Y-%m-%d"),
            "reason": row.get(f"Work{i}_Reason", ""),
        }
        if exp["job_title"]:
            resume_data["work_experience"].append(exp)

    # Public Service Reappointment
    resume_data["corr_pref"] = {
        "pub_ser": row.get("Condition Preventing", ""),
        "pre_depart": row.get("Previous Department", ""),
    }

    # References (up to 3)
    resume_data["references"] = []
    for i in range(1, 4):
        ref = {
            "name": row.get(f"Reference{i}_Name", ""),
            "relationship": row.get(f"Reference{i}_Relationship", ""),
            "contact": row.get(f"Reference{i}_Contact", ""),
        }
        if ref["name"]:
            resume_data["references"].append(ref)

    # Declaration
    resume_data["declaration"] = {
        "signature": row.get("Signature", ""),
        "date_signed": safe_strptime(row.get("Date Signed", ""), "%Y-%m-%d"),
    }

    # Creation Date
    resume_data["creation_date"] = row.get("Creation Date", "")

    return resume_data

def load_user_data(email):
    """Load user data from USER_DATA_WORKSHEET_NAME worksheet based on email."""
    worksheet = connect_to_google_sheets(USER_SHEET_NAME, USER_DATA_WORKSHEET_NAME)
    if not worksheet:
        return None
    records = worksheet.get_all_records()
    user_record = next((record for record in records if record.get("Email") == email), None)
    if user_record:
        return parse_user_data(user_record)
    return None

def to_str(item):
    """Convert an item to a string, formatting dates as YYYY-MM-DD."""
    if isinstance(item, (date, datetime)):
        return item.strftime("%Y-%m-%d")
    return str(item) if item is not None else ""

def prepare_user_data(resume_data):
    """Prepare resume_data as a flat list for Google Sheets, converting dates to strings."""
    data = []

    # Personal Information
    personal_info = resume_data.get("personal_info", {})
    data.extend([
        to_str(personal_info.get("full_name")),
        to_str(personal_info.get("surname")),
        to_str(personal_info.get("email")),
        to_str(personal_info.get("phone")),
        to_str(personal_info.get("id_num")),
        to_str(personal_info.get("pas_num")),
        to_str(personal_info.get("birth_date")),
        to_str(personal_info.get("sa_citi")),
        to_str(personal_info.get("nationality")),
        to_str(personal_info.get("gender")),
        to_str(personal_info.get("race")),
        to_str(personal_info.get("disability")),
        to_str(personal_info.get("p_location")),
        to_str(personal_info.get("linkedin")),
        to_str(personal_info.get("other_profiles")),
    ])

    # Additional Personal Information
    personal_add_info = resume_data.get("personal_add_info", {})
    data.extend([
        to_str(personal_add_info.get("convicted")),
        to_str(personal_add_info.get("convicted_text")),
        to_str(personal_add_info.get("case")),
        to_str(personal_add_info.get("case_text")),
        to_str(personal_add_info.get("dismissed")),
        to_str(personal_add_info.get("dismissed_text")),
        to_str(personal_add_info.get("disciplinary")),
        to_str(personal_add_info.get("disciplinary_text")),
        to_str(personal_add_info.get("resigned")),
        to_str(personal_add_info.get("resigned_text")),
        to_str(personal_add_info.get("discharged")),
        to_str(personal_add_info.get("pub_pri")),
        to_str(personal_add_info.get("pub_pri_text")),
        to_str(personal_add_info.get("pub_ser")),
        to_str(personal_add_info.get("pri_sec")),
        to_str(personal_add_info.get("pub_sec")),
        to_str(personal_add_info.get("reg_date")),
        to_str(personal_add_info.get("reg_num")),
    ])

    # Correspondence Preferences
    corr_prefs = resume_data.get("corr_prefs", {})
    data.extend([
        to_str(corr_prefs.get("lang_pref")),
        to_str(corr_prefs.get("method")),
        to_str(corr_prefs.get("contact_text")),
    ])

    # Languages (up to 5)
    languages = resume_data.get("languages", [])
    for i in range(5):
        if i < len(languages):
            lang = languages[i]
            data.extend([
                to_str(lang.get("name")),
                to_str(lang.get("speak")),
                to_str(lang.get("read")),
            ])
        else:
            data.extend(["", "", ""])

    # Education (up to 4)
    education = resume_data.get("education", [])
    for i in range(4):
        if i < len(education):
            edu = education[i]
            data.extend([
                to_str(edu.get("institution")),
                to_str(edu.get("degree")),
                to_str(edu.get("field")),
                to_str(edu.get("location")),
                to_str(edu.get("graduation_date")),
            ])
        else:
            data.extend(["", "", "", "", ""])

    # Current Qualification
    current_qual = resume_data.get("current_qual", {})
    data.append(to_str(current_qual.get("current_qual")))

    # Work Experience (up to 3)
    work_experience = resume_data.get("work_experience", [])
    for i in range(3):
        if i < len(work_experience):
            exp = work_experience[i]
            data.extend([
                to_str(exp.get("job_title")),
                to_str(exp.get("company")),
                to_str(exp.get("dates_start")),
                to_str(exp.get("dates_end")),
                to_str(exp.get("reason")),
            ])
        else:
            data.extend(["", "", "", "", ""])

    # Public Service Reappointment
    corr_pref = resume_data.get("corr_pref", {})
    data.extend([
        to_str(corr_pref.get("pub_ser")),
        to_str(corr_pref.get("pre_depart")),
    ])

    # References (up to 3)
    references = resume_data.get("references", [])
    for i in range(3):
        if i < len(references):
            ref = references[i]
            data.extend([
                to_str(ref.get("name")),
                to_str(ref.get("relationship")),
                to_str(ref.get("contact")),
            ])
        else:
            data.extend(["", "", ""])

    # Declaration
    declaration = resume_data.get("declaration", {})
    data.extend([
        to_str(declaration.get("signature")),
        to_str(declaration.get("date_signed")),
    ])

    # Creation Date
    data.append(to_str(resume_data.get("creation_date")))

    return data