from aiogram.fsm.state import State, StatesGroup


class CreateGameState(StatesGroup):
    waiting_field = State()
    waiting_address = State()
    waiting_date = State()
    waiting_max_players = State()