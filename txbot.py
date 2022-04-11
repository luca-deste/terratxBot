import telebot
import requests
from config import token
import sqlite3
from sqlite3 import Error
import time
from functions import *
from telebot import types

url = "https://api.extraterrestrial.money/v1/txs/by_account?account="
database = r'./users.db'
bot = telebot.TeleBot(token, parse_mode=None)
user_started = {}
conn = createConnection(database)

createUserTable = '''CREATE TABLE IF NOT EXISTS users (chatid integer NOT NULL,addr text);'''
print('Created User table')
createTableSql(conn, createUserTable)

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
            print('User added to database')
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
            removeAddr(message)
        elif message.text == 'info':
            print('called info from handle response')
            info(message)
        else:
            print('i dunno wat that is')
    except Exception as e:
        print(e)
bot.polling()