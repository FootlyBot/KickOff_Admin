from aiogram import Router, F
from aiogram.types import Message

from database.matches import (
    get_team_table,
    finish_game
)

from keyboards.admin_menu import admin_menu

router = Router()


@router.message(F.text == "📊 Таблица")
async def table(message: Message):

    table_text = get_team_table()

    await message.answer(table_text, parse_mode="HTML")


@router.message(F.text == "🏁 Завершить матчи")
async def finish(message: Message):

    finish_game()

    await message.answer(
        "🏁 Матчи завершены",
        reply_markup=admin_menu
    )