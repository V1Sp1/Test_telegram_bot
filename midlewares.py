from telebot import TeleBot
from telebot.types import Message
from telebot.handler_backends import BaseMiddleware, CancelUpdate


class RegMiddleware(BaseMiddleware):
    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.authorized = {}
        self.update_types = ['message']
    def pre_process(self, message: Message, data):
        if not message.from_user.id in self.authorized or self.authorized[message.from_user.id] == False:
            self.authorized[message.from_user.id] = False
            if message.text != "/start":
                self.bot.send_message(message.chat.id, 'Необходимо представиться!')
                return CancelUpdate()
            return

    def post_process(self, message, data, exception):
        if message.text == "/start":
            self.authorized[message.from_user.id] = True

class ChatMiddleware(BaseMiddleware):
    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.update_types = ['message']
    def pre_process(self, message: Message, data):
        data["chat"] = message.chat
        return

    def post_process(self, message, data, exception):
        pass
