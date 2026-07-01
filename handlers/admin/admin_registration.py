from aiogram import Router, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.filters import CommandStart, Command

from database.admins import (
    get_active_admin_by_telegram_id,
    get_super_admins,
    create_admin
)
from database.admin_requests import (
    get_pending_request_by_telegram_id,
    create_admin_request,
    get_admin_request_by_id,
    approve_admin_request,
    reject_admin_request
)
from keyboards.admin_menu import admin_menu

router = Router()


# ----------------------
# KEYBOARDS
# ----------------------

def request_admin_access_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔐 Запросить доступ",
                    callback_data="request_admin_access"
                )
            ]
        ]
    )


def review_admin_request_keyboard(request_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Одобрить",
                    callback_data=f"approve_admin:{request_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"reject_admin:{request_id}"
                )
            ]
        ]
    )


# ----------------------
# HELPERS
# ----------------------

def format_user_info(user) -> str:
    username = f"@{user.username}" if user.username else "не указан"
    last_name = user.last_name if user.last_name else "не указана"

    return (
        f"Имя: {user.first_name}\n"
        f"Фамилия: {last_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user.id}"
    )


def format_request_info(request: dict) -> str:
    username = f"@{request['username']}" if request.get("username") else "не указан"
    last_name = request.get("last_name") or "не указана"

    return (
        f"Имя: {request.get('first_name')}\n"
        f"Фамилия: {last_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {request.get('telegram_id')}"
    )


def is_super_admin(admin: dict | None) -> bool:
    return bool(
        admin
        and admin.get("role") == "super_admin"
        and admin.get("is_active") is True
    )


# ----------------------
# START
# ----------------------

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Это админ-панель KickOff ⚽\n\n"
        "Для входа или запроса доступа используйте команду /admin",
        reply_markup=ReplyKeyboardRemove()
    )


# ----------------------
# ADMIN ENTRY
# ----------------------

@router.message(Command("admin"))
async def admin_entry(message: Message):
    admin = get_active_admin_by_telegram_id(message.from_user.id)

    if admin:
        await message.answer(
            "Вы вошли как администратор ⚽",
            reply_markup=admin_menu
        )
        return

    await message.answer(
        "У вас пока нет доступа к админ-панели.\n\n"
        "Вы можете отправить заявку супер-администраторам.\n"
        "После подтверждения вам откроется управление играми.",
        reply_markup=request_admin_access_keyboard()
    )


# ----------------------
# REQUEST ACCESS
# ----------------------

@router.callback_query(lambda c: c.data == "request_admin_access")
async def request_admin_access(callback: CallbackQuery, bot: Bot):
    user = callback.from_user

    admin = get_active_admin_by_telegram_id(user.id)

    if admin:
        await callback.message.answer(
            "Вы уже являетесь администратором ⚽",
            reply_markup=admin_menu
        )
        await callback.answer()
        return

    existing_request = get_pending_request_by_telegram_id(user.id)

    if existing_request:
        await callback.message.answer(
            "Ваша заявка уже отправлена и ожидает подтверждения."
        )
        await callback.answer()
        return

    admin_request = create_admin_request(
        telegram_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )

    super_admins = get_super_admins()

    if not super_admins:
        await callback.message.answer(
            "Заявка создана, но супер-администраторы не найдены. "
            "Обратитесь к владельцу проекта."
        )
        await callback.answer()
        return

    request_text = (
        "🔐 Новая заявка на админ-доступ\n\n"
        f"{format_user_info(user)}"
    )

    for super_admin in super_admins:
        await bot.send_message(
            chat_id=super_admin["telegram_id"],
            text=request_text,
            reply_markup=review_admin_request_keyboard(admin_request["id"])
        )

    await callback.message.answer(
        "Заявка отправлена ✅\n"
        "Ожидайте подтверждения супер-администратором."
    )

    await callback.answer()


# ----------------------
# APPROVE REQUEST
# ----------------------

@router.callback_query(lambda c: c.data.startswith("approve_admin:"))
async def approve_request(callback: CallbackQuery, bot: Bot):
    reviewer = get_active_admin_by_telegram_id(callback.from_user.id)

    if not is_super_admin(reviewer):
        await callback.answer(
            "У вас нет прав на подтверждение заявок.",
            show_alert=True
        )
        return

    request_id = callback.data.split(":")[1]
    admin_request = get_admin_request_by_id(request_id)

    if not admin_request:
        await callback.answer(
            "Заявка не найдена.",
            show_alert=True
        )
        return

    if admin_request["status"] != "pending":
        await callback.answer(
            "Эта заявка уже обработана.",
            show_alert=True
        )
        return

    create_admin(
        telegram_id=admin_request["telegram_id"],
        first_name=admin_request.get("first_name"),
        last_name=admin_request.get("last_name"),
        username=admin_request.get("username"),
        role="admin"
    )

    approve_admin_request(
        request_id=request_id,
        reviewed_by=callback.from_user.id
    )

    try:
        await bot.send_message(
            chat_id=admin_request["telegram_id"],
            text=(
                "Ваша заявка на админ-доступ одобрена ✅\n\n"
                "Теперь вы можете использовать команду /admin"
            )
        )
    except Exception:
        pass

    await callback.message.edit_text(
        "✅ Заявка одобрена\n\n"
        f"{format_request_info(admin_request)}"
    )

    await callback.answer("Заявка одобрена")


# ----------------------
# REJECT REQUEST
# ----------------------

@router.callback_query(lambda c: c.data.startswith("reject_admin:"))
async def reject_request(callback: CallbackQuery, bot: Bot):
    reviewer = get_active_admin_by_telegram_id(callback.from_user.id)

    if not is_super_admin(reviewer):
        await callback.answer(
            "У вас нет прав на отклонение заявок.",
            show_alert=True
        )
        return

    request_id = callback.data.split(":")[1]
    admin_request = get_admin_request_by_id(request_id)

    if not admin_request:
        await callback.answer(
            "Заявка не найдена.",
            show_alert=True
        )
        return

    if admin_request["status"] != "pending":
        await callback.answer(
            "Эта заявка уже обработана.",
            show_alert=True
        )
        return

    reject_admin_request(
        request_id=request_id,
        reviewed_by=callback.from_user.id
    )

    try:
        await bot.send_message(
            chat_id=admin_request["telegram_id"],
            text="Ваша заявка на админ-доступ отклонена ❌"
        )
    except Exception:
        pass

    await callback.message.edit_text(
        "❌ Заявка отклонена\n\n"
        f"{format_request_info(admin_request)}"
    )

    await callback.answer("Заявка отклонена")