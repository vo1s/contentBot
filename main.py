import asyncio
import logging

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

#from handlers import check_handler, common_handlers, scammer_handlers, report_handler, empty_handler
from config import config
from aiogram import Bot
from aiogram import Dispatcher

from handlers import photo_handler, common_handler, profile_handler

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    )
)
dp = Dispatcher()


async def main():
    # dp.message.middleware(AntiFloodMiddleware())
    #dp.message.middleware(CheckSubscription())

    logging.basicConfig(level=logging.INFO)
    dp.include_router(photo_handler.router)
    dp.include_router(common_handler.router)
    dp.include_router(profile_handler.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
