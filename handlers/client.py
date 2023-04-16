import logging

from aiogram import types

from bot import dp
from database import db_functions
from texts.ru_RU import messages

# Задаём схему логирования.
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.DEBUG)


async def start(message: types.Message) -> None:
    """
    Функция, исполняющаяся при и пользовании команды /start
    :param message: экземпляр сообщения
    """
    try:
        await db_functions.initialize_user(str(message.from_user.id))
        await message.answer(messages.start_message, parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(f"{start.__name__}: {e}. Пользователь с id {message.from_user.id}.")


def register_client():
    """
    Регистрирует команды бота.
    """
    dp.register_message_handler(start, commands=['start'])
