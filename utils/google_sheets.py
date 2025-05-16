import gspread
import streamlit as st
import os
import json
from utils.constants import USER_SHEET_NAME, USER_LOGIN_WORKSHEET_NAME,USER_DATA_WORKSHEET_NAME, USER_DATA_HEADERS, USER_LOGIN_HEADERS
from google.oauth2.service_account import Credentials

# Define API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def connect_to_google_sheets(sheet_name: str, worksheet_name: str):
    """Connect to a Google Sheets spreadsheet and worksheet, creating them if they don't exist."""
    try:
        creds_dict = None
        # Attempt to load credentials from Streamlit secrets
        if "GOOGLE_CREDENTIALS" in st.secrets:
            creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        # Fallback to local JSON file
        elif os.path.exists("job_assist_cred.json"):
            with open("job_assist_cred.json", "r") as f:
                creds_dict = json.load(f)
            st.write("Using local credentials file")
        
        if not creds_dict:
            st.error("No credentials found")
            return None
        
        # Validate required credential keys
        required_keys = [
            "type", "project_id", "private_key_id", "private_key",
            "client_email", "client_id", "auth_uri", "token_uri",
            "auth_provider_x509_cert_url", "client_x509_cert_url"
        ]
        missing_keys = [k for k in required_keys if k not in creds_dict]
        if missing_keys:
            st.error(f"Missing required credential keys: {', '.join(missing_keys)}")
            return None
        
        # Authorize with Google Sheets API
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        
        # Open or create the spreadsheet
        try:
            spreadsheet = gc.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            spreadsheet = gc.create(sheet_name)
            spreadsheet.share(creds_dict["client_email"], perm_type="user", role="writer")
        
        # Open or create the worksheet
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            if worksheet_name == USER_DATA_WORKSHEET_NAME:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=len(USER_DATA_HEADERS))
                worksheet.append_row(USER_DATA_HEADERS)
            elif worksheet_name == USER_LOGIN_WORKSHEET_NAME:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=6)
                worksheet.append_row(USER_LOGIN_HEADERS)
            else:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=20)
        
        return worksheet
    except Exception as e:
        st.error(f"Google Sheets connection failed: {type(e).__name__}: {str(e)}")
        return None

def add_new_row(sheet: gspread.Worksheet, data: list) -> bool:
    """Add a new row to the specified worksheet."""
    try:
        sheet.append_row(data)
        return True
    except Exception as e:
        st.error(f"Failed to add new row: {type(e).__name__}: {str(e)}")
        return False

def get_column_letter(col_index):
    """Convert a column index (1-based) to a column letter (e.g., 1 -> A, 27 -> AA, 129 -> EA)."""
    letters = ""
    while col_index > 0:
        col_index, remainder = divmod(col_index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters

def update_row(sheet: gspread.Worksheet, row_index: int, data: list) -> bool:
    """Update a specific row in the worksheet."""
    try:
        num_cols = len(data)
        if num_cols == 0:
            st.error("No data provided to update the row.")
            return False
        # Generate the correct column letter for the end column
        end_col_letter = get_column_letter(num_cols)
        cell_range = f"A{row_index}:{end_col_letter}{row_index}"
        sheet.update(cell_range, [data])
        return True
    except Exception as e:
        st.error(f"Failed to update row {row_index}: {type(e).__name__}: {str(e)}")
        return False

def find_and_update_row(sheet: gspread.Worksheet, search_column: int, search_value: str, update_data: list) -> bool:
    """Find a row by value in a specific column and update it."""
    try:
        all_values = sheet.get_all_values()
        for idx, row in enumerate(all_values):
            if len(row) > search_column and row[search_column] == search_value:
                return update_row(sheet, idx + 1, update_data)
        st.warning(f"No row found with '{search_value}' in column {search_column}")
        return False
    except Exception as e:
        st.error(f"Failed to find and update row: {type(e).__name__}: {str(e)}")
        return False