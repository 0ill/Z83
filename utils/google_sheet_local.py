import os
import json
from google.oauth2.service_account import Credentials
import gspread

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def connect_to_google_sheets(sheet_name: str, worksheet_name: str) -> gspread.Worksheet | None:
    """
    Connect to Google Sheets using service account credentials.
    
    Args:
        sheet_name (str): Name of the spreadsheet.
        worksheet_name (str): Name of the worksheet.
    
    Returns:
        gspread.Worksheet or None: The worksheet if successful, None otherwise.
    """
    try:
        creds_dict = None

        # Check environment variable for credentials
        #if "GOOGLE_CREDENTIALS" in os.environ:
        #    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        #    if "private_key" in creds_dict:
        #        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        # Fallback to local JSON file
        if os.path.exists("job_assist_cred.json"):
            with open("job_assist_cred.json", "r") as f:
                creds_dict = json.load(f)
            print("Using local credentials file")

        # Validate credentials
        if not creds_dict:
            print("Error: No credentials found")
            return None

        required_keys = [
            "type", "project_id", "private_key_id", "private_key",
            "client_email", "client_id", "auth_uri", "token_uri",
            "auth_provider_x509_cert_url", "client_x509_cert_url"
        ]
        missing_keys = [k for k in required_keys if k not in creds_dict]
        if missing_keys:
            print(f"Error: Missing required credential keys: {', '.join(missing_keys)}")
            return None

        # Create credentials and authorize
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(credentials)

        # Open or create spreadsheet
        try:
            spreadsheet = gc.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            spreadsheet = gc.create(sheet_name)
            spreadsheet.share(creds_dict["client_email"], perm_type="user", role="writer")

        # Open or create worksheet
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=6)
            if sheet_name == "Users":
                worksheet.append_row(["name", "surname", "email", "phone", "password", "creation"])

        return worksheet

    except Exception as e:
        print(f"Google Sheets connection failed: {type(e).__name__}: {str(e)}")
        return None

def add_new_row(sheet: gspread.Worksheet, data: list) -> bool:
    """Add a new row to the Google Sheet."""
    try:
        sheet.append_row(data)
        return True
    except Exception as e:
        print(f"Failed to add new row: {type(e).__name__}: {str(e)}")
        return False

def update_row(sheet: gspread.Worksheet, row_index: int, data: list) -> bool:
    """Update an existing row in the Google Sheet."""
    try:
        num_cols = len(data)
        cell_range = f"A{row_index}:{chr(64 + num_cols)}{row_index}"
        sheet.update(cell_range, [data])
        return True
    except Exception as e:
        print(f"Failed to update row {row_index}: {type(e).__name__}: {str(e)}")
        return False

def find_and_update_row(sheet: gspread.Worksheet, search_column: int, search_value: str, update_data: list) -> bool:
    """Find a row by value in a column and update it."""
    try:
        all_values = sheet.get_all_values()
        for idx, row in enumerate(all_values):
            if len(row) > search_column and row[search_column] == search_value:
                return update_row(sheet, idx + 1, update_data)
        print(f"No row found with '{search_value}' in column {search_column}")
        return False
    except Exception as e:
        print(f"Failed to find and update row: {type(e).__name__}: {str(e)}")
        return False