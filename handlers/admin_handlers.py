from aiogram import Router, types, F

from api.api_cactuspay import create_payment
from filters.is_admin import AdminFilter

router = Router()

@router.message(F.text == "⚙️ Админ", AdminFilter())
async def subscribe_menu(message: types.Message):

    url = await create_payment('iOczjq8NBsdSfFyVPDmZ', 1000)
    print(url)
