import telebot
import requests
import datetime
from config import token
import sqlite3
from sqlite3 import Error
import time
from functions import *
from telebot import types
import threading
from datetime import datetime as dt

url = "https://api.extraterrestrial.money/v1/txs/by_account?account="
hashUrl = "https://terrasco.pe/mainnet/tx/"
database = r'./users.db'
bot = telebot.TeleBot(token, parse_mode=None)
user_started = {}
conn = createConnection(database)

createUserTable = '''CREATE TABLE IF NOT EXISTS users (chatid integer NOT NULL,addr text,date timestamp);'''
print('Created User table')
createTableSql(conn, createUserTable)

def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func

@bot.message_handler(commands=['start'])
def starting(message):
    chat_id = message.chat.id
    if not chat_id in user_started:
        user_started[chat_id] = True
        time.sleep(0.5)
        user_started.pop(chat_id)
        try:
            if not checkUserExistence(conn, chat_id):
                createUser(conn,chat_id)
                print('created chat id index for table')
            else:
                pass
            bot.delete_message(message.chat.id,message.id)
            bot.send_message(chat_id,'hi,welcome to the terra transaction Bot')
            markup = types.ReplyKeyboardMarkup()
            itemAdd = types.KeyboardButton('Add Address')
            itemRemove = types.KeyboardButton('Remove Address')
            itemInfo = types.KeyboardButton('info')
            markup.row(itemAdd,itemRemove)
            markup.row(itemInfo)
            msg = bot.send_message(chat_id, "what can i do for you", reply_markup=markup)
            bot.register_next_step_handler(msg, handleResponse)
        except Exception as e:
            print(e)
    else:
        print('qualcosa non va')

def menu(chat_id):
    markup = types.ReplyKeyboardMarkup()
    itemAdd = types.KeyboardButton('Add Address')
    itemRemove = types.KeyboardButton('Remove Address')
    itemInfo = types.KeyboardButton('info')
    markup.row(itemAdd,itemRemove)
    markup.row(itemInfo)
    msg = bot.send_message(chat_id, "what can i do for you", reply_markup=markup)
    bot.register_next_step_handler(msg, handleResponse)


def addAddr(message):
    chat_id = message.chat.id
    try:
        print('addAddr Started')
        bot.delete_message(message.chat.id,message.id)
        if message.text == 'Back':
            print('User want to go back')
            menu(chat_id)
        elif message.text[0:5] == 'terra':
            print('User want to monitor terra address')
            addAddrToDatabase(conn,(message.text,chat_id))
            addDateToDatabase(conn,(dt.now(),chat_id))
            print('User added to database')
            bot.send_message(chat_id,'Perfect! now i will notify you when a transaction that regards your address will be transmitted. Pleas note that it might be a delay between the notification and the actual transaction on the blockchain.')
            menu(chat_id)
        else:
            print('i dunno wat user want to do')
            bot.send_message('Sorry, i can\'t understand your language') #TODO add github link page
            menu(chat_id)
    except Exception as e:
        print(e)

def handleResponse(message):
    chat_id=message.chat.id
    try:
        print('handleResponse function called')
        if message.text == 'Add Address':
            print('called add address from handle response')
            bot.delete_message(message.chat.id,message.id)
            markup = types.ReplyKeyboardMarkup()
            itemBack = types.KeyboardButton('Back')
            markup.row(itemBack)
            msg = bot.send_message(chat_id, "Please, send me the address that you want to monitor. Please remember that for now you can only monitor one address at time.", reply_markup=markup)
            bot.register_next_step_handler(msg,addAddr)
        elif message.text == "Remove Address":
            print('called Remove Address from handle response')
            bot.delete_message(message.chat.id,message.id)
            rmAddrFromDatabase(conn,(chat_id,))
            print('User deleted')
            bot.send_message(chat_id,'You\'re account was succesfullly deleted.')
            menu(chat_id)
        elif message.text == 'info':
            print('called info from handle response')
            info(message)
        else:
            print('i dunno wat that is')
            bot.send_message(chat_id,'Sorry, i can\'t understand your language')
            menu(chat_id)
    except Exception as e:
        print(e)

@background
def infinityWalletUpdates():
    while True:
        trxDict = {}
        try:
            chatlist = returnAllChatIds(conn)
        except TypeError:
            print('there was a typeerror')
            time.sleep(10)
        if chatlist != []:
            for chat_id in chatlist:
                tx = 0
                chat_id = chat_id[0]
                trxDict[chat_id]={}
                addr = returnAddress(conn,chat_id)
                print(addr)
                date = dt.strptime(returnDateFromId(conn,chat_id), '%Y-%m-%d %H:%M:%S')
                print(date)
                if addr:
                    trxList = requests.get(url + addr)
                    print(trxList.status_code)
                    if trxList.status_code == 200:
                        trxList = trxList.json()
                        print(trxList['txs'][tx]['timestamp'])
                        timestamp = dt.strptime(trxList['txs'][tx]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                        print(timestamp > date)
                        if timestamp > date:
                            print('diocan')
                            trxDict[chat_id]['timestamp'] = timestamp
                            trxDict[chat_id]['txNum'] = []
                            while timestamp > date and tx < 9:
                                trxDict[chat_id]['txNum'].insert(0,tx)
                                tx = tx + 1
                                print(tx)
                                timestamp = dt.strptime(trxList['txs'][tx]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                            for transaction in trxDict[chat_id]['txNum']:
                                TxHash = trxList["txs"][transaction]['txhash']
                                bot.send_message(chat_id,'I\'ve found a new transaction to your address!\n You can find more info about it here: '+hashUrl+TxHash)
                            addDateToDatabase(conn,(trxDict[chat_id]['timestamp'],chat_id))
                        else:
                            print('no new transactions for this address, chat id: ' + str(chat_id))
                    else:
                        print('this is probably not a valid terra address sorry' + str(chat_id))
                        pass
                else:
                    pass
                    time.sleep(10)
        else:
            pass
            time.sleep(10)
    time.sleep(10)



        #['txs'][0]['timestamp']
        #datetimeObj = datetime.strptime(noform, '%Y-%m-%dT%H:%M:%SZ')

infinityWalletUpdates()
bot.polling()