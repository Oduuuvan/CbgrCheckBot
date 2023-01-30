from aiogram import Bot

from core.keyboards.inline_keyboards import first_keyboard
from core.services import db
from core.services.utils import current_datetime


async def mailing(bot: Bot):
    users = await db.get_mailing_users()
    for user in users:
        user_id = user[0]
        await db.add_journal_entry(user_id=user_id, checking_time=current_datetime())
        await bot.send_message(chat_id=user_id, text='Пора отмечаться!', reply_markup=first_keyboard())



