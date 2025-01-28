import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


from dataclasses import dataclass

from datetime import datetime

from config import TOKEN_FILE, SCOPE, CREDENTIALS_FILE, EXPANSES_SHEET_NAME, EXPANSES_ROW_START, EXPANSES_COLUMNS, EXPANSES_CATEGORIES_RANGE, EXPANSES_RANGE, EXPANSES_STATISTICS_COLUMNS, EXPANSES_STATISTICS_ROW_START


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


    def sync(self, sheet: str):
        expanses_categories = self.get_expanses_categories(sheetId=sheet)
        last_row = self.get_rows_number(sheetId=sheet)
        self.cache[sheet] = sheet_data(last_row, expanses_categories)

        
    def get_sheet_data(self, sheet):
        if sheet not in self.cache:
            self.sync(sheet=sheet)
        return self.cache[sheet]


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
    
    def get_rows_number(self, sheetId: str) -> int:
        range = f"{EXPANSES_SHEET_NAME}!{EXPANSES_COLUMNS[0]}{EXPANSES_ROW_START}:{EXPANSES_COLUMNS[0]}"
        result = self.sheet.values().get(spreadsheetId=sheetId, range=range).execute()
        return EXPANSES_ROW_START + len(result.get('values', [])) - 1
    
    def get_expanses_categories(self, sheetId: str) -> list[str]:
        result = self.sheet.values().get(spreadsheetId=sheetId, range=EXPANSES_CATEGORIES_RANGE).execute()
        return result.get('values', [])[0]
    
    def add_expanses(self,sheetId: str, category_index: int, amount: float, teg = "", comment = ""):
        sheet_data = self.get_sheet_data(sheetId)
    
        now = datetime.now()
        time  = now.strftime("%m/%d/%Y %H:%M:%S")

        data = [time, sheet_data.expanses_categories[category_index], amount, "Python", teg, comment]
        result = self.sheet.values().append(spreadsheetId=sheetId, 
                                    range = EXPANSES_RANGE, 
                                    valueInputOption = "USER_ENTERED",
                                    insertDataOption = "INSERT_ROWS",
                                    body ={"values": [data]}).execute()    
        self.cache[sheetId].last_row += 1
        return (time, sheet_data.expanses_categories[category_index], amount, teg, comment)

    
    def get_last_transactions(self,sheetId: str,  n = 5):
        sheet_data = self.get_sheet_data(sheetId)

        start_row = max(sheet_data.last_row - n + 1, EXPANSES_ROW_START)
        range_notation = f"{EXPANSES_SHEET_NAME}!{EXPANSES_COLUMNS[0]}{start_row}:{EXPANSES_COLUMNS[1]}{sheet_data.last_row}"

        result = self.sheet.values().get(spreadsheetId=sheetId, range=range_notation).execute()
        rows = result.get('values', [])
        return rows
    def clear_last_transactions(self, sheetId: str, n = 1):
        if sheetId not in self.cache:
            self.sync(sheet=sheetId)
            
        start_row = max(self.cache[sheetId].last_row - n + 1, EXPANSES_ROW_START)
        clear_request = self.sheet.values().clear(
            spreadsheetId=sheetId,
            range= f"{EXPANSES_SHEET_NAME}!{EXPANSES_COLUMNS[0]}{start_row}:{EXPANSES_COLUMNS[1]}{self.cache[sheetId].last_row}"
        ).execute()
        self.cache[sheetId].last_row -= n
    def get_statistics(self, sheetId: str,  month: int):

        sheet_data = self.get_sheet_data(sheetId)
        row_number = EXPANSES_STATISTICS_ROW_START - 1 + month
        data_range = f"{EXPANSES_SHEET_NAME}!{EXPANSES_STATISTICS_COLUMNS[0]}{row_number}:{EXPANSES_STATISTICS_COLUMNS[1]}{row_number}"
        result = self.sheet.values().get(spreadsheetId=sheetId, range=data_range).execute().get('values', [])[0]
        month = result[0]
        sum = result[1]
        category_dict = {}
    
        for i in range(len(sheet_data.expanses_categories)):
            category_dict[sheet_data.expanses_categories[i]] = result[i + 2]
        return [month, category_dict, sum]
        
    def get_users_spreadsheets(self) -> map:
        result = self.sheet.values().get(spreadsheetId=USERS_SPREADSHEET_ID, range=USERS_RANGE).execute().get('values', [])
        user_map = {int(user_id): sheet_id for user_id, sheet_id in result}
        return user_map
    def check_user_sheet(self, sheet):
        try:
            expanses_categories = self.get_expanses_categories(sheetId=sheet)
            last_row = self.get_rows_number(sheetId=sheet)
        except Exception as ex:
            print(ex)
            return -1
        return 0
    def add_new_user(self, user_id, sheet):
        self.sync(sheet)
        data = [user_id, sheet]
        result = self.sheet.values().append(spreadsheetId=USERS_SPREADSHEET_ID, 
                                    range = USERS_RANGE, 
                                    valueInputOption = "USER_ENTERED",
                                    insertDataOption = "INSERT_ROWS",
                                    body ={"values": [data]}).execute()    
        

    


if __name__ == "__main__":
    fin_manager = FinManager()
    users = fin_manager.get_users_spreadsheets()
    print(fin_manager.copy_template())
    # print(users)
    # while True:
    #     print("Functions:")
    #     print("1 - add expanses")
    #     print("2 - check last 5 expanses")
    #     print("3 - Cancel last transaction")
    #     print("4 - Get statistics")
    #     func = int(input("Function number: "))
    #     if func == 1:
    #         amount = float(input("Enter amount: "))
    #         comment = input("Comment: ")
    #         teg = input("Teg: ")
    #         print("Select the category:")
    #         for c in range(len(fin_manager.expanses_categories)):
    #             print(c + 1, fin_manager.expanses_categories[c])
    #         category_index = int(input("Enter category index: "))
    #         fin_manager.add_expanses(category_index - 1, amount, teg, comment)
    #         print("Saved into table")
    #     elif func == 2:
    #         res = fin_manager.get_last_transactions()
    #         for i in range(len(res)):
    #             print(i+1, res[i][0], res[i][1], res[i][2])
    #     elif func == 3:
    #         fin_manager.clear_last_transactions()
    #         print("Last transaction removed")
    #     elif func == 4:
    #         month_number = int(input("Number month"))
    #         [month, expanses, sum] = fin_manager.get_statistics(month_number)
    #         print(f"==={month}===")
    #         for key, value in expanses.items():
    #             print(f"{key}:", value)
    #         print(f"Sum: {sum}")
        
        
    
