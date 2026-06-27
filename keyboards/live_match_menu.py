from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def build_live_keyboard(team_a: str, team_b: str):

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"⚽ {team_a}"),
                KeyboardButton(text=f"⚽ {team_b}")
            ],
            [KeyboardButton(text="🏁 Завершить матч")]
        ],
        resize_keyboard=True
    )