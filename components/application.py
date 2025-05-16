import streamlit as st
from datetime import datetime
import json
from fillpdf import fillpdfs
import base64
from utils.helpers import parse_user_data, prepare_user_data
from utils.google_sheets import connect_to_google_sheets, add_new_row, find_and_update_row
from utils.constants import (
    YES_NO, GENDER, RACE, CORRESP, LANGS, LANG_LEVELS, NUM_LANGUAGES, NUM_QUALIFICATIONS, NUM_EMPLOYMENT_HISTORIES,
    NUM_REFERENCES, RESUME_SECTIONS, APP_FORM_SECTIONS, USER_SHEET_NAME, USER_DATA_WORKSHEET_NAME
)

def initialize_session_state():
    """Initialize session state variables."""
    if "current_section" not in st.session_state:
        st.session_state.current_section = "Application Form"
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = {
            "creation_date": datetime.now().strftime("%Y-%m-%d"),
            "personal_info": {},
            "personal_add_info": {},
            "corr_prefs": {},
            "current_qual": {},
            "professional_summary": {},
            "work_experience": [],
            "education": [],
            "languages": [],
            "skills": [],
            "certifications": [],
            "projects": [],
            "additional_info": {},
            "references": [],
            "declaration": {}
        }
    # Add flags to clear inputs for Languages, Education, Work Experience, and References
    if "clear_language_input" not in st.session_state:
        st.session_state.clear_language_input = False
    if "clear_education_input" not in st.session_state:
        st.session_state.clear_education_input = False
    if "clear_work_experience_input" not in st.session_state:
        st.session_state.clear_work_experience_input = False
    if "clear_references_input" not in st.session_state:
        st.session_state.clear_references_input = False
    if "clear_skill_input" not in st.session_state:
        st.session_state.clear_skill_input = False

def z83(jobx=None):
    """Generate Z83 form PDF."""
    form_fields = fillpdfs.get_form_fields("editable Approved New Z83 form Gazetted 6 Nov 2020.pdf")

    def get_nested(data, keys, default=""):
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
            else:
                return default
        return data if data is not None else default
    if jobx != None:
        form_fields['Position for which you are applying as advertised'] = jobx.get('Position Title', '')
        form_fields['Department where the position was advertised'] = jobx.get('Department', '')
        form_fields['Reference number as stated in the advert'] =  jobx.get('Reference Number', '')
        form_fields['If you are offered the position when can you start OR how much notice must you serve with your current employer'] = "immediate"

    personal_info = st.session_state.resume_data.get("personal_info", {})
    form_fields["Surname and Full names"] = get_nested(personal_info, ["full_name"])
    form_fields["Surname and Full names_2"] = get_nested(personal_info, ["surname"])
    birth_date = get_nested(personal_info, ["birth_date"])
    if isinstance(birth_date, datetime):
        form_fields["DDMMYY"] = birth_date.strftime("%d%m%y")
    else:
        form_fields["DDMMYY"] = birth_date
    form_fields["Identity Number"] = get_nested(personal_info, ["id_num"])
    form_fields["Passport2 number"] = get_nested(personal_info, ["pas_num"])
    race_mapping = {"African": "Choice1", "White": "Choice2", "Coloured": "Choice3", "Indian": "Choice4", "Other": "Choice5"}
    form_fields["Group2"] = race_mapping.get(get_nested(personal_info, ["race"]), "")
    gender_mapping = {"Female": "Choice6", "Male": "Choice7"}
    form_fields["Group3"] = gender_mapping.get(get_nested(personal_info, ["gender"]), "")
    yes_no_mapping = {"Yes": "Choice6", "No": "Choice7"}
    yes_no_mapping_2 = {"Yes": "Choice1", "No": "Choice2"}
    form_fields["Group4"] = yes_no_mapping.get(get_nested(personal_info, ["disability"]), "")
    form_fields["Group5"] = yes_no_mapping.get(get_nested(personal_info, ["sa_citi"]), "")
    form_fields["Text5"] = get_nested(personal_info, ["nationality"])
    form_fields["Group6"] = yes_no_mapping.get(get_nested(personal_info, ["work_permit"]), "")
    personal_add_info = st.session_state.resume_data.get("personal_add_info", {})
    form_fields["Group7"] = yes_no_mapping.get(get_nested(personal_add_info, ["convicted"]), "")
    form_fields["Text6"] = get_nested(personal_add_info, ["convicted_text"])
    form_fields["Group8"] = yes_no_mapping.get(get_nested(personal_add_info, ["case"]), "")
    form_fields["Text7"] = get_nested(personal_add_info, ["case_text"])
    form_fields["Group9"] = yes_no_mapping.get(get_nested(personal_add_info, ["dismissed"]), "")
    form_fields["Text8"] = get_nested(personal_add_info, ["dismissed_text"])
    form_fields["Group10"] = yes_no_mapping.get(get_nested(personal_add_info, ["disciplinary"]), "")
    form_fields["Text9"] = get_nested(personal_add_info, ["disciplinary_text"])
    form_fields["Group11"] = yes_no_mapping.get(get_nested(personal_add_info, ["resigned"]), "")
    form_fields["Text10"] = get_nested(personal_add_info, ["resigned_text"])
    form_fields["Group12"] = yes_no_mapping.get(get_nested(personal_add_info, ["discharged"]), "")
    form_fields["Group13"] = yes_no_mapping.get(get_nested(personal_add_info, ["pub_pri"]), "")
    form_fields["Text11"] = get_nested(personal_add_info, ["pub_pri_text"])
    form_fields["Group14"] = yes_no_mapping.get(get_nested(personal_add_info, ["pub_ser"]), "")
    form_fields["Text12"] = get_nested(personal_add_info, ["pri_sec"])
    form_fields["Text14"] = get_nested(personal_add_info, ["pub_sec"])
    form_fields["Text15"] = str(get_nested(personal_add_info, ["reg_date"])) if get_nested(personal_add_info, ["reg_date"]) else "N/A"
    form_fields["Text16"] = get_nested(personal_add_info, ["reg_num"])
    full_name = get_nested(personal_info, ["full_name"])
    surname = get_nested(personal_info, ["surname"])
    form_fields["Text1"] = "".join([n[0].upper() for n in f"{full_name} {surname}".split() if n])
    corr_prefs = st.session_state.resume_data.get("corr_prefs", {})
    form_fields["Preferred language for correspondence"] = get_nested(corr_prefs, ["lang_pref"])
    corr_mapping = {"Post": "Choice1", "E-mail": "Choice2", "Fax": "Choice3", "Telephone": "Choice4"}
    form_fields["Group16"] = corr_mapping.get(get_nested(corr_prefs, ["method"]), "")
    form_fields["Contact details in terms of the above"] = get_nested(corr_prefs, ["contact_text"])
    languages = st.session_state.resume_data.get("languages", [])
    for i in range(5):
        lang = languages[i] if i < len(languages) else {}
        form_field_name = f"Languages specifyRow1{'_' + str(i+1) if i > 0 else ''}"
        form_fields[form_field_name] = lang.get("name", "")
        form_fields[f"Dropdown3.0.{i}"] = lang.get("speak", "")
        form_fields[f"Dropdown3.1.{i}"] = lang.get("read", "")
    education = st.session_state.resume_data.get("education", [])
    for i in range(4):
        edu = education[i] if i < len(education) else {}
        form_fields[f"Name of SchoolTechnical CollegeRow{i+1}"] = edu.get("institution", "")
        form_fields[f"Name of qualification obtainedRow{i+1}"] = f"{edu.get('degree', '')} {edu.get('field', '')}".strip()
        form_fields[f"Year obtainedRow{i+1}"] = edu.get("graduation_date", "")
    current_qual = st.session_state.resume_data.get("current_qual", {})
    form_fields["Current study institution and qualification"] = get_nested(current_qual, ["current_qual"])
    work_experience = st.session_state.resume_data.get("work_experience", [])
    for i in range(3):
        exp = work_experience[i] if i < len(work_experience) else {}
        form_fields[f"Employer including current employerRow{i+1}"] = exp.get("company", "")
        form_fields[f"Post heldRow{i+1}"] = exp.get("job_title", "")
        form_fields[f"Dropdown1.{i}.0"] = exp.get("dates_start").month if exp.get("dates_start") != None else " "
        form_fields[f"YYRow{i+1}"] = exp.get("dates_start").year if exp.get("dates_start") != None else " "
        form_fields[f"Dropdown1.{i}.1"] = exp.get("dates_end", " ").month if exp.get("dates_end") != None else " "
        form_fields[f"YYRow{i+1}_2"] = exp.get("dates_end", " ").year if exp.get("dates_end") != None else " "
        form_fields[f"Reason for leavingRow{i+1}"] = exp.get("reason", "")
    corr_pref = st.session_state.resume_data.get("corr_pref", {})
    form_fields["Group17"] = yes_no_mapping_2.get(get_nested(corr_pref, ["pub_ser"]), "Choice2")
    form_fields["If yes Provide the name of the previous employing department and indicate the nature of the condition"] = get_nested(corr_pref, ["pre_depart"])
    references = st.session_state.resume_data.get("references", [])
    for i in range(3):
        ref = references[i] if i < len(references) else {}
        form_fields[f"NameRow{i+1}"] = ref.get("name", "")
        form_fields[f"Relationship to youRow{i+1}"] = ref.get("relationship", "")
        form_fields[f"Tel No office hoursRow{i+1}"] = ref.get("contact", "")
    declaration = st.session_state.resume_data.get("declaration", {})
    form_fields["Signature"] = get_nested(declaration, ["signature"])
    date_signed = get_nested(declaration, ["date_signed"])
    form_fields["Date"] = date_signed.strftime("%Y-%m-%d") if isinstance(date_signed, datetime) else date_signed
    form_fields["Initials"] = form_fields["Text1"]
    pdf_name = "newpdf_z83_"+str(get_nested(personal_info, ["id_num"]))+".pdf"
    try:
        fillpdfs.write_fillable_pdf(
            input_pdf_path="editable Approved New Z83 form Gazetted 6 Nov 2020.pdf",
            output_pdf_path = pdf_name,
            data_dict=form_fields
        )
        st.success("Z83 form generated successfully as 'newpdf.pdf'!")

        # Display the PDF
        if jobx == None:
            with open(pdf_name, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button(
                    label="Download Z83 Form",
                    data=pdf_bytes,
                    file_name="Z83_Form_"+str(get_nested(personal_info, ["id_num"]))+".pdf",
                    mime="application/pdf",
                    key="download_z83_pdf", use_container_width=True
            )
        else:
            with open(pdf_name, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button(
                    label="Download Z83 Form",
                    data=pdf_bytes,
                    file_name="Z83_Form_"+str(get_nested(personal_info, ["id_num"]))+"_"+jobx.get('Reference Number', '')+".pdf",
                    mime="application/pdf",
                    key="download_z83_pdf", use_container_width=True)
        
        # Optionally embed the PDF for inline viewing
        st.markdown("### Preview Z83 Form")
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" width="100%" height="600px"></iframe>',
            unsafe_allow_html=True
        )

    except FileNotFoundError:
        st.error("Failed to generate PDF: Input PDF file not found.")
        return
    except Exception as e:
        st.error(f"Failed to generate PDF: {type(e).__name__}: {str(e)}")
        return
    if jobx == None:
        # Connect to the worksheet
        worksheet = connect_to_google_sheets(USER_SHEET_NAME, USER_DATA_WORKSHEET_NAME)
        if not worksheet:
            st.error("Could not connect to the user data worksheet.")
            return

        # Prepare the data from resume_data
        data = prepare_user_data(st.session_state.resume_data)

        # Get the user's email from resume_data
        email = st.session_state.resume_data.get("personal_info", {}).get("email", "").lower()

        if not email:
            st.error("Email is required to save application data.")
            return

        # Check if the user's data already exists by email (Email is in column 3, index 2)
        if find_and_update_row(worksheet, 2, email, data):
            st.success("Application data updated successfully in Google Sheets!")
        else:
            # If no existing row was found, add a new row
            if add_new_row(worksheet, data):
                st.success("Application data saved successfully to Google Sheets!")
            else:
                st.error("Failed to save application data to Google Sheets.")

# --- Application Form Sections ---

def save_personal_info():
    """Save personal information from the form."""
    personal_info = st.session_state.resume_data.get("personal_info", {})
    surname = st.session_state.get("surname", personal_info.get("surname", ""))
    full_name = st.session_state.get("full_names", personal_info.get("full_name", ""))
    birth_date = st.session_state.get("dob", personal_info.get("birth_date", None))
    sa_citi = st.session_state.get("citizenship_radio", personal_info.get("sa_citi", "Yes"))
    id_num = st.session_state.get("id_number", personal_info.get("id_num", ""))
    phone = st.session_state.get("resume_phone", personal_info.get("phone", ""))
    email = st.session_state.get("resume_email", personal_info.get("email", "")).lower()
    race = st.session_state.get("race_select", personal_info.get("race", "African"))
    pas_num = st.session_state.get("passport_number", personal_info.get("pas_num", ""))
    work_permit = st.session_state.get("work_permit_radio", personal_info.get("work_permit", "Yes"))
    p_location = st.session_state.get("resume_location", personal_info.get("p_location", ""))
    nationality = st.session_state.get("nationality", personal_info.get("nationality", ""))
    gender = st.session_state.get("gender_radio", personal_info.get("gender", "Female"))
    linkedin = st.session_state.get("resume_linkedin", personal_info.get("linkedin", ""))
    other_profiles = st.session_state.get("resume_other_profiles", personal_info.get("other_profiles", ""))
    disability = st.session_state.get("disability_radio", personal_info.get("disability", "No"))

    if not full_name or not email:
        st.error("Full name and email are required.")
        return False
    elif len(id_num) != 13 and sa_citi == "Yes":
        st.error("South African ID number must be 13 digits.")
        return False
    else:
        st.session_state.resume_data["personal_info"] = {
            "full_name": full_name, 
            "surname": surname, 
            "birth_date": birth_date,
            "sa_citi": sa_citi, 
            "work_permit": work_permit, 
            "id_num": id_num,
            "pas_num": pas_num, 
            "race": race, 
            "nationality": "N/A" if sa_citi == "Yes" else nationality,
            "gender": gender, 
            "disability": disability, 
            "p_location": p_location,
            "phone": phone, 
            "email": email, 
            "linkedin": linkedin,
            "other_profiles": other_profiles
        }
        st.success("Personal Information saved!")
        return True

def create_personal_info():
    """Handle personal information section."""
    with st.expander("Personal Information", expanded=False):
        personal_info = st.session_state.resume_data.get("personal_info", {})
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Surname", value=personal_info.get("surname", ""), key="surname")
            st.text_input("Full names", value=personal_info.get("full_name", ""), key="full_names")
            st.date_input("Date of Birth", value=personal_info.get("birth_date", None), key="dob")
            st.radio("South African citizen", YES_NO, index=YES_NO.index(personal_info.get("sa_citi", "Yes")), key="citizenship_radio", horizontal=True)
            st.text_input("Identity Number", value=personal_info.get("id_num", ""), key="id_number")
            st.text_input("Phone Number", value=personal_info.get("phone", ""), key="resume_phone")
            st.text_input("Professional Email", value=personal_info.get("email", ""), key="resume_email")
            st.selectbox("Race", RACE, index=RACE.index(personal_info.get("race", "African")), key="race_select")
        with col2:
            st.text_input("Passport Number", value=personal_info.get("pas_num", ""), key="passport_number")
            st.radio("Work permit", YES_NO, index=YES_NO.index(personal_info.get("work_permit", "Yes")), key="work_permit_radio", horizontal=True)
            st.text_input("Location (City, State/Province, Country)", value=personal_info.get("p_location", ""), key="resume_location")
            st.text_input("Nationality", value=personal_info.get("nationality", ""), key="nationality")
            st.radio("Gender", GENDER, index=GENDER.index(personal_info.get("gender", "Male")), key="gender_radio", horizontal=True)
            st.text_input("LinkedIn URL", value=personal_info.get("linkedin", ""), key="resume_linkedin")
            st.text_input("Other Professional Profiles", value=personal_info.get("other_profiles", ""), key="resume_other_profiles")
            st.radio("Disability", YES_NO, index=YES_NO.index(personal_info.get("disability", "No")), key="disability_radio", horizontal=True)

        if st.button("Save Personal Information", key="save_resume_personal_info"):
            save_personal_info()

def save_add_personal_info():
    """Save additional personal information from the form."""
    personal_add_info = st.session_state.resume_data.get("personal_add_info", {})
    convicted = st.session_state.get("convicted_radio", personal_add_info.get("convicted", "No"))
    convicted_text = st.session_state.get("convicted_txt", personal_add_info.get("convicted_text", ""))
    case = st.session_state.get("case_radio", personal_add_info.get("case", "No"))
    case_text = st.session_state.get("case_txt", personal_add_info.get("case_text", ""))
    dismissed = st.session_state.get("dismissed_radio", personal_add_info.get("dismissed", "No"))
    dismissed_text = st.session_state.get("dismissed_txt", personal_add_info.get("dismissed_text", ""))
    disciplinary = st.session_state.get("disciplinary_radio", personal_add_info.get("disciplinary", "No"))
    disciplinary_text = st.session_state.get("disciplinary_txt", personal_add_info.get("disciplinary_text", ""))
    resigned = st.session_state.get("resigned_radio", personal_add_info.get("resigned", "No"))
    resigned_text = st.session_state.get("resigned_txt", personal_add_info.get("resigned_text", ""))
    pub_pri = st.session_state.get("pub_pri_radio", personal_add_info.get("pub_pri", "No"))
    pub_pri_text = st.session_state.get("pub_pri_txt", personal_add_info.get("pub_pri_text", ""))
    discharged = st.session_state.get("discharged_radio", personal_add_info.get("discharged", "No"))
    pub_ser = st.session_state.get("pub_ser_radio", personal_add_info.get("pub_ser", "No"))
    pri_sec = st.session_state.get("pri_sec", personal_add_info.get("pri_sec", ""))
    pub_sec = st.session_state.get("pub_sec", personal_add_info.get("pub_sec", ""))
    reg_date = st.session_state.get("reg_date", personal_add_info.get("reg_date", None))
    reg_num = st.session_state.get("reg_num", personal_add_info.get("reg_num", ""))

    st.session_state.resume_data["personal_add_info"] = {
        "convicted": convicted, 
        "convicted_text": convicted_text if convicted == "Yes" else "N/A",
        "case": case, 
        "case_text": case_text if case == "Yes" else "N/A",
        "dismissed": dismissed, 
        "dismissed_text": dismissed_text if dismissed == "Yes" else "N/A",
        "disciplinary": disciplinary, 
        "disciplinary_text": disciplinary_text if disciplinary == "Yes" else "N/A",
        "resigned": resigned, 
        "resigned_text": resigned_text if resigned == "Yes" else "N/A",
        "discharged": discharged, 
        "pub_pri": pub_pri, 
        "pub_pri_text": pub_pri_text if pub_pri == "Yes" else "N/A",
        "pub_ser": pub_ser, 
        "pri_sec": pri_sec, 
        "pub_sec": pub_sec,
        "reg_date": "N/A" if not reg_date else reg_date,
        "reg_num": "N/A" if not reg_num else reg_num,
    }
    st.success("Additional Personal Information saved!")
    return True

def create_add_personal_info():
    """Handle additional personal information section."""
    with st.expander("Additional Personal Information", expanded=False):
        personal_add_info = st.session_state.resume_data.get("personal_add_info", {})
        col1, col2 = st.columns(2)
        with col1:
            st.radio("Have you been convicted?", YES_NO, index=YES_NO.index(personal_add_info.get("convicted", "No")), key="convicted_radio", horizontal=True)
            st.text_input("If yes, provide details", value=personal_add_info.get("convicted_text", ""), key="convicted_txt", disabled=st.session_state.get("convicted_radio") == "No")
            st.radio("Do you have any pending criminal case?", YES_NO, index=YES_NO.index(personal_add_info.get("case", "No")), key="case_radio", horizontal=True)
            st.text_input("If yes, provide details", value=personal_add_info.get("case_text", ""), key="case_txt", disabled=st.session_state.get("case_radio") == "No")
            st.radio("Dismissed for misconduct from Public Service?", YES_NO, index=YES_NO.index(personal_add_info.get("dismissed", "No")), key="dismissed_radio", horizontal=True)
            st.text_input("If yes, provide details", value=personal_add_info.get("dismissed_text", ""), key="dismissed_txt", disabled=st.session_state.get("dismissed_radio") == "No")
            st.radio("Pending disciplinary case?", YES_NO, index=YES_NO.index(personal_add_info.get("disciplinary", "No")), key="disciplinary_radio", horizontal=True)
            st.text_input("If yes, provide details", value=personal_add_info.get("disciplinary_text", ""), key="disciplinary_txt", disabled=st.session_state.get("disciplinary_radio") == "No")
            st.radio("Resigned pending disciplinary proceeding?", YES_NO, index=YES_NO.index(personal_add_info.get("resigned", "No")), key="resigned_radio", horizontal=True)
            st.text_input("If yes, provide details", value=personal_add_info.get("resigned_text", ""), key="resigned_txt", disabled=st.session_state.get("resigned_radio") == "No")
        with col2:
            st.radio("Conducting business with the State?", YES_NO, index=YES_NO.index(personal_add_info.get("pub_pri", "No")), key="pub_pri_radio", horizontal=True)
            st.text_input("If yes, provide details", value=personal_add_info.get("pub_pri_text", ""), key="pub_pri_txt", disabled=st.session_state.get("pub_pri_radio") == "No")
            st.radio("Discharged/retired due to ill-health?", YES_NO, index=YES_NO.index(personal_add_info.get("discharged", "No")), key="discharged_radio", horizontal=True)
            st.radio("Relinquish business interests if employed?", YES_NO, index=YES_NO.index(personal_add_info.get("pub_ser", "No")), key="pub_ser_radio", horizontal=True)
            st.write("Total years of experience:")
            st.text_input("Private Sector", value=personal_add_info.get("pri_sec", ""), key="pri_sec")
            st.text_input("Public Sector", value=personal_add_info.get("pub_sec", ""), key="pub_sec")
            st.write("If your profession requires registration:")
            st.date_input("Registration Date", value=None if personal_add_info.get("reg_date")=="N/A" else personal_add_info.get("reg_date",None), key="reg_date")
            st.text_input("Registration Number", value=personal_add_info.get("reg_num", ""), key="reg_num")

        if st.button("Save Additional Personal Information", key="save_add_personal_info"):
            save_add_personal_info()

def save_correspondence_prefs():
    """Save correspondence preferences from the form."""
    corr_prefs = st.session_state.resume_data.get("corr_prefs", {})
    lang_pref = st.session_state.get("pref_lang_select", corr_prefs.get("lang_pref", "English"))
    method = st.session_state.get("corr_method_radio", corr_prefs.get("method", "Post"))
    contact_text = st.session_state.get("contact_details", corr_prefs.get("contact_text", ""))

    if not contact_text:
        st.error("Contact details are required.")
        return False
    else:
        st.session_state.resume_data["corr_prefs"] = {
            "lang_pref": lang_pref, "method": method, "contact_text": contact_text
        }
        st.success("Correspondence Preferences saved!")
        return True

def create_correspondence_prefs():
    """Handle correspondence preferences section."""
    with st.expander("Correspondence Preferences", expanded=False):
        corr_prefs = st.session_state.resume_data.get("corr_prefs", {})
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Preferred language", LANGS, index=LANGS.index(corr_prefs.get("lang_pref", "English")), key="pref_lang_select")
        with col2:
            method = st.radio("Method for correspondence", CORRESP, index=CORRESP.index(corr_prefs.get("method", "Post")), key="corr_method_radio", horizontal=True)
            contact_label = {"Post": "Postal Address", "E-mail": "Email Address", "Fax": "Fax Number", "Telephone": "Phone Number"}.get(method, "Contact details")
            st.text_input(contact_label, value=corr_prefs.get("contact_text", ""), key="contact_details")

        if st.button("Save Correspondence Preferences", key="save_corr_prefs"):
            save_correspondence_prefs()

def save_languages():
    """Save languages from the form (if a new language is being added)."""
    lang_name = st.session_state.get("lang_name", "")
    lang_speak = st.session_state.get("lang_speak", "")
    lang_read = st.session_state.get("lang_read", "")

    if lang_name:
        if not lang_name:
            st.error("Language name is required.")
            return False
        else:
            st.session_state.resume_data.setdefault("languages", []).append({
                "name": lang_name, "speak": lang_speak, "read": lang_read
            })
            st.success("Language added!")
            st.session_state.clear_language_input = True
            st.rerun()
    return True

def create_languages():
    """Handle languages section."""
    with st.expander("Languages", expanded=False):
        if st.session_state.resume_data.get("languages", []):
            st.subheader("Current Languages")
            for i, lang in enumerate(st.session_state.resume_data["languages"]):
                with st.container(border=True):
                #with st.expander(f"{lang.get('name', 'Language')}", expanded=False):
                    st.write(f"**Speak Level:** {lang.get('speak', '')}")
                    st.write(f"**Read/Write Level:** {lang.get('read', '')}")
                    if st.button(f"Remove Language {i+1}", key=f"remove_lang_{i}"):
                        st.session_state.resume_data["languages"].pop(i)
                        st.rerun()

        st.subheader("Add New Language")
        lang_name_default = "" if st.session_state.clear_language_input else st.session_state.get("lang_name", "")
        lang_speak_default = " " if st.session_state.clear_language_input else st.session_state.get("lang_speak", " ")
        lang_read_default = " " if st.session_state.clear_language_input else st.session_state.get("lang_read", " ")

        st.text_input("Language Name", value=lang_name_default, key="lang_name")
        st.selectbox("Speak Level", LANG_LEVELS, index=LANG_LEVELS.index(lang_speak_default), key="lang_speak")
        st.selectbox("Read/Write Level", LANG_LEVELS, index=LANG_LEVELS.index(lang_read_default), key="lang_read")

        if st.button("Add Language", key="add_lang"):
            save_languages()

        if st.session_state.clear_language_input:
            st.session_state.clear_language_input = False

def save_education_history():
    """Save education history from the form (if a new education entry is being added)."""
    current_qual = st.session_state.get("current_qual", "")
    degree = st.session_state.get("edu_degree", "")
    field = st.session_state.get("edu_field", "")
    institution = st.session_state.get("edu_inst", "")
    location = st.session_state.get("edu_loc", "")
    graduation_date = st.session_state.get("edu_date", "")

    st.session_state.resume_data["current_qual"] = {"current_qual": current_qual}

    if degree or institution:
        if not degree or not institution:
            st.error("Degree and institution are required.")
            return False
        else:
            st.session_state.resume_data.setdefault("education", []).append({
                "degree": degree, "field": field, "institution": institution,
                "location": location, "graduation_date": graduation_date
            })
            st.success("Education added!")
            st.session_state.clear_education_input = True
            st.rerun()
    return True

def create_education_history():
    """Handle education history section."""
    with st.expander("Education", expanded=False):
        current_qual_data = st.session_state.resume_data.get("current_qual", {})
        st.subheader("Current Studies")
        st.text_input("Current study institution and qualification", value=current_qual_data.get("current_qual", "N/A"), key="current_qual")

        if st.session_state.resume_data.get("education", []):
            st.subheader("Current Education")
            for i, edu in enumerate(st.session_state.resume_data["education"]):
                with st.container(border=True):
                #with st.expander(f"{edu.get('degree', 'Degree')} in {edu.get('field', 'Field')} - {edu.get('institution', 'Institution')}", expanded=False):
                    st.write(f"**Graduation Date:** {edu.get('graduation_date', '')}")
                    if st.button(f"Remove Education {i+1}", key=f"remove_edu_{i}"):
                        st.session_state.resume_data["education"].pop(i)
                        st.rerun()

        st.subheader("Add New Education")
        degree_default = "" if st.session_state.clear_education_input else st.session_state.get("edu_degree", "")
        field_default = "" if st.session_state.clear_education_input else st.session_state.get("edu_field", "")
        inst_default = "" if st.session_state.clear_education_input else st.session_state.get("edu_inst", "")
        loc_default = "" if st.session_state.clear_education_input else st.session_state.get("edu_loc", "")
        date_default = "" if st.session_state.clear_education_input else st.session_state.get("edu_date", "")

        st.text_input("Degree (e.g., BA, BS, MA, PhD)", value=degree_default, key="edu_degree")
        st.text_input("Field of Study/Major", value=field_default, key="edu_field")
        st.text_input("Institution Name", value=inst_default, key="edu_inst")
        st.text_input("Institution Location", value=loc_default, key="edu_loc")
        st.text_input("Graduation Date (e.g., May 2023)", value=date_default, key="edu_date")

        if st.button("Add Education", key="add_edu"):
            save_education_history()

        if st.session_state.clear_education_input:
            st.session_state.clear_education_input = False

def save_work_experience():
    """Save work experience from the form (if a new position is being added)."""
    pub_ser = st.session_state.get("pub_ser", "No")
    pre_depart = st.session_state.get("pre_depart", "")
    job_title = st.session_state.get("exp_title", "")
    company = st.session_state.get("exp_company", "")
    start_dates = st.session_state.get("exp_dates_start", "")
    end_dates = st.session_state.get("exp_dates_end", "")
    reason = st.session_state.get("exp_reason", "")

    st.session_state.resume_data["corr_pref"] = {"pub_ser": pub_ser, 
                                                 "pre_depart": pre_depart if pub_ser == "Yes" else "N/A"}

    if job_title or company:
        if not job_title or not company:
            st.error("Job title and company are required.")
            return False
        else:
            st.session_state.resume_data.setdefault("work_experience", []).append({
                "job_title": job_title, "company": company, "dates_start": start_dates, "dates_end": end_dates, "reason": reason
            })
            st.session_state.resume_data["work_experience"] = sorted(
                st.session_state.resume_data["work_experience"],
                key=lambda x: x["dates_start"],
                reverse=True
            )
            st.success("Position added!")
            st.session_state.clear_work_experience_input = True
            st.rerun()
    return True

def create_work_experience():
    """Handle work experience section."""
    with st.expander("Work Experience", expanded=False):
        corr_pref = st.session_state.resume_data.get("corr_pref", {})
        st.subheader("Public Service History")
        st.radio("Condition preventing reappointment?", YES_NO, index=YES_NO.index(corr_pref.get("pub_ser", "No")), key="pub_ser", horizontal=True)
        st.text_input("If yes, provide department and condition", value=corr_pref.get("pre_depart", "N/A"), key="pre_depart", disabled=st.session_state.get("pub_ser") == "No")

        if st.session_state.resume_data.get("work_experience", []):
            st.subheader("Current Work Experience")
            for i, exp in enumerate(st.session_state.resume_data["work_experience"]):
                with st.container(border=True):
                #with st.expander(f"{exp.get('job_title', 'Position')} at {exp.get('company', 'Company')}", expanded=False):
                    st.write(f"**Start Dates:** {exp.get('dates_start', '')}")
                    st.write(f"**End Dates:** {exp.get('dates_end', '')}")
                    st.write(f"**Reason for Leaving:** {exp.get('reason', '')}")
                    if st.button(f"Remove Position {i+1}", key=f"remove_exp_{i}"):
                        st.session_state.resume_data["work_experience"].pop(i)
                        st.rerun()

        st.subheader("Add New Position")
        title_default = "" if st.session_state.clear_work_experience_input else st.session_state.get("exp_title", "")
        company_default = "" if st.session_state.clear_work_experience_input else st.session_state.get("exp_company", "")
        start_dates_default = "" if st.session_state.clear_work_experience_input else st.session_state.get("exp_dates_start", "")
        end_dates_default = "" if st.session_state.clear_work_experience_input else st.session_state.get("exp_dates_end", "")
        reason_default = "" if st.session_state.clear_work_experience_input else st.session_state.get("exp_reason", "")

        st.text_input("Job Title", value=title_default, key="exp_title")
        st.text_input("Company Name", value=company_default, key="exp_company")
        st.date_input("Date of Employment", value=None, key="exp_dates_start")
        st.date_input("Date of end of Employment", value=None, key="exp_dates_end")
        st.text_input("Reason for Leaving", value=reason_default, key="exp_reason")

        if st.button("Add Position", key="add_exp"):
            save_work_experience()

        if st.session_state.clear_work_experience_input:
            st.session_state.clear_work_experience_input = False

def save_references():
    """Save references from the form (if a new reference is being added)."""
    ref_name = st.session_state.get("ref_name", "")
    ref_relationship = st.session_state.get("ref_rel", "")
    ref_contact = st.session_state.get("ref_contact", "")

    if ref_name or ref_contact:
        if not ref_name or not ref_contact:
            st.error("Name and contact information are required.")
            return False
        else:
            st.session_state.resume_data.setdefault("references", []).append({
                "name": ref_name, "relationship": ref_relationship, "contact": ref_contact
            })
            st.success("Reference added!")
            st.session_state.clear_references_input = True
            st.rerun()
    return True

def create_references():
    """Handle references section."""
    with st.expander("References", expanded=False):
        if st.session_state.resume_data.get("references", []):
            st.subheader("Current References")
            for i, ref in enumerate(st.session_state.resume_data["references"]):
                with st.container(border=True):
                #with st.expander(f"{ref.get('name', 'Reference')}", expanded=False):
                    st.write(f"**Name:** {ref.get('name', '')}")
                    st.write(f"**Relationship:** {ref.get('relationship', '')}")
                    st.write(f"**Contact:** {ref.get('contact', '')}")
                    if st.button(f"Remove Reference {i+1}", key=f"remove_ref_{i}"):
                        st.session_state.resume_data["references"].pop(i)
                        st.rerun()

        st.subheader("Add New Reference")
        name_default = "" if st.session_state.clear_references_input else st.session_state.get("ref_name", "")
        rel_default = "" if st.session_state.clear_references_input else st.session_state.get("ref_rel", "")
        contact_default = "" if st.session_state.clear_references_input else st.session_state.get("ref_contact", "")

        st.text_input("Reference Name", value=name_default, key="ref_name")
        st.text_input("Professional Relationship", value=rel_default, key="ref_rel")
        st.text_input("Contact Information", value=contact_default, key="ref_contact")

        if st.button("Add Reference", key="add_ref"):
            save_references()

        if st.session_state.clear_references_input:
            st.session_state.clear_references_input = False

def save_declaration():
    """Save declaration from the form."""
    signature = st.session_state.get("declaration_sig", "")
    date_signed = st.session_state.get("declaration_date", datetime.today())

    if not signature:
        st.error("Signature is required.")
        return False
    else:
        st.session_state.resume_data["declaration"] = {
            "signature": signature, "date_signed": date_signed
        }
        st.success("Declaration saved!")
        z83()
        return True

def create_declaration():
    """Handle declaration section."""
    with st.expander("Declaration", expanded=False):
        declaration = st.session_state.resume_data.get("declaration", {})
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Declaration Signature", value=declaration.get("signature", ""), key="declaration_sig")
        with col2:
            st.date_input("Declaration Date", value=declaration.get("date_signed", datetime.today()), key="declaration_date")

        if st.button("Save and Generate Z83 Form", key="save_declaration"):
            save_declaration()

def show_application_form_content():
    """Render application form content."""
    st.title("Application Form")
    create_personal_info()
    create_add_personal_info()
    create_correspondence_prefs()
    create_languages()
    create_education_history()
    create_work_experience()
    create_references()
    create_declaration()

# --- Resume Builder Sections ---

def save_professional_summary():
    """Save professional summary from the form."""
    summary = st.session_state.get("summary", "")
    if not summary:
        st.error("Professional summary is required.")
        return False
    else:
        st.session_state.resume_data["professional_summary"] = {"summary": summary}
        st.success("Professional Summary saved!")
        return True

def create_professional_summary():
    """Handle professional summary section."""
    with st.expander("Professional Summary", expanded=False):
        professional_summary = st.session_state.resume_data.get("professional_summary", {})
        st.text_area("Professional Summary", value=professional_summary.get("summary", ""), key="summary", height=200)
        if st.button("Save Professional Summary", key="save_professional_summary"):
            save_professional_summary()

def save_skills():
    """Add a new skill to the resume data."""
    skill_name = st.session_state.get("skill_name", "")
    skill_level = st.session_state.get("skill_level", "")

    if skill_name:
        if not skill_name:
            st.error("Skill name is required.")
            return False
        else:
            st.session_state.resume_data.setdefault("skills", []).append({
                "name": skill_name, "level": skill_level
            })
            st.success("Skill added!")
            st.session_state.clear_skill_input = True
            st.rerun()
    return True

def create_skills():
    """Handle skills section."""
    with st.expander("Skills", expanded=False):
        if st.session_state.resume_data.get("skills", []):
            st.subheader("Current Skills")
            cols = st.columns(2)
            for i, skill in enumerate(st.session_state.resume_data["skills"]):
                with cols[0]:
                    st.markdown(f"- **{skill.get('name', 'Skill')}**: {skill.get('level', '')}")
                with cols[1]:
                    if st.button("Remove", key=f"remove_skill_{i}"):
                        st.session_state.resume_data["skills"].pop(i)
                        st.rerun()

        st.subheader("Add New Skill")
        skill_name_default = "" if st.session_state.get("clear_skill_input", False) else st.session_state.get("skill_name", "")
        skill_level_default = "" if st.session_state.get("clear_skill_input", False) else st.session_state.get("skill_level", "")

        st.text_input("Skill Name", value=skill_name_default, key="skill_name")
        proficiency_levels = ["", "Beginner", "Intermediate", "Advanced", "Expert"]
        skill_level_index = proficiency_levels.index(skill_level_default) if skill_level_default in proficiency_levels else 0
        st.selectbox("Proficiency Level", proficiency_levels, index=skill_level_index, key="skill_level")

        if st.button("Add Skill", key="add_skill"):
            save_skills()

        if st.session_state.get("clear_skill_input", False):
            st.session_state.clear_skill_input = False

def save_certifications():
    """Save certifications from the form (if a new certification is being added)."""
    cert_name = st.session_state.get("cert_name", "")
    cert_date = st.session_state.get("cert_date", "")

    if cert_name or cert_date:
        if not cert_name:
            st.error("Certification name is required.")
            return False
        else:
            st.session_state.resume_data.setdefault("certifications", []).append({
                "name": cert_name, "date": cert_date
            })
            st.success("Certification added!")
            return True
    return True

def create_certifications():
    """Handle certifications section."""
    with st.expander("Certifications & Professional Development", expanded=False):
        if st.session_state.resume_data.get("certifications", []):
            st.subheader("Current Certifications")
            for i, cert in enumerate(st.session_state.resume_data["certifications"]):
                with st.expander(f"{cert.get('name', 'Certification')}", expanded=False):
                    st.write(f"**Date:** {cert.get('date', '')}")
                    if st.button(f"Remove Certification {i+1}", key=f"remove_cert_{i}"):
                        st.session_state.resume_data["certifications"].pop(i)
                        st.rerun()

        st.subheader("Add New Certification")
        st.text_input("Certification Name", key="cert_name")
        st.text_input("Date Received (e.g., May 2023)", key="cert_date")
        if st.button("Add Certification", key="add_cert"):
            save_certifications()

def save_projects():
    """Save projects from the form (if a new project is being added)."""
    project_name = st.session_state.get("project_name", "")
    project_desc = st.session_state.get("project_desc", "")

    if project_name or project_desc:
        if not project_name:
            st.error("Project name is required.")
            return False
        else:
            st.session_state.resume_data.setdefault("projects", []).append({
                "name": project_name, "description": project_desc
            })
            st.success("Project added!")
            return True
    return True

def create_projects():
    """Handle projects section."""
    with st.expander("Projects", expanded=False):
        if st.session_state.resume_data.get("projects", []):
            st.subheader("Current Projects")
            for i, proj in enumerate(st.session_state.resume_data["projects"]):
                with st.expander(f"{proj.get('name', 'Project')}", expanded=False):
                    st.write(f"**Description:** {proj.get('description', '')}")
                    if st.button(f"Remove Project {i+1}", key=f"remove_proj_{i}"):
                        st.session_state.resume_data["projects"].pop(i)
                        st.rerun()

        st.subheader("Add New Project")
        st.text_input("Project Name", key="project_name")
        st.text_area("Project Description", key="project_desc", height=100)
        if st.button("Add Project", key="add_proj"):
            save_projects()

def save_additional_info():
    """Save additional information from the form."""
    hobbies = st.session_state.get("hobbies", "")
    achievements = st.session_state.get("achievements", "")
    st.session_state.resume_data["additional_info"] = {
        "hobbies": hobbies,
        "achievements": achievements
    }
    st.success("Additional Information saved!")
    return True

def create_additional_info():
    """Handle additional information section."""
    with st.expander("Additional Information", expanded=False):
        additional_info = st.session_state.resume_data.get("additional_info", {})
        st.text_input("Hobbies and Interests", value=additional_info.get("hobbies", ""), key="hobbies")
        st.text_area("Achievements", value=additional_info.get("achievements", ""), key="achievements", height=100)
        if st.button("Save Additional Information", key="save_additional_info"):
            save_additional_info()

def save_review_download():
    """Placeholder for review and download (no saving required)."""
    return True

def create_review_download():
    """Handle review and download section."""
    with st.expander("Review & Download", expanded=False):
        st.subheader("Review Your Resume")
        resume_data = st.session_state.resume_data

        st.write("**Personal Information**")
        st.json(resume_data.get("personal_info", {}))
        st.write("**Professional Summary**")
        st.json(resume_data.get("professional_summary", {}))
        st.write("**Work Experience**")
        st.json(resume_data.get("work_experience", []))
        st.write("**Education**")
        st.json(resume_data.get("education", []))
        st.write("**Skills**")
        st.json(resume_data.get("skills", {}))
        st.write("**Certifications**")
        st.json(resume_data.get("certifications", []))
        st.write("**Projects**")
        st.json(resume_data.get("projects", []))
        st.write("**Additional Information**")
        st.json(resume_data.get("additional_info", {}))
        st.write("**References**")
        st.json(resume_data.get("references", []))

        st.download_button(
            label="Download Resume Data (JSON)",
            data=json.dumps(resume_data, default=str),
            file_name="resume.json",
            mime="application/json"
        )

def show_resume_builder_content():
    """Render resume builder content."""
    st.title("Resume Builder")
    create_personal_info()
    create_professional_summary()
    create_work_experience()
    create_education_history()
    create_skills()
    create_certifications()
    create_projects()
    create_additional_info()
    create_references()
    create_review_download()

# --- Main Component ---

def job_application_assistant():
    """Main job application assistant component."""
    st.title("Job Application Assistant")
    with st.container(border=True):
        initialize_session_state()
        col1, col2, col1x, col2x = st.columns(4)
        with col1:
            st.markdown("Explore job application assistant below.")
        with col1x:
            if st.button("Jobs", key="jobs_app", use_container_width=True):
                st.session_state.current_app_state = "Jobs"
                st.rerun()
        with col2x:
            if st.button("View/Apply selections", key="apply", use_container_width=True):
                st.session_state.current_app_state = "Apply"
                st.rerun()

        col1s, col2s = st.columns(2)
        with col1s:
            if st.button("Go to Application Form", use_container_width=True, key="go_to_form"):
                st.session_state.current_section = "Application Form"
                st.rerun()
        with col2s:
            if st.button("Go to Resume Builder", use_container_width=True, key="go_to_resume"):
                st.session_state.current_section = "Resume Builder"
                st.rerun()

        if st.session_state.current_section == "Application Form":
            with st.container(border=True):
                show_application_form_content()
        elif st.session_state.current_section == "Resume Builder":
            with st.container(border=True):
                show_resume_builder_content()
                
        if st.button("Back to Jobs", use_container_width=True):
            st.session_state.current_app_state = "Jobs"
            st.rerun()