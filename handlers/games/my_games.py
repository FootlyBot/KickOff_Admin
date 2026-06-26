from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin
from database.matches import create_teams_for_game

from keyboards.admin_menu import admin_menu

router = Router()


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

        keyboard = None

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
            f"👥 {game['current_players']}/{game['max_players']}\n"
            f"⚡ {game['status']}",
            parse_mode="HTML",
            reply_markup=keyboard
        )


# ✅ НОВЫЙ CALLBACK: формирование команд
@router.callback_query(F.data.startswith("start_match_"))
async def start_match(callback: CallbackQuery):

    game_id = callback.data.split("_")[2]

    teams, error = create_teams_for_game(game_id)

    if error:
        await callback.message.answer(f"🚫 {error}")
        return

    text = "Команды сформированы 👥\n\n"

    for t in teams:
        text += f"{t['name']}\n"

        for i, p in enumerate(t["players"], 1):
            text += f"{i}. {p['user_id']}\n"

        text += "\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Следующий матч", callback_data="next_match")],
            [InlineKeyboardButton(text="📊 Таблица", callback_data=f"table_{game_id}")],
            [InlineKeyboardButton(text="🏁 Закончить матчи", callback_data=f"finish_{game_id}")]
        ]
    )

    await callback.message.answer(text)
    await callback.message.answer("Меню матчей:", reply_markup=keyboard)

    await callback.answer()