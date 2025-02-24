import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


from dataclasses import dataclass

from datetime import datetime

from config import TOKEN_FILE, SCOPE, CREDENTIALS_FILE, EXPANSES_SHEET_NAME, EXPANSES_ROW_START, EXPANSES_COLUMNS, expanses_categories_rage, expanses_range, EXPANSES_STATISTICS_COLUMNS, EXPANSES_STATISTICS_ROW_START, EXTRA_SHEET_SOURCE_SPREADSHEET_ID, EXTRA_SHEET_SOURCE_ID


from config import USERS_SPREADSHEET_ID, USERS_RANGE

@dataclass
class sheet_data:
    last_row: int
    expanses_categories: list

class FinManager:
    sheet = None

    cache = {}
    last_row = 0
    expanses_categories = []
    def __init__(self):
        self.sheet = self.connect()

    def get_sheet_identifier(self, sheet_id, sheet_name):
        return f"{sheet_id}/{sheet_name}"


    def sync(self, sheet: str, sheet_name: str):
        expanses_categories = self.get_expanses_categories(sheetId=sheet, sheet_name=sheet_name)
        last_row = self.get_rows_number(sheetId=sheet, sheet_name=sheet_name)

        sheet_identifier = self.get_sheet_identifier(sheet, sheet_name)
        self.cache[sheet_identifier] = sheet_data(last_row, expanses_categories)

        
    def get_sheet_data(self, sheet, sheet_name):
        sheet_identifier = self.get_sheet_identifier(sheet, sheet_name)
        if sheet_identifier not in self.cache:
            self.sync(sheet=sheet, sheet_name=sheet_name)
        return self.cache[sheet_identifier]


    def connect(self) -> Resource:
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPE)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPE
                )
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

        try:
            service = build("sheets", "v4", credentials=creds)

            sheet = service.spreadsheets()
        except HttpError as err:
            print(err)
        return sheet
    
    def get_rows_number(self, sheetId: str, sheet_name: str) -> int:
        range = f"{sheet_name}!{EXPANSES_COLUMNS[0]}:{EXPANSES_COLUMNS[0]}"
        result = self.sheet.values().get(spreadsheetId=sheetId, range=range).execute()
        return len(result.get('values', []))
    
    def get_expanses_categories(self, sheetId: str, sheet_name: str) -> list[str]:
        result = self.sheet.values().get(spreadsheetId=sheetId, range=expanses_categories_rage(sheet_name)).execute()
        return result.get('values', [])[0]
    
    def add_expanses(self,sheetId: str, category_index: int, amount: float, teg = "", comment = "", sheet_name = None):
        sheet_data = self.get_sheet_data(sheetId, sheet_name)
    
        now = datetime.now()
        time  = now.strftime("%m/%d/%Y %H:%M:%S")

        data = [time, sheet_data.expanses_categories[category_index], amount, "Python", teg, comment]
        result = self.sheet.values().append(spreadsheetId=sheetId, 
                                    range = expanses_range(sheet_name), 
                                    valueInputOption = "USER_ENTERED",
                                    insertDataOption = "INSERT_ROWS",
                                    body ={"values": [data]}).execute()    
        self.sync(sheetId, sheet_name)
        return (time, sheet_data.expanses_categories[category_index], amount, teg, comment)

    
    def get_last_transactions(self,sheetId: str, sheet_name: str,  n = 5):
        sheet_data = self.get_sheet_data(sheetId, sheet_name)
        expanses_row_start = 4
        if sheet_name == EXPANSES_SHEET_NAME:
            expanses_row_start = EXPANSES_ROW_START
        start_row = max(sheet_data.last_row - n + 1, expanses_row_start)
        range_notation = f"{sheet_name}!{EXPANSES_COLUMNS[0]}{start_row}:{EXPANSES_COLUMNS[1]}{sheet_data.last_row}"

        result = self.sheet.values().get(spreadsheetId=sheetId, range=range_notation).execute()
        rows = result.get('values', [])
        return rows
    def clear_last_transactions(self, sheetId: str, sheet_name: str, n = 1):

        sheet_data = self.get_sheet_data(sheetId, sheet_name)
        expanses_row_start = 4
        if sheet_name == EXPANSES_SHEET_NAME:
            expanses_row_start = EXPANSES_ROW_START
            
        start_row = max(sheet_data.last_row - n + 1, expanses_row_start)
        clear_request = self.sheet.values().clear(
            spreadsheetId=sheetId,
            range= f"{sheet_name}!{EXPANSES_COLUMNS[0]}{start_row}:{EXPANSES_COLUMNS[1]}{sheet_data.last_row}"
        ).execute()
        self.sync(sheetId, sheet_name)

    def get_statistics(self, sheetId: str, sheet_name: str, month: int):

        sheet_data = self.get_sheet_data(sheetId, sheet_name)
        row_number = EXPANSES_STATISTICS_ROW_START - 1 + month
        data_range = f"{EXPANSES_SHEET_NAME}!{EXPANSES_STATISTICS_COLUMNS[0]}{row_number}:{EXPANSES_STATISTICS_COLUMNS[1]}{row_number}"
        result = self.sheet.values().get(spreadsheetId=sheetId, range=data_range).execute().get('values', [])[0]
        month = result[0]
        sum = result[1]
        category_dict = {}
    
        for i in range(len(sheet_data.expanses_categories)):
            category_dict[sheet_data.expanses_categories[i]] = result[i + 2]
        return [month, category_dict, sum]
    
    def get_statistics_extra_sheets(self, sheetId: str, sheet_name: str):
        sheet_data = self.get_sheet_data(sheetId, sheet_name)
        data_range = f"{sheet_name}!A2:W2"
        result = self.sheet.values().get(spreadsheetId=sheetId, range=data_range).execute().get('values', [])[0]
        sum = result[0]

        category_dict = {}
        for i in range(len(sheet_data.expanses_categories)):
            category_dict[sheet_data.expanses_categories[i]] = result[i + 1]
        return [category_dict, sum]


        
    def get_users_spreadsheets(self) -> map:
        result = self.sheet.values().get(spreadsheetId=USERS_SPREADSHEET_ID, range=USERS_RANGE).execute().get('values', [])
        user_map = {int(user_id): sheet_id for user_id, sheet_id in result}
        return user_map
    
    def check_user_sheet(self, sheet):
        try:
            expanses_categories = self.get_expanses_categories(sheetId=sheet, sheet_name=EXPANSES_SHEET_NAME)
            last_row = self.get_rows_number(sheetId=sheet, sheet_name=EXPANSES_SHEET_NAME)
        except Exception as ex:
            print(ex)
            return -1
        return 0

    def add_new_user(self, user_id, sheet):
        self.sync(sheet, sheet_name=EXPANSES_SHEET_NAME)
        data = [user_id, sheet]
        result = self.sheet.values().append(spreadsheetId=USERS_SPREADSHEET_ID, 
                                    range = USERS_RANGE, 
                                    valueInputOption = "USER_ENTERED",
                                    insertDataOption = "INSERT_ROWS",
                                    body ={"values": [data]}).execute()
    
    
    def add_new_table(self, sheet, sheet_name):
        source_spreadsheet_id = EXTRA_SHEET_SOURCE_SPREADSHEET_ID
        source_sheet_id = EXTRA_SHEET_SOURCE_ID
        request = self.sheet.sheets().copyTo(
        spreadsheetId=source_spreadsheet_id,
        sheetId=source_sheet_id,
        body={"destinationSpreadsheetId": sheet}
        )
        response = request.execute()
        new_sheet_id = response['sheetId']

        # Rename the copied sheet
        rename_request = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": new_sheet_id,
                            "title": sheet_name
                        },
                        "fields": "title"
                    }
                }
            ]
        }
        
        self.sheet.batchUpdate(
            spreadsheetId=sheet,
            body=rename_request
        ).execute()

        self.sync(sheet, sheet_name)

    def get_sheets(self, spreadsheet_id):
        sheet_metadata = self.sheet.get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])

        default_sheets = {"Доходы", "Сводная", "Диаграммы"}

        return {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in sheets if sheet['properties']['title'] not in default_sheets}

        
    
