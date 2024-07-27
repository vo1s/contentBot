from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.utils.formatting import as_list, as_marked_section, Bold, as_line

from db import add_user, get_user_by_id
from keyboards.main_keyboard import main_keyboard
from keyboards.payment_keyboard import deposit_keyboard

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
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
💸 Баланс: {user['balance']} 💎 Tokens
👥 Приглашенные пользователи: {user['refs']}
💰 Заработано за рефералов: {user['refs_bonus']} 💎
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
⚜️ Premium подписка: {'✅ Активна' if user['subscription_status'] == 'paid' else '❌ Не активна'}
        """
        await message.answer(text=content, reply_markup=deposit_keyboard(), message_effect_id="5046509860389126442")
    else:
        await message.answer("Информация о пользователе не найдена, попробуйте перезагрузить бота!")
