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
    await update.message.reply_text("Provide your password: ")
    return PASSWORD


async def password(update, context) -> int:
    """Stores the password and tries to log in."""
    user = update.message.from_user
    logging.info("Getting password")
    context.user_data['pass'] = update.message.text
    login = loginUser(context.user_data.get('email', 'Not_found'), context.user_data.get(
        'pass', 'Not_found'), update.message.chat.username, update.message.chat_id)
    if login[0] == "success":
        await update.message.reply_text(f"Nice to meet you {login[1]}! Now you can use commands. Check /help for its list")
        return ConversationHandler.END
    elif login[0] == "incorrect_cred":
        await update.message.reply_text(f'Incorrect Password. Try once again. Provide email:')
        return EMAIL
    elif login[0] == "no_user":
        await update.message.reply_text(f'User with provided email is not registered. Maybe you should visit our application first. Check it out and return with your email right back:')
        return EMAIL
    else:
        await update.message.reply_text(f'Login failed. Try once again. Provide email:')
        return EMAIL
