from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message

from core.filters.cmd_filters import filter_start, filter_stop, filter_mailing, filter_change_name
from core.filters.states_filters import StateFIO
from core.services import db

router = Router()


async def set_commands(bot: Bot):
    commands_list = [
                    BotCommand(command='start', description='Начать работу с ботом'),
                    BotCommand(command='stop', description='Завершить работу с ботом'),
                    BotCommand(command='mailing', description='Присоединиться к рассылке'),
                    BotCommand(command='change_name', description='Изменить значения ФИО'),
                    ]
    await bot.set_my_commands(commands=commands_list)


@router.message(filter_start)
async def cmd_start(message: Message, state: FSMContext):
    if not await db.user_exists(user_id=message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.username)

    if await db.user_is_deleted(user_id=message.from_user.id):
        await message.answer('Введите свои Фамилию и Имя\n'
                             'Просьба отнестись серьезно. т.к. эти данные будут в отчете.\n\n'
                             'Если Вы вдруг захотите изменить данные, напишите /change_name')
        await state.set_state(StateFIO.GET_FIO)
    else:
        await message.answer('Я Вас уже знаю!')


@router.message(filter_stop)
async def cmd_stop(message: Message):
    if not await db.user_is_deleted(user_id=message.from_user.id):
        await db.set_is_deleted(message.from_user.id, True)
        await message.answer('До встречи!\nЕсли снова захотите присоединиться, пишите: /start')
    else:
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')


@router.message(filter_mailing)
async def cmd_mailing(message: Message):
    if not await db.user_is_deleted(user_id=message.from_user.id):
        await db.set_is_mailing(message.from_user.id, True)
        await message.answer('Вы снова добавлены к рассылке!')
    else:
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')


@router.message(filter_change_name)
async def cmd_change_name(message: Message, state: FSMContext):
    if not await db.user_is_deleted(user_id=message.from_user.id):
        await message.answer('Введите новые значения Фамилии и Имени')
        await state.set_state(StateFIO.GET_FIO)
    else:
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')
