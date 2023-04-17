import logging

from aiogram import types

from bot import dp


@dp.message_handler(content_types=['text'])
async def on_all_not_command_message(message: types.Message) -> None:
    """
    Функция, отвечающая за запуск действий с текстом, отправленным пользователем
    :param message: экземпляр сообщения
    """
    logging.debug(f"Получил текст. Пользователь с id {message.from_user.id}.")
    await message.answer(message.text)
