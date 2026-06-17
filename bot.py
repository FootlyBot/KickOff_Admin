import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

from handlers.admin_registration import router as admin_router
from handlers.games import router as games_router


async def main():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(admin_router)
    dp.include_router(games_router)

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())