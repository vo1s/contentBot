from datetime import datetime

from aiogram import Router, types
from aiogram.filters import CommandStart

from db import add_user
from keyboards.main_keyboard import main_keyboard
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    user_data = {
        "_id": user_id,
        "username": message.from_user.username,
        "subscription_status": "free",
        "registration_date": datetime.now(),
        "is_premium": message.from_user.is_premium,
        "balance": 10,
        "private_status": False,
        "photo_index": 1
    }
    await add_user(user_data)

    await message.answer(f"Добро пожаловать в бота!", reply_markup=main_keyboard)
