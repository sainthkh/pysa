import sys
import argparse
import os
import sqlite3
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

def init(args):
    cur.execute('''CREATE TABLE prices
        (code text, high int, low int, start int, end int, date text)''')
    cur.execute('''CREATE TABLE companies
        (code text, name text)''')
    cur.execute('''CREATE TABLE config
        (key text, value text)''')

def update(args):
    openapi = init_openapi()
    print(openapi.get_total_data('005930', 2020, 4, 24))

def update_companies(args):
    print('Creating table...')
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='companies' ''')

    if cur.fetchone()[0] == 1: 
        cur.execute('''DROP TABLE companies''')
    
    # type: 
    #  - 0: 정상
    #  - 1: 불성실공시법인
    #  - 2: 관리종목
    cur.execute('''CREATE TABLE companies
        (code text, name text, category text, product text, type integer)''')

    print('Downloading...')
    c = companies.get_companies()

    print('Inserting data...')
    for index, row in c.iterrows():
        cur.execute('''INSERT INTO companies VALUES (?,?,?,?,?)''', (row['code'], row['code_name'], row['category'], row['product'], 0))
    
    con.commit()

    print('Update finished.')

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_add = subparsers.add_parser('init')
parser_add.set_defaults(func=init)

parser_sub = subparsers.add_parser('update')
parser_sub.set_defaults(func=update)

parser_sub = subparsers.add_parser('update-companies')
parser_sub.set_defaults(func=update_companies)

args = parser.parse_args()
args.func(args)
