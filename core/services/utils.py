from datetime import datetime

from pytz import timezone


def current_datetime():
    return datetime.now(timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')


def current_date():
    return current_datetime().split(' ')[0]
