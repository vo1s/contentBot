from aiogram import Router
from aiogram.filters import Filter
from aiogram.types import Message


class IsDigit(Filter):
    def __init__(self, number: int) -> None:
        self.number = number

    async def __call__(self, message: Message) -> bool:
        return isinstance(message.text, int)

