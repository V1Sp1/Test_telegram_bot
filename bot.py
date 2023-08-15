import telebot
from telebot.util import extract_arguments
from random import randrange
from datetime import datetime
import requests
from private_config import api_token
from setting import command_start, command_help, command_cat_img, command_bank, command_echo


bot = telebot.TeleBot(api_token)


bot.set_my_commands([
    telebot.types.BotCommand(f"/{command_start}", "welcome message"),
    telebot.types.BotCommand(f"/{command_help}", "print usage"),
    telebot.types.BotCommand(f"/{command_cat_img}", "send random image with cat"),
    telebot.types.BotCommand(f"/{command_bank}", "allows you to find out the exchange rates"),
    telebot.types.BotCommand(f"/{command_echo}", "send the message text after the command"),
])


@bot.message_handler(commands=[command_start])
def start_message(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} {message.from_user.last_name}")

@bot.message_handler(commands=[command_help])
def start_message(message):
    bot.send_message(message.chat.id, f"/{command_start} - приветственное сообщение\n"
                                      f"/{command_help} - список команд\n"
                                      f"/{command_cat_img} - посылает случайную картинку кота из набора\n"
                                      f"/{command_bank} - выводит курс доллара и евро к рублю\n"
                                      f"/{command_echo} - посылает текст сообщения после команды\n") # arguments of command

@bot.message_handler(commands=[command_cat_img])
def send_img(message):
    img = open(f"./imgs/testImg{randrange(5)}.jpg", 'rb')
    bot.send_photo(message.chat.id, img, caption="cute cat")


@bot.message_handler(commands=[command_bank])
def send_bank(message):
    response = requests.get('https://www.cbr-xml-daily.ru/latest.js')
    if response.status_code != 200:
        bot.send_message(message.chat.id, "Ошибка сервера валют")
        return
    parseRes = response.json()
    date = datetime.fromtimestamp(parseRes['timestamp'])
    bot.send_message(message.chat.id,
                     f"Курсы валют на момент: {date.strftime('%d.%m.%Y, %H:%M:%S')} \n"
                     f"USD: {1 / parseRes['rates']['USD']}\nEUR: {1 / parseRes['rates']['EUR']}")


@bot.message_handler(commands=[command_echo])
def echo(message):
    bot.send_message(message.chat.id, f"{extract_arguments(message.text)}")

@bot.message_handler(content_types=["text"])
def rubbish_message(message):
    bot.reply_to(message, "Прекрасно сказано!")

if __name__ == '__main__':
    bot.infinity_polling()