from aiogram import Router, F
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.filters.callback_filters import filter_office, filter_remote, filter_not_work, filter_missclick
from core.filters.states_filters import StateReasonNotWork
from core.services import db
from core.services.utils import current_datetime
from core.keyboards.inline_keyboards import missclick_keyboard, first_keyboard

router = Router()


@router.callback_query(filter_office)
async def office_callback(callback: CallbackQuery):
    await db.add_journal_entry(checking_time=current_datetime(), user_id=callback.from_user.id, is_check=True,
                               status_name=callback.data.split(':')[1])
    await callback.message.edit_text('<b><i>В офисе</i></b>', reply_markup=missclick_keyboard())


@router.callback_query(filter_remote)
async def remote_callback(callback: CallbackQuery):
    await db.add_journal_entry(checking_time=current_datetime(), user_id=callback.from_user.id, is_check=True,
                               status_name=callback.data.split(':')[1])
    await callback.message.edit_text('<b><i>Удалённо</i></b>', reply_markup=missclick_keyboard())


@router.callback_query(filter_not_work)
async def not_work_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Чтобы я Вас отметил, напишите причину почему Вы сегодня не работаете')
    await state.set_state(StateReasonNotWork.GET_REASON)


@router.callback_query(filter_missclick)
async def not_work_callback(callback: CallbackQuery):
    await db.add_journal_entry(checking_time=current_datetime(), user_id=callback.from_user.id)
    await db.set_is_mailing(callback.from_user.id, True)
    await callback.message.edit_text('Выберите снова', reply_markup=first_keyboard())
