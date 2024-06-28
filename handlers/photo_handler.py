from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import InputFile, FSInputFile

from db import add_user, get_content_collection, get_users_collection, get_user_by_id
from keyboards.main_keyboard import main_keyboard, Pagination, paginator
from main import bot

router = Router()
photos_collection = get_content_collection()
users_collection = get_users_collection()


async def get_photo(page: int):
    photo = await photos_collection.find().skip(page - 1).limit(1).to_list(length=1)
    if photo:
        return photo[0]
    return None


@router.message(F.text == "📸 Смотреть фото")
async def profile(message: types.Message):
    user = await get_user_by_id(message.from_user.id)
    photo_index = user["photo_index"]
    photo = await get_photo(photo_index)
    if photo:
        await message.answer_photo(FSInputFile(photo['file_path']), reply_markup=paginator(photo_index))
    else:
        await message.reply("No photos found.")


@router.callback_query(Pagination.filter(F.action.in_(["prev", "next"])))
async def process_callback(callback_query: types.CallbackQuery, callback_data: Pagination):
    photos_amounts = await photos_collection.count_documents({})

    if callback_data.action == "prev":
        page = max(callback_data.page - 1, 1)
    elif callback_data.action == "next":
        page = min(callback_data.page + 1, photos_amounts)

    await users_collection.update_one(
        {"_id": callback_query.from_user.id},
        {"$set": {"photo_index": page}},
    )

    photo = await get_photo(page)
    if photo:
        await bot.edit_message_media(
            media=types.InputMediaPhoto(type="photo", media=FSInputFile(photo['file_path'])),
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=paginator(page)
        )
    else:
        await callback_query.answer("No more photos.")
