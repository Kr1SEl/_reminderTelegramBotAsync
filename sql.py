import sqlite3

con = sqlite3.connect("users.sqlite")
cur = con.cursor()
cur.execute(
    "CREATE TABLE user(user_id, app_name, app_surname, app_email, tg_username, tg_chat_id)")
