import asyncio

from aiogram import Router, types, F, Bot
from aiogram.enums import DiceEmoji
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from db import manage_balance, get_user_by_id
from keyboards.casino_keyboards import *
from states import Casino

router = Router()


@router.message(F.text == "🎰 Казино")
async def earn(message: types.Message):
    content = f"""
🎰 <b>Выберите нужную вам игру:</b>
<i>Играйте на свой страх и риск, ведь шанс проиграть больше чем выиграть
Этот способ для рисковых и подкрутить тут невозможно</i>
    """
    await message.answer(content, parse_mode="html", reply_markup=casino_keyboard())


@router.callback_query(F.data == 'back_casino')
async def choose(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await earn(call.message)
    await call.answer()


@router.callback_query(F.data.startswith("casino_choose"))
async def choose(call: CallbackQuery, state: FSMContext):
    game = call.data.split(":")[1]
    user = await get_user_by_id(call.from_user.id)
    await state.clear()
    if game == "dice":

        content = f"""
🎲 Кубик
Ваша задача угадать, какое из 6 чисел выпадет на кубике.

Ваш баланс: {user['balance']} 💎 Gems
Введите число от 1 до 6:
            """
        await call.message.answer(content)
        await state.set_state(Casino.bet)
    elif game == "darts":

        content = f"""
🎯 Дартс
Ваша задача попасть в яблочко на мишени. Если у вас получится, вы умножите свою ставку в 3 раза.

Ваш баланс: {user['balance']} 💎 Gems
Введите вашу ставку:
                    """
        await call.message.answer(content)
        await state.set_state(Casino.darts)
    elif game == "slots":

        content = f"""
🎰 Слоты

Текущие призы:
7️⃣7️⃣7️⃣ = x7 от ставки
🍇🍇🍇 = x4 от ставки
🍋🍋🍋 = x3 от ставки
💀💀💀 = x2 от ставки

Любой другой результат лишит вас ставки

Ваш баланс: {user['balance']} 💎 Gems
Введите вашу ставку:
                            """
        await call.message.answer(content)
        await state.set_state(Casino.slots)
    else:
        content = f"""
        🎳 Боулинг
Ваша задача - сбить все кегли. Если у вас получится, вы умножите свою ставку в 3 раза.

Ваш баланс: {user['balance']} 💎 Gems
Введите вашу ставку:
                                    """
        await call.message.answer(content)
        await state.set_state(Casino.ball)


@router.message(Casino.bet, F.text)
async def dice(message: types.Message, state: FSMContext, bot: Bot):
    try:
        number = int(message.text)
        if 1 <= number <= 6:
            await state.update_data(guess=number)
            user = await get_user_by_id(message.from_user.id)
            content = f"""
Минимальная ставка: <b>3 💎 Гема</b>
Ваш Баланс: <b>{user['balance']}</b>

<i>Введите вашу ставку</i>
            """
            await message.answer(content, parse_mode="html", reply_markup=back_casino_keyboard())
            await state.set_state(Casino.dice)
        else:
            await message.answer("Введите число от 1 до 6.", reply_markup=back_casino_keyboard())
    except ValueError:
        await message.answer("<b>❌ Вы должны загадать число от 1 до 6, введите его еще раз.</b>", parse_mode="html",
                             reply_markup=back_casino_keyboard())


@router.message(Casino.bet, ~F.text)
async def not_text(message: types.Message, state: FSMContext, bot: Bot):
    await message.answer("<b>❌ Вы должны загадать число от 1 до 6, введите его еще раз.</b>", parse_mode="html",
                         reply_markup=back_casino_keyboard())


@router.message(Casino.dice, F.text)
async def dice(message: types.Message, state: FSMContext, bot: Bot):
    try:
        bet = int(message.text)
        user = await get_user_by_id(message.from_user.id)
        if bet < 3:
            await message.answer("Минимальная ставка в данной игре - <b>3 💎 Гема!</b>", parse_mode="html",
                                 reply_markup=back_casino_keyboard())
        elif bet > user['balance']:
            await message.answer(f"Недостаточно средств! Ваша максимальная ставка - <b>{user['balance']} 💎 Гема!</b>",
                                 parse_mode="html", reply_markup=back_casino_keyboard())
        else:
            data = await state.get_data()
            new_balance = await manage_balance(message.from_user.id, bet, 'subtract')

            msg = await message.answer_dice(emoji=DiceEmoji.DICE)
            await asyncio.sleep(3)

            if int(data['guess']) == msg.dice.value:  # Если кубик совпал с загаданным значением
                new_balance = await manage_balance(message.from_user.id, bet * 2, 'add')
                await message.answer(f"Поздравлям, ваше число совпало с кубиком, баланс <b>{new_balance}</b>",
                                     parse_mode="html", reply_markup=back_casino_keyboard())
            else:  # если кубик не совпал с указанным значением
                await message.answer(f"К сожалению, вы не угадали :( В следующий раз обязательно повезет!",
                                     reply_markup=back_casino_keyboard())
            await state.clear()
    except ValueError:
        await message.answer("<b>❌ Вы должны ввести ставку в виде числа! Попробуйте еще раз.</b>", parse_mode="html",
                             reply_markup=back_casino_keyboard())


@router.message(Casino.darts, F.text)
async def dice(message: types.Message, state: FSMContext):
    try:
        bet = int(message.text)
        user = await get_user_by_id(message.from_user.id)
        if bet < 3:
            await message.answer("Минимальная ставка в данной игре - <b>3 💎 Гема!</b>", parse_mode="html",
                                 reply_markup=back_casino_keyboard())
        elif bet > user['balance']:
            await message.answer(f"Недостаточно средств! Ваша максимальная ставка - <b>{user['balance']} 💎 Гема!</b>",
                                 parse_mode="html", reply_markup=back_casino_keyboard())
        else:
            data = await state.get_data()
            new_balance = await manage_balance(message.from_user.id, bet, 'subtract')

            msg = await message.answer_dice(emoji=DiceEmoji.DART)
            await asyncio.sleep(2)
            if msg.dice.value == 6:  # Если бросок произошел ровно в центр
                new_balance = await manage_balance(message.from_user.id, bet * 4, 'add')
                await message.answer(f"Поздравлям, вы попали ровно в центр! Баланс <b>{new_balance}</b>",
                                     parse_mode="html", reply_markup=back_casino_keyboard())
            else:  # если не в центр
                await message.answer(f"К сожалению, вы не попали :( В следующий раз обязательно повезет!",
                                     reply_markup=back_casino_keyboard())
            await state.clear()
    except ValueError:
        await message.answer("<b>❌ Вы должны ввести ставку в виде числа! Попробуйте еще раз.</b>", parse_mode="html",
                             reply_markup=back_casino_keyboard())


@router.message(Casino.slots)
async def dice(message: types.Message, state: FSMContext):
    try:
        bet = int(message.text)
        user = await get_user_by_id(message.from_user.id)
        if bet < 3:
            await message.answer("Минимальная ставка в данной игре - <b>3 💎 Гема!</b>", parse_mode="html",
                                 reply_markup=back_casino_keyboard())
        elif bet > user['balance']:
            await message.answer(f"Недостаточно средств! Ваша максимальная ставка - <b>{user['balance']} 💎 Гема!</b>",
                                 parse_mode="html", reply_markup=back_casino_keyboard())
        else:
            data = await state.get_data()
            new_balance = await manage_balance(message.from_user.id, bet, 'subtract')

            msg = await message.answer_dice(emoji=DiceEmoji.SLOT_MACHINE)
            await asyncio.sleep(2)
            rewards = {64: 8, 43: 4, 22: 5, 1: 3}
            if int(msg.dice.value) in rewards.keys():
                new_balance = await manage_balance(message.from_user.id, bet * rewards[int(msg.dice.value)], 'add')
                await message.answer(f"Поздравлям, вы забрали джекпот! Баланс <b>{new_balance}</b>",
                                     parse_mode="html", reply_markup=back_casino_keyboard())
            else:
                await message.answer(f"К сожалению, не повезло :( В следующий раз обязательно повезет!",
                                     reply_markup=back_casino_keyboard())
            await state.clear()
    except ValueError:
        await message.answer("<b>❌ Вы должны ввести ставку в виде числа! Попробуйте еще раз.</b>", parse_mode="html",
                             reply_markup=back_casino_keyboard())


@router.message(Casino.ball)
async def dice(message: types.Message, state: FSMContext):
    try:
        bet = int(message.text)
        user = await get_user_by_id(message.from_user.id)
        if bet < 3:
            await message.answer("Минимальная ставка в данной игре - <b>3 💎 Гема!</b>", parse_mode="html",
                                 reply_markup=back_casino_keyboard())
        elif bet > user['balance']:
            await message.answer(f"Недостаточно средств! Ваша максимальная ставка - <b>{user['balance']} 💎 Гема!</b>",
                                 parse_mode="html", reply_markup=back_casino_keyboard())
        else:
            data = await state.get_data()
            new_balance = await manage_balance(message.from_user.id, bet, 'subtract')

            msg = await message.answer_dice(emoji=DiceEmoji.BOWLING)
            await asyncio.sleep(2.5)

            if msg.dice.value == 6:  # Если бросок произошел ровно в центр
                new_balance = await manage_balance(message.from_user.id, bet * 4, 'add')
                await message.answer(f"Поздравлям, вы выбили страйк! Баланс <b>{new_balance}</b>",
                                     parse_mode="html", reply_markup=back_casino_keyboard())
            else:  # если не в центр
                await message.answer(f"К сожалению, вы не сумели :( В следующий раз обязательно повезет!",
                                     reply_markup=back_casino_keyboard())
            await state.clear()
    except ValueError:
        await message.answer("<b>❌ Вы должны ввести ставку в виде числа! Попробуйте еще раз.</b>", parse_mode="html",
                             reply_markup=back_casino_keyboard())
