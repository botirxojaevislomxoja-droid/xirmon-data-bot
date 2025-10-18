import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID, CREDENTIALS_FILE

def connect_to_google_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet


def create_brand_sheet(brand_name):
    """Agar brendga list bo‘lmasa — yangisini yaratadi"""
    spreadsheet = connect_to_google_sheets()
    try:
        sheet = spreadsheet.worksheet(brand_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=brand_name, rows=100, cols=10)
        sheet.append_row(["Rasm URL", "Nomi (UZ)", "Nomi (RU)", "Tavsif (UZ)", "Tavsif (RU)"])
    return sheet


def add_product_to_brand(brand_name, data):
    """Berilgan brend listiga mahsulotni yozadi"""
    spreadsheet = connect_to_google_sheets()
    try:
        sheet = spreadsheet.worksheet(brand_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = create_brand_sheet(brand_name)
    sheet.append_row(data)
