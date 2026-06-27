from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


game_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➡️ Следующий матч")],
        [KeyboardButton(text="📊 Таблица")],
        [KeyboardButton(text="🏁 Завершить матчи")]
    ],
    resize_keyboard=True
)