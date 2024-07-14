from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types import Message
from config import config
from keyboards.main_keyboard import subscribe


class CheckSubscription(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        chat_member = await event.bot.get_chat_member(config.channel_name.get_secret_value(), event.from_user.id)

        if chat_member.status == "left":
            content = """
🔔 Подпишись на наш канал, чтобы пользоваться ботом
🌐 В нашем канале ты всегда найдешь актуальную ссылку на бота!
            """
            original_command = event.text
            await event.answer(
                content,
                reply_markup=subscribe(original_command.replace(' ', '?'), event.from_user.id, event.from_user.username)
            )
            raise CancelHandler()
        else:
            return await handler(event, data)
