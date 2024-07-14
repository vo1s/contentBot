import re
from datetime import datetime

from aiogram import Router, types, F, Bot
from aiogram.enums import DiceEmoji
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message, CallbackQuery

from db import add_user, get_user_by_id, get_users_collection
from keyboards.main_keyboard import *

router = Router()

users_collection = get_users_collection()


# Вынесение общих данных для добавления пользователя в отдельную функцию
async def add_user_data(user_id, username, is_premium):
    user_data = {
        "_id": user_id,
        "username": username if username else None,
        "subscription_status": "free",
        "registration_date": datetime.now(),
        "is_premium": is_premium,
        "balance": 10,
        "private_status": False,
        "photo_index": 1,
        "max_photo_index": 1,
        "refs": 0,
        "refs_bonus": 0
    }
    await add_user(user_data)


@router.message(CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'^\d+$'))))
async def cmd_start_user(message: Message, command: CommandObject, user_id: int = None, username: str = None,
                         is_premium: bool = None):
    if user_id is None:
        user_id = message.from_user.id
    if username is None:
        username = message.from_user.username
    if is_premium is None:
        is_premium = message.from_user.is_premium

    args_id = int(command.args)
    print(args_id)
    # Даем преференции пригласившему
    user = await get_user_by_id(args_id)
    referall = await get_user_by_id(user_id)
    print(referall, user_id, user)
    if user and referall is None:
        print("passed")
        count_user_refs = user["refs"]
        balance = user["balance"]
        ref_bonus = user["refs_bonus"]
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "refs": int(count_user_refs) + 1,
                "balance": int(balance) + 10,
                "refs_bonus": int(ref_bonus) + 10
            }},
        )
        await add_user_data(user_id, username, is_premium)
        await message.answer("Добро пожаловать в бота!", reply_markup=main_keyboard)
    else:
        await message.answer("Добро пожаловать в бота!", reply_markup=main_keyboard)


@router.message(CommandStart())
async def command_start_handler(message: types.Message, user_id: int = None, username: str = None,
                                is_premium: bool = None) -> None:
    if user_id is None:
        user_id = message.from_user.id
    if username is None:
        username = message.from_user.username
    if is_premium is None:
        is_premium = message.from_user.is_premium

    await add_user_data(user_id, username, is_premium)
    await message.answer("Добро пожаловать в бота!", reply_markup=main_keyboard)


@router.callback_query(F.data.startswith('check_subscription'))
async def check_subscription(callback_query: CallbackQuery):
    user_id = int(callback_query.data.split(':')[2])
    username = callback_query.data.split(':')[3]
    is_premium = callback_query.from_user.is_premium

    chat_member = await callback_query.bot.get_chat_member(config.channel_name.get_secret_value(), user_id)

    if chat_member.status != "left":
        await callback_query.answer("Спасибо за подписку! Теперь у вас есть доступ к боту.")
        await callback_query.message.delete()

        # Извлекаем оригинальную команду из callback_data
        original_command = callback_query.data.split(':', 1)[1]
        print(original_command)
        bot_name = config.bot_name.get_secret_value()

        # Вызов команд с правильными параметрами пользователя
        if original_command.startswith(f'/start?'):
            command_args = original_command.split('?', 1)[1].split(':')[0]
            fake_command = CommandObject(command_args)
            await cmd_start_user(callback_query.message, fake_command, user_id, username, is_premium)
        else:
            await command_start_handler(callback_query.message, user_id, username, is_premium)
    else:
        await callback_query.answer(
            "Вы еще не подписались на канал. Пожалуйста, подпишитесь и попробуйте снова.",
            show_alert=True
        )


@router.message(F.text == "🔝 Главное меню")
async def earn(message: types.Message):
    await message.answer("🔝 Главное меню", reply_markup=main_keyboard)
