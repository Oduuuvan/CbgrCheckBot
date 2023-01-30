from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message

from core.config import Config
from core.keyboards.inline_keyboards import first_keyboard
from core.services import db
from core.services.utils import StateFIO, current_datetime

router = Router()


async def set_commands(bot: Bot):
    commands_list = [
                    BotCommand(command='start', description='Начать работу с ботом'),
                    BotCommand(command='stop', description='Завершить работу с ботом'),
                    BotCommand(command='mailing', description='Присоединиться к рассылке'),
                    BotCommand(command='change_name', description='Изменить значения ФИО'),
                    BotCommand(command='test', description='Отладочная команда')
                    ]
    await bot.set_my_commands(commands=commands_list)


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    if not await db.user_exists(user_id=message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.username)
        await message.answer('Введите свои Фамилию и Имя\n'
                             'Просьба отнестись серьезно. т.к. эти данные будут в отчете.\n\n'
                             'Если Вы вдруг захотите изменить данные, напишите /change_name')
        await state.set_state(StateFIO.GET_FIO)
    else:
        await message.answer('Я Вас уже знаю!')


@router.message(Command('stop'))
async def cmd_stop(message: Message):
    if await db.user_exists(user_id=message.from_user.id):
        await db.del_user(message.from_user.id)
        await message.answer('До встречи!\nЕсли снова захотите присоединиться, пишите: /start')
    else:
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')


@router.message(Command('mailing'))
async def cmd_mailing(message: Message):
    if await db.user_exists(user_id=message.from_user.id):
        await db.set_is_mailing(message.from_user.id, True)
        await message.answer('Вы снова добавлены к рассылке!')
    else:
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')


@router.message(Command('change_name'))
async def cmd_change_name(message: Message, state: FSMContext):
    if await db.user_exists(user_id=message.from_user.id):
        await message.answer('Введите новые значения Фамилии и Имени')
        await state.set_state(StateFIO.GET_FIO)
    else:
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')


@router.message(Command('test'))
async def cmd_test(message: Message):
    await db.add_journal_entry(user_id=Config.admin_ids, checking_time=current_datetime())
    await message.answer(text='test', reply_markup=first_keyboard())


@router.message(Command('test1'))
async def cmd_test1(message: Message):
    await db.add_journal_entry(user_id=Config.admin_ids, checking_time=current_datetime())
    await message.answer(text='test', reply_markup=first_keyboard())
