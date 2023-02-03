from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message

from core import bot
from core.config import Config
from core.filters.cmd_filters import filter_start, filter_stop, filter_mailing, filter_change_name, filter_test_mailing, \
    filter_report, filter_stop_mailing, filter_test_del_msg
from core.filters.states_filters import StateFIO
from core.handlers.scheduled import send_report, mailing, delete_mailing_messages
from core.services import db

router = Router()


async def set_commands(_bot: Bot):
    commands_list = [
        BotCommand(command='start', description='Начать работу с ботом'),
        BotCommand(command='stop', description='Завершить работу с ботом'),
        BotCommand(command='mailing', description='Присоединиться к рассылке'),
        BotCommand(command='stop_mailing', description='Покинуть к рассылку'),
        BotCommand(command='change_name', description='Изменить значения ФИО'),
        BotCommand(command='report', description='Получить отчет за сегодняшний день. Команда только '
                                                 'для админа')
    ]
    await _bot.set_my_commands(commands=commands_list)


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
    if await db.user_is_deleted(user_id=message.from_user.id):
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')
    else:
        await db.set_is_deleted(message.from_user.id, True)
        await message.answer('До встречи!\nЕсли снова захотите присоединиться, пишите: /start')


@router.message(filter_mailing)
async def cmd_mailing(message: Message):
    if await db.user_is_deleted(user_id=message.from_user.id):
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')
    else:
        if await db.user_is_mailing(user_id=message.from_user.id):
            await message.answer('Вы и так участвуете в рассылке')
        else:
            await db.set_is_mailing(message.from_user.id, True)
            await message.answer('Вы снова добавлены в список участников рассылки!')


@router.message(filter_stop_mailing)
async def cmd_mailing(message: Message):
    if await db.user_is_deleted(user_id=message.from_user.id):
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')
    else:
        if not await db.user_is_mailing(user_id=message.from_user.id):
            await message.answer('Вы и так не участвуете в рассылке')
        else:
            await db.set_is_mailing(message.from_user.id, False)
            await message.answer('Вы покинули список участников рассылки!')


@router.message(filter_change_name)
async def cmd_change_name(message: Message, state: FSMContext):
    if await db.user_is_deleted(user_id=message.from_user.id):
        await message.answer('Я Вас не знаю -_-\nНапишите /start, и мы с Вами познакомимся')
    else:
        await message.answer('Введите новые значения Фамилии и Имени')
        await state.set_state(StateFIO.GET_FIO)


@router.message(filter_report)
async def cmd_report(message: Message):
    if message.from_user.id == Config.admin_id or message.from_user.id == Config.user_id_report:
        await send_report(bot)
    else:
        await message.answer(text='Извините, но вам нельзя(')


@router.message(filter_test_mailing)
async def cmd_test_mailing(message: Message):
    print('test_mailing')
    if message.from_user.id == Config.admin_id:
        await mailing(bot)
    else:
        await message.answer(text='Извините, но вам нельзя(')


@router.message(filter_test_del_msg)
async def cmd_del_msg(message: Message):
    print('test_del_msg')
    if message.from_user.id == Config.admin_id:
        await delete_mailing_messages(bot)
    else:
        await message.answer(text='Извините, но вам нельзя(')
