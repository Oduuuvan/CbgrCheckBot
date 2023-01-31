from aiogram import Bot
from aiogram.types import FSInputFile

from core.config import Config
from core.keyboards.inline_keyboards import first_keyboard
from core.services import db
from core.services.utils import current_datetime, current_date
from aiofiles import open, os
from aiocsv import AsyncWriter


async def mailing(bot: Bot):
    users = await db.get_mailing_users()
    for user in users:
        user_id = user[0]
        await db.add_journal_entry(user_id=user_id, checking_time=current_datetime())
        await bot.send_message(chat_id=user_id, text='Пора отмечаться!', reply_markup=first_keyboard())


async def send_report(bot: Bot = None):
    csv_path = f'{Config.csv_folder}report-{current_date()}.csv'
    async with open(csv_path, 'w') as f:
        writer = AsyncWriter(f, delimiter=';', dialect='unix')
        await writer.writerow(('Сотрудник', 'Статус', 'Где работает', 'Почему не работает', 'Дата рассылки'))
        rows = await db.get_data_for_report(current_date())
        await writer.writerows(rows)
    await bot.send_document(chat_id=Config.admin_id,
                            document=FSInputFile(csv_path))
    await os.remove(csv_path)
