from datetime import datetime

from aiogram.types import CallbackQuery
from pytz import timezone

from core.services import db


def current_datetime():
    return datetime.now(timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')


def current_date():
    return current_datetime().split(' ')[0]
