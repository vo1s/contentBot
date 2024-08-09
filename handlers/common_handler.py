from aiocryptopay import AioCryptoPay, Networks
from aiogram import Router, types, F
from aiogram.enums import ParseMode

from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message, CallbackQuery

from db import get_user_by_id, get_users_collection, add_user_data
from handlers.earn_handler import earn

from keyboards.main_keyboard import *
import re

from keyboards.payment_keyboard import payment_keyboard, payment_keyboard_subscription

router = Router()

users_collection = get_users_collection()
admins = list(map(int, config.admins.get_secret_value().split(',')))


@router.message(CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'^\d+$'))))
async def cmd_start_user(message: Message, command: CommandObject, user_id: int = None, username: str = None):
    if user_id is None:
        user_id = message.from_user.id
    if username is None:
        username = message.from_user.username

    args_id = int(command.args)
    # Даем преференции пригласившему
    user = await get_user_by_id(args_id)
    referall = await get_user_by_id(user_id)
    if user and (referall is None):
        count_user_refs = user['reff_info']["refs"]
        balance = user["balance"]
        ref_bonus = user['reff_info']["refs_bonus"]
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "reff_info.refs": int(count_user_refs) + 1,
                "balance": int(balance) + 10,
                "reff_info.refs_bonus": int(ref_bonus) + 10
            }},
        )
        await add_user_data(user_id, username)
        # записываем id инвайтера к реффералу
        new_user = await get_user_by_id(user_id)
        await users_collection.update_one(
            {"_id": new_user["_id"]},
            {"$set": {
                "reff_info.reff_id": user["_id"]
            }}
        )
        is_admin = message.from_user.id in admins
        await message.answer("Добро пожаловать в бота!", reply_markup=main_keyboard(is_admin))
    else:
        is_admin = message.from_user.id in admins
        await message.answer("Добро пожаловать в бота!", reply_markup=main_keyboard(is_admin))


@router.message(CommandStart())
async def command_start_handler(message: types.Message, user_id: int = None, username: str = None) -> None:
    if user_id is None:
        user_id = message.from_user.id
    if username is None:
        username = message.from_user.username

    await add_user_data(user_id, username)
    is_admin = message.from_user.id in admins
    await message.answer("Добро пожаловать в бота!", reply_markup=main_keyboard(is_admin))


@router.message(Command("menu"))
async def cmd_test1(message: types.Message):
    is_admin = message.from_user.id in admins
    await message.answer("🔝 Главное меню", reply_markup=main_keyboard(is_admin))


@router.callback_query(F.data.startswith('check_subscription'))
async def check_subscription(callback_query: CallbackQuery):
    user_id = int(callback_query.data.split(':')[2])
    username = callback_query.data.split(':')[3]
    is_premium = callback_query.from_user.is_premium

    chat_member = await callback_query.bot.get_chat_member(config.channel_name.get_secret_value(), user_id)

    if chat_member.status != "left":
        await callback_query.answer("Спасибо за подписку! Теперь у вас есть доступ к боту.")
        await callback_query.message.delete()
        original_command = callback_query.data.split(':', 1)[1]
        print(original_command)
        bot_name = config.bot_name.get_secret_value()
        if original_command.startswith(f'/start?'):
            command_args = original_command.split('?', 1)[1].split(':')[0]
            fake_command = CommandObject(args=command_args, command='start')
            await cmd_start_user(callback_query.message, fake_command, user_id, username)
        else:
            await command_start_handler(callback_query.message, user_id, username)
    else:
        await callback_query.answer(
            "Вы еще не подписались на канал. Пожалуйста, подпишитесь и попробуйте снова.",
            show_alert=True
        )


@router.callback_query(F.data == 'invite_friends')
async def choose(call: CallbackQuery):
    await earn(call.message)
    await call.answer()


@router.message(F.text == "🔝 Главное меню")
async def main_menu(message: types.Message):
    is_admin = message.from_user.id in admins
    await message.answer("🔝 Главное меню", reply_markup=main_keyboard(is_admin))


async def notify_no_tokens(message):
    content = """
❌ У тебя закончились 💎 Tokens, жми
💎 Заработать Tokens или 💎 Пополни баланс (в профиле)

⚜️ Premium подписка дает неограниченный доступ
*(0 💎 Tokens за просмотр)*

👫 <b>Зарабатывай по 10 💎 Tokens (15 RUB) за каждого приглашенного друга!</b>
    """
    await message.delete()
    await message.answer(text=content, parse_mode=ParseMode.HTML, reply_markup=no_money_keyboard())


@router.message(F.text == "🔒 Подписка")
async def subscribe_menu(message: types.Message):
    content = f"""
❗️ ВНИМАНИЕ АКЦИЯ ❗️
💵 Стоимость подписки всего: 299 рублей(вместо 599 RUB)

⚜️ Premium подписка:
- неограниченный доступ (0 💎 Tokens за просмотр)
- самый запрещенный и жаркий контент 🔞
- повышенные проценты реферальной программы (12% и 3%)
⚜️ Premium подписка активируется навсегда
(если бот забанят, подписка будет работать в новом) 🔞


⚡️ Покупай сейчас и наслаждайся 💦
👇 Нажми кнопку ниже для оплаты 👇
    """
    user = await get_user_by_id(message.chat.id)
    subs_status = user['subscription_status']
    if subs_status == 'free':
        await message.answer(content, reply_markup=payment_keyboard_subscription(299))
    else:
        await message.answer('У вас активирована премиум подписка! Спасибо и наслаждайтесь!')
