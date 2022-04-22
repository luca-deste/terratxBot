import telebot
from telebot import types
import requests
import datetime
import sqlite3
from sqlite3 import Error
import time
from datetime import datetime as dt
import threading
#___________________________
from config import token
from functions import *
#___________________________
url = "https://api.extraterrestrial.money/v1/txs/by_account?account="
hashUrl = "https://terrasco.pe/mainnet/tx/"
database = r'./users.db'
bot = telebot.TeleBot(token, parse_mode=None)
user_started = {}
conn = createConnection(database)
createUserTable = '''CREATE TABLE IF NOT EXISTS users (chatid integer NOT NULL,addr text,date timestamp);'''
createTableSql(conn, createUserTable)
#___________________________
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func
#___________________________
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
        print('qualcosa non va') #TODO: send a message to let user know something might be wrong
#___________________________
def menu(chat_id):
    markup = types.ReplyKeyboardMarkup()
    itemAdd = types.KeyboardButton('Add Address')
    itemRemove = types.KeyboardButton('Remove Address')
    itemInfo = types.KeyboardButton('info')
    markup.row(itemAdd,itemRemove)
    markup.row(itemInfo)
    msg = bot.send_message(chat_id, "what can i do for you", reply_markup=markup)
    bot.register_next_step_handler(msg, handleResponse)
#___________________________
def addAddr(message):
    chat_id = message.chat.id
    try:
        bot.delete_message(message.chat.id,message.id)
        if message.text == 'Back':
            menu(chat_id)
        elif message.text[0:5] == 'terra':
            addAddrToDatabase(conn,(message.text,chat_id))
            addDateToDatabase(conn,(dt.now(),chat_id))
            bot.send_message(chat_id,'Perfect! now i will notify you when a transaction that regards your address will be transmitted. Pleas note that it might be a delay between the notification and the actual transaction on the blockchain.')
            menu(chat_id)
        else:
            bot.send_message('Sorry, i can\'t understand your language') #TODO add github link page
            menu(chat_id)
    except Exception as e:
        print(e)
#___________________________
def handleResponse(message):
    chat_id=message.chat.id
    try:
        if message.text == 'Add Address':
            print('called add address from handle response')
            bot.delete_message(message.chat.id,message.id)
            markup = types.ReplyKeyboardMarkup()
            itemBack = types.KeyboardButton('Back')
            markup.row(itemBack)
            msg = bot.send_message(chat_id, "Please, send me the address that you want to monitor. Please remember that for now you can only monitor one address at time.", reply_markup=markup)
            bot.register_next_step_handler(msg,addAddr)
        elif message.text == "Remove Address":
            bot.delete_message(message.chat.id,message.id)
            rmAddrFromDatabase(conn,(chat_id,))
            bot.send_message(chat_id,'You\'re account was succesfullly deleted.')
            menu(chat_id)
        elif message.text == 'info':
            info(message) #TODO: create info message
        else:
            bot.send_message(chat_id,'Sorry, i can\'t understand your language')
            menu(chat_id)
    except Exception as e:
        print(e)
#___________________________
@background
def infinityWalletUpdates():
    while True:
        trxDict = {}
        try:
            chatlist = returnAllChatIds(conn)
        except TypeError:
            time.sleep(10)
        if chatlist != []:
            for chat_id in chatlist:
                tx = 0
                chat_id = chat_id[0]
                trxDict[chat_id]={}
                addr = returnAddress(conn,chat_id)
                date = dt.strptime(returnDateFromId(conn,chat_id), '%Y-%m-%d %H:%M:%S')
                if addr:
                    trxList = requests.get(url + addr)
                    if trxList.status_code == 200: #TODO: add possibility of status code 500 for server error
                        trxList = trxList.json()
                        timestamp = dt.strptime(trxList['txs'][tx]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                        if timestamp > date:
                            trxDict[chat_id]['timestamp'] = timestamp
                            trxDict[chat_id]['txNum'] = []
                            while timestamp > date and tx < 9:
                                trxDict[chat_id]['txNum'].insert(0,tx)
                                tx = tx + 1
                                timestamp = dt.strptime(trxList['txs'][tx]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                            for transaction in trxDict[chat_id]['txNum']:
                                TxHash = trxList["txs"][transaction]['txhash']
                                bot.send_message(chat_id,'I\'ve found a new transaction to your address!\n You can find more info about it here: '+hashUrl+TxHash)
                            addDateToDatabase(conn,(trxDict[chat_id]['timestamp'],chat_id))
                        else:
                            print('no new transactions for this address, chat id: ' + str(chat_id))
                            pass
                    else:
                        print('this is probably not a valid terra address sorry' + str(chat_id))
                        pass
                else:
                    pass
        else:
            pass
        time.sleep(120)
#___________________________
infinityWalletUpdates()
bot.polling()