from datetime import datetime

from aiogram.types import CallbackQuery, Message
from pytz import timezone

from core import bot
from core.config import Config
from core.services import db


def current_datetime():
    return datetime.now(timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')


def current_date():
    return current_datetime().split(' ')[0]


async def send_of_late_user(callback: CallbackQuery | Message):
    if current_datetime().split(' ')[1] > '09:30:00':
        user_name = await db.get_user_name_for_report(callback.from_user.id)
        await bot.send_message(chat_id=Config.user_id_report,
                               text=f'Опоздун: <b><i><a href="https://t.me/{callback.from_user.username}">{user_name}'
                                    f'</a></i></b> отметился',
                               disable_web_page_preview=True)
