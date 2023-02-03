__all__ = ['bot']

from aiogram import Bot
from core.config import Config

bot = Bot(token=Config.token, parse_mode='HTML')

