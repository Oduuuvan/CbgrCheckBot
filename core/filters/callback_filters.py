from aiogram import F
from aiogram.filters.callback_data import CallbackData


class MyCallback(CallbackData, prefix="status"):
    callback: str


filter_office = MyCallback.filter(F.callback == 'office')
filter_remote = MyCallback.filter(F.callback == 'remote')
filter_not_work = MyCallback.filter(F.callback == 'not_work')
filter_missclick = MyCallback.filter(F.callback == 'missclick')
