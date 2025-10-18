import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 🔹 Google Sheets credentialni Render environment variable dan olish
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if not creds_json:
    raise Exception("❌ GOOGLE_APPLICATION_CREDENTIALS_JSON topilmadi! Renderda Environment Variable qo‘shilganligini tekshiring.")

creds_dict = json.loads(creds_json)
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
gc = gspread.authorize(creds)


def connect_to_google_sheets():
    """Google Sheets bilan bog‘lanish"""
    # Spreadsheet ID ni environment variable orqali olish
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    if not spreadsheet_id:
        raise Exception("❌ SPREADSHEET_ID environment variable kiritilmagan!")

    spreadsheet = gc.open_by_key(spreadsheet_id)
    return spreadsheet


def create_brand_sheet(brand_name):
    """Agar brendga tegishli list bo‘lmasa — yangisini yaratadi"""
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

