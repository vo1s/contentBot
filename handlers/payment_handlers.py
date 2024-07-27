from aiogram import Router, F, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery

from api.crypto_bot_api import crypto_bot
from db import get_user_by_id, update_subscription_status, manage_balance
from handlers.common_handler import subscribe_menu
from keyboards.payment_keyboard import currencies, check_crypto_bot_payment_keyboard, payment_keyboard, stars_keyboard, \
    payment_keyboard_stars, stars_keyboard_subscription, contact_admin_keyboard
from states import Deposit

router = Router()


@router.callback_query(F.data.startswith('pay_crypto_keyboard'))
async def pay_crypto(call: CallbackQuery, bot: Bot):
    rub_amount = call.data.split(':')[1]
    await bot.edit_message_text(
        text='👇 Выберите криптовалюту для оплаты:',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=currencies(int(rub_amount))
    )
    await call.answer()


# ---------------------- Оплата CryptoBot

@router.callback_query(F.data.startswith('back_to_pay_menu'))
async def back_to_pay_menu(call: CallbackQuery, bot: Bot):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await subscribe_menu(call.message)
    await call.answer()


@router.callback_query(F.data.startswith('create_invoice_crypto'))
async def pay_crypto_check(call: CallbackQuery, bot: Bot):
    content = f"""
⌛️ После оплаты нажмите "🔍 Проверить оплату"
(Активация автоматическая сразу после проверки оплаты)
    """
    currency = call.data.split(':')[1]
    rub_amount = call.data.split(':')[2]
    exchange_rates = await crypto_bot.get_exchange_rates()
    for rate in exchange_rates:
        if rate.source == currency and rate.target == 'RUB':
            crypto_sum = rate.rate
            invoice = await crypto_bot.create_invoice(asset=currency, amount=float(rub_amount) / crypto_sum)
            await bot.edit_message_text(
                text=content,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=check_crypto_bot_payment_keyboard(invoice.invoice_id, invoice.bot_invoice_url, rub_amount)
            )
    await call.answer()


@router.callback_query(F.data.startswith('check_crypto_bot_payment'))
async def check_crypto_bot_payment(call: CallbackQuery, bot: Bot):
    invoice_id = call.data.split(':')[1]
    rub_amount = call.data.split(':')[2]
    invoice = await crypto_bot.get_invoices(invoice_ids=[invoice_id])
    #print(rub_amount)
    if invoice[0].status == 'paid':
        if rub_amount == '299':
            await update_subscription_status(call.message.chat.id, 'paid')
            await bot.edit_message_text(
                text="Ваша подписка успешно оплачена! Поздравляю",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,

            )
        else:
            new_balance = await manage_balance(call.message.chat.id, int(rub_amount)*2, 'add')
            await bot.edit_message_text(
                text=f"Ваш баланс успешно пополнен! Баланс - <b>{new_balance} 💎</b>",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
    elif invoice[0].status == 'expired':
        await call.answer("Срок действия вашего счета истек. Попробуйте создать новый!", show_alert=True)
    else:
        await call.answer("Ваш счет еще не оплачен! Оплатите и возвращайтесь", show_alert=True)
    await call.answer()


# ---------------------- Оплата Stars
@router.callback_query(F.data.startswith('enter_money'))
async def enter_money(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    content = """
💸 Введите сумму пополнения   2 💎 Tokens = 1 RUB
💰 Минимальная сумма пополнения 50 RUB
    """
    await state.set_state(Deposit.money_amount)

    await bot.edit_message_text(
        text=content,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    await call.answer()


# Клавиатура для оплаты поплнения счета
@router.message(Deposit.money_amount, F.text.regexp(r'^[1-9]\d*$'))
async def pay_stars(message: types.Message, bot: Bot, state: FSMContext):
    money_amount = int(message.text)
    if money_amount < 50:
        await message.answer("Минимальная сумма пополнения <b>50 RUB</b>!")
    else:
        content = "👇 Выберите способ оплаты:"
        await message.answer(content, reply_markup=payment_keyboard(money_amount))

        await state.clear()


@router.message(Deposit.money_amount)
async def pay_stars_wrong(message: types.Message, bot: Bot):
    await message.answer("Пожалуйста, введите верное числовое значение суммы пополнения!")


# оплата подписки звездами
@router.callback_query(F.data.startswith('pay_stars_subscription'))
async def pay_stars(call: CallbackQuery, bot: Bot):
    content = f"""
Для оплаты подписки с использованием <b>Stars</b> ⭐пополните счет на опредленную сумму
Заданную телеграммом, далее пополните внутренний счет бота, выбрав один из представленных вариантов!
    """
    await bot.edit_message_text(
        text=content,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=stars_keyboard_subscription()
    )


# оплата депозита звездами
@router.callback_query(F.data.startswith('pay_stars'))
async def pay_stars(call: CallbackQuery, bot: Bot):
    content = f"""
Для пополнения счета с использованием <b>Stars</b> ⭐пополните счет на опредленную сумму
Заданную телеграммом, далее пополните внутренний счет бота, выбрав один из представленных вариантов!
    """
    await bot.edit_message_text(
        text=content,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=stars_keyboard()
    )


@router.callback_query(F.data.startswith('create_stars_invoice'))
async def pay_stars(call: CallbackQuery, bot: Bot):
    amount_stars = int(call.data.split(':')[1])
    amount_rubles = int(call.data.split(':')[2])
    prices = [LabeledPrice(label="XTR", amount=amount_stars)]
    await call.message.answer_invoice(
        title="Пополнение счета",
        description=f"Пополнить счет на {amount_stars} ⭐ - {amount_rubles} RUB",
        prices=prices,
        provider_token="",
        payload=f"{call.message.chat.id}:{amount_rubles}",
        currency="XTR",
        reply_markup=payment_keyboard_stars(amount_stars),
    )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: types.Message):
    user_id = message.successful_payment.invoice_payload.split(":")[0]
    amount_rubles = message.successful_payment.invoice_payload.split(":")[1]

    if amount_rubles == '299':
        await update_subscription_status(message.chat.id, 'paid')
        await message.answer("Ваша подписка оплачена! Поздравляю!")
    else:
        new_balance = await manage_balance(int(user_id), round(int(amount_rubles) * 2), 'add')
        content = f"""
<b>Огромное спасибо!</b>

Вы пополнили счет на {amount_rubles} RUB
Ваш баланс составляет {new_balance} 💎
        """
        await message.answer(
            text=content,
            message_effect_id="5104841245755180586",
        )


# Хендлеры оплаты вручную через администратора
@router.callback_query(F.data.startswith('pay_by_hand'))
async def pay_stars(call: CallbackQuery, bot: Bot):
    rub_amount = int(call.data.split(':')[1])
    content = f"""
💸 Для пополнения баланса вы можете напрямую связаться с администратором и получить реквизиты для оплаты

Нажмите кнопку <b>"💬 Написать"</b> для связи👇
    """
    await bot.edit_message_text(
        text=content,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=contact_admin_keyboard(rub_amount)
    )

