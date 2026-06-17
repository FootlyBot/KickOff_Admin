from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from states.create_game import CreateGameState

from database.admins import get_admin_by_telegram_id
from database.games import create_game, get_games_by_admin, cancel_game

router = Router()


# -------------------------
# СОЗДАНИЕ ИГРЫ ⚽
# -------------------------

@router.message(lambda m: m.text == "⚽ Создать игру")
async def start_game(message: Message, state: FSMContext):

    admin = get_admin_by_telegram_id(message.from_user.id)

    if not admin:
        await message.answer("🚫 Нет доступа")
        return

    await message.answer("🏟 Введите название поля:")
    await state.set_state(CreateGameState.waiting_field)


@router.message(CreateGameState.waiting_field)
async def field(message: Message, state: FSMContext):

    await state.update_data(field_name=message.text)

    await message.answer("📍 Введите адрес поля:")
    await state.set_state(CreateGameState.waiting_address)


@router.message(CreateGameState.waiting_address)
async def address(message: Message, state: FSMContext):

    await state.update_data(address=message.text)

    await message.answer("📅 Введите дату и время:\n\nПример: 21.06.2026 19:00")
    await state.set_state(CreateGameState.waiting_date)


@router.message(CreateGameState.waiting_date)
async def date(message: Message, state: FSMContext):

    await state.update_data(game_date=message.text)

    await message.answer("👥 Введите максимальное количество игроков:")
    await state.set_state(CreateGameState.waiting_max_players)


@router.message(CreateGameState.waiting_max_players)
async def save_game(message: Message, state: FSMContext):

    data = await state.get_data()

    admin = get_admin_by_telegram_id(message.from_user.id)[0]

    try:
        game_date = datetime.strptime(
            data["game_date"],
            "%d.%m.%Y %H:%M"
        ).isoformat()
    except ValueError:
        await message.answer("⚠️ Неверный формат даты")
        return

    create_game(
        admin_id=admin["id"],
        field_name=data["field_name"],
        address=data["address"],
        game_date=game_date,
        max_players=int(message.text)
    )

    await message.answer(
        f"""
🎉 ИГРА СОЗДАНА!

🏟 Поле: {data['field_name']}
📍 Адрес: {data['address']}
📅 Дата: {data['game_date']}
👥 Игроки: 0/{message.text}
"""
    )

    await state.clear()


# -------------------------
# МОИ ИГРЫ 📋
# -------------------------

@router.message(lambda m: m.text == "📋 Мои игры")
async def my_games(message: Message):

    admin = get_admin_by_telegram_id(message.from_user.id)

    if not admin:
        await message.answer("🚫 Нет доступа")
        return

    admin = admin[0]

    games = get_games_by_admin(admin["id"])

    if not games:
        await message.answer("📭 У вас пока нет созданных игр")
        return

    for game in games:

        status_icon = "🟢" if game["status"] == "active" else "🔴"

        keyboard = None

        if game["status"] == "active":
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="❌ Отменить игру",
                            callback_data=f"cancel_{game['id']}"
                        )
                    ]
                ]
            )

        await message.answer(
            f"""
{status_icon} <b>{game['field_name']}</b>

📍 <i>{game['address']}</i>
📅 {game['game_date']}
👥 0/{game['max_players']}

⚡ Статус: {game['status']}
""",
            parse_mode="HTML",
            reply_markup=keyboard
        )


# -------------------------
# ОТМЕНА ИГРЫ ❌
# -------------------------

@router.callback_query(F.data.startswith("cancel_"))
async def cancel_game_handler(callback: CallbackQuery):

    game_id = callback.data.split("_")[1]

    cancel_game(game_id)

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>Игра отменена</b>",
        parse_mode="HTML"
    )

    await callback.answer("Игра отменена")