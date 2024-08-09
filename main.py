import asyncio
import logging

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from aiogram import Bot
from aiogram import Dispatcher

from handlers import photo_handler, common_handler, profile_handler, earn_handler, casino_handlers, video_handler, \
    payment_handlers, withdraw_handlers, admin_handlers
from middlewares.check_sub_middlware import CheckSubscription

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
    dp.include_router(earn_handler.router)
    dp.include_router(casino_handlers.router)
    dp.include_router(video_handler.router)
    dp.include_router(payment_handlers.router)
    dp.include_router(withdraw_handlers.router)
    dp.include_router(admin_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == '__main__':
    asyncio.run(main())
