# Очищаем Main.py и создаём базовый шаблон
import os
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("Ошибка: BOT_TOKEN не найден!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# КАЖДЫЙ ПИШЕТ СВОЮ ЛОГИКУ ЗДЕСЬ

if __name__ == '__main__':
    bot.polling()