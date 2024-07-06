import re
from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from db import add_user, get_user_by_id, get_users_collection
from keyboards.main_keyboard import *

router = Router()

users_collection = get_users_collection()


@router.message(CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'^\d+$'))))
async def cmd_start_user(message: Message, command: CommandObject):
    args_id = int(command.args)
    print(args_id)
    # даем преференции пригласившему
    user = await get_user_by_id(args_id)
    referall = await get_user_by_id(message.from_user.id)
    print(referall, message.from_user.id, user)
    if user and referall is None:
        print("passed")
        count_user_refs = user["refs"]
        balance = user["balance"]
        ref_bonus = user["refs_bonus"]
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"refs": int(count_user_refs) + 1, "balance": int(balance) + 10,
                      "refs_bonus": int(ref_bonus) + 10}},
        )
        #Добление рефералла в систему
        user_data = {
            "_id": message.from_user.id,
            "username": message.from_user.username if message.from_user.username else None,
            "subscription_status": "free",
            "registration_date": datetime.now(),
            "is_premium": message.from_user.is_premium,
            "balance": 10,
            "private_status": False,
            "photo_index": 1,
            "refs": 0,
            "refs_bonus": 0
        }
        await add_user(user_data)
        await message.answer(f"Добро пожаловать в бота!", reply_markup=main_keyboard)
    else:
        await message.answer(f"Добро пожаловать в бота!", reply_markup=main_keyboard)


@router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    user_data = {
        "_id": user_id,
        "username": message.from_user.username if message.from_user.username else None,
        "subscription_status": "free",
        "registration_date": datetime.now(),
        "is_premium": message.from_user.is_premium,
        "balance": 10,
        "private_status": False,
        "photo_index": 1,
        "refs": 0,
        "refs_bonus": 0
    }
    await add_user(user_data)

    await message.answer(f"Добро пожаловать в бота!", reply_markup=main_keyboard)


@router.message(F.text == "🔝 Главное меню")
async def earn(message: types.Message):
    await message.answer("🔝 Главное меню", reply_markup=main_keyboard)
