import asyncio

from database.games import delete_old_cancelled_games


async def cleanup_loop():

    while True:

        try:
            delete_old_cancelled_games()
            print("Cleanup done")

        except Exception as e:
            print("Cleanup error:", e)

        # раз в 24 часа
        await asyncio.sleep(60 * 60 * 24)


if __name__ == "__main__":
    asyncio.run(cleanup_loop())