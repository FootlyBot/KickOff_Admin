from aiogram import Router, F
from aiogram.types import Message

from database.matches import (
    get_active_match,
    add_goal,
    finish_match
)

from database.games import get_games_by_admin
from database.admins import get_admin_by_telegram_id

from keyboards.match_menu import game_menu

router = Router()


def get_game_id(admin_id):
    games = get_games_by_admin(admin_id)
    for g in games:
        if g.get("is_running"):
            return g["id"]
    return None


# =========================
# GOAL HANDLING
# =========================
@router.message(F.text.startswith("⚽ ГОЛ!"))
async def goal(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)
    if not admin:
        return

    game_id = get_game_id(admin[0]["id"])
    if not game_id:
        await message.answer("Нет активной игры")
        return

    match = get_active_match(game_id)
    if not match:
        await message.answer("Нет активного матча")
        return

    if "🟡" in message.text:
        add_goal(match["id"], "A")
        await message.answer("🟡 ГОЛ!")

    elif "🔴" in message.text:
        add_goal(match["id"], "B")
        await message.answer("🔴 ГОЛ!")


# =========================
# FINISH MATCH
# =========================
@router.message(F.text == "🏁 Завершить матч")
async def finish(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)
    if not admin:
        return

    game_id = get_game_id(admin[0]["id"])
    if not game_id:
        return

    match = get_active_match(game_id)
    if not match:
        return

    finish_match(match["id"])

    await message.answer(
        "🏁 Матч завершён",
        reply_markup=game_menu
    )