from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types


def casino_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🎲 Кубик", callback_data=f"casino_choose:dice"),
        ],
        [
            InlineKeyboardButton(text="🎯 Дартс", callback_data=f"casino_choose:darts"),
        ],
        [
            InlineKeyboardButton(text="🎰 Слоты", callback_data=f"casino_choose:slots"),
        ],
        [
            InlineKeyboardButton(text="🎳 Боулинг", callback_data=f"casino_choose:ball"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_casino_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🔙 Назад к играм", callback_data=f"back_casino"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
