from aiogram import Bot, Dispatcher
import logging
import asyncio

from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from core.filters.cmd_filters import filter_test_mailing, filter_test_report
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

    # Отладочные команды
    @dp.message(filter_test_mailing)
    async def cmd_test_mailing(message: Message, _bot: Bot = bot):
        print('test_mailing')
        if message.from_user.id == Config.admin_id:
            await mailing(_bot)
        else:
            await message.answer(text='Извините, но вам нельзя(')

    @dp.message(filter_test_report)
    async def cmd_test_report(message: Message, _bot: Bot = bot):
        print('test_report')
        if message.from_user.id == Config.admin_id:
            await send_report(_bot)
        else:
            await message.answer(text='Извините, но вам нельзя(')

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
