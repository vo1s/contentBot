from aiogram import Router, types, F

from config import config
from db import get_user_by_id
from keyboards.main_keyboard import earn_keyboard

router = Router()


@router.message(F.text == "💰 Заработать")
async def earn(message: types.Message):
    content = f"""
👇 Выбери действие:
    """
    await message.answer(content, reply_markup=earn_keyboard)


@router.message(F.text == "👥 Пригласить друзей")
async def earn(message: types.Message):
    bot_name = config.bot_name.get_secret_value()
    user = await get_user_by_id(message.chat.id)
    content = f"""
🎁 Пригласи друзей и получи 10 💎 Tokens (за каждого) <i>[не выводимые]</i>:

📎 Нажми на ссылку для копирования 👇
👉 <code>https://t.me/{bot_name}?start={message.from_user.id}</code>

📊 Статистика приглашенных пользователей: {user['reff_info']['refs']}
💰 Заработано за приглашенных пользователей: {user["reff_info"]['refs_bonus']} 💎 Tokens
💶 Заработано с депозитов и подписок приглашенных пользователей <i></i>: {user["reff_info"]['earned_by_deposit']} 💎 Tokens
    """
    await message.answer(content, parse_mode="HTML")
