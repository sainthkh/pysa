import sys
import argparse
import os
import sqlite3
import datetime
import stock.companies as companies
from stock.openapi import init_openapi
import exchange_calendars as ecal

print('Pysa를 실행했습니다.')

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

    date = _most_recent_trade_date()

    openapi = init_openapi()

    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    counter = 0

    for row in cur.fetchall():
        code, name = row
        if not table_exists(code):
            print('테이블 생성 중({}/950): {}({})'.format(counter + 1, name, code))
            cur.execute('''CREATE TABLE '{}'
                (date text, open integer, high integer, low integer, close integer, volume integer)'''.format(code))
        
            data = openapi.get_first_600_days(code, date.year, date.month, date.day)
            data.reverse()

            for d in data:
                cur.execute('''INSERT INTO '{}' VALUES (?, ?, ?, ?, ?, ?) '''.format(code), (d['date'], d['open'], d['high'], d['low'], d['close'], d['volume']))
        else:
            print('테이블 업데이트 중({}/950): {}({})'.format(counter + 1, name, code))

            cur.execute('''SELECT date FROM '{}' ORDER BY date DESC LIMIT 1'''.format(code))

            fetched = cur.fetchone()

            most_recent_db_date = ''

            if fetched is None:
                most_recent_db_date = '00000000' 
            else:
                most_recent_db_date = fetched[0]

            if most_recent_db_date == most_recent_trade_date:
                print('최신 정보. 다음 회사로 이동합니다.')
                continue

            data = openapi.get_first_600_days(code, date.year, date.month, date.day)

            recent_data = []

            for d in data:
                if d['date'] > most_recent_db_date:
                    recent_data.append(d)

            recent_data.reverse()

            for d in recent_data:
                cur.execute('''INSERT INTO '{}' VALUES (?, ?, ?, ?, ?, ?) '''.format(code), (d['date'], d['open'], d['high'], d['low'], d['close'], d['volume']))
        
        con.commit()

        counter += 1

        if counter > 950:
            print('업데이트 완료')
            break

def update_all(args):
    if not table_exists('companies'):
        print('update-companies로 회사 목록을 생성해 주세요.')
        return

    if not table_exists('settings'):
        cur.execute('''CREATE TABLE 'settings'
            (key text, value text)''')
    
    date = _most_recent_trade_date()

    openapi = init_openapi()

    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    for row in cur.fetchall():
        code, name = row
        if not table_exists(code):
            print('테이블 생성 중: {}({})'.format(name, code))
            cur.execute('''CREATE TABLE '{}'
                (date text, open integer, high integer, low integer, close integer, volume integer)'''.format(code))
        
            data = openapi.get_total_data(code, date.year, date.month, date.day)
            data.reverse()

            for d in data:
                cur.execute('''INSERT INTO '{}' VALUES (?, ?, ?, ?, ?, ?) '''.format(code), (d['date'], d['open'], d['high'], d['low'], d['close'], d['volume']))
        else:
            print('{} 회사 정보가 존재합니다. 넘어갑니다.'.format(name))

        con.commit()

        if openapi.count_over():
            print('호출 횟수가 초과되었습니다. 종료합니다.')
            break

def _most_recent_trade_date():
    date = datetime.date.today()

    print('오늘: ' + date.strftime('%Y%m%d'))

    if datetime.datetime.now().hour < 16:
        date = date - datetime.timedelta(days=1)

    xkrx = ecal.get_calendar("XKRX")
    range = xkrx.sessions_in_range(date - datetime.timedelta(days=7), date)
    date = range[-1]
    most_recent_trade_date = date.strftime('%Y%m%d')

    print('최근 거래일: ' + most_recent_trade_date)

    return date

def update_companies(args):
    print('테이블 생성 중...')

    if table_exists('companies'):
        cur.execute('''DROP TABLE companies''')

    # type: 
    #  - 0: 정상
    #  - 1: 불성실공시법인
    #  - 2: 관리종목
    # market:
    #  - 0: KOSPI
    #  - 1: KOSDAQ
    cur.execute('''CREATE TABLE companies
        (code text, name text, category text, product text, type integer, market int)''')

    print('회사 목록 다운로드 중...')
    company_lists = [companies.get_companies_kospi(), companies.get_companies_kosdaq()]

    print('데이터 입력 중...')
    for i, c in enumerate(company_lists):
        for index, row in c.iterrows():
            cur.execute('''INSERT INTO companies VALUES (?,?,?,?,?,?)''', (row['code'], row['code_name'], row['category'], row['product'], 0, i))
        
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

parser_sub = subparsers.add_parser('update-all')
parser_sub.set_defaults(func=update_all)

parser_sub = subparsers.add_parser('update-companies')
parser_sub.set_defaults(func=update_companies)

parser_sub = subparsers.add_parser('drop')
parser_sub.set_defaults(func=drop_data_tables)

args = parser.parse_args()
args.func(args)
