from variables import *
from .api import *
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, constants
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from datetime import datetime, date


async def action_set_selection(update, context) -> int:
    """Stores the info about action set (user or group)"""
    user = update.message.from_user
    context.user_data['r_action_set'] = update.message.text
    logging.info("Action set of %s: %s",
                 user.first_name, update.message.text)
    if update.message.text == 'Group':
        groups = getGroupsOfUser(context.user_data.get(
            'user_id', userExists(update.effective_chat.id)[0]))
        if len(groups) > 0:
            parsed_groups = parseGroups(groups)
            if context.user_data.get('act', 'Not found') == 'add_reminder':
                await update.message.reply_text(f"Please, provide Group ID \n\nYour groups \U0001F46F: \n{parsed_groups}", parse_mode=constants.ParseMode.MARKDOWN_V2, reply_markup=ReplyKeyboardRemove())
                return GROUP_SELECTION
            elif context.user_data.get('act', 'Not found') == 'delete_reminder':
                await update.message.reply_text(f"Please, provide Group ID \n\nYour groups \U0001F46F: \n{parsed_groups}", parse_mode=constants.ParseMode.MARKDOWN_V2, reply_markup=ReplyKeyboardRemove())
                return GROUP_SELECTION
            else:
                await update.message.reply_text(f'Something went wrong, please try again later \U0001F4F6', reply_markup=ReplyKeyboardRemove())
                return ConversationHandler.END
        else:
            context.user_data['r_group_id'] = None
            if context.user_data.get('act', 'Not found') == 'add_reminder':
                await update.message.reply_text(f"You are not a member of any group, adding reminder to account.\nThink about the name for your reminder \U0001F914:", reply_markup=ReplyKeyboardRemove())
                return NAME
            elif context.user_data.get('act', 'Not found') == 'delete_reminder':
                reminders = listReminders(
                    context.user_data.get('user_id', userExists(update.effective_chat.id)[0]))
                if reminders == None:
                    await update.message.reply_text(f"You have no reminders, there is nothing to delete \U0001F60C")
                    return ConversationHandler.END
                else:
                    await update.message.reply_text(f"No group reminders \U00002639. Select a personal reminder to delete \U0000274C: \n{reminders}", parse_mode=constants.ParseMode.MARKDOWN_V2)
                    return DELETE
            else:
                await update.message.reply_text(f'Something went wrong, please try again later \U0001F4F6', reply_markup=ReplyKeyboardRemove())
                return ConversationHandler.END
    elif update.message.text == 'Account':
        context.user_data['r_group_id'] = None
        if context.user_data.get('act', 'Not found') == 'add_reminder':
            await update.message.reply_text("Working with <b>Account</b>. Think about the name for your reminder \U0001F914:", parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
            return NAME
        elif context.user_data.get('act', 'Not found') == 'delete_reminder':
            reminders = listReminders(
                context.user_data.get('user_id', userExists(update.effective_chat.id)[0]))
            if reminders == None:
                await update.message.reply_text(f"You have no reminders, there is nothing to delete \U0001F60C")
                return ConversationHandler.END
            else:
                await update.message.reply_text(f"Select a reminder to delete \U0000274C: \n{reminders}", parse_mode=constants.ParseMode.MARKDOWN_V2)
                return DELETE
    else:
        await update.message.reply_text(f'Something went wrong, please try again later \U0001F4F6', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


async def select_group(update, context) -> int:
    """Stores the info about groupID"""
    user = update.message.from_user
    groupID = getGroupID(context.user_data.get(
        'user_id', userExists(update.effective_chat.id)[0]), int(update.message.text))
    if groupID == None:
        logging.info("Groups doesn't exist for user %s",
                     user.first_name)
        context.user_data['r_group_id'] = None
        if context.user_data.get('act', 'Not found') == 'add_reminder':
            await update.message.reply_text(f"You are not a member of any group, adding reminder to account.\nThink about the name for your reminder \U0001F914")
            return NAME
        else:
            await update.message.reply_text(f'Something went wrong, please try again later \U0001F4F6', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
    elif groupID == 'incorrect_num':
        logging.info("Incorrect Group ID of %s",
                     user.first_name)
        await update.message.reply_text(f"Incorrect Group ID, please try again \U0000274C: ")
        return GROUP_SELECTION
    else:
        logging.info("Group ID of %s: %s",
                     user.first_name, groupID)
        context.user_data['r_group_id'] = groupID
        if context.user_data.get('act', 'Not found') == 'add_reminder':
            await update.message.reply_text(f"Working with group №<b>{update.message.text}</b>. Think about the name for your reminder \U0001F914:", parse_mode='HTML')
            return NAME
        elif context.user_data.get('act', 'Not found') == 'add_user_to_group':
            await update.message.reply_text(f"Working with group №<b>{update.message.text}</b>. Think about the name for your reminder \U0001F914:", parse_mode='HTML')
            return NAME
        elif context.user_data.get('act', 'Not found') == 'delete_reminder':
            reminders = listGroupReminders(groupID)
            if reminders == None:
                await update.message.reply_text(f"There are no reminders in the group, nothing to delete \U0001F60C")
                return ConversationHandler.END
            else:
                await update.message.reply_text(f"Deleting reminder from group №{update.message.text}\.\nSelect a reminder to delete \U0000274C: \n{reminders}", parse_mode=constants.ParseMode.MARKDOWN_V2)
                return DELETE
        else:
            await update.message.reply_text(f'Something went wrong, please try again later \U0001F4F6', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END


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
        reply_keyboard, one_time_keyboard=True, input_field_placeholder="How often the reminder should be repeated?"
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
    await update.message.reply_text(f"Very well! Tell me the day, when you would like to receive the first reminder (f:`yyyy-mm-dd`, e.g. <b>`{date.today()}`</b>) \U0001F4C6:", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
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
    await update.message.reply_text("Well done! Tell me the day, when you would like to receive the first reminder (f:`yyyy-mm-dd`, e.g. `2002-11-08`) \U0001F4C6:", reply_markup=ReplyKeyboardRemove())
    return DATE


async def set_date(update, context) -> int:
    """Stores the info about the reminder date"""
    user = update.message.from_user
    validate_date = dateIsValid(update.message.text)
    if validate_date[0]:
        context.user_data['r_date'] = update.message.text
        logging.info("Reminder first date of %s: %s",
                     user.first_name, context.user_data['r_date'])
        await update.message.reply_text("Very nice! Tell me the time to send you a reminder (f:`hh:mm`, e.g. `00:00`-`23:59`) \U000023F0:")
        return TIME
    else:
        logging.info("Invalid date input of %s: %s",
                     user.first_name, update.message.text)
        if validate_date[1] == 'date_less_than_today':
            await update.message.reply_text(f"The minimum possible date is <b>today - {str(datetime.now())[:10]}</b> \U0001F915. Please, try again:", parse_mode='HTML')
        else:
            await update.message.reply_text("Date is invalid \U0001F915. Please, try again(f:`yyyy-mm-dd`, e.g. `2002-11-08`): ")
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
        context.user_data.get('r_time', 'Not found'),
        context.user_data.get('r_action_set', 'Not found'),
        context.user_data.get('r_group_id', 'Not found'))
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
        'user_id', userExists(update.effective_chat.id)[0]), rem_num, context.user_data.get('r_action_set', 'Not found'), context.user_data.get('r_group_id', 'Not found'))
    if result == 'success':
        await update.message.reply_text(f"Reminder Deleted \U00002705!")
    elif result == 'incorrect_num':
        await update.message.reply_text(f"Incorrect ID \U0000274C. Try again:")
        return DELETE
    else:
        await update.message.reply_text(f'Something went wrong, please try again later \U0001F4F6')
    return ConversationHandler.END
