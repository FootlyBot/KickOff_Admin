from datetime import datetime

from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states.create_game import CreateGameState
from database.admins import get_admin_by_telegram_id
from database.games import create_game
from keyboards.admin_menu import admin_menu

router = Router()


cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отменить создание")]],
    resize_keyboard=True
)


@router.message(lambda m: m.text == "⚽ Создать игру")
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


@router.message(CreateGameState.waiting_field)
async def field(message: Message, state: FSMContext):

    await state.update_data(field_name=message.text)

    await message.answer("📍 Введите адрес:", reply_markup=cancel_keyboard)

    await state.set_state(CreateGameState.waiting_address)


@router.message(CreateGameState.waiting_address)
async def address(message: Message, state: FSMContext):

    await state.update_data(address=message.text)

    await message.answer("📅 Введите дату:", reply_markup=cancel_keyboard)

    await state.set_state(CreateGameState.waiting_date)


@router.message(CreateGameState.waiting_date)
async def date(message: Message, state: FSMContext):

    await state.update_data(game_date=message.text)

    await message.answer("👥 Введите max игроков:", reply_markup=cancel_keyboard)

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

        max_players = int(message.text)

    except:
        await message.answer("⚠️ Ошибка ввода", reply_markup=cancel_keyboard)
        return

    create_game(
        admin_id=admin["id"],
        field_name=data["field_name"],
        address=data["address"],
        game_date=game_date,
        max_players=max_players
    )

    await state.clear()

    await message.answer(
        f"🎉 Игра создана!\n\n🏟 {data['field_name']}\n📍 {data['address']}",
        reply_markup=admin_menu
    )