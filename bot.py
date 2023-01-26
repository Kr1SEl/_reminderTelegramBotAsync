import os
import logging
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, constants
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
        await update.message.reply_text(f'Welcome, <b>{user[1]}</b>! Check out /help \U0001F978', parse_mode='HTML')
        return ConversationHandler.END
    else:
        await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet \U0001F512.\n\nProvide email:')
        return EMAIL


async def add(update, context) -> int:
    """Starts conversation about reminder creation"""
    if userExists(update.effective_chat.id):
        user = update.message.from_user
        logging.info("Starting conversation about reminder creation")
        await update.message.reply_text("Reminder wizzard is here \U0001F52E. To cancel acton write /menu.\nThink about the name for your reminder \U0001F914: ")
        return NAME
    else:
        await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet \U0001F512.\n\nProvide email:')
        return EMAIL


async def list_rem(update, context) -> int:
    """Starts conversation about reminder creation"""
    if userExists(update.effective_chat.id):
        user = update.message.from_user
        logging.info("Listing user reminders")
        reminders = listReminders(
            context.user_data.get('user_id', userExists(update.effective_chat.id)[0]))
        if reminders == None:
            await update.message.reply_text(f"You have no reminders, there is nothing to show \U0001F60C")
            return ConversationHandler.END
        else:
            await update.message.reply_text(f"Your reminders \U0001F4D1: \n{reminders}", parse_mode=constants.ParseMode.MARKDOWN_V2)
            return ConversationHandler.END
    else:
        await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet \U0001F512.\n\nProvide email:')
        return EMAIL


async def delete(update, context) -> int:
    """Starts conversation about reminder creation"""
    if userExists(update.effective_chat.id):
        user = update.message.from_user
        logging.info("Starting conversation about reminder delition")
        reminders = listReminders(
            context.user_data.get('user_id', userExists(update.effective_chat.id)[0]))
        if reminders == None:
            await update.message.reply_text(f"You have no reminders, there is nothing to delete \U0001F60C")
            return ConversationHandler.END
        else:
            await update.message.reply_text(f"Select a reminder to delete \U0000274C: \n{reminders}", parse_mode=constants.ParseMode.MARKDOWN_V2)
            return DELETE
    else:
        await update.message.reply_text(f'Seems like you have not connected your Telegram account to reminder system yet \U0001F512.\n\nProvide email:')
        return EMAIL


async def help_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and checks if user logged in"""
    await update.message.reply_text(
        """List of commands \U0001FA96:\n
/add - Add new reminder
/list - List all reminders
/delete - Delete reminder""", parse_mode='HTML')
    return ConversationHandler.END


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Action canceled \U0000274C", reply_markup=ReplyKeyboardRemove()
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
    application.add_handler(CommandHandler("help", help_user))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            "start", start), CommandHandler("add", add), CommandHandler("list", list_rem), CommandHandler("delete", delete)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_description)],
            FREQUENCY: [MessageHandler(filters.Regex("^(No repetition|Daily|Monthly|Custom)$"), set_frequency)],
            TIME: [MessageHandler(filters.Regex(
                "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"), set_time)],
            DATE: [MessageHandler(filters.Regex(
                "^\d+-\d+-\d+$"), set_date)],
            DELETE: [MessageHandler(filters.Regex(
                "^[1-9][0-9]*$"), delete_reminder)],
            CUSTOM_FREQ: [MessageHandler(filters.Regex(
                "^[1-9][0-9]*$"), set_custom_frequency)],
            CUSTOM_FREQ_MEASURE: [MessageHandler(filters.Regex("^(Months|Days|Weeks)$"), set_custom_frequency_measure)],
        },
        fallbacks=[CommandHandler("menu", show_menu)],
    )
    application.add_handler(conv_handler)
    # application.job_queue.run_repeating(
    #     callback_send_reminder, interval=60, first=3)
    application.run_polling()


if __name__ == "__main__":
    main()
