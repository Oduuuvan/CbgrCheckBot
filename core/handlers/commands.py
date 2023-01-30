from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import BotCommand, Message

from core.keyboards.inline_keyboards import first_keyboard
from core.services import db

router = Router()


async def set_commands(bot: Bot):
    commands_list = [
                    BotCommand(command='start', description='Начать работу с ботом'),
                    BotCommand(command='stop', description='Завершить работу с ботом'),
                    BotCommand(command='test', description='Отладочная команда')
                    ]
    await bot.set_my_commands(commands=commands_list)


@router.message(Command('start'))
async def cmd_start(message: Message):
    if not await db.user_exists(user_id=message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name,
                          message.from_user.last_name)
        await message.answer('Привет, я тебя запомнил!')
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
    await message.answer(text='test', reply_markup=first_keyboard())
