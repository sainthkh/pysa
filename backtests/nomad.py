import argparse
import os
import sqlite3
import json

dbPath = os.getcwd() + '/../db.db'
con = sqlite3.connect(dbPath)
cur = con.cursor()

def gather(_):
    cur.execute('SELECT code, name FROM companies WHERE type = 0')

    result = {}

    for row in cur.fetchall():
        code, name = row

        print(name, code)

        volume_diff(name, code, result)
    
    json.dump(result, open('nomad.json', 'w', encoding='utf8'), indent=2, ensure_ascii=False)

def volume_diff(name, code, result):
    cur.execute('''SELECT date, volume, open, close, high, low from '{}' '''.format(code))

    DATE = 0
    VOLUME = 1
    OPEN = 2
    CLOSE = 3
    HIGH = 4
    LOW = 5

    rows = cur.fetchall()
    size = len(rows)

    dates = []

    # volume 1000만, 25% 확인.
    for i, row in enumerate(rows):
        if i < 6:
            continue

        if i == size - 1 - 15:
            break

        volume_yesterday = rows[i-1][VOLUME]
        volume_today = rows[i][VOLUME]
        volume_tomorrow = rows[i+1][VOLUME]

        if volume_yesterday == 0:
            continue

        if (
            volume_today > 10000000 and 
            (i > 0 and volume_today > 5 * rows[i - 1][VOLUME]) and
            volume_tomorrow < .25 * volume_today and
            rows[i + 1][CLOSE] < rows[i + 1][OPEN]
        ):
            # dates.append(row)
            # print(date, rows[i-1][1], volume, close)
            # 7일 평균 계산 및 확인.
            sum = 0
            for j in range(7):
                sum = sum + rows[i + 1 - j][CLOSE]
            
            avg = sum / 7

            close_tomorrow = rows[i + 1][CLOSE]

            if (close_tomorrow > .95 * avg and close_tomorrow < 1.05 * avg):
                purchase_price = rows[i + 1][CLOSE]
                highs = []
                lows = []
                
                for j in range(15):
                    date_index = i + 2 + j
                    if (rows[date_index][HIGH] > purchase_price * 1.02):
                        highs.append((rows[date_index][DATE], rows[date_index][HIGH]))
                    
                    if (rows[date_index][LOW] < purchase_price * .95):
                        lows.append((rows[date_index][DATE], rows[date_index][LOW]))
                
                # print('**', rows[i + 1][DATE], rows[i + 1][CLOSE])
                # print('high:', highs)
                # print('low:', lows)

                data = {
                    "date": rows[i + 1][DATE],
                    "close": rows[i + 1][CLOSE],
                    "highs": highs,
                    "lows": lows,
                }

                dates.append(data)
    
    result['''{}({})'''.format(name, code)] = dates

def research(_):
    data = json.load(open('nomad.json', 'r', encoding='utf8'))

    success_rate(data)
    yearly(data)

def success_rate(data):
    counter = 0
    empty_high = 0

    for key, value in data.items():
        counter = counter + 1

        for date in value:
            if len(date["highs"]) == 0:
                empty_high = empty_high + 1
    
    print(f'총: {counter}, 실패: {empty_high}, 비율: {empty_high / counter}')

def yearly(data):
    years = {}

    for key, value in data.items():
        for date in value:
            year = date["date"][:4]

            if not year in years:
                years[year] = 0
            
            years[year] = years[year] + 1
    
    print("연간 횟수")
    years = dict(sorted(years.items()))
    for y, count in years.items():
        print(f'{y}: {count}')

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_sub = subparsers.add_parser('gather')
parser_sub.set_defaults(func=gather)

parser_sub = subparsers.add_parser('res')
parser_sub.set_defaults(func=research)

args = parser.parse_args()
args.func(args)
