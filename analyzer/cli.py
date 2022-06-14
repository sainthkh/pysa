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

def volume_diff(args):
    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    companies = [[], [], []]

    for row in cur.fetchall():
        code, name = row

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

def volume_and_increase(args):
    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    companies = [[], [], []]

    for row in cur.fetchall():
        code, name = row

        if table_exists(code):
            cur.execute('''SELECT volume, close from '{}' ORDER BY date DESC LIMIT 2'''.format(code))

            data = []

            for d in cur.fetchall():
                data.append({
                    'volume': d[0],
                    'close': d[1],
                })
            
            if len(data) == 0:
                continue

            if (data[0]['close'] > 1.2 * data[1]['close']): # 20% 이상 상승
                if data[0]['volume'] > 10000000:
                    companies[0].append((code, name))
                elif data[0]['volume'] > 5000000:
                    companies[1].append((code, name))
                else:
                    companies[2].append((code, name))
    
    for c in companies:
        print_companies(c)

def month_dec(args):
    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    companies = []

    for row in cur.fetchall():
        code, name = row

        if table_exists(code):
            cur.execute('''SELECT close from '{}' ORDER BY date DESC LIMIT 25'''.format(code))
        
            data = []

            for d in cur.fetchall():
                data.append({
                    'close': d[0],
                })
            
            if len(data) < 25:
                continue
            
            if (data[0]['close'] < 0.6 * data[24]['close']):
                print(name, code, 1 - data[0]['close'] / data[24]['close'])

def minimum(args):
    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    companies = []

    for row in cur.fetchall():
        code, name = row

        if table_exists(code):
            cur.execute('''SELECT low from '{}' ORDER BY date DESC LIMIT 250'''.format(code))

            data = []

            for d in cur.fetchall():
                data.append({
                    'low': d[0],
                })
            
            today_lowest = True

            for i in range(1, len(data)):
                if data[0]['low'] > data[i]['low']:
                    today_lowest = False
                    break
            
            if today_lowest:
                companies.append((code, name))
    
    print_companies(companies)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_sub = subparsers.add_parser('volume-diff')
parser_sub.set_defaults(func=volume_diff)

parser_sub = subparsers.add_parser('volume-inc')
parser_sub.set_defaults(func=volume_and_increase)

parser_sub = subparsers.add_parser('month-dec')
parser_sub.set_defaults(func=month_dec)

parser_sub = subparsers.add_parser('min')
parser_sub.set_defaults(func=minimum)

args = parser.parse_args()
args.func(args)
