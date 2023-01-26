import os
import logging
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from logic.login import *
from logic.actions import *
from logic.api import *
from variables import *

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and checks if user logged in"""
    user = userExists(update.effective_chat.id)
    if user:
        context.user_data['user_id'] = user[0]
        await update.message.reply_text(f'Welcome, {user[1]}! Now you can use menu to select action to perform',)
    else:
        await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet.\nProvide email:')
        return EMAIL


async def add(update, context) -> int:
    """Starts conversation about reminder creation"""
    if userExists(update.effective_chat.id):
        user = update.message.from_user
        logging.info("Starting conversation about reminder creation")
        await update.message.reply_text("Reminder wizzard is here. To cancel acton write /menu.\nThink about the name for your reminder: ")
        return NAME
    else:
        await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet.\nProvide email:')
        return EMAIL


async def list_rem(update, context) -> int:
    """Starts conversation about reminder creation"""
    if userExists(update.effective_chat.id):
        user = update.message.from_user
        logging.info("Listing user reminders")
        reminders = listReminders(
            context.user_data.get('user_id', userExists(update.effective_chat.id)[0]))
        await update.message.reply_text(f"Here are your reminders: \n{reminders}")
    else:
        await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet.\nProvide email:')
        return EMAIL


# async def update(update, context) -> int:
#     """Starts conversation about reminder creation"""
#     if userExists(update.effective_chat.id):
#         user = update.message.from_user
#         logging.info("Starting conversation about updating ")
#         await update.message.reply_text("Select a reminder to update: <Some List>")
#     else:
#         await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet. Provide email:')
#         return EMAIL


async def delete(update, context) -> int:
    """Starts conversation about reminder creation"""
    if userExists(update.effective_chat.id):
        user = update.message.from_user
        logging.info("Starting conversation about reminder delition")
        reminders = listReminders(
            context.user_data.get('user_id', userExists(update.effective_chat.id)[0]))
        await update.message.reply_text(f"Select a reminder to delete: \n{reminders}")
        return DELETE
    else:
        await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet.\nProvide email:')
        return EMAIL


async def help_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and checks if user logged in"""
    await update.message.reply_text(f'Welcome to the bot. You can use commands as /add, /list, /delete',)


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Action canceled. You are in menu now, write /help to check out avaliable commands", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def callback_send_reminder(context: ContextTypes.DEFAULT_TYPE):
    reminders = calculateCurrentReminders()
    await context.bot.send_message(chat_id='5528046211', text='One message every minute')


def main() -> None:
    """Run the bot."""
    application = (
        Application.builder()
        .token(os.getenv('TG_TOKEN'))
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_user))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            "start", start), CommandHandler("add", add), CommandHandler("list", list_rem), CommandHandler("delete", delete)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_description)],
            FREQUENCY: [MessageHandler(filters.Regex("^(Monthly|Daily|Weekly|Custom)$"), set_frequency)],
            TIME: [MessageHandler(filters.Regex(
                "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"), set_time)],
            DELETE: [MessageHandler(filters.Regex(
                "^[1-9][0-9]*$"), delete_reminder)],
            CUSTOM_FREQ: [MessageHandler(filters.Regex(
                "^[1-9][0-9]*$"), set_custom_frequency)],
            CUSTOM_FREQ_MEASURE: [MessageHandler(filters.Regex("^(Minutes|Hours|Days|Weeks)$"), set_custom_frequency_measure)],
        },
        fallbacks=[CommandHandler("menu", show_menu)],
    )
    application.add_handler(conv_handler)
    application.job_queue.run_repeating(
        callback_send_reminder, interval=60, first=3)
    application.run_polling()


if __name__ == "__main__":
    main()
