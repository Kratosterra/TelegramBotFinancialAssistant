from aiogram import executor

from bot import dp
from handlers import client

# Регистрируем команды.
client.register_client()
# Используем polling и пропускаем те команды, которые были даны вне работы бота.
executor.start_polling(dp, skip_updates=True)
