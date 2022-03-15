import telebot
import requests
from config import token

url = "https://api.extraterrestrial.money/v1/txs/by_account?account="

bot = telebot.TeleBot(token, parse_mode=None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hi')

'''@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)'''

bot.polling()