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
    # если не первая фотка, то                        |
    # показываем всегда следующую, кроме последней    v
    photos_amounts = await photos_collection.count_documents({})
    photo_index = user["photo_index"] if user["photo_index"] == 1 or user["photo_index"] == photos_amounts else \
        user["photo_index"] + 1
    photo = await get_photo(photo_index)
    if await check_balance(user['_id']):
        await manage_balance(user['_id'], 2, 'subtract')
        await message.answer_photo(FSInputFile(photo['file_path']), reply_markup=paginator(photo_index))
    else:
        await notify_no_tokens(message)


# @router.callback_query(Pagination.filter(F.action.in_(["prev", "next"])))
# async def pagination_photo(callback_query: types.CallbackQuery, callback_data: Pagination):
#     photos_amounts = await photos_collection.count_documents({})
#     user = await get_user_by_id(callback_query.from_user.id)
#     if await check_balance(user['_id']):  # проверяем баланс пользователя на наличие хотя бы двух гемов
#         if callback_data.action == "prev":
#             page = max(callback_data.page - 1, 1)
#         else:
#             print(await manage_balance(user['_id'], 2, 'subtract'))
#             page = min(callback_data.page + 1, photos_amounts)
#
#         await users_collection.update_one(
#             {"_id": callback_query.from_user.id},
#             {"$set": {"photo_index": page}},
#         )
#         await callback_query.answer()
#         photo = await get_photo(page)
#         if photo:
#             await bot.edit_message_media(
#                 media=types.InputMediaPhoto(type="photo", media=FSInputFile(photo['file_path'])),
#                 chat_id=callback_query.message.chat.id,
#                 message_id=callback_query.message.message_id,
#                 reply_markup=paginator(page)
#             )
#         else:
#             await callback_query.answer("No more photos.")
#     else:
#         await notify_no_tokens(callback_query.message)

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
                print(await manage_balance(user['_id'], 2, 'subtract'))
            await update_page_index(user['_id'], page, users_collection, user['max_photo_index'])
        else:
            await notify_no_tokens(callback_query.message)

    await callback_query.answer()
    page_index = await get_current_page_index(callback_query.from_user.id)
    photo = await get_photo(page_index)
    with suppress(TelegramBadRequest):
        if photo:
            await bot.edit_message_media(
                media=types.InputMediaPhoto(type="photo", media=FSInputFile(photo['file_path'])),
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=paginator(page_index)
            )
        else:
            await callback_query.answer("No more photos.")


@router.callback_query(F.data == 'invite_friends')
async def choose(call: CallbackQuery):
    await earn(call.message)
    await call.answer()
