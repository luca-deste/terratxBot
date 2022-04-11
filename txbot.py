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
                print('cis')
            else:
                pass
            bot.delete_message(message.chat.id,message.id)
            bot.send_message(chat_id,'hi,welcome to the terra transaction Bot')
            markup = types.ReplyKeyboardMarkup()
            itemAdd = types.KeyboardButton('Add Address')
            itemRemove = types.KeyboardButton('Remove Address')
            markup.row(itemAdd,itemRemove)
            msg = bot.send_message(chat_id, "what can i do for you", reply_markup=markup)
            bot.register_next_step_handler(msg, handleResponse)
        except Exception as e:
            print(e)
    else:
        print('qualcosa non va')

bot.polling()