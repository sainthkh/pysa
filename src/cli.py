import sys
import argparse
import os
import sqlite3
import stock.companies as companies
from stock.openapi import init_openapi

dbPath = os.getcwd() + '/db.db'
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
    print(openapi.get_total_data('005930', '210906'))

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
