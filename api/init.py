import os
import sqlite3

dbPath = os.path.join(os.getcwd(), '..', 'db.db')
con = sqlite3.connect(dbPath)
cur = con.cursor()

cur.execute('''CREATE TABLE prices
    (code text, date text, open int, high int, low int, close int)''')
cur.execute('''CREATE TABLE companies
    (code text, name text)''')
cur.execute('''CREATE TABLE config
    (key text, value text)''')