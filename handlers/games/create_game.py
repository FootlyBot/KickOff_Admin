from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from states.create_game import CreateGameState
from database.admins import get_admin_by_telegram_id
from database.games import create_game
from keyboards.admin_menu import admin_menu

router = Router()


# -------------------------
# CANCEL KEYBOARD
# -------------------------

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отменить создание")]],
    resize_keyboard=True
)


# -------------------------
# GLOBAL CANCEL (FIX)
# -------------------------

@router.message(StateFilter("*"), F.text == "❌ Отменить создание")
async def cancel_create_game(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "❌ Создание игры отменено",
        reply_markup=admin_menu
    )


# -------------------------
# START GAME
# -------------------------

@router.message(F.text == "⚽ Создать игру")
async def start_game(message: Message, state: FSMContext):

    admin = get_admin_by_telegram_id(message.from_user.id)

    if not admin:
        await message.answer("🚫 Нет доступа")
        return

    await message.answer(
        "🏟 Введите название поля:",
        reply_markup=cancel_keyboard
    )

    await state.set_state(CreateGameState.waiting_field)


# -------------------------
# FIELD
# -------------------------

@router.message(CreateGameState.waiting_field)
async def field(message: Message, state: FSMContext):

    await state.update_data(field_name=message.text)

    await message.answer(
        "📍 Введите адрес:",
        reply_markup=cancel_keyboard
    )

    await state.set_state(CreateGameState.waiting_address)


# -------------------------
# ADDRESS
# -------------------------

@router.message(CreateGameState.waiting_address)
async def address(message: Message, state: FSMContext):

    await state.update_data(address=message.text)

    await message.answer(
        "📅 Введите дату (dd.mm.yyyy hh:mm):",
        reply_markup=cancel_keyboard
    )

    await state.set_state(CreateGameState.waiting_date)


# -------------------------
# DATE
# -------------------------

@router.message(CreateGameState.waiting_date)
async def date(message: Message, state: FSMContext):

    await state.update_data(game_date=message.text)

    await message.answer(
        "👥 Введите max игроков:",
        reply_markup=cancel_keyboard
    )

    await state.set_state(CreateGameState.waiting_max_players)


# -------------------------
# SAVE GAME (FIXED)
# -------------------------

@router.message(CreateGameState.waiting_max_players)
async def save_game(message: Message, state: FSMContext):

    data = await state.get_data()

    admin = get_admin_by_telegram_id(message.from_user.id)

    if not admin:
        await message.answer("🚫 Нет доступа", reply_markup=admin_menu)
        await state.clear()
        return

    admin = admin[0]

    # --- safe date parse
    try:
        game_date = datetime.strptime(
            data["game_date"],
            "%d.%m.%Y %H:%M"
        ).isoformat()
    except ValueError:
        await message.answer(
            "⚠️ Неверный формат даты (dd.mm.yyyy hh:mm)",
            reply_markup=cancel_keyboard
        )
        return

    # --- safe int parse
    try:
        max_players = int(message.text)
        if max_players <= 0:
            raise ValueError()
    except ValueError:
        await message.answer(
            "⚠️ Введите корректное число игроков",
            reply_markup=cancel_keyboard
        )
        return

    # --- create game
    create_game(
        admin_id=admin["id"],
        field_name=data["field_name"],
        address=data["address"],
        game_date=game_date,
        max_players=max_players
    )

    await state.clear()

    await message.answer(
        f"""
🎉 <b>ИГРА СОЗДАНА!</b>

🏟 {data['field_name']}
📍 {data['address']}
📅 {data['game_date']}
👥 0/{max_players}
""",
        parse_mode="HTML",
        reply_markup=admin_menu
    )