import requests
import sqlite3
import json

con = sqlite3.connect("users.sqlite")
cur = con.cursor()


def addUser(user_id, app_name, app_surname, app_email, tg_username, tg_chat_id):
    cur.execute(f"""
    INSERT INTO user VALUES
        ({user_id}, '{app_name}', '{app_surname}', '{app_email}', '{tg_username}', {tg_chat_id})
    """)
    con.commit()


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
        addUser(response.json()['id'], response.json()
                ['name'], response.json()['surname'], response.json()['email'], tg_username, tg_chat_id)
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
        message += f"№{n}: {rem['date']} - {rem['name']}\n"
        n += 1
    return message


def deleteReminder(user_id, rem_num):
    url = f"http://localhost:9080/user/{user_id}/reminders"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    if len(response) < 1:
        return None
    elif len(response) < rem_num-1:
        return "incorrect_num"
    else:
        rem_id = response[rem_num-1]['id']
        url = f"http://localhost:9080/user/{user_id}/delete/reminder/{rem_id}"
        print(url)
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
    return requests


def calculateCurrentReminders():
    reminders = fetchRemindersForAllUsers()
    if reminders == None:
        return None
    for rem in reminders:
        ...


def createReminder(r_name, r_freq, r_time):
    return f'Reminder with name {r_name} created, will be repeated: {r_freq}. Notification will be sent in {r_time}'
