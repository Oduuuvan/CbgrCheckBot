from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton

from core.services.utils import MyCallback


def first_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    btn_office = InlineKeyboardButton(text='В офисе', callback_data=MyCallback(callback='office').pack())
    btn_remote = InlineKeyboardButton(text='На удалёнке', callback_data=MyCallback(callback='remote').pack())
    btn_not_work = InlineKeyboardButton(text='Не работаю', callback_data=MyCallback(callback='not_work').pack())
    kb.add(btn_office).add(btn_remote).add(btn_not_work)
    return kb.as_markup()


def missclick_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    btn_missclick = InlineKeyboardButton(text='Изменить статус', callback_data=MyCallback(callback='missclick').pack())
    kb.add(btn_missclick)
    return kb.as_markup()
