from aiogram import Router, F
from aiogram.types import Message

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin

from database.matches_service import get_active_match, add_goal
from database.results_service import finish_match

from keyboards.game_menu import game_menu

router = Router()


def get_game_id(admin_id):
    games = get_games_by_admin(admin_id)
    for g in games:
        if g.get("is_running"):
            return g["id"]
    return None


# =========================
# GOAL
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

    # получаем команды матча
    team_a_name = match.get("team_a_name")
    team_b_name = match.get("team_b_name")

    text = message.text

    if team_a_name in text:
        add_goal(match["id"], "A")
        await message.answer(f"⚽ Гол: {team_a_name}")

    elif team_b_name in text:
        add_goal(match["id"], "B")
        await message.answer(f"⚽ Гол: {team_b_name}")

    else:
        await message.answer("Команда не определена")


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