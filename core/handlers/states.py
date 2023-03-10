from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.filters.states_filters import StateReasonNotWork, StateFIO
from core.services import db
from core.keyboards.inline_keyboards import missclick_keyboard
from core.services.utils import current_datetime, send_of_late_user, validate_FIO

router = Router()


@router.message(StateReasonNotWork.GET_REASON)
async def get_reason(message: Message, state: FSMContext):
    if message.text is None:
        await message.answer('Пожалуйста, вводите причину отсутствия текстом')
    else:
        await db.add_journal_entry(checking_time=current_datetime(), user_id=message.from_user.id, is_check=True,
                                   status_name='not_work', reason_not_work=message.text,
                                   message_id=message.message_id+1)
        await db.set_is_mailing(message.from_user.id, False)
        await message.answer(f'<b><i>Не работаю</i></b>\n\nПричина: {message.text}\n\n'
                             f'Вы покинули список участников рассылки. Чтобы снова участвовать в рассылке, либо '
                             f'измените выбор, либо напишите /mailing',
                             reply_markup=missclick_keyboard())
        await send_of_late_user(message)
        await state.clear()


@router.message(StateFIO.GET_FIO)
async def get_fio(message: Message, state: FSMContext):
    await db.set_is_deleted(message.from_user.id, False)
    if message.text is None:
        await message.answer('Пожалуйста, вводите ФИО текстом')
    else:
        if validate_FIO(message.text):
            await db.set_name_for_report(message.from_user.id, message.text)
            await message.answer(f'Теперь Вы записаны как: <b><i>{message.text}</i></b>')
            await state.clear()
        else:
            await message.answer('Неверный формат ФИО')
