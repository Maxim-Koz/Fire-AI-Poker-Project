import sqlite3

name = 'jeff'  
pword = 'password123' #!change to where an import later


conn = sqlite3.connect('login.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users
    (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    score INTEGER  -- Optional, can be null
    ''')

