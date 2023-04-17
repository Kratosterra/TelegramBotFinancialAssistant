import logging

import coloredlogs
from aiogram import executor

from bot import dp
from handlers import client

# Оформляем логирование.
coloredlogs.install(level='DEBUG')
logger = logging.getLogger(__name__)
coloredlogs.install(
    level='DEBUG', logger=logger,
    fmt='%(asctime)s.%(msecs)03d %(filename)s:%(lineno)d %(levelname)s %(message)s'
)

# Регистрируем команды.
client.register_client()
# Используем polling и пропускаем те команды, которые были даны вне работы бота.
executor.start_polling(dp, skip_updates=True)
