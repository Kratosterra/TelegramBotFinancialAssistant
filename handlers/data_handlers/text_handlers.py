import logging
import re
import time
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from bot import dp
from database import db_functions
from handlers.keyboards import inline_keybords
from handlers.models.categories_deletion_model import CategoriesAddingForm
from handlers.models.income_spend_model import IncomeSpendForm
from handlers.models.report_model import ReportForm
from handlers.models.settings_model import SettingsForm
from texts.ru_RU import messages


@dp.message_handler(
    lambda message: message.text.replace('.', '', 1).isdigit() or message.text.replace(',', '', 1).isdigit(),
    state=IncomeSpendForm.value)
async def process_sum_from_user_message_handler(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая работает со всеми сообщениями, содержащими только число.
     Если число подходит, оправляет пользователю меню с выбором типа суммы.
    :type state: FSMContext
    :type message: Message
    :param message: Экземпляр сообщения.
    :param state: Состояние.
    """
    try:
        # Устанавливаем форму в is_spend
        await IncomeSpendForm.next()
        sum_str = message.text.replace(',', '.')
        if float(sum_str) > 10000000000 or float(sum_str) < 0.01:
            await message.answer("Это уже слишком для меня!\nЧисло либо очень большое, либо очень маленькое!",
                                 reply_markup=inline_keybords.clear_inline)
            await IncomeSpendForm.value.set()
            return
        await state.update_data(value=round(float(sum_str), 2))
        await message.answer(
            f"Сумма: {round(float(sum_str), 2)} {await db_functions.get_user_currency(str(message.from_user.id))}",
            reply_markup=inline_keybords.income_spend_inline, disable_notification=True)
    except Exception as e:
        if e == "Message is too long":
            await message.answer("Это слишком большое сообщение для меня!", reply_markup=inline_keybords.clear_inline)
        else:
            logging.error(
                f"{process_sum_from_user_message_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='income:income_spend_sum', state='*')
async def add_income_type_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отсылает сообщение с кнопками для настройки дохода.
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Начинаем добавлять доход. Пользователь с id {call.message.from_user.id}.")
        await call.answer()
        await call.message.delete()
        # Устанавливаем тип суммы.
        await state.update_data(is_spend=False)
        await call.message.answer(
            f"Доход {(await state.get_data())['value']} {await db_functions.get_user_currency(str(call.from_user.id))}",
            reply_markup=inline_keybords.income_sum_inline, disable_notification=True)
    except Exception as e:
        logging.error(f"{add_income_type_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='spend:income_spend_sum', state='*')
async def add_spend_type_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отсылает сообщение с кнопками для настройки траты.
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Начинаем добавлять трату. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await call.message.delete()
        # Устанавливаем тип суммы.
        await state.update_data(is_spend=True)
        await call.message.answer(
            f"Добавляем трату {(await state.get_data())['value']} "
            f"{await db_functions.get_user_currency(str(call.from_user.id))}",
            reply_markup=inline_keybords.spend_sum_inline, disable_notification=True)
    except Exception as e:
        logging.error(f"{add_spend_type_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='change_date:sum', state=IncomeSpendForm.is_spend)
async def add_date_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая отвечает за обработку нажатия на кнопку изменения даты суммы, отправляя сообщение с календарём.
    :type call: CallbackQuery
    :param call: Вызов от кнопки.
    """
    try:
        logging.debug(f"Отправляем календарь для выбора даты суммы. Пользователь с id {call.from_user.id}.")
        year = datetime.now().year
        month = datetime.now().month
        calendar_keyboard = await inline_keybords.generate_calendar(year, month)
        await IncomeSpendForm.date.set()
        await call.message.answer("Выберите дату:", reply_markup=calendar_keyboard, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{add_date_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(text_contains='category:spend_sum', state=IncomeSpendForm.is_spend)
async def add_category_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая отвечает за обработку нажатия на кнопку категории, отсылая сообщение с кнопками для выбора.
    :type call: CallbackQuery
    :param call: Вызов от кнопки.
    """
    try:
        logging.debug(f"Отправляем сообщение с кнопками для выбора категории. Пользователь с id {call.from_user.id}.")
        categories_raw = await db_functions.return_all_categories(str(call.from_user.id))
        categories = list(categories_raw.keys())
        keyboard = await inline_keybords.generate_category_keyboard(categories)
        await IncomeSpendForm.category.set()
        if len(categories) == 0:
            await call.message.answer("У вас нет категорий, добавьте их в настройках.", reply_markup=keyboard,
                                      disable_notification=True)
        else:
            await call.message.answer("Выберите категорию:", reply_markup=keyboard, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{add_category_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(text_contains='sub:spend_sum', state=IncomeSpendForm.is_spend)
async def add_subcategory_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за обработку нажатия на кнопку подкатегории, отсылая сообщение для выбора.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(
            f"Отправляем сообщение с кнопками для выбора подкатегории. Пользователь с id {call.from_user.id}.")
        categories_raw = await db_functions.return_all_categories(str(call.from_user.id))
        data = await state.get_data()
        if 'category' not in data.keys():
            keyboard = await inline_keybords.generate_subcategory_keyboard([])
            await call.message.answer("Выберете категорию для того, чтобы добавлять подкатегорию.",
                                      reply_markup=keyboard, disable_notification=True)
        else:
            if data['category'] in categories_raw.keys() and len(categories_raw[data['category']]) > 0:
                keyboard = await inline_keybords.generate_subcategory_keyboard(categories_raw[data['category']])
                print(categories_raw[data['category']])
                await call.message.answer("Выберете подкатегорию:",
                                          reply_markup=keyboard, disable_notification=True)
            else:
                keyboard = await inline_keybords.generate_subcategory_keyboard([])
                await call.message.answer("Сначала добавьте подкатегории в свою категорию.",
                                          reply_markup=keyboard, disable_notification=True)
        await call.answer()
        await IncomeSpendForm.subcategory.set()
    except Exception as e:
        logging.error(f"{add_subcategory_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:category:'), state=IncomeSpendForm.category)
async def add_category_sum_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на выбор категории кнопкой, добавляя информацию в состояние.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Получаем категорию. Пользователь с id {call.from_user.id}.")
        category = call.data[16:]
        await call.message.delete()
        await state.update_data(category=str(category))
        await state.update_data(subcategory=None)
        await call.answer(f"Категория: {category} установлена! Подкатегория сброшена!")
        await IncomeSpendForm.is_spend.set()
    except Exception as e:
        logging.error(f"{add_category_sum_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.answer("Произошла непредвиденная ошибка, попробуйте присвоить категорию снова!")
        await call.message.delete()
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:subcategory:'),
                           state=IncomeSpendForm.subcategory)
async def add_subcategory_sum_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на выбор подкатегории кнопкой, добавляя информацию в состояние.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Получаем подкатегорию. Пользователь с id {call.from_user.id}.")
        category = call.data[19:]
        await call.message.delete()
        await state.update_data(subcategory=str(category))
        await call.answer(f"Подкатегория: {category} установлена!")
        await IncomeSpendForm.is_spend.set()
    except Exception as e:
        logging.error(f"{add_subcategory_sum_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.answer("Произошла непредвиденная ошибка, попробуйте присвоить категорию снова!")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(text_contains='proceed:sum', state=IncomeSpendForm.is_spend)
async def proceed_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на кнопку добавления суммы как траты или дохода. Закрывает набор состояний.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Добавляем информацию. Пользователь с id {call.from_user.id}.")
        logging.debug(await state.get_data())
        value = (await state.get_data())['value']
        name = None
        date = None
        if 'date' in (await state.get_data()).keys():
            date = (await state.get_data())['date']
        if 'name' in (await state.get_data()).keys():
            name = (await state.get_data())['name']
        if not (await state.get_data())['is_spend']:
            if date is None:
                st = await db_functions.add_income(user_id=str(call.from_user.id), value=value, name=name,
                                                   date=time.strftime("%Y-%m-%d", time.gmtime()))
            else:
                st = await db_functions.add_income(user_id=str(call.from_user.id), value=value, name=name, date=date)
        else:
            category = None
            subcategory = None
            if 'category' in (await state.get_data()).keys():
                category = (await state.get_data())['category']
            if 'subcategory' in (await state.get_data()).keys():
                subcategory = (await state.get_data())['subcategory']
            if date is None:
                st = await db_functions.add_spend(user_id=str(call.from_user.id), value=value, name=name,
                                                  category=category,
                                                  subcategory=subcategory,
                                                  date=time.strftime("%Y-%m-%d", time.gmtime()))
            else:
                st = await db_functions.add_spend(user_id=str(call.from_user.id), category=category,
                                                  subcategory=subcategory, value=value, name=name, date=date)
        await call.message.delete()
        if st:
            await call.answer(f"Добавление завершено успешно!")
            await call.message.answer(f"Добавление завершено успешно!", reply_markup=inline_keybords.clear_inline)
        else:
            await call.answer(f"Добавление не завершено, повторите попытку!")
            await call.message.answer(f"Добавление не завершено, повторите попытку!",
                                      reply_markup=inline_keybords.clear_inline)
        await state.finish()
        await IncomeSpendForm.value.set()
    except Exception as e:
        logging.error(f"{proceed_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.answer("При добавлении произошла ошибка, попробуйте еще раз! Нажав 'Отмена'")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='name:sum', state=IncomeSpendForm.is_spend)
async def add_name_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку имени, отправляя запрос на предоставление имени суммы.
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Изменяем имя суммы. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await IncomeSpendForm.name.set()
        await call.message.answer("Отправьте имя суммы.", reply_markup=inline_keybords.refuse_to_input,
                                  disable_notification=True)
    except Exception as e:
        logging.error(f"{add_name_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(text_contains='input::stop', state=IncomeSpendForm.name)
async def refuse_to_input_name_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор имени суммы.
    :type state: FSMContext
    :type call: CallbackQuery
    :param state: Текущее состояние.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Отменяем ввод имени! Пользователь с id {call.from_user.id}.")
        await call.answer("Отменяем ввод!")
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(IncomeSpendForm.is_spend)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{refuse_to_input_name_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.is_spend.set()


@dp.message_handler(state=IncomeSpendForm.name)
async def add_name_message_handler(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая реагирует на отправление любого сообщения, после нажатия на кнопку добавления имени.
    :type state: FSMContext
    :type message: Message
    :param message: Экземпляр сообщения.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Получаем имя. Пользователь с id {message.from_user.id}.")
        try:
            await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        except Exception as e:
            logging.debug(e)
        if len(message.text) > 75:
            await message.delete()
            await message.answer("Имя суммы не должно быть больше 75 символов, повторите ввод, снова отправьте имя)",
                                 reply_markup=inline_keybords.refuse_to_input)
            await IncomeSpendForm.name.set()
        else:
            await message.delete()
            name = str(message.text)
            name = re.sub(r'[^\w\s]', '', name)
            if len(name) < 3:
                await message.answer(
                    "Имя суммы не должно быть меньше 3 символов, повторите ввод, снова отправьте имя)",
                    reply_markup=inline_keybords.refuse_to_input)
                await IncomeSpendForm.name.set()
                return
            await state.update_data(name=name)
            await message.answer(f"Имя: {name} установлено!", disable_notification=True,
                                 reply_markup=inline_keybords.clear_inline)
            await IncomeSpendForm.is_spend.set()
    except Exception as e:
        logging.error(f"{add_name_message_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await message.delete()
        await message.answer("Произошла непредвиденная ошибка, попробуйте изменить имя снова!")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('date:'), state=IncomeSpendForm.date)
async def add_date_num_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на нажатие кнопки в календаре.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Получаем дату. Пользователь с id {call.from_user.id}.")
        year, month, day = map(int, call.data.split(':')[1:])
        data = datetime(year, month, day).strftime("%Y-%m-%d")
        await state.update_data(date=str(data))
        await call.answer(f"Дата: {data} установлена!")
        await call.message.delete()
        await IncomeSpendForm.is_spend.set()
    except Exception as e:
        logging.error(f"{add_date_num_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте изменить дату снова!")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(text_contains='cancel',
                           state=[IncomeSpendForm.is_spend, IncomeSpendForm.value,
                                  CategoriesAddingForm.start, SettingsForm.start, ReportForm.start,
                                  ReportForm.small_report, ReportForm.big_report])
async def cancel_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Позволяет пользователю завершить любое действие. Сбрасывает набор состояний.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем состояние. Сбрасываем набор состояний. Пользователь с id {call.from_user.id}.')
        current_state = await state.get_state()
        if current_state is None:
            await IncomeSpendForm.value.set()
            return
        await state.finish()
        await call.answer(text='Отмена!')
        await call.message.delete()
        await IncomeSpendForm.value.set()
    except Exception as e:
        logging.error(f"{cancel_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='ignore', state='*')
async def ignore_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая игнорирует нажатие, на неактивные кнопки.
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f'Игнорируем кнопку. Пользователь с id {call.from_user.id}.')
        await call.answer("Это не кнопка!")
    except Exception as e:
        logging.error(f"{ignore_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.message_handler(content_types=['text'], state='*')
async def on_all_not_command_message_handler(message: types.Message, state: FSMContext) -> None:
    """
    Функция, отвечающая за запуск действий с текстом без команд, отправленным пользователем.
    Создаёт подсказки для пользователя.
    :type state: FSMContext
    :type message: Message
    :param state: Состояние.
    :param message: Экземпляр сообщения
    """
    try:
        logging.debug(f"Получил текст. Пользователь с id {message.from_user.id}.")
        check = message.text
        current_state = await state.get_state()
        if current_state != IncomeSpendForm.value.state and current_state is not None:
            await message.delete()
            await message.answer(messages.error, parse_mode="MarkdownV2",
                                 reply_markup=inline_keybords.clear_inline)
        if check.replace('.', '', 1).isdigit() and current_state is not None:
            if float(message.text) > 0:
                pass
            else:
                await message.delete()
                await message.answer(messages.hint_message, parse_mode="MarkdownV2",
                                     reply_markup=inline_keybords.clear_inline)
        elif current_state is not None and current_state == IncomeSpendForm.value.state:
            await message.delete()
            await message.answer(messages.hint_message, parse_mode="MarkdownV2",
                                 reply_markup=inline_keybords.clear_inline)
        # Возобновляем форму, если бот завершался после того, как пользователь ввел /start.
        current_state = await state.get_state()
        if current_state is None:
            await message.answer(messages.repair_of_functional, parse_mode="MarkdownV2",
                                 reply_markup=inline_keybords.clear_inline)
            await IncomeSpendForm.value.set()
    except Exception as e:
        if e == "Message is too long":
            await message.answer("Это слишком большое сообщение для меня!", reply_markup=inline_keybords.clear_inline)
        else:
            logging.error(f"{on_all_not_command_message_handler.__name__}: {e}. "
                          f"Пользователь с id {message.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('previous_month'), state=IncomeSpendForm.date)
async def process_previous_month_button_handler(call: CallbackQuery) -> None:
    """
    Функция, реагирующая на нажатие на кнопку в календаре, переносящую на прошлый месяц, изменяет календарь.
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Пересоздаём календарь за предыдущий месяц. Пользователь с id {call.from_user.id}.")
        year, month = map(int, call.data.split(':')[1:])
        new_month = month - 1
        new_year = year
        if new_month < 1:
            new_month = 12
            new_year = year - 1
        keyboard = await inline_keybords.generate_calendar(new_year, new_month)
        await dp.bot.edit_message_reply_markup(call.message.chat.id,
                                               call.message.message_id,
                                               reply_markup=keyboard)
        await dp.bot.answer_callback_query(call.id)
        await call.answer()
    except Exception as e:
        logging.error(f"{process_previous_month_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('next_month'), state=IncomeSpendForm.date)
async def process_next_month_button_handler(call: CallbackQuery) -> None:
    """
    Функция, реагирующая на нажатие на кнопку в календаре, переносящую на следующий месяц, изменяет календарь.
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Пересоздаём календарь за следующий месяц. Пользователь с id {call.from_user.id}.")
        year, month = map(int, call.data.split(':')[1:])
        new_month = month + 1
        new_year = year
        if new_month > 12:
            new_month = 1
            new_year = year + 1
        keyboard = await inline_keybords.generate_calendar(new_year, new_month)
        await dp.bot.edit_message_reply_markup(call.message.chat.id,
                                               call.message.message_id,
                                               reply_markup=keyboard)
        await dp.bot.answer_callback_query(call.id)
        await call.answer()
    except Exception as e:
        logging.error(f"{process_next_month_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.is_spend.set()


@dp.callback_query_handler(text_contains='calendar:delete', state=IncomeSpendForm.date)
async def cancel_calendar_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор даты, возвращая в прошлое состояние с сохранением данных.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем выбор даты. Пользователь с id {call.from_user.id}.')
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(IncomeSpendForm.is_spend)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_calendar_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.is_spend)


@dp.callback_query_handler(text_contains='category:delete', state=IncomeSpendForm.category)
async def cancel_category_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор категории, возвращая в прошлое состояние с сохранением данных.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем выбор категории. Пользователь с id {call.from_user.id}.')
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(IncomeSpendForm.is_spend)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_category_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.is_spend)


@dp.callback_query_handler(text_contains='subcategory:delete', state=IncomeSpendForm.subcategory)
async def cancel_subcategory_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор подкатегории, возвращая в прошлое состояние с сохранением данных.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем выбор подкатегории. Пользователь с id {call.from_user.id}.')
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(IncomeSpendForm.is_spend)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_subcategory_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.is_spend)


@dp.callback_query_handler(state='*', text_contains="message:clear")
async def clear_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая удаляет сообщение по нажатию на кнопку.
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f'Скрываем сообщение. Пользователь с id {call.from_user.id}.')
        await call.message.delete()
        await call.answer("Скрыто!")
    except Exception as e:
        logging.error(f"{clear_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(state='*')
async def ignore_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая игнорирует нажатие на неактивные кнопки.
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f'Игнорируем кнопку. Пользователь с id {call.from_user.id}.')
        await call.answer("Недоступно! Завершите работу с текущим меню!")
    except Exception as e:
        logging.error(f"{ignore_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.value.set()
