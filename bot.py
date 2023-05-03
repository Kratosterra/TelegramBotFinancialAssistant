from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config.config import TOKEN_API

# Создаём машинное хранилище.
storage = MemoryStorage()
# Создаём экземпляр бота.
bot = Bot(TOKEN_API)
# Создаём диспетчер, передавая ему экземпляр бота и экземпляр хранилища.
dp = Dispatcher(bot, storage=storage)
