# Google Sheets
JOB_SHEET_NAME = "Job Data"
JOB_WORKSHEET_NAME = "JobData"
USER_SHEET_NAME = "Users"
USER_LOGIN_WORKSHEET_NAME = "UserLogin"
USER_DATA_WORKSHEET_NAME = "UserData"

# Session Keys
SESSION_KEYS = {
    "signup_clicked": False,
    "login_clicked": False,
    "signup_login": False,
    "current_user": None,
    "current_app_state": "Jobs",
    "current_section": "Application Form",
    "resume_page": 0,
    "app_form_page": 0,
}

JOB_SESSION_KEYS = {
    "current_page": 1,
    "dialog_open": False,
    "selected_job": None,
    "filter_department": "All",
    "filter_province": "All",
    "filter_city": "All",
    "selection_dialog_open": False,
    "filtered_jobs": [],
}

# Application Form Constants
RACE = ["African", "White", "Coloured", "Indian", "Other"]
CORRESP = ["Post", "E-mail", "Fax", "Telephone"]
LANGS = ["English", "Afrikaans", "Zulu", "Other"]
YES_NO = ["Yes", "No"]
LANG_LEVELS = [" ", "Good", "Fair", "Poor"]
GENDER = ["Female","Male"]

NUM_LANGUAGES = 5
NUM_QUALIFICATIONS = 4
NUM_EMPLOYMENT_HISTORIES = 3
NUM_REFERENCES = 3

RESUME_SECTIONS = [
    "Personal Information", "Professional Summary", "Work Experience",
    "Education", "Skills", "Certifications & Professional Development",
    "Projects", "Additional Information", "References", "Review & Download"
]

APP_FORM_SECTIONS = [
    "Personal Information", "Correspondence Preferences", "Languages",
    "Formal Qualifications", "Employment History", "Public Service Reappointment",
    "References", "Declaration"
]

# UI Labels
BUTTON_LABELS = {
    "signup": ("Sign Up :material/how_to_reg:", "signup_button"),
    "login": ("Login :material/login:", "login_button"),
    "logout": ("Logout :material/logout:", "logout_button"),
}

PAGE_SIZE = 3

USER_DATA_HEADERS = [
    "Full Name", "Surname", "Email", "Phone", "ID Number", "Passport Number", "Birth Date", 
    "SA Citizen", "Nationality", "Gender", "Race", "Disability", "Location", "LinkedIn", "Other Profiles",
    "Convicted", "Convicted Details", "Pending Case", "Case Details", "Dismissed", "Dismissed Details", 
    "Disciplinary", "Disciplinary Details", "Resigned", "Resigned Details", "Discharged", 
    "Business with State", "Business Details", "Relinquish Business", "Private Sector Exp", 
    "Public Sector Exp", "Registration Date", "Registration Number",
    "Language Preference", "Method", "Contact Details",
    "Language1_Name", "Language1_Speak", "Language1_Read",
    "Language2_Name", "Language2_Speak", "Language2_Read",
    "Language3_Name", "Language3_Speak", "Language3_Read",
    "Language4_Name", "Language4_Speak", "Language4_Read",
    "Language5_Name", "Language5_Speak", "Language5_Read",
    "Education1_Institution", "Education1_Degree", "Education1_Field", "Education1_Location", "Education1_Graduation",
    "Education2_Institution", "Education2_Degree", "Education2_Field", "Education2_Location", "Education2_Graduation",
    "Education3_Institution", "Education3_Degree", "Education3_Field", "Education3_Location", "Education3_Graduation",
    "Education4_Institution", "Education4_Degree", "Education4_Field", "Education4_Location", "Education4_Graduation",
    "Current Qualification",
    "Work1_JobTitle", "Work1_Company", "Work1_StartDate", "Work1_EndDate", "Work1_Reason",
    "Work2_JobTitle", "Work2_Company", "Work2_StartDate", "Work2_EndDate", "Work2_Reason",
    "Work3_JobTitle", "Work3_Company", "Work3_StartDate", "Work3_EndDate", "Work3_Reason",
    "Condition Preventing", "Previous Department",
    "Reference1_Name", "Reference1_Relationship", "Reference1_Contact",
    "Reference2_Name", "Reference2_Relationship", "Reference2_Contact",
    "Reference3_Name", "Reference3_Relationship", "Reference3_Contact",
    "Signature", "Date Signed",
    "Creation Date"
]
USER_LOGIN_HEADERS = ["name", "surname", "email", "phone", "password", "creation"]