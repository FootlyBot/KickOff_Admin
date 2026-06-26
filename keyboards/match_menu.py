from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


match_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➡️ Следующий матч")],
        [KeyboardButton(text="📊 Таблица")],
        [KeyboardButton(text="🏁 Завершить матчи")]
    ],
    resize_keyboard=True
)