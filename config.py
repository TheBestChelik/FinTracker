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

EXTRA_SHEET_SOURCE_SPREADSHEET_ID = '1GabHhP7FQhO04_5Y3QAuAaMMJr0BmP_etS0Px4ZD9PU'
EXTRA_SHEET_SOURCE_ID = '1308786482'

def expanses_categories_rage(sheet_name):
    if sheet_name == EXPANSES_SHEET_NAME:
        return f"{EXPANSES_SHEET_NAME}!D3:Y3"
    return f'{sheet_name}!B1:W1'

def expanses_range(sheet_name = EXPANSES_SHEET_NAME):

    return f"{sheet_name}!{EXPANSES_COLUMNS[0]}:{EXPANSES_COLUMNS[1]}"
#TELEGRAM BOT
class CALLBACK_DATA: #4 charc to encode button action
    cancel_input = "CANI"
    cancel_transaction = "CANT"
    expanses = "EXPS"
    statistics = "STAT"
    tables = "TABL"
    add_table = "ATBL"

