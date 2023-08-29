import telebot
from telebot.util import extract_arguments
from telebot.custom_filters import StateFilter
from random import randrange
from datetime import datetime
import requests

from filters import IsText
from midlewares import RegMiddleware, ChatMiddleware
from private_config import api_token
from setting import command_start, command_help, command_cat_img, command_bank, command_echo, command_sum
from states import RegStates, SumStates

bot = telebot.TeleBot(api_token, use_class_middlewares=True)



bot.set_my_commands([
    telebot.types.BotCommand(f"/{command_start}", "welcome message"),
    telebot.types.BotCommand(f"/{command_help}", "print usage"),
    telebot.types.BotCommand(f"/{command_cat_img}", "send random image with cat"),
    telebot.types.BotCommand(f"/{command_bank}", "allows you to find out the exchange rates"),
    telebot.types.BotCommand(f"/{command_echo}", "send the message text after the command"),
    telebot.types.BotCommand(f"/{command_sum}", "asks for 2 numbers and prints their sum"),
])


@bot.message_handler(commands=[command_start], state=[None])
def start_name(message, chat):
    bot.set_state(user_id = message.from_user.id, state = RegStates.name, chat_id = chat.id)
    bot.send_message(message.chat.id, "Напишите ваше имя:")

@bot.message_handler(content_types=["text"], state=RegStates.name, is_text=True)
def start_surname(message, chat):
    bot.add_data(user_id = message.from_user.id, chat_id = chat.id, name = message.text)
    bot.set_state(user_id = message.from_user.id, state = RegStates.surname, chat_id = chat.id)
    bot.send_message(chat.id, "Напишите вашу фамилию:")

@bot.message_handler(content_types=["text"], state=RegStates.surname, is_text=True)
def start_done(message, chat):
    bot.add_data(user_id = message.from_user.id, chat_id = chat.id, surname = message.text)
    bot.set_state(user_id = message.from_user.id, state = RegStates.done, chat_id = chat.id)
    bot.send_message(chat.id, "Вы успешно зарегестрированы в боте!")

@bot.message_handler(commands=[command_start], state=RegStates.done)
def hello_message(message, chat):
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=chat.id) as data:
        bot.send_message(chat.id, f"Привет, {data['name']} {data['surname']}")

@bot.message_handler(content_types=telebot.util.content_type_media, state=[RegStates.name, RegStates.surname, SumStates.num1, SumStates.num2], is_text=False)
def start_error(message, chat):
    bot.send_message(chat.id, "Введите корректный текст, пожалуйста")

@bot.message_handler(commands=[command_help])
def help_message(message, chat):
    bot.send_message(chat.id, f"/{command_start} - приветственное сообщение\n"
                                      f"/{command_help} - список команд\n"
                                      f"/{command_cat_img} - посылает случайную картинку кота из набора\n"
                                      f"/{command_bank} - выводит курс доллара и евро к рублю\n"
                                      f"/{command_echo} - посылает текст сообщения после команды\n"  # arguments of command
                                      f"/{command_sum} - запрашивает 2 числа и вычисляет сумму") # arguments of command

@bot.message_handler(commands=[command_cat_img])
def send_img(message, chat):
    img = open(f"./imgs/testImg{randrange(5)}.jpg", 'rb')
    bot.send_photo(chat.id, img, caption="cute cat")


@bot.message_handler(commands=[command_bank])
def send_bank(message, chat):
    response = requests.get('https://www.cbr-xml-daily.ru/latest.js')
    if response.status_code != 200:
        bot.send_message(chat.id, "Ошибка сервера валют")
        return
    parseRes = response.json()
    date = datetime.fromtimestamp(parseRes['timestamp'])
    bot.send_message(chat.id,
                     f"Курсы валют на момент: {date.strftime('%d.%m.%Y, %H:%M:%S')} \n"
                     f"USD: {1 / parseRes['rates']['USD']}\nEUR: {1 / parseRes['rates']['EUR']}")


@bot.message_handler(commands=[command_echo])
def echo(message, chat):
    bot.send_message(chat.id, f"{extract_arguments(message.text)}")


@bot.message_handler(commands=[command_sum])
def sum(message, chat):
    bot.send_message(chat.id, "Введите первое число:")
    bot.set_state(user_id=message.from_user.id, state=SumStates.num1, chat_id=chat.id)


@bot.message_handler(content_types=["text"], state=SumStates.num1, is_text=True)
def sum_num1(message, chat):
    try:
        num = int(message.text)
        bot.add_data(user_id = message.from_user.id, chat_id = chat.id, num1 = num)
        bot.send_message(chat.id, "Введите второе число:")
        bot.set_state(user_id = message.from_user.id, state = SumStates.num2, chat_id = chat.id)
    except:
        bot.send_message(chat.id, "Введите корректное число!")


@bot.message_handler(content_types=["text"], state=SumStates.num2, is_text=True)
def sum_num2(message, chat):
    try:
        num = int(message.text)
    except:
        bot.send_message(chat.id, "Введите корректное число!")
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=chat.id) as data:
        bot.send_message(chat.id, f"Сумма: {data['num1'] + num}")
    bot.set_state(user_id = message.from_user.id, state = RegStates.done, chat_id = chat.id)



@bot.message_handler(content_types=telebot.util.content_type_media)
def rubbish_message(message):
    bot.reply_to(message, "Это просто чудесно!")


bot.add_custom_filter(StateFilter(bot))
bot.add_custom_filter(IsText())

bot.setup_middleware(RegMiddleware(bot))
bot.setup_middleware(ChatMiddleware(bot))

if __name__ == '__main__':
    bot.infinity_polling()