from typing import Literal

import pymongo
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config

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

earn_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="👥 Пригласить друзей"),
    ],
    [
        KeyboardButton(text="🎰 Казино"),
    ],
    [
        KeyboardButton(text="🔝 Главное меню")
    ],
], resize_keyboard=True, one_time_keyboard=False, selective=True)


class Pagination1(CallbackData, prefix="pag"):
    action: str
    page: int
    max_photo_index: int
    index_type: Literal['photo_index', 'video_index']


def paginator1(page: int = 0, max_photo_index: int = 0,
               index_type: Literal['photo_index', 'video_index'] = 'video_index'):
    builder = InlineKeyboardBuilder()
    if index_type == 'photo_index':
        last_button = InlineKeyboardButton(text="К последнему фото",
                                           callback_data=f"navigate_last_bought_image:{max_photo_index}")
    else:
        last_button = InlineKeyboardButton(text="К последнему видео",
                                           callback_data=f"navigate_last_bought_video:{max_photo_index}")

    builder.row(
        InlineKeyboardButton(text="👈", callback_data=Pagination(action="prev1", page=page,
                                                                max_photo_index=max_photo_index,
                                                                index_type=index_type).pack()),
        InlineKeyboardButton(text="👉", callback_data=Pagination(action="next1", page=page,
                                                                max_photo_index=max_photo_index,
                                                                index_type=index_type).pack()),
        last_button,
        width=2
    )
    return builder.as_markup()


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int
    max_photo_index: int
    index_type: Literal['photo_index', 'video_index']


def paginator(page: int = 0, max_photo_index: int = 0,
              index_type: Literal['photo_index', 'video_index'] = 'photo_index'):
    builder = InlineKeyboardBuilder()
    if index_type == 'photo_index':
        last_button = InlineKeyboardButton(text="К последнему фото",
                                           callback_data=f"navigate_last_bought_image:{max_photo_index}")
    else:
        last_button = InlineKeyboardButton(text="К последнему видео",
                                           callback_data=f"navigate_last_bought_video:{max_photo_index}")

    builder.row(
        InlineKeyboardButton(text="👈", callback_data=Pagination(action="prev", page=page,
                                                                max_photo_index=max_photo_index,
                                                                index_type=index_type).pack()),
        InlineKeyboardButton(text="👉", callback_data=Pagination(action="next", page=page,
                                                                max_photo_index=max_photo_index,
                                                                index_type=index_type).pack()),
        last_button,
        width=2
    )
    return builder.as_markup()


def no_money_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="⚜️ Premium подписка", callback_data=f"premium_buy"),
        ],

        [
            InlineKeyboardButton(text="👥 Пригласить друзей", callback_data=f"invite_friends"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subscribe(original_command: str, user_id: int, username: str):
    buttons = [
        [
            InlineKeyboardButton(text="⚜️ Подписаться", url=config.channel_link.get_secret_value()),
        ],
        [
            InlineKeyboardButton(text="🔒️ Проверить",
                                 callback_data=f"check_subscription:{original_command}:{user_id}:{username}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
