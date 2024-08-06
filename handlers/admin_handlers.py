from aiogram import Router, types, F

from filters.is_admin import AdminFilter

router = Router()

@router.message(F.text == "⚙️ Админ", AdminFilter())
async def subscribe_menu(message: types.Message):
    await message.answer("asd")
