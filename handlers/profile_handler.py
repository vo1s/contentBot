from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.utils.formatting import as_list, as_marked_section, Bold, as_line

from db import add_user, get_user_by_id
from keyboards.main_keyboard import main_keyboard

router = Router()


@router.message(F.text == "👤 Профиль")
async def profile(message: types.Message):
    user = await get_user_by_id(message.from_user.id)
    if user:
        content = f"""
📱 Ваш профиль

🔑 ID: {user['_id']}
👤 Логин: {user['username']}
📆 Дата регистрации: {user['registration_date'].strftime('%d-%m-%Y %H:%M')}

💸 Баланс: {user['balance']} 💎 Tokens

⚜️ Premium подписка: {'✅ Активна' if user['subscription_status'] == 'premium' else '❌ Не активна'}
👁‍🗨 Telegram Premium: {'✅ Активен' if user['is_premium'] == True else '❌ Не активен'}
        """
        await message.answer(content)
    else:
        await message.answer("Информация о пользователе не найдена, попробуйте перезагрузить бота!")
