from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config


def confirm_withdraw_keyboard_admin(amount_rub: int, user_id: int):
    buttons = [
        [
            InlineKeyboardButton(text="💰Подтвердить", callback_data=f"admin_confirm_withdraw:{amount_rub}:{user_id}"),
        ],
        [
            InlineKeyboardButton(text="🙅🏻‍Отклонить", callback_data=f"admin_decline_withdraw:{amount_rub}:{user_id}")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_money(url: str):
    buttons = [
        [
            InlineKeyboardButton(text="💰Получить", url=url),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)