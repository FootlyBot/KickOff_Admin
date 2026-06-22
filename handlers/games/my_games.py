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

    games = get_games_by_admin(admin[0]["id"])

    if not games:
        await message.answer("📭У вас пока нет игр")
        return

    for game in games:

        keyboard = None

        if game["status"] == "active":
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data=f"cancel_{game['id']}"
                    )]
                ]
            )

        await message.answer(
            f"{game['field_name']}\n📍 {game['address']}",
            reply_markup=keyboard
        )