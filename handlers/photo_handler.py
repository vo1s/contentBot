from contextlib import suppress

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, CallbackQuery

from db import get_content_collection, get_users_collection, get_user_by_id, check_balance, manage_balance, \
    update_page_index, get_current_page_index
from handlers.earn_handler import earn
from keyboards.main_keyboard import Pagination, paginator, no_money_keyboard
from main import bot

router = Router()
photos_collection = get_content_collection()
users_collection = get_users_collection()


async def get_photo(page: int):
    photo = await photos_collection.find().skip(page - 1).limit(1).to_list(length=1)
    if photo:
        return photo[0]
    return None


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


@router.message(F.text == "📸 Смотреть фото")
async def profile(message: types.Message):
    user = await get_user_by_id(message.from_user.id)
    max_photo_index = user['max_photo_index']
    # если не первая фотка, то                        |
    # показываем всегда следующую, кроме последней    v
    photos_amounts = await photos_collection.count_documents({})
    photo_index = user["photo_index"] if user["photo_index"] == 1 or user["photo_index"] == photos_amounts else \
        user["photo_index"] + 1
    photo = await get_photo(photo_index)
    if await check_balance(user['_id']):
        content = f"""
💦Номер последней купленной фотографии: <b>{max_photo_index}</b>
💦Номер текущей фотографии: <b>{photo_index}</b>
        """
        await manage_balance(user['_id'], 2, 'subtract')
        await message.answer_photo(FSInputFile(
            photo['file_path']),
            reply_markup=paginator(photo_index, max_photo_index),
            caption=content,
            parse_mode=ParseMode.HTML
        )
    else:
        await notify_no_tokens(message)


@router.callback_query(Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_photo(callback_query: types.CallbackQuery, callback_data: Pagination):
    photos_amounts = await photos_collection.count_documents({})
    user = await get_user_by_id(callback_query.from_user.id)
    if callback_data.action == "prev":
        page = max(callback_data.page - 1, 1)
        await update_page_index(user['_id'], page, users_collection, user['max_photo_index'])
    else:
        if await check_balance(
                user['_id']):  # проверяем баланс пользователя на наличие хотя бы двух гемов или премиум подписку
            page = min(callback_data.page + 1, photos_amounts)
            if page > user['max_photo_index']:
                await manage_balance(user['_id'], 2, 'subtract')
            await update_page_index(user['_id'], page, users_collection, user['max_photo_index'])
        else:
            await notify_no_tokens(callback_query.message)

    await callback_query.answer()
    page_index = await get_current_page_index(callback_query.from_user.id)
    photo = await get_photo(page_index)
    with suppress(TelegramBadRequest):
        if photo:
            content = f"""
💦Номер последней купленной фотографии: <b>{user['max_photo_index']}</b>
💦Номер текущей фотографии: <b>{page_index}</b>
                    """

            await bot.edit_message_media(
                media=types.InputMediaPhoto(type="photo", media=FSInputFile(photo['file_path'])),
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,

            )
            await bot.edit_message_caption(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=paginator(page_index, user['max_photo_index']),
                caption=content,
                parse_mode=ParseMode.HTML
            )
        else:
            await callback_query.answer("No more photos.")


@router.callback_query(F.data.startswith('navigate_last_bought_image'))
async def navigate_to_last_image(call: CallbackQuery):
    max_photo_index = int(call.data.split(':')[1])

    photo = await get_photo(max_photo_index)
    with suppress(TelegramBadRequest):
        if photo:
            content = f"""
💦Номер последней купленной фотографии: <b>{max_photo_index}</b>
💦Номер текущей фотографии: <b>{max_photo_index}</b>
                        """

            await bot.edit_message_media(
                media=types.InputMediaPhoto(type="photo", media=FSInputFile(photo['file_path'])),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,

            )
            await bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=paginator(max_photo_index, max_photo_index),
                caption=content,
                parse_mode=ParseMode.HTML
            )
            await call.answer()
        else:
            await call.answer("No more photos.")


@router.callback_query(F.data == 'invite_friends')
async def choose(call: CallbackQuery):
    await earn(call.message)
    await call.answer()
