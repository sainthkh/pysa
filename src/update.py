import os
import sqlite3
from stock.openapi import *
from stock.companies import *
from datetime import *

dbPath = os.path.join(os.getcwd(), 'db.db')
con = sqlite3.connect(dbPath)
cur = con.cursor()

lastDate = date.today() if datetime.now().hour >= 18 else date.today() - timedelta(days=1)
lastDate = date.strftime(lastDate, '%Y%m%d')

api = init_openapi()

companies = get_companies_kosdaq()

for index, row in companies.iterrows():
    code = row['code']
    print(row['code'], row['code_name'])

    data = api.get_first_600_days(code, lastDate)

    for d in data:
        cur.execute("INSERT INTO prices VALUES (?,?,?,?,?,?)", 
            (code, d['date'], d['open'], d['high'], d['low'], d['close']))

    con.commit()

con.close()