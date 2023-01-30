from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message

from core.keyboards.inline_keyboards import first_keyboard
from core.services import db
from core.services.utils import StateFIO, current_datetime

router = Router()


async def set_commands(bot: Bot):
    commands_list = [
                    BotCommand(command='start', description='Начать работу с ботом'),
                    BotCommand(command='stop', description='Завершить работу с ботом'),
                    BotCommand(command='test', description='Отладочная команда')
                    ]
    await bot.set_my_commands(commands=commands_list)


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    if not await db.user_exists(user_id=message.from_user.id):
        await message.answer('Привет, напиши свои Фамилию и Имя\n'
                             'Просьба отнестись серьезно. т.к. эти данные будут в отчете')
        await state.set_state(StateFIO.GET_FIO)
    else:
        await message.answer('Я тебя уже знаю!')


@router.message(Command('stop'))
async def cmd_start(message: Message):
    if await db.user_exists(user_id=message.from_user.id):
        await db.del_user(message.from_user.id)
        await message.answer('До встречи!\nЕсли снова захочешь присоединиться, пиши: /start')
    else:
        await message.answer('Я тебя не знаю -_-')


@router.message(Command('test'))
async def cmd_test(message: Message):
    users = await db.all_users()
    for user in users:
        print(user)
        await db.add_journal_entry(user_id=user[0], checking_time=current_datetime())
    await message.answer(text='test', reply_markup=first_keyboard())
