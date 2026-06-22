from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.games import cancel_game

router = Router()


@router.callback_query(F.data.startswith("cancel_"))
async def cancel_game_handler(callback: CallbackQuery):

    game_id = callback.data.split("_")[1]

    cancel_game(game_id)

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ отменено"
    )

    await callback.answer()