import argparse
import os
import sqlite3

dbPath = os.getcwd() + '/../db.db'
con = sqlite3.connect(dbPath)
cur = con.cursor()

def table_exists(name: str):
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ''', (name,))

    if cur.fetchone()[0] == 1: 
        return True
    
    return False

def print_companies(companies):
    print('-----------------------------------------------------')

    if len(companies) == 0:
        print('없음')
    else:
        for c in companies:
            print('{}({})'.format(c[1], c[0]))

def find(args):
    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    companies = [[], [], []]

    for row in cur.fetchall():
        code, name = row

        # print('검색중: {}({})'.format(name, code))

        if table_exists(code):
            cur.execute('''SELECT volume, open, close from '{}' ORDER BY date DESC LIMIT 3'''.format(code))

            data = []

            for d in cur.fetchall():
                data.append({
                    'volume': d[0],
                    'open': d[1],
                    'close': d[2],
                })
            
            if len(data) == 0:
                continue

            if (
                data[2]['open'] > data[2]['close'] and # 음봉
                data[1]['volume'] > 5 * data[0]['volume'] and data[2]['volume'] < 0.12 * data[1]['volume'] # 거래량 감소
            ):
                if data[1]['volume'] > 10000000:
                    companies[0].append((code, name))
                elif data[1]['volume'] > 7500000:
                    companies[1].append((code, name))
                elif data[1]['volume'] > 5000000:
                    companies[2].append((code, name))
    
    for c in companies:
        print_companies(c)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_sub = subparsers.add_parser('find')
parser_sub.set_defaults(func=find)

args = parser.parse_args()
args.func(args)