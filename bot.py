import telebot
import os

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)
