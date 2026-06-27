from aiogram import Bot, Dispatcher
import asyncio

from config import BOT_TOKEN

from handlers.admin.admin_registration import router as admin_router
from handlers.games.create_game import router as create_game_router
from handlers.games.my_games import router as my_games_router
from handlers.games.cancel_created_games import router as cancel_game_router
from handlers.games.match_menu import router as match_menu_router
from handlers.games.live_match import router as live_match_router


async def main():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(admin_router)
    dp.include_router(create_game_router)
    dp.include_router(my_games_router)
    dp.include_router(cancel_game_router)
    dp.include_router(match_menu_router)
    dp.include_router(live_match_router)

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())