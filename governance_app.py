import streamlit as st
import datetime

# --- App Configuration ---
st.set_page_config(
    page_title="Traditional Governance Platform",
    page_icon="🏛️",
    layout="wide"
)

# --- Dummy Data (Replace with real data source in a full app) ---
announcements = [
    {"date": "2025-04-10", "title": "Community Meeting Scheduled", "details": "A community meeting will be held at the Tribal Hall on April 25th at 10:00 AM to discuss water infrastructure."},
    {"date": "2025-04-05", "title": "Youth Development Program Applications Open", "details": "Applications for the skills development program are now open. Collect forms from the council office."},
    {"date": "2025-03-20", "title": "Reminder: Initiation Season Safety", "details": "Please adhere to the safety guidelines outlined by the Customary Initiation Act. Contact the Council for info."},
]

events = [
    {"date": "2025-05-01", "event": "May Day Celebration", "location": "Community Hall"},
    {"date": "2025-06-15", "event": "Youth Day Workshop", "location": "Council Office"},
]

directory = {
    "Mahikeng Traditional Council (Example)": {
        "Contact Person": "Council Secretary",
        "Phone": "018-XXX-XXXX (Placeholder)",
        "Email": "secretary@mahikengtc.gov.za (Placeholder)",
        "Address": "123 Tribal Authority Rd, Mmabatho (Placeholder)"
    },
    "Mahikeng Local Municipality (Example)": {
        "Department": "Community Services / Public Liaison",
        "Phone": "018-YYY-YYYY (Placeholder)",
        "Website": "www.mahikeng.gov.za (Placeholder)"
    },
    "Commission on Traditional Leadership Disputes and Claims": {
        "Type": "National Body",
        "Purpose": "Handles leadership and boundary disputes.",
        "Contact Info": "Refer to COGTA website for current details."
    }
}

resources = {
    "COGTA Website": "https://www.cogta.gov.za",
    "Dept. of Agriculture, Land Reform & Rural Development": "https://www.dalrrd.gov.za/",
    "SALGA (SA Local Government Association)": "https://www.salga.org.za/",
    "National House of Traditional & Khoi-San Leaders": "Link Placeholder (Check COGTA)"
}

legislation_info = {
    "Constitution (Chapter 12)": "Recognises the institution, status, and role of traditional leadership according to customary law, subject to the Constitution. Allows for legislation to define roles and establish Houses/Councils.",
    "Traditional and Khoi-San Leadership Act (TKLA)": "Aims to standardise traditional leadership structures, define roles more clearly, provide for recognition processes, and regulate aspects like succession and land administration cooperation. (Consult Act for details).",
    "Municipal Structures/Systems Acts": "Define the powers and functions of municipalities, including service delivery and development planning. Traditional leaders can participate in council meetings (often non-voting) as per the Act.",
    "Customary Initiation Act": "Regulates initiation practices to ensure safety, prevent abuse, and align with constitutional rights. Requires registration and adherence to health/safety standards."
}

roles_info = """
**General Roles (can vary by specific legislation & custom):**

**Traditional Leadership (e.g., Kgosi/Kgosiagadi, Council):**
* Custodian of custom, culture, and heritage.
* Facilitate community development in partnership with government.
* Promote social cohesion and harmony.
* Administer traditional justice (within legal framework).
* Assist with land administration matters (as per legislation).
* Liaise between community and government structures.
* Support implementation of specific government programs.

**Municipalities:**
* Responsible for local government administration.
* Primary responsibility for service delivery (water, sanitation, electricity, roads etc.).
* Develop and implement Integrated Development Plans (IDPs).
* Pass local by-laws.
* Manage municipal budgets and finances.
* Ensure democratic governance and public participation at local level.

**Key Area of Cooperation:** Integrated Development Planning (IDP), service delivery coordination, land use management, disaster management, local economic development.
"""

land_info = """
**Communal Land Information (General Overview):**

* Much rural land falls under communal tenure, often administered historically by traditional authorities.
* Post-1994 legislation aims to formalise rights and regulate administration. Acts like the TKLA and others outline roles for traditional councils in land matters, often requiring cooperation with government departments (like DALRRD).
* Rights of community members living on communal land are protected by law (e.g., Interim Protection of Informal Land Rights Act - IPILRA).
* Disputes regarding land allocation or rights within communal areas can be complex. Initial resolution may be sought via the Traditional Council, but formal legal avenues and government departments may be required.
* For specific advice or disputes, consult the relevant Traditional Council, the Dept. of Agriculture, Land Reform & Rural Development (DALRRD), or seek legal aid from organisations specialising in land rights.
"""

land_distribution = {"Agricultural": 40, "Residential": 30, "Commercial": 20, "Other": 10}

# --- Sidebar Navigation ---
st.sidebar.title("Navigation Menu")
page = st.sidebar.radio("Go to", ["Home", "Information Hub", "Communication", "Land Information", "Resources & Links"])

# --- Display Current Info ---
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))  # SAST = UTC+2
st.sidebar.markdown("---")
st.sidebar.write(f"📍 Location: Mmabatho, North West")
st.sidebar.write(f"🗓️ Date: {now.strftime('%A, %B %d, %Y')}")
st.sidebar.write(f"🕒 Time: {now.strftime('%I:%M:%S %p %Z')}")

# --- Page Content ---
if page == "Home":
    st.title("🏛️ Welcome to the Traditional Governance Platform (Prototype)")
    st.markdown("---")
    st.write("""
    This platform aims to improve communication and access to information for traditional leaders, councils, community members, and government stakeholders in South Africa.

    **Navigate using the menu on the left.**

    **Disclaimer:** This is a prototype demonstrating potential features. Information presented is illustrative and may not be fully accurate or complete. Always consult official sources and relevant authorities.
    """)

    # Feedback Form
    st.markdown("---")
    st.subheader("💬 Help Us Improve")
    with st.form("feedback_form"):
        feedback_name = st.text_input("Your Name (Optional)")
        feedback_email = st.text_input("Your Email (Optional)")
        feedback_message = st.text_area("Your Feedback *")
        feedback_submitted = st.form_submit_button("Submit Feedback")
        if feedback_submitted:
            if not feedback_message:
                st.error("Please provide your feedback.")
            else:
                st.success("Thank you for your feedback!")

elif page == "Information Hub":
    st.title("ℹ️ Information Hub")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📜 Legislation Overview", "👥 Roles & Responsibilities", "📞 Directory"])

    with tab1:
        st.header("📜 Legislation Overview")
        search_term = st.text_input("Search Legislation", key="leg_search")
        filtered_legislation = {k: v for k, v in legislation_info.items() if search_term.lower() in k.lower() or search_term.lower() in v.lower()}
        if filtered_legislation:
            for title, info in filtered_legislation.items():
                with st.expander(f"{title}"):
                    st.write(info)
        else:
            st.info("No matching legislation found.")
        st.caption("Note: This is a simplified summary. Always refer to the full official Acts.")

    with tab2:
        st.header("👥 Roles & Responsibilities")
        st.markdown(roles_info)
        st.caption("Note: Specific roles can differ based on province, custom, and evolving legislation.")

    with tab3:
        st.header("📞 Directory (Example Contacts)")
        search_term = st.text_input("Search Directory", key="dir_search")
        filtered_directory = {k: v for k, v in directory.items() if any(search_term.lower() in str(val).lower() for val in v.values())}
        if filtered_directory:
            st.table(filtered_directory)
        else:
            st.info("No matching contacts found.")
        st.caption("Note: Contact details are placeholders.")

elif page == "Communication":
    st.title("📢 Communication Channels")
    st.markdown("---")

    st.subheader("📅 Upcoming Events")
    if events:
        st.table(events)
    else:
        st.info("No upcoming events.")

    st.subheader("📌 Community Announcements")
    if announcements:
        for announcement in announcements:
            with st.container(border=True):
                st.write(f"**{announcement['title']}** ({announcement['date']})")
                st.write(announcement['details'])
    else:
        st.info("No current announcements.")

    st.markdown("---")
    st.subheader("❓ Submit a Query or Report an Issue (Simulation)")
    st.write("Use this form to send a non-urgent query to the relevant council/municipality (Example).")

    with st.form("query_form"):
        name = st.text_input("Your Name (Optional)")
        area = st.text_input("Your Area/Village *")
        query_type = st.selectbox("Type of Query *", ["Service Delivery Issue", "Land Matter Inquiry", "Community Program Info", "General Question", "Other"])
        details = st.text_area("Please provide details *")
        contact_info = st.text_input("Your Contact Number/Email (Optional - for response)")

        submitted = st.form_submit_button("Submit Query")
        if submitted:
            if not area or not details or not query_type:
                st.error("Please fill in all required fields marked with *")
            else:
                st.success(f"Thank you, {name if name else 'community member'}! Your query about '{query_type}' in {area} has been logged for review. Reference ID: SIM{str(hash(details))[:6]}")

elif page == "Land Information":
    st.title("🏞️ Land Information")
    st