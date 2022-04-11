from functions import *
from config import token
import time
import sqlite3
from sqlite3 import Error
import requests
import telebot

url = "https://api.extraterrestrial.money/v1/txs/by_account?account="
database = r'./users.db'
bot = telebot.TeleBot(token, parse_mode=None)
conn = createConnection(database)
users_database= {}

def returnchatid(conn):
    cur = conn.cursor()
    arra = []
    sql='select chatid from users'
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        arra.append(row[0])
    return arra

def returnaddress(conn,chatid):
    cur = conn.cursor()
    sql ='select addr from users where chatid=?'
    cur.execute(sql,(chatid,))
    row = cur.fetchone()[0]
    return row

def users_db_fill():
    users = returnchatid(conn)
    addr = []
    print(users)
    for user in users:
        addr.append(returnaddress(conn,user))
        print(addr)


print(users_db_fill())
