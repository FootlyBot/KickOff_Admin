from aiogram import Router
from aiogram.types import Message

from aiogram.fsm.context import FSMContext
from keyboards.admin_menu import admin_menu

router = Router()


@router.message(lambda m: m.text == "❌ Отменить создание")
async def cancel_create(message: Message, state: FSMContext):

    if not await state.get_state():
        await message.answer("Нет активного создания", reply_markup=admin_menu)
        return

    await state.clear()

    await message.answer("❌ Отменено", reply_markup=admin_menu)