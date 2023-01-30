from aiogram import Bot, Dispatcher
import logging
import asyncio

from config import Config
from core.handlers import commands, callback, states
from services import db
from handlers.commands import set_commands


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    # Инициализация базы данных
    await db.init_database()

    # Создание бота и главного роутера
    bot = Bot(token=Config.token, parse_mode='HTML')
    dp = Dispatcher()

    # Подключение роутеров
    dp.include_router(commands.router)
    dp.include_router(callback.router)
    dp.include_router(states.router)

    await set_commands(bot)
    print('Bot started')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
