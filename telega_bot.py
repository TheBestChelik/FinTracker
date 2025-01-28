from datetime import datetime
from telegram import CallbackQuery, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters


from fin_manager import FinManager
from config import TELEGRAM_TOKEN, CALLBACK_DATA
import text
import utils
# Command handler to send a reply keyboard





class TeleBot:
    fin_manager = None
    users = None
    def __init__(self, fin_manager = None):
        if fin_manager:
            self.fin_manager = fin_manager
        else:
            self.fin_manager = FinManager()

        self.users = self.fin_manager.get_users_spreadsheets()
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        app.add_handler(CommandHandler("start", self.start))

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.parse_user_input))
        app.add_handler(CallbackQueryHandler(self.button))

        app.run_polling()
    
    def get_user_id(self, update) -> int:
        """Returns the user ID for both regular updates and callback queries."""
        if type(update) == Update:  # If it's a callback query (button click)
            return update.message.chat.id
        elif type(update) == CallbackQuery:  # If it's a regular message update
            return update.from_user.id
        else:
            raise Exception("User id not found")
    def user_sheet(self, user_id: int):
        if user_id in self.users:
            return self.users[user_id]
        self.users = self.fin_manager.get_users_spreadsheets()
        if user_id in self.users:
            return self.users[user_id]
        raise Exception("User sheet not found")

    def identify_user(self, update):
        user_id = self.get_user_id(update)
        return self.user_sheet(user_id)

    

    
    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await text.BUTTON_FUNCTIONS[query.data[0:4]](self, query)

    async def add_new_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = self.get_user_id(update)
        sheet = update.message.text
        if self.fin_manager.check_user_sheet(sheet) == -1:
            await update.message.reply_text(
            "Invalid"
            )
            return
        self.fin_manager.add_new_user(user_id, sheet)
        self.users[user_id] = sheet
        await self.start(update, context)

    async def check_new_user(self, update):
        user_id = self.get_user_id(update)
        if user_id in self.users:
            return False
        await update.message.reply_text(
           "Enter you spreadsheet id to continue"
        )
        return True


    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await self.check_new_user(update):
            return
        
        keyboard = [
            list(text.FUNCTIONS.keys()),  # First row
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            text.START_TEXT, reply_markup=reply_markup
        )

    async def parse_user_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.get_user_id(update) not in self.users:
            await self.add_new_user(update, context)
            return
        user_input = update.message.text
        if user_input in text.FUNCTIONS:
            await text.FUNCTIONS[user_input](self, update, context)
            return
        else:
            await self.add_expanses(update, context)
            return
    
    async def get_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        now = datetime.now()
        sheet = self.identify_user(update)
        text = utils.get_statistics_month(now.month, now.year, self.fin_manager, sheet)

        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data=utils.encode_statistics_callback(now.month - 1, now.year)),
                                            InlineKeyboardButton(">>", callback_data=utils.encode_statistics_callback(now.month + 1, now.year))]])
        await update.message.reply_text(f"```\n{text}\n```", parse_mode="MarkdownV2", reply_markup=reply_markup)
    
    async def get_last_expanses(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sheet = self.identify_user(update)
        expanses = self.fin_manager.get_last_transactions(sheetId=sheet)
        filtered_expenses = [(expanses[i][1], float(expanses[i][2].replace(" ", ""))) for i in range(len(expanses))]
        text = utils.create_table(filtered_expenses, f"Last {len(expanses)}")
        await update.message.reply_text(f"```\n{text}\n```", parse_mode="MarkdownV2")
    
    async def button_cancel_input(self, query):
        await query.edit_message_text("❌ Ввод отменен")

    async def button_cancel_transaction(self, query):
        sheet = self.identify_user(query)
        self.fin_manager.clear_last_transactions(sheetId=sheet)
        await query.edit_message_text("❌ Ввод отменен")

    async def button_expanses_category(self, query):
        sheet = self.identify_user(query)
        (cat_index, amount, comment, teg) = utils.decode_expanses_callback(query.data)

        (time, category, amount, teg, comment) = self.fin_manager.add_expanses(sheet, cat_index, amount, teg, comment)
        text = f"✅️ Внес {amount} в {category}"
        if comment:
            text += f"\n💬 {comment}"
        if teg:
            text += f"\n🏷️ {teg}"
        text += f"\n🗓 {time}"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data=CALLBACK_DATA.cancel_transaction)]])
        await query.edit_message_text(text, reply_markup=reply_markup)
    async def button_get_statistics(self, query):
        sheet = self.identify_user(query)
        month, year = utils.decode_statistics_callback(query.data)
       
        text = utils.get_statistics_month(month, year, self.fin_manager, sheet)

        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data=utils.encode_statistics_callback(month - 1, year)),
                                            InlineKeyboardButton(">>", callback_data=utils.encode_statistics_callback(month + 1, year))]])
        await query.edit_message_text(f"```\n{text}\n```", parse_mode="MarkdownV2", reply_markup=reply_markup)
    
    
    
    async def add_expanses(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sheet = self.identify_user(update)
        user_input = update.message.text
        try:
            (amount, comment, teg) = utils.parse_expanses_input(user_input)
        except Exception:
            await update.message.reply_text(text.ERROR_INCORRECT_INPUT)
            return
        keyboard = []
        i = 0
        categories = self.fin_manager.get_sheet_data(sheet=sheet).expanses_categories
        while i < len(categories) - 1:
            keyboard.append(
                [InlineKeyboardButton(categories[i], callback_data=utils.encode_expanses_callback(i, amount, comment, teg)),
            InlineKeyboardButton(categories[i+1], callback_data=utils.encode_expanses_callback(i+1, amount, comment, teg))])
            i += 2
        keyboard.append([InlineKeyboardButton(text.CANCEL_TRANSACTION, callback_data=CALLBACK_DATA.cancel_input)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text.SELECT_CATEGORY, reply_markup=reply_markup)
    
    



def main():
    tb = TeleBot()
    
    
if __name__ == "__main__":
    main()
