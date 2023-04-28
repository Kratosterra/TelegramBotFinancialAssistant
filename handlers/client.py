import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from bot import dp
from database import db_functions
from handlers.document_handlers import on_import_from_user_handler
from handlers.keyboards import keyboard, inline_keybords
from handlers.models.categories_deletion_model import CategoriesAddingForm
from handlers.models.income_spend_model import IncomeSpendForm
from handlers.models.report_model import ReportForm
from handlers.models.settings_model import SettingsForm
from helpers import information
from texts.ru_RU import messages


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message) -> None:
    """
    Функция, исполняющаяся при и пользовании команды /start.
    :param message: Экземпляр сообщения
    """
    try:
        logging.debug(f"/start. Пользователь с id {message.from_user.id}.")
        await db_functions.initialize_user(str(message.from_user.id))
        await message.answer(messages.start_message, parse_mode="MarkdownV2", reply_markup=keyboard.main_menu)
        await IncomeSpendForm.value.set()
    except Exception as e:
        logging.error(f"{start.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals=['📊 Отчёты и экспорт', '/report']), state=IncomeSpendForm.value)
async def on_report(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на предоставление отчета или экспорта.
    :param message: Экземпляр сообщения
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await ReportForm.start.set()
        await message.answer(
            "*Отчёты и экспорт\!* 📊\n\nЗдесь вам доступна возможность получить *отчёт* по месяцам в чат или"
            " *полноценный отчет* со всеми наименованиями за выбранный период в формате *\.xls*\.\n"
            "Также вы можете произвести экспорт, вам будет прислан файл в формате *\.csv*\!\n", parse_mode="MarkdownV2",
            reply_markup=inline_keybords.report_inline)
    except Exception as e:
        logging.error(f"{on_report.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals=['ℹ️ Бюджет', '/budget']), state=IncomeSpendForm.value)
async def on_info(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на предоставление информации по текущему состоянию бюджета.
    :param message: Экземпляр сообщения.
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await message.answer(f"*ℹ️ Бюджет*"
                             f"{await information.get_budget_of_user(str(message.from_user.id))}",
                             parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(f"{on_info.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals=['🛠 Категории', '/categories']), state=IncomeSpendForm.value)
async def on_incomes_spends(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на работу с тратами и доходами.
    :param message: Экземпляр сообщения.
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await CategoriesAddingForm.start.set()
        await message.answer(
            "*Категории и удаление\!* 📈\n\nТут вы можете *добавить и удалить* категории/подкатегории\.\n"
            "А также *удалить* доходы/траты\!", parse_mode="MarkdownV2",
            reply_markup=inline_keybords.income_spend_category_inline)
    except Exception as e:
        logging.error(f"{on_incomes_spends.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals=['📝 Траты и доходы', '/sums']), state=IncomeSpendForm.value)
async def on_incomes_spends(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на работу с тратами и доходами.
    :param message: Экземпляр сообщения.
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await message.answer(
            "*Траты и доходы\!* 📝\nЭта кнопка \- просто подсказка\.\n\n"
            "Чтобы добавить сумму, просто оправьте *число* или *фото чека* в чат\!\n"
            "Пример: *123* или *123\.32* или *123\,32*\n\n"
            "_*Hint:* Отправьте документ *\.csv*, чтобы импортировать данные\!_", parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(f"{on_incomes_spends.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals=['⚙️ Настройки', '/settings']), state=IncomeSpendForm.value)
async def on_settings(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на открытие настроек.
    :param message: Экземпляр сообщения.
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await SettingsForm.start.set()
        await message.answer(
            "*Настройки\!* ⚙️\n\nТут вы сможете *сменить валюту*, перенести *остаток по средствам* с прошлого месяца\.\n"
            "Добавить или удалить *события* трат или доходов\, которые повторяются каждый месяц в заданный день\!\n"
            "Настроить *цель* по сэкономленным средствам и *лимит* по тратам за месяц\!\n", parse_mode="MarkdownV2",
            reply_markup=inline_keybords.settings_inline)
    except Exception as e:
        logging.error(f"{on_settings.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(Text(equals=['🆘 Помощь', '/help']), state=IncomeSpendForm.value)
async def on_help(message: types.Message) -> None:
    """
    Функция, ответственная за обработку запроса на предоставление инструкции по работе.
    :param message: Экземпляр сообщения.
    """
    try:
        await db_functions.execute_events(str(message.from_user.id))
        await message.delete()
        await message.answer(messages.help_message, parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(f"{on_help.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(content_types=['document', 'photo'], state=[IncomeSpendForm.value, '*'])
async def on_files(message: types.Message, state: FSMContext) -> None:
    """
    Функция, отвечающая за запуск действий с фото для сканирования и обработкой документов.
    :param message: Экземпляр сообщения.
    """
    try:
        current_state = await state.get_state()
        if current_state is None:
            await message.answer(messages.repair_of_functional, parse_mode="MarkdownV2")
            await IncomeSpendForm.value.set()
            return
        elif current_state != IncomeSpendForm.value.state:
            await message.delete()
            return
        if message.document:
            await db_functions.execute_events(str(message.from_user.id))
            logging.debug(f"Получил документ {message.document.file_name}. Пользователь с id {message.from_user.id}.")
            await on_import_from_user_handler(message, state)
        if message.photo:
            await db_functions.execute_events(str(message.from_user.id))
            logging.debug(f"Получил фото. Пользователь с id {message.from_user.id}.")
            await message.answer("*Сканирование QR\.\.\.*", parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(f"{on_files.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.message_handler(content_types=["audio", "sticker", "video", "video_note", "voice", "location", "contact"],
                    state=IncomeSpendForm.value)
async def on_all_not_command_message(message: types.Message) -> None:
    """
    Функция, отвечающая пользователю на непредусмотренный тип входных данных.
    :param message: Экземпляр сообщения.
    """
    logging.debug(f"Получил неизвестный тип сообщения. Пользователь с id {message.from_user.id}.")
    await message.answer(text=messages.not_in_bot_message, parse_mode="MarkdownV2")


def register_client() -> None:
    """
    Регистрирует команды бота.
    """
    dp.register_message_handler(start, commands=['start'])
