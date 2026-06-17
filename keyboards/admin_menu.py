from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚽ Создать игру")],
        [KeyboardButton(text="📋 Мои игры")],
        [KeyboardButton(text="👤 Профиль")]
    ],
    resize_keyboard=True
)