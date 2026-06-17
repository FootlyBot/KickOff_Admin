from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from database.admins import get_admin_by_telegram_id, create_admin
from keyboards.admin_menu import admin_menu

router = Router()


# ----------------------
# STATES
# ----------------------

class AdminReg(StatesGroup):
    waiting_first_name = State()
    waiting_last_name = State()


# ----------------------
# START
# ----------------------

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):

    admin = get_admin_by_telegram_id(message.from_user.id)

    if admin:
        await message.answer(
            "Вы уже админ ⚽",
            reply_markup=admin_menu
        )
        return

    await message.answer("Введите имя:")
    await state.set_state(AdminReg.waiting_first_name)


# ----------------------
# FIRST NAME
# ----------------------

@router.message(StateFilter(AdminReg.waiting_first_name))
async def first_name(message: Message, state: FSMContext):

    await state.update_data(first_name=message.text)

    await message.answer("Введите фамилию:")
    await state.set_state(AdminReg.waiting_last_name)


# ----------------------
# LAST NAME
# ----------------------

@router.message(StateFilter(AdminReg.waiting_last_name))
async def last_name(message: Message, state: FSMContext):

    data = await state.get_data()

    create_admin(
        telegram_id=message.from_user.id,
        first_name=data["first_name"],
        last_name=message.text
    )

    await message.answer(
        "Регистрация завершена ⚽",
        reply_markup=admin_menu
    )

    await state.clear()