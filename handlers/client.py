import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from bot import dp
from database import db_functions
from handlers.keyboards import keyboard
from handlers.models.income_spend_model import IncomeSpendForm
from texts.ru_RU import messages


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message) -> None:
    """
    Функция, исполняющаяся при и пользовании команды /start
    :param message: экземпляр сообщения
    """
    try:
        logging.debug(f"/start. Пользователь с id {message.from_user.id}.")
        await db_functions.initialize_user(str(message.from_user.id))
        await message.answer(messages.start_message, parse_mode="MarkdownV2", reply_markup=keyboard.main_menu)
        await IncomeSpendForm.value.set()
    except Exception as e:
        logging.error(f"{start.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals='📝 Отчёты и экспорт'), state=IncomeSpendForm.value)
async def on_report(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на предоставление отчета или экспорта
    :param message: экземпляр сообщения
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.answer("Активируем Отчёты и экспорт")
        await message.delete()
    except Exception as e:
        logging.error(f"{on_report.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals='ℹ️ Информация'), state=IncomeSpendForm.value)
async def on_info(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на предоставление информации по текущему состоянию бюджета
    :param message: экземпляр сообщения
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await message.answer("Активируем Информация")
    except Exception as e:
        logging.error(f"{on_info.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals='📈 Траты и Доходы'), state=IncomeSpendForm.value)
async def on_incomes_spends(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на работу с тратами и доходами
    :param message: экземпляр сообщения
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await message.answer("Активируем Траты и Доходы")
    except Exception as e:
        logging.error(f"{on_incomes_spends.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals='⚙️ Настройки'), state=IncomeSpendForm.value)
async def on_settings(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на открытие настроек
    :param message: экземпляр сообщения
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await message.answer("Активируем Настройки")
    except Exception as e:
        logging.error(f"{on_settings.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals='🆘 Помощь'), state=IncomeSpendForm.value)
async def on_help(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на предоставление инструкции по работе
    :param message: экземпляр сообщения
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await message.answer(messages.help_message, parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(f"{on_help.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(content_types=['document', 'photo'], state=IncomeSpendForm.value)
async def on_files(message: types.Message) -> None:
    """
    Функция, отвечающая за запуск действий с фото для сканирования и обработкой документов
    :param message: экземпляр сообщения
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        if message.document:
            logging.debug(f"Получил документ {message.document.file_name}. Пользователь с id {message.from_user.id}.")
            await message.answer("Импорт")
        if message.photo:
            logging.debug(f"Получил фото. Пользователь с id {message.from_user.id}.")
            await message.answer("Сканирование QR")
    except Exception as e:
        logging.error(f"{on_files.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(content_types=["audio", "sticker", "video", "video_note", "voice", "location", "contact"],
                    state=IncomeSpendForm.value)
async def on_all_not_command_message(message: types.Message) -> None:
    """
    Функция, отвечающая пользователю на непредусмотренный тип входных данных
    :param message: экземпляр сообщения
    """
    logging.debug(f"Получил неизвестный тип сообщения. Пользователь с id {message.from_user.id}.")
    await message.answer(text=messages.not_in_bot_message, parse_mode="MarkdownV2")


def register_client() -> None:
    """
    Регистрирует команды бота.
    """
    dp.register_message_handler(start, commands=['start'])
