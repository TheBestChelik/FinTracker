from telega_bot import TeleBot
from config import CALLBACK_DATA

START_TEXT = "Отправь любое число и выбери категорию 👇"
ERROR_INCORRECT_INPUT = """⚠️ Неверный формат ввода, допустимы только числа, знаки арифметических операций  (+,-,/,*). 
ℹ️ Пример: 10 или 10,6 или 2+2.5"""
CANCEL_TRANSACTION = "❌ Отмена"
SELECT_CATEGORY = "Выберите категорию."

FUNCTIONS = {"📊 Расход по категориям": TeleBot.get_statistics,
             "💸 Мои последние расходы": TeleBot.get_last_expanses}

BUTTON_FUNCTIONS = {CALLBACK_DATA.cancel_input: TeleBot.button_cancel_input,
                    CALLBACK_DATA.cancel_transaction: TeleBot.button_cancel_transaction,
                    CALLBACK_DATA.expanses: TeleBot.button_expanses_category,
                    CALLBACK_DATA.statistics: TeleBot.button_get_statistics}