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


async def set_name(update, context) -> int:
    """Stores the info about reminder name"""
    user = update.message.from_user
    context.user_data['r_name'] = update.message.text
    logging.info("Reminder name of %s: %s",
                 user.first_name, update.message.text)
    await update.message.reply_text("Great! Write some description for your reminder: ")
    return DESCRIPTION


async def set_description(update, context) -> int:
    """Stores the info about reminder description"""
    user = update.message.from_user
    reply_keyboard = [["Monthly", "Daily"], ["Weekly", "Custom"]]
    context.user_data['r_desc'] = update.message.text
    logging.info("Reminder description of %s: %s",
                 user.first_name, update.message.text)
    await update.message.reply_text("Great! Select frequency of reminder: ", reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder="Frequency?"
    ))
    return FREQUENCY


async def set_frequency(update, context) -> int:
    """Stores the info about the reminder frequency"""
    user = update.message.from_user
    reply_keyboard = [["Minutes", "Hours"], ["Days", "Weeks"]]
    freq = update.message.text
    logging.info("Reminder frequency of %s: %s",
                 user.first_name, update.message.text)
    if freq == 'Monthly':
        context.user_data['r_freq'] = 7*24*60  # ???
    elif freq == 'Daily':
        context.user_data['r_freq'] = 24*60
    elif freq == 'Weekly':
        context.user_data['r_freq'] = 7*24*60
    elif freq == 'Custom':
        await update.message.reply_text("Please, select frequency measure: ", reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Frequency measure?"))
        return CUSTOM_FREQ_MEASURE
    await update.message.reply_text("Very nice! Tell me the time to send you a reminder(Format `hh:mm`)", reply_markup=ReplyKeyboardRemove())
    return TIME


async def set_custom_frequency_measure(update, context) -> int:
    """Stores the info about the reminder custom frequency measure"""
    user = update.message.from_user
    context.user_data['r_freq_measure'] = update.message.text
    logging.info("Reminder custom frequency measure of %s: %s",
                 user.first_name, update.message.text)
    await update.message.reply_text(f"How often you would like to receive reminder(number of <b>{update.message.text}</b>):", parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
    return CUSTOM_FREQ


async def set_custom_frequency(update, context) -> int:
    """Stores the info about the reminder custom frequency"""
    user = update.message.from_user
    period = int(update.message.text)
    freq = context.user_data.get('r_freq_measure', 'Not_found')
    if freq == 'Minutes':
        context.user_data['r_freq'] = period
    elif freq == 'Hours':
        context.user_data['r_freq'] = period*60
    elif freq == 'Days':
        context.user_data['r_freq'] = period*24*60
    elif freq == 'Weeks':
        context.user_data['r_freq'] = period*7*24*60
    else:
        await update.message.reply_text("Something went wrong. Try again, please!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    logging.info("Reminder custom frequency of %s: %s",
                 user.first_name, context.user_data['r_freq'])
    await update.message.reply_text("Very nice! Tell me the time to send you a reminder(Format `hh:mm`)", reply_markup=ReplyKeyboardRemove())
    return TIME


async def set_time(update, context) -> int:
    """Stores the info about the reminder time and ends the conversation"""
    user = update.message.from_user
    context.user_data['r_time'] = update.message.text
    logging.info("Reminder time of %s: %s",
                 user.first_name, update.message.text)
    reminder = createReminder(context.user_data.get(
        'r_name', 'Not found'), context.user_data.get('r_freq', 'Not found'), context.user_data.get('r_time', 'Not found'))
    await update.message.reply_text(f"Well done! {reminder}")
    return ConversationHandler.END


async def delete_reminder(update, context) -> int:
    """Stores the info about reminder number to delete and deletes it"""
    user = update.message.from_user
    rem_num = int(update.message.text)
    logging.info("Delete reminder of %s: with №%s",
                 user.first_name, rem_num)
    result = deleteReminder(context.user_data.get(
        'user_id', userExists(update.effective_chat.id)[0]), rem_num)
    await update.message.reply_text(f"Well done! {result}")
    return ConversationHandler.END
