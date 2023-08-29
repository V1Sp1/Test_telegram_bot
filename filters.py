from telebot.types import Message
from telebot.custom_filters import SimpleCustomFilter

class IsText(SimpleCustomFilter):
    key = "is_text"

    def check(self, update: Message) -> bool:
        return not((update.text == None) or ("/" == update.text[0]))