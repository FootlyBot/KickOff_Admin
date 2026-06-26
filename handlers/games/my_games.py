from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.admins import get_admin_by_telegram_id
from database.games import get_games_by_admin

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