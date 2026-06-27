from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def build_live_keyboard(team_a_name: str, team_b_name: str):

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"⚽ ГОЛ! {team_a_name}"),
                KeyboardButton(text=f"⚽ ГОЛ! {team_b_name}")
            ],
            [KeyboardButton(text="🏁 Завершить матч")]
        ],
        resize_keyboard=True
    )