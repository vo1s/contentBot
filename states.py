from aiogram.fsm.state import StatesGroup, State


class Withdraw(StatesGroup):
    amount = State()


class Deposit(StatesGroup):
    money_amount = State()


class Casino(StatesGroup):
    dice = State()
    darts = State()
    slots = State()
    ball = State()
    bet = State()
