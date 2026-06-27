from aiogram import Router, F
from aiogram.types import Message

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin

from database.matches_service import get_next_match, get_team_name
from keyboards.live_match_menu import build_live_keyboard

router = Router()


def get_game_id(admin_id):
    games = get_games_by_admin(admin_id)
    for g in games:
        if g.get("is_running"):
            return g["id"]
    return None


@router.message(F.text == "➡️ Следующий матч")
async def next_match(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)
    if not admin:
        return

    game_id = get_game_id(admin[0]["id"])

    match = get_next_match(game_id)

    if not match:
        await message.answer("Матчи закончились")
        return

    team_a = get_team_name(match["team_a_id"])
    team_b = get_team_name(match["team_b_id"])

    await message.answer(
        f"⚽ Матч начался!\n🆚 {team_a} vs {team_b}",
        reply_markup=build_live_keyboard(team_a, team_b)
    )