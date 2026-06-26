from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin
from database.matches import create_teams_for_game
from database.supabase_client import supabase

from keyboards.admin_menu import admin_menu
from keyboards.match_menu import match_menu

router = Router()


def get_current_players_count(game_id: str) -> int:
    res = (
        supabase.table("game_players")
        .select("id", count="exact")
        .eq("game_id", game_id)
        .execute()
    )
    return res.count or 0


# =========================
# MY GAMES
# =========================
@router.message(lambda m: m.text == "📋 Мои игры")
async def my_games(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)

    if not admin:
        await message.answer("🚫 Нет доступа")
        return

    admin = admin[0]

    games = get_games_by_admin(admin["id"])

    if not games:
        await message.answer("📭 У вас пока нет игр")
        return

    for game in games:

        status_icon = "🟢" if game["status"] == "active" else "🔴"

        current_players = get_current_players_count(game["id"])

        keyboard = None

        # ❗ если игра идёт — не даём запускать снова
        if game.get("is_running"):
            await message.answer(
                f"⚠️ <b>{game['field_name']}</b>\n"
                f"Игра уже идёт",
                parse_mode="HTML"
            )
            continue

        if game["status"] == "active":
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⚽️ Начать матчи",
                            callback_data=f"start_match_{game['id']}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Отменить",
                            callback_data=f"cancel_{game['id']}"
                        )
                    ]
                ]
            )

        await message.answer(
            f"{status_icon} <b>{game['field_name']}</b>\n"
            f"📍 {game['address']}\n"
            f"📅 {game['game_date']}\n"
            f"👥 {current_players}/{game['max_players']}\n"
            f"⚡ {game['status']}",
            parse_mode="HTML",
            reply_markup=keyboard
        )


# =========================
# START MATCHES
# =========================
@router.callback_query(F.data.startswith("start_match_"))
async def start_match(callback: CallbackQuery):

    game_id = callback.data.split("_")[2]

    supabase.table("games").update({
        "is_running": True
    }).eq("id", game_id).execute()

    teams, error = create_teams_for_game(game_id)

    if error:
        await callback.message.answer(f"🚫 {error}")
        return

    text = "👥 <b>Команды сформированы</b>\n\n"

    for t in teams:
        text += f"{t['name']}\n"

        for i, p in enumerate(t["players"], 1):
            text += f"{i}. {p['user_id']}\n"

        text += "\n"

    await callback.message.answer(text, parse_mode="HTML")

    await callback.message.answer(
        "🎮 <b>Матчи начались</b>",
        reply_markup=match_menu,
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# FINISH MATCHES (FIXED)
# =========================
@router.message(F.text == "🏁 Завершить матчи")
async def finish_matches(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)

    if not admin:
        await message.answer("🚫 Нет доступа")
        return

    admin = admin[0]

    games = get_games_by_admin(admin["id"])

    active_game = None

    for g in games:
        if g.get("is_running"):
            active_game = g
            break

    if not active_game:
        await message.answer("⚠️ Нет активной игры")
        return

    game_id = active_game["id"]

    # ❗ выключаем режим игры
    supabase.table("games").update({
        "is_running": False,
        "status": "finished"
    }).eq("id", game_id).execute()

    # ❗ возвращаем admin меню
    await message.answer(
        "🏁 Матчи завершены",
        reply_markup=admin_menu
    )