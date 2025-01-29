import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USERS_SPREADSHEET_ID = os.getenv("USERS_SPREADSHEET_ID")

# Users table
USERS_RANGE =  "main!A:B"



SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
EXPANSES_SHEET_NAME = "Расходы"
EXPANSES_ROW_START = 17
EXPANSES_COLUMNS = ("A", "F")
EXPANSES_STATISTICS_ROW_START = 4
EXPANSES_STATISTICS_COLUMNS = ("B", "Y")
EXPANSES_CATEGORIES_RANGE = f"{EXPANSES_SHEET_NAME}!D3:Y3"
EXPANSES_RANGE = f"{EXPANSES_SHEET_NAME}!{EXPANSES_COLUMNS[0]}{EXPANSES_ROW_START}:{EXPANSES_COLUMNS[1]}{EXPANSES_ROW_START}"
#TELEGRAM BOT
class CALLBACK_DATA: #4 charc to encode button action
    cancel_input = "CANI"
    cancel_transaction = "CANT"
    expanses = "EXPS"
    statistics = "STAT"

