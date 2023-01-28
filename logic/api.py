import requests
import sqlite3
import json
import re
from datetime import datetime, timedelta, date

con = sqlite3.connect("users.sqlite")
cur = con.cursor()


def addUser(user_id, app_name, app_surname, app_email, tg_username, tg_chat_id):
    res = cur.execute(f"""
    SELECT app_name FROM user WHERE user_id={user_id}
    """).fetchall()
    if len(res) > 0:
        return (False, f'User <b>{res[0][0]}</b> is already connected to another Telegram account \U0001F6B7\n\nProvide email:')
    cur.execute(f"""
    INSERT INTO user VALUES
        ({user_id}, '{app_name}', '{app_surname}', '{app_email}', '{tg_username}', {tg_chat_id})
    """)
    con.commit()
    return (True, )


def getChatIDFromUserID(user_id):
    res = cur.execute(
        f"SELECT tg_chat_id FROM user WHERE user_id = {user_id}")
    return res.fetchone()


def getUsersForGroup(group_id):
    url = f"http://localhost:9080/group/{group_id}/users"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    users = list()
    for rsp in response:
        users.append(rsp['id'])
    return users


def getGroupsOfUser(user_id):
    url = f"http://localhost:9080/user/{user_id}/groups"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    return response


def parseGroups(groups):
    message = ''
    n = 1
    for group in groups:
        message += f"`№{n}: {group['name']}`\n"
        n += 1
    return message


def getGroupID(user_id, index):
    url = f"http://localhost:9080/user/{user_id}/groups"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    if len(response) < 1:
        return None
    elif len(response) <= index-1:
        return "incorrect_num"
    return response[index-1]['id']


def userExists(user_id):
    res = cur.execute(
        f"SELECT user_id, app_name FROM user WHERE tg_chat_id = {user_id}")
    return res.fetchone()


def loginUser(email, password, tg_username, tg_chat_id):
    url = "http://localhost:9080/user/login"
    payload = json.dumps({
        "password": f"{password}",
        "email": f"{email}"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        db_response = addUser(response.json()['id'], response.json()
                              ['name'], response.json()['surname'], response.json()['email'], tg_username, tg_chat_id)
        if db_response[0] == False:
            return ("user_conn_exists", db_response[1])
        else:
            return ("success", response.json()['name'])
    else:
        if response.json()['code'] == "INCORRECT_CREDENTIALS":
            return ("incorrect_cred",)
        else:
            return ("no_user",)
    return ("error",)


def listReminders(user_id):
    url = f"http://localhost:9080/user/{user_id}/reminders"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    if len(response) < 1:
        return None
    message = ""
    n = 1
    for rem in response:
        message += f"`№{n}: {rem['date']} - {rem['name']}`\n"
        n += 1
    return message


def listGroupReminders(group_id):
    url = f"http://localhost:9080/group/{group_id}/reminders"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    if len(response) < 1:
        return None
    message = ""
    n = 1
    for rem in response:
        message += f"`№{n}: {rem['date']} - {rem['name']}`\n"
        n += 1
    return message


def listRemindersAndGroupReminders(user_id):
    message = ''
    url = f"http://localhost:9080/user/{user_id}/reminders"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload, verify=False).json()
    n = 1
    if len(response) > 0:
        message += 'Personal reminders \U0001F451:\n'
        for rem in response:
            message += f"`№{n}: {rem['date']} - {rem['name']}`\n"
            n += 1
    groups = getGroupsOfUser(user_id)
    if n > 1:
        message += '\n'
    if len(groups) > 0:
        n = 1
        message += 'Group reminders \U0001F46F:\n'
        for group in groups:
            url = f"http://localhost:9080/group/{group['id']}/reminders"
            payload = {}
            headers = {}
            response = requests.request(
                "GET", url, headers=headers, data=payload).json()
            for rmd in response:
                message += f"`№{n}: {group['name']} - {rmd['date']} - {rmd['name']}`\n"
                n += 1
    if message == '' or message == 'Group reminders \U0001F46F:\n':
        return None
    return message


def deleteReminder(id_, rem_num, action, group_id):
    url = ''
    if action == 'Group':
        if group_id != None:
            url = f"http://localhost:9080/group/{group_id}/reminders"
        else:
            return 400
    else:
        url = f"http://localhost:9080/user/{id_}/reminders"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    if len(response) < 1:
        return None
    elif len(response) <= rem_num-1:
        return "incorrect_num"
    else:
        rem_id = response[rem_num-1]['id']
        url = ''
        if action == 'Group':
            if id_ != None:
                url = f"http://localhost:9080/group/{group_id}/delete/reminder/{rem_id}"
            else:
                return 400
        else:
            url = f"http://localhost:9080/user/{id_}/delete/reminder/{rem_id}"
        payload = {}
        headers = {}
        response = requests.request(
            "DELETE", url, headers=headers, data=payload)
        if response.status_code == 200:
            return 'success'
        else:
            return 'error'


def fetchRemindersForAllUsers():
    url = 'http://localhost:9080/reminder'
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    return response


def calculateCurrentReminders():
    reminders = fetchRemindersForAllUsers()
    today_date = str(date.today())
    time = datetime.now().strftime("%H:%M")
    notify = list()
    if reminders == None:
        return None
    for rem in reminders:
        if rem['period'] == 0:
            if rem['date'] == today_date:
                if rem['time'][:-3] == time:
                    notify.append(rem)
        elif rem['period'] < 0:
            if check_reminder_months(rem['date'], rem['period'], today_date):
                if rem['time'][:-3] == time:
                    notify.append(rem)
        else:
            if check_reminder_days(rem['date'], rem['period'], today_date):
                if rem['time'][:-3] == time:
                    notify.append(rem)
    return notify


def check_reminder_days(start_date, frequency, current_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    current_date = datetime.strptime(current_date, "%Y-%m-%d")
    delta = current_date - start_date
    if delta.days % frequency == 0:
        return True
    else:
        return False


def check_reminder_months(start_date, frequency, current_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    current_date = datetime.strptime(current_date, "%Y-%m-%d")
    delta_years = current_date.year - start_date.year
    delta_months = current_date.month - start_date.month
    months_since_start = delta_years*12 + delta_months
    if months_since_start % frequency == 0:
        return True
    else:
        return False


def createReminder(user_id, r_name, r_desc, r_freq, r_date, r_time, action, group_id):
    url = ''
    if action == 'Group':
        if group_id != None:
            url = f"http://localhost:9080/group/{group_id}/add/reminder"
        else:
            return 400
    else:
        url = f"http://localhost:9080/user/{user_id}/add/reminder"
    payload = json.dumps({
        "name": f"{r_name}",
        "description": f"{r_desc}",
        "period": r_freq,
        "date": f"{r_date}",
        "time": f"{r_time}"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.status_code


def dateIsValid(date):
    date_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    try:
        if date_regex.match(date):
            if date[:10] >= str(datetime.now())[:10]:
                return (True,)
            else:
                return (False, 'date_less_than_today')
        else:
            return (False, 'invalid_date')
    except ValueError:
        return (False, 'invalid_date')
