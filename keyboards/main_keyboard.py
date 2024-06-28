import pymongo
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="📸 Смотреть фото"),
        KeyboardButton(text="👤 Профиль"),
        KeyboardButton(text="🗂 Категории")
    ],
    [
        KeyboardButton(text="📹 Смотреть видео"),
        KeyboardButton(text="💰 Заработать"),
        KeyboardButton(text="🔒 Подписка"),
    ],
], resize_keyboard=True, one_time_keyboard=False, selective=True)


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int


def paginator(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Prev", callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text="Next", callback_data=Pagination(action="next", page=page).pack()),
        width=2
    )
    return builder.as_markup()
