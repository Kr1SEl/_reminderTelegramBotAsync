import sqlite3

con = sqlite3.connect("users.sqlite")
cur = con.cursor()

# (user_id, app_name, app_surname, app_email, tg_username, tg_chat_id)


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


# addUser(1, "r", "r", "r", "r", 1)

# print(userExists(1)[0])

def delUser(user_id):
    cur.execute(
        f"DELETE FROM user WHERE user_id={user_id}")
    con.commit()


delUser(1)
