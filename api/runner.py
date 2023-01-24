import asyncio
import sys
import sqlite3
import os
import argparse

dbPath = os.getcwd() + '/../db.db'
con = sqlite3.connect(dbPath)
cur = con.cursor()

async def run_update_all():
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

        print("프로세스를 실행했습니다.")

        # Wait for the subprocess exit.
        await proc.wait()
        
        print("프로세스를 종료합니다.")
    
    print("업데이트가 완료되었습니다.")

def update_all(args):
    asyncio.run(run_update_all())

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_sub = subparsers.add_parser('update-all')
parser_sub.set_defaults(func=update_all)

args = parser.parse_args()
args.func(args)
