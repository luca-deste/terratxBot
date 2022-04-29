import telebot
from telebot import types
import datetime
import sqlite3
from sqlite3 import Error
import time
from datetime import datetime as dt
from datetime import timedelta
import threading
from terra_sdk.client.lcd import LCDClient
#___________________________
from functions import *
from config import token
from config import command #Comment this line to use is by yourself
#___________________________

hashUrl = "https://terrasco.pe/mainnet/tx/"
database = r'./users.db'
bot = telebot.TeleBot(token, parse_mode=None)
user_started = {}
conn = createConnection(database)
createUserTable = '''CREATE TABLE IF NOT EXISTS users (chatid integer NOT NULL,addr text);'''
createTableSql(conn, createUserTable)
terra = LCDClient(chain_id="columbus-5", url="https://bombay-lcd.terra.dev")
#___________________________
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func
#___________________________
@bot.message_handler(commands=['start','restart'])
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
        print('qualcosa non va') 
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
        if not checkUserExistence(conn, chat_id):
                createUser(conn,chat_id)
        else:
            pass
        if message.text == 'Back':
            menu(chat_id)
        elif message.text[0:5] == 'terra':
            addAddrToDatabase(conn,(message.text,chat_id))
            addDateToDatabase(conn,((dt.now() - timedelta(hours=2)),chat_id))
            bot.send_message(chat_id,'Perfect! now i will notify you when a transaction that regards your address will be transmitted. Pleas note that it might be a delay between the notification and the actual transaction on the blockchain.')
            menu(chat_id)
        else:
            bot.send_message('Sorry, i can\'t understand your language. If you have a problem you can report it on my github page at: https://github.com/williDuckFoxx/terratxBot')
            menu(chat_id)
    except Exception as e:
        print(e)
#___________________________
def info(message):
    chat_id = message.chat.id
    bot.delete_message(message.chat.id,message.id)
    bot.send_message(chat_id,"Terra transactions bot it\'s a bot developed to help users track their transactions on the terra blockchain.\nIf you want to follow along whit the project or ask for new features you can enter in the group chat (https://t.me/terratxbotgroup)")
    bot.send_message(chat_id,"If you want to help the project you can go on the Github page on https://github.com/williDuckFoxx/terratxBot and leave a star. Or consider to make a small donation to the account")
    bot.send_message(chat_id,"terra1qkyj360typg25plq3ffylwj5grm8wn3n2p53ha")
    menu(chat_id)
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
        elif message.text == 'info' or message.text == '/info':
            info(message)
        #Comment from here to use it by yourself (remove # from the nex line)
        #'''
        elif message.text == command:
            bot.delete_message(message.chat.id,message.id)
            msg = bot.send_message(chat_id,'Please send me the message that you want to transmit.')
            bot.register_next_step_handler(msg,comunication)
        #'''
        #Comment till here to use it by yourself (remove # from the next line)
        else:
            bot.send_message(chat_id,'Sorry, i can\'t understand your language. If you have a problem you can report it on my github page at: https://github.com/williDuckFoxx/terratxBot')
            menu(chat_id)
    except Exception as e:
        print(e)
#___________________________
#Comment from Here to use it by yourself (Just remove the # from the next line)
#'''
def comunication(message):
    text = message.text
    users = returnAllChatIds(conn)
    bot.delete_message(message.chat.id,message.id)
    for user in users:
        print(user)
        bot.send_message(user[0],text)
    menu(message.chat.id)
#'''
#Comment till here to use it by yourself (Just remove the # from the previus line)
#___________________________
@background
def newWalletUpdates():
    while True:
        try:
            starTime = dt.now()
            print(starTime)
            time.sleep(3)
            addresses = returnAllAddr(conn)
            print(addresses)
            encoded_trx = terra.tendermint.block_info()['block']['data']['txs']
            for trx in encoded_trx:
                print(trx)
                for addr in addresses:
                    print(addr[0] + ' from wallet update')
                    if addr[0] in str(terra.tx.decode(trx).to_data()):
                        print('''FOOOUND''')
                        txHash = terra.tx.hash(terra.tx.decode(trx))
                        print(txHash)
                        chat_id = returnChatid(conn,addr[0])
                        print(chat_id)
                        bot.send_message(chat_id, 'I\'ve found a new transaction to your address!\n You can find more info about it here: ' + hashUrl + txHash)
                    else:
                        print('not this time') 
            stopTime = dt.now()
            print(stopTime)
            print('exec time = ' + str(starTime-stopTime))
        except:
            time.sleep(2)
            pass  
#___________________________
newWalletUpdates()
bot.polling()