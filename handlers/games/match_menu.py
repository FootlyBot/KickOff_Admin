from aiogram import Router, F
from aiogram.types import Message

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin

from database.matches_service import get_next_match, get_team_name
from database.table_service import get_team_table, get_winner
from database.game_service import finish_game

from keyboards.admin_menu import admin_menu
from keyboards.live_match_menu import build_live_keyboard

router = Router()


# =========================
# GAME ID (ОДИН ИСТОЧНИК ИСТИНЫ)
# =========================
def get_active_game_id(admin_id: str):

    games = get_games_by_admin(admin_id)

    for g in games:
        if g.get("is_running"):
            return g["id"]

    return None


# =========================
# NEXT MATCH
# =========================
@router.message(F.text == "➡️ Следующий матч")
async def next_match(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)
    if not admin:
        return

    admin = admin[0]

    game_id = get_active_game_id(admin["id"])
    if not game_id:
        await message.answer("Нет активной игры")
        return

    match = get_next_match(game_id)

    if not match:
        await message.answer("Матчи закончились")
        return

    team_a_name = get_team_name(match["team_a_id"])
    team_b_name = get_team_name(match["team_b_id"])

    await message.answer(
        f"⚽ Матч начался!\n"
        f"🆚 {team_a_name} vs {team_b_name}",
        reply_markup=build_live_keyboard(team_a_name, team_b_name)
    )


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

    # Get the winner
    winner = get_winner(game_id)
    
    if winner:
        if winner["is_tie"]:
            winner_text = (
                f"🏆 <b>ПОБЕДИТЕЛИ</b> 🏆\n\n"
                f"🥇 {winner['name']}\n\n"
                f"Результаты:\n"
                f"✅ Победы: {winner['wins']}\n"
                f"🤝 Ничьи: {winner['draws']}\n"
                f"❌ Поражения: {winner['losses']}"
            )
        else:
            winner_text = (
                f"🏆 <b>ПОБЕДИТЕЛЬ</b> 🏆\n\n"
                f"🥇 {winner['name']}\n\n"
                f"Результаты:\n"
                f"✅ Победы: {winner['wins']}\n"
                f"🤝 Ничьи: {winner['draws']}\n"
                f"❌ Поражения: {winner['losses']}"
            )
        
        await message.answer(winner_text, parse_mode="HTML")

    await message.answer(
        "🏁 Матчи завершены",
        reply_markup=admin_menu
    )