from aiogram import Router, F
from aiogram.types import Message

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin

from database.matches_service import get_active_match, add_goal, finish_match


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
@router.message(F.text.startswith("⚽"))
async def goal(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)
    if not admin:
        return

    admin = admin[0]

    game_id = get_game_id(admin["id"])
    if not game_id:
        await message.answer("Нет активной игры")
        return

    match = get_active_match(game_id)
    if not match:
        await message.answer("Нет активного матча")
        return

    text = message.text

    team_a_name = match.get("team_a_name")
    team_b_name = match.get("team_b_name")

    if team_a_name in text:
        add_goal(match["id"], "A")
        await message.answer(f"⚽ Гол за {team_a_name}")

    elif team_b_name in text:
        add_goal(match["id"], "B")
        await message.answer(f"⚽ Гол за {team_b_name}")

    else:
        await message.answer("Не удалось определить команду")


# =========================
# FINISH MATCH
# =========================
@router.message(F.text == "🏁 Завершить матч")
async def finish(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)
    if not admin:
        return

    admin = admin[0]

    game_id = get_game_id(admin["id"])
    if not game_id:
        await message.answer("Нет активной игры")
        return

    match = get_active_match(game_id)
    if not match:
        await message.answer("Нет активного матча")
        return

    finish_match(match["id"])

    await message.answer("🏁 Матч завершён")