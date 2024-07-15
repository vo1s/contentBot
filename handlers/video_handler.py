from contextlib import suppress

from aiogram import Router, types, F, Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, CallbackQuery

from db import get_content_collection, get_users_collection, get_user_by_id, check_balance, manage_balance, \
    update_page_index, get_current_page_index, get_videos_collection
from handlers.common_handler import notify_no_tokens
from keyboards.main_keyboard import Pagination, paginator, paginator1

router = Router()
video_collection = get_videos_collection()
users_collection = get_users_collection()


async def get_video(page: int):
    video = await video_collection.find().skip(page - 1).limit(1).to_list(length=1)
    if video:
        return video[0]
    return None


@router.message(F.text == "📹 Смотреть видео")
async def profile(message: types.Message):
    user = await get_user_by_id(message.from_user.id)
    max_video_index = user['max_video_index']
    # если не первое видео, то                        |
    # показываем всегда следующее, кроме последнего    v
    video_amounts = await video_collection.count_documents({})
    video_index = user["video_index"] if user["video_index"] == 1 or user["video_index"] == video_amounts else \
        user["video_index"] + 1
    photo = await get_video(video_index)
    if await check_balance(user['_id']):
        content = f"""
💦Номер последнего купленного видео: <b>{max_video_index}</b>
💦Номер текущего видео: <b>{video_index}</b>
        """
        await manage_balance(user['_id'], 2, 'subtract')
        await message.answer_video(FSInputFile(
            photo['file_path']),
            reply_markup=paginator1(video_index, max_video_index, 'video_index'),
            caption=content,
            parse_mode=ParseMode.HTML
        )
    else:
        await notify_no_tokens(message)


@router.callback_query(Pagination.filter(F.action.in_(["prev1", "next1"])))
async def pagination_video(callback_query: types.CallbackQuery, callback_data: Pagination, bot: Bot):
    video_amounts = await video_collection.count_documents({})
    user = await get_user_by_id(callback_query.from_user.id)
    if callback_data.action == "prev1":
        page = max(callback_data.page - 1, 1)
        await update_page_index(user['_id'], page, users_collection, user['max_video_index'], 'video_index')
    else:
        if await check_balance(
                user['_id']):  # проверяем баланс пользователя на наличие хотя бы двух гемов или премиум подписку
            page = min(callback_data.page + 1, video_amounts)
            if page > user['max_video_index']:
                await manage_balance(user['_id'], 2, 'subtract')
            await update_page_index(user['_id'], page, users_collection, user['max_video_index'], 'video_index')
        else:
            await notify_no_tokens(callback_query.message)

    await callback_query.answer()
    page_index = await get_current_page_index(callback_query.from_user.id, 'video_index')
    video = await get_video(page_index)
    with suppress(TelegramBadRequest):
        if video:
            content = f"""
💦Номер последнего купленного видео: <b>{user['max_video_index']}</b>
💦Номер текущего видео: <b>{page_index}</b>
                    """

            await bot.edit_message_media(
                media=types.InputMediaVideo(type="video", media=FSInputFile(video['file_path'])),
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,

            )
            await bot.edit_message_caption(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=paginator1(page_index, user['max_video_index'], 'video_index'),
                caption=content,
                parse_mode=ParseMode.HTML
            )
        else:
            await callback_query.answer("No more photos.")


@router.callback_query(F.data.startswith('navigate_last_bought_video'))
async def navigate_to_last_video(call: CallbackQuery, bot: Bot):
    max_video_index = int(call.data.split(':')[1])

    video = await get_video(max_video_index)
    with suppress(TelegramBadRequest):
        if video:
            content = f"""
💦Номер последнего купленного видео: <b>{max_video_index}</b>
💦Номер текущего видео: <b>{max_video_index}</b>
                        """

            await bot.edit_message_media(
                media=types.InputMediaVideo(type="video", media=FSInputFile(video['file_path'])),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,

            )
            await bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=paginator1(max_video_index, max_video_index, 'video_index'),
                caption=content,
                parse_mode=ParseMode.HTML
            )
            await call.answer()
        else:
            await call.answer("No more photos.")



