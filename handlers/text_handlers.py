import logging
import time
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from bot import dp
from database import db_functions
from handlers.keyboards import inline_keybords
from handlers.models.income_spend_model import IncomeSpendForm
from texts.ru_RU import messages


@dp.message_handler(lambda message: message.text.replace('.', '', 1).isdigit() and float(message.text) > 0,
                    state=IncomeSpendForm.value)
async def process_sum_from_user(message: types.Message, state: FSMContext):
    try:
        await IncomeSpendForm.next()
        if float(message.text) > 1000000000000 or float(message.text) < 0.01:
            await message.answer("Это уже слишком для меня!")
            await IncomeSpendForm.value.set()
            return
        await state.update_data(value=round(float(message.text), 2))
        await message.answer(
            f"Сумма: {round(float(message.text), 2)} {await db_functions.get_user_currency(str(message.from_user.id))}",
            reply_markup=inline_keybords.income_spend_inline)
    except Exception as e:
        if e == "Message is too long":
            await message.answer("Это слишком большое сообщение для меня!")
        else:
            logging.error(f"{process_sum_from_user.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='income:income_spend_sum', state='*')
async def activate_adding_income(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        logging.debug(f"Начинаем добавлять доход. Пользователь с id {call.message.from_user.id}.")
        await call.message.delete()
        await state.update_data(isSpend=False)
        await call.message.answer(
            f"Доход {(await state.get_data())['value']} {await db_functions.get_user_currency(str(call.from_user.id))}",
            reply_markup=inline_keybords.income_sum_inline)
    except Exception as e:
        logging.error(f"{activate_adding_income.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='spend:income_spend_sum', state='*')
async def activate_adding_spend(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        logging.debug(f"Начинаем добавлять трату. Пользователь с id {call.message.from_user.id}.")
        await call.message.delete()
        await state.update_data(isSpend=True)
        await call.message.answer(
            f"Добавляем трату {(await state.get_data())['value']} {await db_functions.get_user_currency(str(call.from_user.id))}",
            reply_markup=inline_keybords.spend_sum_inline)
    except Exception as e:
        logging.error(f"{activate_adding_spend.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='change_date:sum', state=IncomeSpendForm.isSpend)
async def send_date_picker(call: CallbackQuery):
    try:
        await call.answer()
        year = datetime.now().year
        month = datetime.now().month
        # генерируем inline клавиатуру для текущего месяца
        calendar_keyboard = await inline_keybords.generate_calendar(year, month)
        # отправляем сообщение с клавиатурой
        await IncomeSpendForm.date.set()
        await call.message.answer("Выберите дату:", reply_markup=calendar_keyboard)
    except Exception as e:
        logging.error(f"{send_date_picker.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")
        await IncomeSpendForm.isSpend.set()


@dp.callback_query_handler(text_contains='category:spend_sum', state=IncomeSpendForm.isSpend)
async def send_category_picker(call: CallbackQuery):
    try:
        await call.answer()
        # генерируем inline клавиатуру для текущего месяца
        categories_raw = await db_functions.return_all_categories(str(call.from_user.id))
        categories = list(categories_raw.keys())
        keyboard = await inline_keybords.generate_category_keyboard(categories)
        # отправляем сообщение с клавиатурой
        await IncomeSpendForm.category.set()
        if len(categories) == 0:
            await call.message.answer("У вас нет категорий, добавьте их в настройках.", reply_markup=keyboard)
        else:
            await call.message.answer("Выберите категорию:", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"{send_category_picker.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.isSpend.set()


@dp.callback_query_handler(text_contains='sub:spend_sum', state=IncomeSpendForm.isSpend)
async def send_sub_category_picker(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        # генерируем inline клавиатуру для текущего месяца
        categories_raw = await db_functions.return_all_categories(str(call.from_user.id))
        data = await state.get_data()
        if 'category' not in data.keys():
            keyboard = await inline_keybords.generate_subcategory_keyboard([])
            await call.message.answer("Выберете категорию для того, чтобы добавлять подкатегорию.",
                                      reply_markup=keyboard)
        else:
            if data['category'] in categories_raw.keys() and len(categories_raw[data['category']]) > 0:
                keyboard = await inline_keybords.generate_subcategory_keyboard(categories_raw[data['category']])
                await call.message.answer("Выберете подкатегорию:",
                                          reply_markup=keyboard)
            else:
                keyboard = await inline_keybords.generate_subcategory_keyboard([])
                await call.message.answer("Сначала добавьте подкатегории в свою категорию:",
                                          reply_markup=keyboard)
        # отправляем сообщение с клавиатурой
        await IncomeSpendForm.subcategory.set()
    except Exception as e:
        logging.error(f"{send_category_picker.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.isSpend.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:category:'), state=IncomeSpendForm.category)
async def add_category_message_handler(call: CallbackQuery, state: FSMContext):
    try:
        logging.debug(f"Получаем категорию. Пользователь с id {call.from_user.id}.")
        category = call.data[16:]
        await call.message.delete()
        await state.update_data(category=str(category))
        await state.update_data(subcategory=None)
        await call.message.answer(f"Категория: {category} установлена! Подкатегория сброшена!")
        await IncomeSpendForm.isSpend.set()
    except Exception as e:
        logging.error(f"{add_category_message_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте присвоить категорию снова!")
        await IncomeSpendForm.isSpend.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:subcategory:'),
                           state=IncomeSpendForm.subcategory)
async def add_category_message_handler(call: CallbackQuery, state: FSMContext):
    try:
        logging.debug(f"Получаем подкатегорию. Пользователь с id {call.from_user.id}.")
        category = call.data[19:]
        await call.message.delete()
        await state.update_data(subcategory=str(category))
        await call.message.answer(f"Подкатегория: {category} установлена!")
        await IncomeSpendForm.isSpend.set()
    except Exception as e:
        logging.error(f"{add_category_message_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте присвоить категорию снова!")
        await IncomeSpendForm.isSpend.set()


@dp.callback_query_handler(text_contains='proceed:sum', state=IncomeSpendForm.isSpend)
async def proceed_handler(call: CallbackQuery, state: FSMContext):
    try:
        logging.debug(f"Добавляем информацию. Пользователь с id {call.from_user.id}.")
        await call.answer()
        logging.debug(await state.get_data())
        value = (await state.get_data())['value']
        name = None
        date = None
        if 'date' in (await state.get_data()).keys():
            date = (await state.get_data())['date']
        if 'name' in (await state.get_data()).keys():
            name = (await state.get_data())['name']
        if not (await state.get_data())['isSpend']:
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
            await call.message.answer(f"Добавление завершено успешно!")
        else:
            await call.message.answer(f"Добавление не завершено, повторите попытку!")
        await state.finish()
        await IncomeSpendForm.value.set()
    except Exception as e:
        logging.error(f"{proceed_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.answer("При добавлении произошла ошибка, попробуйте еще раз! Нажав 'Отмена'")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='name:sum', state=IncomeSpendForm.isSpend)
async def add_name_handler(call: CallbackQuery, state: FSMContext):
    try:
        logging.debug(f"Изменяем имя. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await IncomeSpendForm.name.set()
        await call.message.answer("Отправьте имя суммы.")
    except Exception as e:
        logging.error(f"{add_name_handler.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")
        await IncomeSpendForm.isSpend.set()


@dp.message_handler(state=IncomeSpendForm.name)
async def add_name_message_handler(message: types.Message, state: FSMContext):
    try:
        try:
            await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        except Exception as e:
            logging.debug(e)
        logging.debug(f"Получаем имя. Пользователь с id {message.from_user.id}.")
        if len(message.text) > 75:
            await message.delete()
            await message.answer("Имя суммы не должно быть больше 75 символов, повторите ввод имени в чате."
                                 " То есть, снова отправьте имя)")
            await IncomeSpendForm.name.set()
        else:
            await message.delete()
            await state.update_data(name=str(message.text))
            await message.answer(f"Имя: {str(message.text)} установлено!")
            await IncomeSpendForm.isSpend.set()
    except Exception as e:
        logging.error(f"{add_name_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await message.delete()
        await message.answer("Произошла непредвиденная ошибка, попробуйте изменить имя снова!")
        await IncomeSpendForm.isSpend.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('date:'), state=IncomeSpendForm.date)
async def add_date_message_handler(call: CallbackQuery, state: FSMContext):
    try:
        logging.debug(f"Получаем дату. Пользователь с id {call.from_user.id}.")
        year, month, day = map(int, call.data.split(':')[1:])
        data = datetime(year, month, day).strftime("%Y-%m-%d")
        await call.message.delete()
        await state.update_data(date=str(data))
        await call.message.answer(f"Дата: {data} установлена!")
        await IncomeSpendForm.isSpend.set()
    except Exception as e:
        logging.error(f"{add_name_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте изменить дату снова!")
        await IncomeSpendForm.isSpend.set()


@dp.callback_query_handler(text_contains='cancel', state='*')
async def cancel_handler(call: CallbackQuery, state: FSMContext):
    """
    Позволяет пользователю завершить любое действие.
    """
    try:
        await call.answer()
        current_state = await state.get_state()
        if current_state is None:
            await IncomeSpendForm.value.set()
            return
        logging.debug(f'Отменяем состояние {current_state}. Пользователь с id {call.message.from_user.id}.')
        await state.finish()
        await call.message.delete()
        await call.message.answer('Отмена!')
        await IncomeSpendForm.value.set()
    except Exception as e:
        logging.error(f"{cancel_handler.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='ignore', state='*')
async def ignore_handler(call: CallbackQuery, state: FSMContext):
    try:
        logging.debug(f'Игнорируем кнопку. Пользователь с id {call.message.from_user.id}.')
        await call.answer()
    except Exception as e:
        logging.error(f"{ignore_handler.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.message_handler(content_types=['text'], state='*')
async def on_all_not_command_message(message: types.Message, state: FSMContext) -> None:
    """
    Функция, отвечающая за запуск действий с текстом, отправленным пользователем
    :param message: экземпляр сообщения
    """
    try:
        logging.debug(f"Получил текст. Пользователь с id {message.from_user.id}.")
        await db_functions.execute_events(str(message.from_user.id))
        check = message.text
        if check.replace('.', '', 1).isdigit():
            if float(message.text) > 0:
                current_state = await state.get_state()
                if current_state is not None:
                    await message.delete()
                    # await message.answer(messages.error, parse_mode="MarkdownV2")
            else:
                await message.delete()
                # await message.answer(messages.hint_message, parse_mode="MarkdownV2", )
        else:
            await message.delete()
            # await message.answer(messages.hint_message, parse_mode="MarkdownV2")
        # Возобновляем форму, если бот завершался после того, как пользователь ввел /start.
        current_state = await state.get_state()
        if current_state is None:
            await message.answer(messages.repair_of_functional, parse_mode="MarkdownV2")
            await IncomeSpendForm.value.set()
    except Exception as e:
        if e == "Message is too long":
            await message.answer("Это слишком большое сообщение для меня!")
        else:
            logging.error(f"{on_all_not_command_message.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('previous_month'), state=IncomeSpendForm.date)
async def process_previous_month_callback(callback_query: CallbackQuery):
    # Получаем год и месяц из callback_data
    year, month = map(int, callback_query.data.split(':')[1:])
    new_month = month - 1
    new_year = year
    if new_month < 1:
        new_month = 12
        new_year = year - 1
    keyboard = await inline_keybords.generate_calendar(new_year, new_month)
    await dp.bot.edit_message_reply_markup(callback_query.message.chat.id,
                                           callback_query.message.message_id,
                                           reply_markup=keyboard)

    await dp.bot.answer_callback_query(callback_query.id)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('next_month'), state=IncomeSpendForm.date)
async def process_next_month_callback(callback_query: CallbackQuery):
    year, month = map(int, callback_query.data.split(':')[1:])
    new_month = month + 1
    new_year = year
    if new_month > 12:
        new_month = 1
        new_year = year + 1
    keyboard = await inline_keybords.generate_calendar(new_year, new_month)
    await dp.bot.edit_message_reply_markup(callback_query.message.chat.id,
                                           callback_query.message.message_id,
                                           reply_markup=keyboard)
    await dp.bot.answer_callback_query(callback_query.id)
    await callback_query.answer()


@dp.callback_query_handler(text_contains='calendar:delete', state=IncomeSpendForm.date)
async def cancel_calendar_handler(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        logging.debug(f'Отменяем выбор даты. Пользователь с id {call.message.from_user.id}.')
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(IncomeSpendForm.isSpend)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_handler.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")
        await state.set_state(IncomeSpendForm.isSpend)


@dp.callback_query_handler(text_contains='category:delete', state=IncomeSpendForm.category)
async def cancel_category_handler(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        logging.debug(f'Отменяем выбор категории. Пользователь с id {call.message.from_user.id}.')
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(IncomeSpendForm.isSpend)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_category_handler.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")
        await state.set_state(IncomeSpendForm.isSpend)


@dp.callback_query_handler(text_contains='subcategory:delete', state=IncomeSpendForm.subcategory)
async def cancel_subcategory_handler(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        logging.debug(f'Отменяем выбор подкатегории. Пользователь с id {call.message.from_user.id}.')
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(IncomeSpendForm.isSpend)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_subcategory_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.isSpend)
