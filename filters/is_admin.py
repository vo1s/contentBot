from aiogram import BaseFilter
from aiogram.types import Message
import os

from config import config


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        admins = list(map(int, config.admins.get_secret_value().split(',')))
        return message.from_user.id in admins
