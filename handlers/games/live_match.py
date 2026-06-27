from aiogram import Router, F
from aiogram.types import Message

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin

from database.matches_service import (
    get_active_match,
    add_goal,
    finish_match,
    get_team_name
)

from keyboards.admin_menu import admin_menu
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
@router.message(F.text.startswith("⚽"))
async def goal(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)
    if not admin:
        return

    game_id = get_game_id(admin[0]["id"])
    match = get_active_match(game_id)

    if not match:
        await message.answer("Нет активного матча")
        await message.answer("📋 Игровое меню восстановлено", reply_markup=game_menu)
        return

    # ✅ БЕРЁМ ИМЕНА ИЗ БД
    team_a = get_team_name(match["team_a_id"])
    team_b = get_team_name(match["team_b_id"])

    # очищаем текст кнопки
    clicked = message.text.replace("⚽ ", "").strip()

    # нормализуем
    team_a_name = team_a.strip()
    team_b_name = team_b.strip()

    if clicked == team_a_name:
        add_goal(match["id"], "A")
        await message.answer(f"⚽ Гол за {team_a_name}")

    elif clicked == team_b_name:
        add_goal(match["id"], "B")
        await message.answer(f"⚽ Гол за {team_b_name}")

    else:
        await message.answer(
            f"Не удалось определить команду\n"
            f"Кнопка: {clicked}\n"
            f"A: {team_a_name}\n"
            f"B: {team_b_name}"
        )

# =========================
# FINISH MATCH
# =========================
@router.message(F.text == "🏁 Завершить матч")
async def finish(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)
    if not admin:
        return

    game_id = get_game_id(admin[0]["id"])
    match = get_active_match(game_id)

    if not match:
        return

    finish_match(match["id"])

    await message.answer("🏁 Матч завершён")
    await message.answer("📋 Игровое меню восстановлено", reply_markup=game_menu)