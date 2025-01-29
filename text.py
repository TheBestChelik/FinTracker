from telega_bot import TeleBot
from config import CALLBACK_DATA


ADD_USER_TEXT = '''
1️⃣ [Скопируй этот файл](https://docs.google.com/spreadsheets/d/1XR7LOMKFs5rEI3pf4CStX4dZFjYjfpe78he6kdzmXzw/edit?usp=sharing) себе на Google Диск 📊\n \
2️⃣ Дай мне доступ на редактирование \(почта: *my\.redmi\.4x\.ua\@gmail\.com*\) ✍️\n \
3️⃣ Отправь мне ссылку или ID твоей таблицы 📎\n\n '''

INVALID_LINK = (
    "📌 Похоже, я не смог распознать ссылку 😕\n"
    "Пожалуйста, отправь **правильную ссылку** на документ или просто **ID таблицы** 📎"
)
NO_ACCESS_LINK = (
    "🚫 Упс\! Я не могу подключиться к твоей таблице 😔\n"
    "Проверь, дал ли ты мне **доступ на редактирование** \(почта: *my\.redmi\.4x\.ua\@gmail\.com*\) ✍️\n"
    "Если всё верно, попробуй отправить ссылку ещё раз 🔄"
)

START_TEXT = "Отправь любое число и выбери категорию 👇"

ERROR_INCORRECT_INPUT = """⚠️ Неверный формат ввода, допустимы только числа, знаки арифметических операций  (+,-,/,*). 
ℹ️ Пример: 10 или 10,6 или 2+2.5"""
CANCEL_TRANSACTION = "❌ Отмена"
SELECT_CATEGORY = "Выберите категорию."

ERROR_MESSAGE = "Что-то пошло не так. Пожалуйста, попробуй ещё раз позже 😊"


FUNCTIONS_KEYBOARD = [["📊 Расход по категориям", "💸 Мои последние расходы"], ["🔄 Синхронизировать"]]
FUNCTIONS = {"📊 Расход по категориям": TeleBot.get_statistics,
             "💸 Мои последние расходы": TeleBot.get_last_expanses,
             "🔄 Синхронизировать": TeleBot.sync_user}

BUTTON_FUNCTIONS = {CALLBACK_DATA.cancel_input: TeleBot.button_cancel_input,
                    CALLBACK_DATA.cancel_transaction: TeleBot.button_cancel_transaction,
                    CALLBACK_DATA.expanses: TeleBot.button_expanses_category,
                    CALLBACK_DATA.statistics: TeleBot.button_get_statistics}