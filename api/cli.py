import sys
import argparse
import os
import sqlite3
import stock.companies as companies
from stock.openapi import init_openapi

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
    c = companies.get_companies()

    for index, row in c.iterrows():
        print(row['code'], row['code_name'], row['category'], row['product'])

    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='companies' ''')

    if cur.fetchone()[0] == 1: 
        cur.execute('''DROP TABLE companies''')
        
    cur.execute('''CREATE TABLE companies
        (code text, name text, category text, product text, type integer)''')

def listStocks(args):
    print('listStocks')

def input(args):
    print('input')

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_add = subparsers.add_parser('init')
parser_add.set_defaults(func=init)

parser_sub = subparsers.add_parser('update')
parser_sub.set_defaults(func=update)

parser_sub = subparsers.add_parser('list')
parser_sub.set_defaults(func=listStocks)

parser_sub = subparsers.add_parser('input')
parser_sub.set_defaults(func=input)

args = parser.parse_args()
args.func(args)
