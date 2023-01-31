from aiogram import Bot, Dispatcher
import logging
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from core.handlers import commands, callback, states
from core.handlers.scheduled import mailing, send_report
from services import db
from handlers.commands import set_commands


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    # Инициализация базы данных
    await db.init_database()

    # Создание бота и главного роутера
    bot = Bot(token=Config.token, parse_mode='HTML')
    dp = Dispatcher()

    # Добавление задач по расписанию
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(mailing, trigger=CronTrigger.from_crontab('0 8 * * MON-FRI'), kwargs={'bot': bot})
    scheduler.add_job(send_report, trigger=CronTrigger.from_crontab('25 9 * * MON-FRI'), kwargs={'bot': bot})
    scheduler.start()

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
