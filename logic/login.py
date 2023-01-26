from variables import *
import sqlite3
from .api import *
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


async def email(update, context) -> int:
    """Stores the email and asks for a password."""
    user = update.message.from_user
    logging.info("Getting email")
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Provide your password \U0001F511: ")
    return PASSWORD


async def password(update, context) -> int:
    """Stores the password and tries to log in."""
    user = update.message.from_user
    logging.info("Getting password")
    context.user_data['pass'] = update.message.text
    login = loginUser(context.user_data.get('email', 'Not_found'), context.user_data.get(
        'pass', 'Not_found'), update.message.chat.username, update.message.chat_id)
    if login[0] == "success":
        await update.message.reply_text(f"Nice to meet you {login[1]}! Now you are allowed to use commands. Check out /help \U0001F978")
        return ConversationHandler.END
    elif login[0] == "incorrect_cred":
        await update.message.reply_text(f'Incorrect Password \U0001F6B7. Try once again.\n\nProvide email:')
        return EMAIL
    elif login[0] == "no_user":
        await update.message.reply_text(f'User with provided email is not registered \U0001F914. Maybe you should visit our application first. \n\nCheck it out and return with your email right back:')
        return EMAIL
    elif login[0] == "user_conn_exists":
        await update.message.reply_text(login[1], parse_mode='HTML')
        return EMAIL
    else:
        await update.message.reply_text(f'Login failed \U0001F6B7. Try once again.\n\nProvide email:')
        return EMAIL
