from variables import *
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
from datetime import datetime


async def set_name(update, context) -> int:
    """Stores the info about reminder name"""
    user = update.message.from_user
    context.user_data['r_name'] = update.message.text
    logging.info("Reminder name of %s: %s",
                 user.first_name, update.message.text)
    await update.message.reply_text("Great! Write some description for your reminder \U0001F4DD:")
    return DESCRIPTION


async def set_description(update, context) -> int:
    """Stores the info about reminder description"""
    user = update.message.from_user
    reply_keyboard = [["Monthly", "Custom", "Daily"], ["No repetition"]]
    context.user_data['r_desc'] = update.message.text
    logging.info("Reminder description of %s: %s",
                 user.first_name, update.message.text)
    await update.message.reply_text("Okay. Select frequency of reminder \U0001F58B: ", reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder="How often the reminder should be repeated??"
    ))
    return FREQUENCY


async def set_frequency(update, context) -> int:
    """Stores the info about the reminder frequency"""
    user = update.message.from_user
    reply_keyboard = [["Days", "Weeks", "Months"]]
    freq = update.message.text
    logging.info("Reminder frequency of %s: %s",
                 user.first_name, update.message.text)
    if freq == 'Monthly':
        context.user_data['r_freq'] = -1
    elif freq == 'Daily':
        context.user_data['r_freq'] = 1
    elif freq == 'No repetition':
        context.user_data['r_freq'] = 0
    elif freq == 'Custom':
        await update.message.reply_text("Please, select frequency measure \U0001F321:", reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Frequency measure?"))
        return CUSTOM_FREQ_MEASURE
    await update.message.reply_text("Very well! Tell me the day, when you would like to receive the first reminder (f:`yyyy-mm-dd`, e.g. `2002-11-08`) \U0001F4C6:", reply_markup=ReplyKeyboardRemove())
    return DATE


async def set_custom_frequency_measure(update, context) -> int:
    """Stores the info about the reminder custom frequency measure"""
    user = update.message.from_user
    context.user_data['r_freq_measure'] = update.message.text
    logging.info("Reminder custom frequency measure of %s: %s",
                 user.first_name, update.message.text)
    await update.message.reply_text(f"How often would you like to be reminded(number of <b>{update.message.text}</b>) \U000023F3:", parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
    return CUSTOM_FREQ


async def set_custom_frequency(update, context) -> int:
    """Stores the info about the reminder custom frequency"""
    user = update.message.from_user
    period = int(update.message.text)
    freq = context.user_data.get('r_freq_measure', 'Not_found')
    if freq == 'Months':
        context.user_data['r_freq'] = period*(-1)
    elif freq == 'Days':
        context.user_data['r_freq'] = period
    elif freq == 'Weeks':
        context.user_data['r_freq'] = period*7
    else:
        await update.message.reply_text(f'Something went wrong, please try again later \U0001F4F6', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    logging.info("Reminder custom frequency of %s: %s",
                 user.first_name, context.user_data['r_freq'])
    await update.message.reply_text("Well done! Tell me the day, when you would like to receive the first reminder (f:`yyyy-mm-dd`, e.g. '2002-11-08') \U0001F4C6:", reply_markup=ReplyKeyboardRemove())
    return DATE


async def set_date(update, context) -> int:
    """Stores the info about the reminder date"""
    user = update.message.from_user
    validate_date = dateIsValid(update.message.text)
    print(validate_date)
    if validate_date[0]:
        context.user_data['r_date'] = update.message.text
        logging.info("Reminder first date of %s: %s",
                     user.first_name, context.user_data['r_date'])
        await update.message.reply_text("Very nice! Tell me the time to send you a reminder (f:`hh:mm`) \U000023F0:")
        return TIME
    else:
        logging.info("Invalid date input of %s: %s",
                     user.first_name, update.message.text)
        if validate_date[1] == 'date_less_than_today':
            await update.message.reply_text(f"The minimum possible date is <b>today - {str(datetime.now())[:10]}</b> \U0001F915. Please, try again:", parse_mode='HTML')
        else:
            await update.message.reply_text("Date is invalid \U0001F915. Please, try again(f:`yyyy-mm-dd`, e.g. '2002-11-08'): ")
        return DATE


async def set_time(update, context) -> int:
    """Stores the info about the reminder time and ends the conversation"""
    user = update.message.from_user
    message = ''
    context.user_data['r_time'] = update.message.text
    logging.info("Reminder time of %s: %s",
                 user.first_name, update.message.text)
    response = createReminder(context.user_data.get('user_id', userExists(update.effective_chat.id)[0]), context.user_data.get(
        'r_name', 'Not found'),
        context.user_data.get('r_desc', 'Not found'),
        context.user_data.get('r_freq', 'Not found'),
        context.user_data.get('r_date', 'Not found'),
        context.user_data.get('r_time', 'Not found'))
    if response == 200:
        message = 'Reminder succesfully created \U00002705'
    else:
        message = 'Something went wrong, please try again later \U0001F4F6'
    await update.message.reply_text(message)
    return ConversationHandler.END


async def delete_reminder(update, context) -> int:
    """Stores the info about reminder number to delete and deletes it"""
    user = update.message.from_user
    rem_num = int(update.message.text)
    logging.info("Delete reminder of %s: with №%s",
                 user.first_name, rem_num)
    result = deleteReminder(context.user_data.get(
        'user_id', userExists(update.effective_chat.id)[0]), rem_num)
    if result == 'success':
        await update.message.reply_text(f"Reminder Deleted \U00002705!")
    elif result == 'incorrect_num':
        await update.message.reply_text(f"Incorrect ID \U0000274C. Try again:")
        return DELETE
    else:
        await update.message.reply_text(f'Something went wrong, please try again later \U0001F4F6')
    return ConversationHandler.END
