import re
import config
def parse_expanses_input(input_str):
    amount = 0.0
    comment = ""
    tag = ""

    matches = re.findall(r"[-+]?\d*\.?\d+|[-+/*]", input_str)  # Match numbers and operators
    tag_match = re.search(r"#\w+", input_str)  # Find a tag starting with #
    comment_match = re.search(r"(?:\s)(?![\d+\-*\/])(.*?)(?=\s?#|$)", input_str)  # Extract comment after math or operators

    math_expression = " ".join(matches)
    try:
        amount = float(eval(math_expression))
    except Exception:
        raise Exception("Amount not provided") 

    if tag_match:
        tag = tag_match.group(0)
    if comment_match:
        comment = comment_match.group(1).strip()

    return amount, comment, tag

def create_table(expenses, head):
    max_len = 0
    for (category, amount) in expenses:
        s = category + str(amount)
        max_len = max(len(s), max_len)
    gap = 5
    table = head + "\n"
    table += "-" * (max_len + gap) + "\n"
    for (category, amount) in expenses:
        amount_str = str(amount)

        table += f"{category}" + " "*(max_len + gap - len(category) - len(amount_str)) + amount_str + "\n"
        table += "-" * (max_len + gap) + "\n"
    return table

def get_statistics_month(month_number, year, fin_manager, sheet, sheet_name):
    [month, expanses, sum] = fin_manager.get_statistics(sheet, sheet_name, month_number)
    filtered_expenses = [(category, amount) for category, amount in expanses.items() if float(amount.replace(" ", "")) > 0]
    sorted_expenses = sorted(filtered_expenses, key=lambda x: float(x[1].replace(" ", "")), reverse=True)
    sorted_expenses.append(("TOTAL", sum))

    text = create_table(sorted_expenses, f"🗓 {month.upper()}, {year}")
    return text
def get_statistics_extra_sheet(fin_manager, sheet, sheet_name):
    [expanses, sum] = fin_manager.get_statistics_extra_sheets(sheet, sheet_name)
    filtered_expenses = [(category, amount) for category, amount in expanses.items() if float(amount.replace(" ", "")) > 0]
    sorted_expenses = sorted(filtered_expenses, key=lambda x: float(x[1].replace(" ", "")), reverse=True)
    sorted_expenses.append(("TOTAL", sum))

    text = create_table(sorted_expenses, sheet_name)
    return text

def encode_statistics_callback(month, year):
    if month == 13:
        month = 1
        year += 1
    elif month == 0:
        month = 12
        year -= 1
    month_str = str(month)
    if len(month_str) == 1:
        month_str = "0" + month_str
    return config.CALLBACK_DATA.statistics + month_str + str(year)
def decode_statistics_callback(callback_data) -> tuple:
    month = int(callback_data[4:6])
    year = int(callback_data[6:10])
    return (month, year)

def encode_expanses_callback(category_index, amount, comment, teg) -> str:
    category_index_str = str(category_index)
    if len(category_index_str) == 1:
        category_index_str = "0" + category_index_str
    amount_str = str(amount)
    if len(amount_str) < 8:
        amount_str += "0" * (8 - len(amount_str))
    comment_len = str(len(comment))
    if len(comment_len) == 1:
        comment_len = "0" + comment_len
    teg_len = str(len(teg))
    if len(teg_len) == 1:
        teg_len = "0" + teg_len
    return config.CALLBACK_DATA.expanses + category_index_str + amount_str + comment_len + comment + teg_len + teg

def decode_expanses_callback(callback_data) -> tuple:
    index = 4
    category_index = int(callback_data[index:index+2])
    index += 2
    amount = float(callback_data[index:index + 8])
    index += 8
    comment_len = int(callback_data[index:index + 2])
    index += 2
    comment = callback_data[index: index + comment_len]
    index += comment_len
    teg_len = int(callback_data[index: index + 2])
    index += 2
    teg = callback_data[index: index + teg_len]
    return (category_index, amount, comment, teg)

def encode_sheet_callback(sheet_id, sheet_name):
    # Convert the sheet ID to a string
    sheet_id_str = str(sheet_id)
    
    # Format the string with the length of the sheet ID and sheet name
    result = f"TABL{len(sheet_id_str):02d}{sheet_id_str}{len(sheet_name):02d}{sheet_name}"
    
    return result
def decode_sheet_callback(callback_data)-> tuple:
    sheet_id_len = int(callback_data[4:6])
    sheet_id = int(callback_data[6:6 + sheet_id_len])
    
    # Extract the length of the sheet name and the sheet name itself
    sheet_name_len = int(callback_data[6 + sheet_id_len:8 + sheet_id_len])
    sheet_name = callback_data[8 + sheet_id_len:8 + sheet_id_len + sheet_name_len]
    
    return sheet_id, sheet_name

def extract_spreadsheet_id(input_str):
    match = re.search(r"(?:/d/|^)([a-zA-Z0-9_-]+)(?:/|$)", input_str)
    return match.group(1) if match else None

    

