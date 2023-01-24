import asyncio
import sys
import sqlite3
import os
import argparse

from stock.calendar import *

dbPath = os.getcwd() + '/../db.db'
con = sqlite3.connect(dbPath)
cur = con.cursor()

async def run_update_all():
    print_today()
    print_most_recent_trade_date()

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

async def run_update_daily():
    print_today()
    print_most_recent_trade_date()

    most_recent_trade_date = find_most_recent_trade_date().strftime('%Y%m%d')

    cur.execute('''SELECT code, name
        FROM    companies
        WHERE   rowid = (SELECT MAX(rowid) FROM companies);''')

    code, name = cur.fetchone()

    while True:
        cur.execute('''SELECT value FROM settings WHERE key="ud-last-company-code"''')
        result = cur.fetchone()
        last_code = '000000' if result is None else result[0]

        cur.execute('''SELECT value FROM settings WHERE key="ud-last-date"''')
        result = cur.fetchone()
        last_date = '00000000' if result is None else result[0]

        if most_recent_trade_date is last_date and code is last_code:
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

def update_daily(args):
    asyncio.run(run_update_daily())

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_sub = subparsers.add_parser('update-all')
parser_sub.set_defaults(func=update_all)

parser_sub = subparsers.add_parser('update')
parser_sub.set_defaults(func=update_daily)

args = parser.parse_args()
args.func(args)
