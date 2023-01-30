from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from pytz import timezone

from core.services import db
from core.services.utils import current_datetime, StateReasonNotWork, StateFIO
from core.keyboards.inline_keyboards import missclick_keyboard

router = Router()


@router.message(StateReasonNotWork.GET_REASON)
async def get_reason(message: Message, state: FSMContext):
    checking_date = message.date.astimezone(timezone('Europe/Moscow')).strftime('%Y-%m-%d')
    status_name = 'not_work'
    await db.change_journal_entry_by_date(user_id=message.from_user.id, checking_date=checking_date,
                                          is_check=True, status_name=status_name, reason_not_work=message.text)
    await message.answer(f'Я тебя отметил!\n<b><i>Не работаю</i></b>\n\nПричина: {message.text}',
                         reply_markup=missclick_keyboard())
    await state.clear()


@router.message(StateFIO.GET_FIO)
async def get_fio(message: Message, state: FSMContext):
    await db.add_user(message.from_user.id, message.from_user.username, message.text)
    await message.answer(f'Теперь ты записан как: <b><i>{message.text}</i></b>')
    await state.clear()
