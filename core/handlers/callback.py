from aiogram import Router, F
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext
from pytz import timezone

from core.services import db
from core.services.utils import current_datetime, MyCallback, StateReasonNotWork, change_journal_entry_callback
from core.keyboards.inline_keyboards import missclick_keyboard, first_keyboard

router = Router()


@router.callback_query(MyCallback.filter(F.callback == 'office'))
async def office_callback(callback: CallbackQuery):
    await change_journal_entry_callback(callback)
    await callback.message.edit_text('Я тебя отметил!\n<b><i>В офисе</i></b>', reply_markup=missclick_keyboard())


@router.callback_query(MyCallback.filter(F.callback == 'remote'))
async def remote_callback(callback: CallbackQuery):
    await change_journal_entry_callback(callback)
    await callback.message.edit_text('Я тебя отметил!\n<b><i>Удаленно</i></b>', reply_markup=missclick_keyboard())


@router.callback_query(MyCallback.filter(F.callback == 'not_work'))
async def not_work_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Чтобы я тебя отметил, напиши причину почему ты сегодня не работаешь')
    await state.set_state(StateReasonNotWork.GET_REASON)


@router.callback_query(MyCallback.filter(F.callback == 'missclick'))
async def not_work_callback(callback: CallbackQuery):
    checking_date = callback.message.date.astimezone(timezone('Europe/Moscow')).strftime('%Y-%m-%d')
    await db.change_journal_entry_by_date(user_id=callback.from_user.id, checking_date=checking_date)
    await callback.message.edit_text('Выбери снова', reply_markup=first_keyboard())

