import asyncio
import logging

from aiogram import Bot, Dispatcher
from handlers import router

from config import settings
bot = Bot(token = settings.TELEGRAM_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    logging.info('System: start')

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('System: stop')
