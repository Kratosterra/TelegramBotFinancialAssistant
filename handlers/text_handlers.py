import logging
import time

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
        await state.update_data(value=float(message.text))
        await message.answer(
            f"Сумма: {message.text} {await db_functions.get_user_currency(str(message.from_user.id))}",
            reply_markup=inline_keybords.income_spend_inline)
    except Exception as e:
        logging.error(f"{process_sum_from_user.__name__}: {e}. Пользователь с id {message.from_user.id}.")


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
                    await message.answer(messages.error, parse_mode="MarkdownV2")
            else:
                await message.delete()
                await message.answer(messages.hint_message, parse_mode="MarkdownV2")
        else:
            await message.answer(messages.hint_message, parse_mode="MarkdownV2")
        # Возобновляем форму, если бот завершался после того, как пользователь ввел /start.
        current_state = await state.get_state()
        if current_state is None:
            await message.answer(messages.repair_of_functional, parse_mode="MarkdownV2")
            await IncomeSpendForm.value.set()
    except Exception as e:
        logging.error(f"{on_all_not_command_message.__name__}: {e}. Пользователь с id {message.from_user.id}.")


@dp.callback_query_handler(text_contains='income:income_spend_sum', state=IncomeSpendForm.isSpend)
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


@dp.callback_query_handler(text_contains='spend:income_spend_sum', state=IncomeSpendForm.isSpend)
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


@dp.callback_query_handler(text_contains='proceed:sum', state='*')
async def proceed_handler(call: CallbackQuery, state: FSMContext):
    """
    Позволяет пользователю завершить любое действие.
    """
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
                await db_functions.add_income(user_id=str(call.from_user.id), value=value, name=name,
                                              date=time.strftime("%Y-%m-%d", time.gmtime()))
            else:
                await db_functions.add_income(user_id=str(call.from_user.id), value=value, name=name, date=date)
        else:
            category = None
            subcategory = None
            if 'category' in (await state.get_data()).keys():
                category = (await state.get_data())['category']
            if 'subcategory' in (await state.get_data()).keys():
                subcategory = (await state.get_data())['subcategory']
            if date is None:
                await db_functions.add_spend(user_id=str(call.from_user.id), value=value, name=name, category=category,
                                             subcategory=subcategory,
                                             date=time.strftime("%Y-%m-%d", time.gmtime()))
            else:
                await db_functions.add_spend(user_id=str(call.from_user.id), category=category,
                                             subcategory=subcategory, value=value, name=name, date=date)
        await call.message.delete()
        await call.message.answer("Добавление завершено!")
        await state.finish()
        await IncomeSpendForm.value.set()
    except Exception as e:
        logging.error(f"{proceed_handler.__name__}: {e}. Пользователь с id {call.message.from_user.id}.")


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
