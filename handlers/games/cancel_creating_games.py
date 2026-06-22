from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message

from aiogram.fsm.context import FSMContext
from keyboards.admin_menu import admin_menu

router = Router()


@router.message(StateFilter("*"), F.text == "❌ Отменить создание")
async def cancel_create_game(message: Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Нет активного создания игры",
            reply_markup=admin_menu
        )
        return

    await state.clear()

    await message.answer(
        "❌ Создание игры отменено",
        reply_markup=admin_menu
    )