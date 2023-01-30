from datetime import datetime
from pytz import timezone
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State


class MyCallback(CallbackData, prefix="my"):
    callback: str


class StateWaitAnswer(StatesGroup):
    GET_REASON = State()


def current_datetime():
    return datetime.now(timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
