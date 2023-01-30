from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.services import db
from core.services.utils import current_datetime, StateWaitAnswer
from core.keyboards.inline_keyboards import missclick_keyboard

router = Router()


@router.message(StateWaitAnswer.GET_REASON)
async def get_reason(message: Message, state: FSMContext):
    checking_time = current_datetime()
    await db.add_journal_entry(is_check=True, status_name='not_work', checking_time=checking_time,
                               user_id=message.from_user.id, reason_not_work=message.text)

    await message.answer(f'Я тебя отметил!\n<b><i>Не работаю</i></b>\n\nПричина: {message.text}',
                         reply_markup=missclick_keyboard())
    await state.update_data(reason_not_work=message.text)
    await state.clear()
