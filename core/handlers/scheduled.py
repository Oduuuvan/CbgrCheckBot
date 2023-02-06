from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile
from aiofiles import open, os
from aiocsv import AsyncWriter

from core import bot
from core.config import Config
from core.keyboards.inline_keyboards import first_keyboard
from core.services import db
from core.services.utils import current_datetime, current_date


async def mailing():
    users = await db.get_mailing_users()
    for user in users:
        user_id = user[0]
        message = await bot.send_message(chat_id=user_id, text='Пора отмечаться!', reply_markup=first_keyboard())
        await db.add_journal_entry(user_id=user_id, checking_time=current_datetime(), message_id=message.message_id)


async def send_report():
    csv_path = f'{Config.csv_folder}report-{current_date()}.csv'
    async with open(csv_path, 'w', encoding='cp1251') as f:
        writer = AsyncWriter(f, delimiter=';', dialect='unix')
        await writer.writerow(('Сотрудник', 'Статус', 'Где работает', 'Почему не работает', 'Дата рассылки'))
        rows = await db.get_data_for_report(current_date())
        await writer.writerows(rows)
    await bot.send_document(chat_id=Config.user_id_report,
                            document=FSInputFile(csv_path))
    await os.remove(csv_path)


async def delete_mailing_messages():
    messages = await db.get_messages_for_delete(current_date())
    for user_id, message_id in messages:
        try:
            await bot.delete_message(user_id, message_id)
        except TelegramBadRequest:
            pass


async def alert_uncheck_users():
    users = await db.get_uncheck_users(current_date())
    if len(users) != 0:
        for user in users:
            user_id = user[0]
            await bot.send_message(chat_id=user_id, text='Уважаемый(ая), Вам уже прилетит от Лены, но вы всё еще '
                                                         'можете отметиться')


async def clear_journal():
    await db.clear_journal(current_date())
