from aiogram.fsm.state import StatesGroup, State


class Casino(StatesGroup):
    dice = State()
    darts = State()
    slots = State()
    ball = State()
    bet = State()
