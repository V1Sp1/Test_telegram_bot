from telebot.handler_backends import State, StatesGroup


class RegStates(StatesGroup):
    name = State()
    surname = State()
    done = State()


class SumStates(StatesGroup):
    num1 = State()
    num2 = State()