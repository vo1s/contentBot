from aiogram import Router, types, F

from keyboards.casino_keyboards import *

router = Router()


@router.message(F.text == "🎰 Казино")
async def earn(message: types.Message):
    content = f"""
🎰 <b>Выберите нужную вам игру:</b>
<i>Играйте на свой страх и риск, ведь шанс проиграть больше чем выиграть
Этот способ для рисковых и подкрутить тут невозможно</i>
    """
    await message.answer(content, parse_mode="html", reply_markup=casino_keyboard())
