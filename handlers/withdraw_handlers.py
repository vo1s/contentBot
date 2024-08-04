from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from api.crypto_bot_api import crypto_bot
from config import config
from db import get_user_by_id
from keyboards.admin_keyboard import confirm_withdraw_keyboard_admin, get_money
from keyboards.payment_keyboard import confirm_withdraw_keyboard, admin
from states import Withdraw

router = Router()


@router.callback_query(F.data.startswith('withdraw_main'))
async def withdraw_main(call: CallbackQuery, state: FSMContext, bot: Bot):
    content = """"""
    user = await get_user_by_id(call.message.chat.id)
    balance = user['balance']
    if balance >= 400:
        content = f"""
<i>Вывод осуществляется от <b>200 рублей</b> (2 💎 = 1 RUB) через CryptoBot в USDT</i>

Введите сумму в<b> RUB</b>, которую хотели бы вывести:
Доступно для вывода: <i><b>{balance / 2}</b></i>
        """
        await state.set_state(Withdraw.amount)
        await call.message.answer(content)
    else:
        content = f"""
<i>Вывод осуществляется от <b>200 рублей</b> (2 💎 = 1 RUB) через CryptoBot в USDT</i>

На вашем счете недостаточно средств для вывода!
Баланс - {balance / 2} RUB
                """
        await call.message.answer(content)
        await call.answer()


@router.message(Withdraw.amount, F.text)
async def withdraw_amount(message: types.Message, state: FSMContext, bot: Bot):
    amount = int(message.text)
    if amount < 200:
        await message.answer("<b>Сумма должно превышать 200 рублей!</b>")
    else:
        content = f"""
    Вы уверены, что хотите вывести {amount} RUB?
        """

        await message.answer(content, reply_markup=confirm_withdraw_keyboard(amount))
        await state.clear()


@router.message(Withdraw.amount, ~F.text)
async def withdraw_amount_wrong(message: types.Message):
    await message.answer("Пожалуйста, введите доступную для вывода сумму!")


@router.callback_query(F.data.startswith('confirm_withdraw'))
async def confirm_withdraw(call: CallbackQuery, bot: Bot):
    content = """
Спасибо! Ваш запрос отправлен на модерацию, ожидайте сообщения в боте!
    """
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=content,
    )
    #await call.message.answer("Спасибо! Ваш запрос отправлен на модерацию, ожидайте сообщения в боте!")
    amount = call.data.split(':')[1]
    moderation_chat_id = config.moderation_chat_id.get_secret_value()
    content = f"""
Заявка на вывод
id: {call.message.chat.id}
Количество: {amount} RUB

Подтвердить?

    """
    await bot.send_message(chat_id=moderation_chat_id, text=content, reply_markup=confirm_withdraw_keyboard_admin(
        int(amount),
        call.message.chat.id)
                           )
    await call.answer()


@router.callback_query(F.data.startswith('admin_confirm_withdraw'))
async def confirm_withdraw(call: CallbackQuery, bot: Bot):
    amount = call.data.split(':')[1]
    user_id = call.data.split(':')[2]
    exchange_rates = await crypto_bot.get_exchange_rates()
    amount_usdt = 0
    for rate in exchange_rates:
        if rate.source == 'USDT' and rate.target == 'RUB':
            amount_usdt = float(amount) / float(rate.rate)
            break
    check = await crypto_bot.create_check(asset='USDT', amount=round(amount_usdt, 2), pin_to_user_id=int(user_id))

    await bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )

    await bot.send_message(chat_id=user_id, text="Получите ваши средства!", reply_markup=get_money(check.bot_check_url))


@router.callback_query(F.data.startswith('admin_decline_withdraw'))
async def confirm_withdraw(call: CallbackQuery, bot: Bot):
    amount = call.data.split(':')[1]
    user_id = call.data.split(':')[2]
    content = """
Ваш запрос на вывод <b>отклонен</b> 😥

Попробуйте еще раз или напишите нам в поддержку!
    """

    await bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )

    await bot.send_message(chat_id=user_id, text=content, reply_markup=admin())
