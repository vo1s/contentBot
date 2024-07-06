from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types


def casino_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🎲 Кубик", callback_data=f"qwe"),
        ],
        [
            InlineKeyboardButton(text="🎯 Дартс", callback_data=f"qwe"),
        ],
        [
            InlineKeyboardButton(text="🎰 Слоты", callback_data=f"qwe"),
        ],
        [
            InlineKeyboardButton(text="🎳 Боулинг", callback_data=f"qwe"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
