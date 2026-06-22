from .create_game import router as create_game_router
from .cancel_creating_games import router as cancel_create_router
from .my_games import router as my_games_router
from .cancel_created_games import router as cancel_game_router

routers = [
    create_game_router,
    cancel_create_router,
    my_games_router,
    cancel_game_router
]