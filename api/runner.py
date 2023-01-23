import asyncio
import sys
import sqlite3
import os

dbPath = os.getcwd() + '/../db.db'
con = sqlite3.connect(dbPath)
cur = con.cursor()

async def update_all():
    cur.execute('''SELECT code, name
        FROM    companies
        WHERE   rowid = (SELECT MAX(rowid) FROM companies);''')

    code, name = cur.fetchone()

    while True:
        cur.execute('''SELECT value FROM settings WHERE key="ua-last-company-code"''')

        value, = cur.fetchone()

        if code == value:
            break

        proc = await asyncio.create_subprocess_exec(
            sys.executable, 'cli.py', 'update-all',
            stdout=asyncio.subprocess.PIPE)

        print("실행했습니다.")

        # Wait for the subprocess exit.
        await proc.wait()
        
        print("종료")

asyncio.run(update_all())
