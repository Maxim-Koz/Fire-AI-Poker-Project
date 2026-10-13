import sqlite3
import hashlib

DB_NAME = "users.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_users_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def add_user(username, password):
    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success


def check_user(username, password):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT password_hash FROM users WHERE username=?", (username,))

    result = cur.fetchone()
    conn.close()

    if result is None:
        return False

    return result[0] == hash_password(password)
