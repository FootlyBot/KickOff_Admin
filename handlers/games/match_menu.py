from aiogram import Router, F
from aiogram.types import Message

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin

from database.table_service import get_team_table
from database.teams_service import get_game_players, assign_player, create_teams_for_game
from database.matches_service import get_active_match, add_goal
from database.game_service import finish_game




from keyboards.admin_menu import admin_menu

router = Router()


def get_active_game_id(admin_id: str):

    games = get_games_by_admin(admin_id)

    for g in games:
        if g.get("is_running"):
            return g["id"]

    return None


# =========================
# TABLE
# =========================
@router.message(F.text == "📊 Таблица")
async def table(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)

    if not admin:
        await message.answer("🚫 Нет доступа")
        return

    admin = admin[0]

    game_id = get_active_game_id(admin["id"])

    if not game_id:
        await message.answer("⚠️ Нет активной игры")
        return

    table_text = get_team_table(game_id)

    await message.answer(table_text, parse_mode="HTML")


# =========================
# FINISH GAME
# =========================
@router.message(F.text == "🏁 Завершить матчи")
async def finish(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)

    if not admin:
        await message.answer("🚫 Нет доступа")
        return

    admin = admin[0]

    game_id = get_active_game_id(admin["id"])

    if not game_id:
        await message.answer("⚠️ Нет активной игры")
        return

    finish_game(game_id)

    await message.answer(
        "🏁 Матчи завершены",
        reply_markup=admin_menu
    )