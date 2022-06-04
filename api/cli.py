import sys
import argparse
import os
import sqlite3
import datetime
import stock.companies as companies
from stock.openapi import init_openapi

is_64bits = sys.maxsize > 2**32
if is_64bits:
    raise Exception('32bit 환경으로 실행하여 주시기 바랍니다.')
else:
    print('32bit env')

dbPath = os.getcwd() + '/../db.db'
con = sqlite3.connect(dbPath)
cur = con.cursor()

def table_exists(name: str):
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ''', (name,))

    if cur.fetchone()[0] == 1: 
        return True
    
    return False

def update(args):
    if not table_exists('companies'):
        print('update-companies로 회사 목록을 생성해 주세요.')
        return

    date = datetime.date.today()

    if datetime.datetime.now().hour < 16:
        date = date - datetime.timedelta(days=1)

    print('날짜: ' + date.strftime('%Y%m%d'))

    openapi = init_openapi()

    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    for row in cur.fetchall():
        code, name = row
        if not table_exists(code):
            print('테이블 생성 중: {}({})'.format(name, code))
            cur.execute('''CREATE TABLE '{}'
                (date text, open integer, high integer, low integer, close integer, volume integer)'''.format(code))
        
        data = openapi.get_first_600_days(code, date.year, date.month, date.day)

        for d in data.reverse():
            cur.execute('''INSERT INTO '{}' VALUES (?, ?, ?, ?, ?, ?) '''.format(code), (d['date'], d['open'], d['high'], d['low'], d['close'], d['volume']))
        
        con.commit()

def update_companies(args):
    print('테이블 생성 중...')

    if table_exists('companies'):
        cur.execute('''DROP TABLE companies''')

    # type: 
    #  - 0: 정상
    #  - 1: 불성실공시법인
    #  - 2: 관리종목
    cur.execute('''CREATE TABLE companies
        (code text, name text, category text, product text, type integer)''')

    print('회사 목록 다운로드 중...')
    c = companies.get_companies()

    print('데이터 입력 중...')
    for index, row in c.iterrows():
        cur.execute('''INSERT INTO companies VALUES (?,?,?,?,?)''', (row['code'], row['code_name'], row['category'], row['product'], 0))
    
    print('불성실공시법인 목록 다운로드 중...')
    ci = companies.get_companies_insincerity()

    print('불성실공시법인 데이터 입력 중...')
    for index, row in ci.iterrows():
        cur.execute('''UPDATE companies SET type = 1 WHERE code = ?''', (row['code'],))

    print('관리종목 목록 다운로드 중...')
    cm = companies.get_companies_managing()

    print('관리종목 데이터 입력 중...')
    for index, row in cm.iterrows():
        cur.execute('''UPDATE companies SET type = 2 WHERE code = ?''', (row['code'],))

    con.commit()

    print('업데이트 완료.')

def drop_data_tables(args):
    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    for row in cur.fetchall():
        code, name = row

        if table_exists(code):
            print('테이블 삭제 중: {}({})'.format(name, code))
            cur.execute('''DROP TABLE '{}' '''.format(code))

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_sub = subparsers.add_parser('update')
parser_sub.set_defaults(func=update)

parser_sub = subparsers.add_parser('update-companies')
parser_sub.set_defaults(func=update_companies)

parser_sub = subparsers.add_parser('drop')
parser_sub.set_defaults(func=drop_data_tables)

args = parser.parse_args()
args.func(args)
