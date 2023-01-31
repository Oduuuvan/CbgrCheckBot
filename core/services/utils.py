from datetime import datetime

from aiogram.types import CallbackQuery
from pytz import timezone

from core.services import db


def current_datetime():
    return datetime.now(timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')


def current_date():
    return current_datetime().split(' ')[0]


async def change_journal_entry_callback(callback: CallbackQuery):
    checking_date = callback.message.date.astimezone(timezone('Europe/Moscow')).strftime('%Y-%m-%d')
    status_name = callback.data.split(':')[1]
    await db.change_journal_entry_by_date(user_id=callback.from_user.id, checking_date=checking_date,
                                          is_check=True, status_name=status_name)
