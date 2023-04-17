import logging

from aiogram import types

from bot import dp
from database import db_functions
from texts.ru_RU import messages


async def start(message: types.Message) -> None:
    """
    Функция, исполняющаяся при и пользовании команды /start
    :param message: экземпляр сообщения
    """
    try:
        logging.debug(f"/start. Пользователь с id {message.from_user.id}.")
        await db_functions.initialize_user(str(message.from_user.id))
        await message.answer(messages.start_message, parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(f"{start.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(content_types=['document', 'photo'])
async def on_files(message: types.Message):
    """
    Функция, отвечающая за запуск действий с фото для сканирования и обработкой документов
    :param message: экземпляр сообщения
    """
    if message.document:
        logging.debug(f"Получил документ {message.document.file_name}. Пользователь с id {message.from_user.id}.")
        await message.answer_document(message.document.file_id)
    if message.photo:
        logging.debug(f"Получил фото. Пользователь с id {message.from_user.id}.")
        await message.answer_photo(message.photo[-1].file_id)


@dp.message_handler(content_types=['text'])
async def on_all_not_command_message(message: types.Message) -> None:
    """
    Функция, отвечающая за запуск действий с текстом, отправленным пользователем
    :param message: экземпляр сообщения
    """
    logging.debug(f"Получил текст. Пользователь с id {message.from_user.id}.")
    await message.answer(message.text)


@dp.message_handler(content_types=["audio", "sticker", "video", "video_note", "voice", "location", "contact"])
async def on_all_not_command_message(message: types.Message) -> None:
    """
    Функция, отвечающая пользователю на непредусмотренный тип входных данных
    :param message: экземпляр сообщения
    """
    logging.debug(f"Получил неизвестный тип сообщения. Пользователь с id {message.from_user.id}.")
    await message.answer(text=messages.not_in_bot_message, parse_mode="MarkdownV2")


def register_client():
    """
    Регистрирует команды бота.
    """
    dp.register_message_handler(start, commands=['start'])
