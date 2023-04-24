import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

import helpers.helpers
from bot import dp
from config import config
from database import db_functions
from handlers.keyboards import inline_keybords
from handlers.models.settings_model import SettingsForm


@dp.callback_query_handler(text_contains='settings:change:currency', state=SettingsForm.start)
async def change_currency_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за смену текущей валюты.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Меняем валюту для пользователя. Пользователь с id {call.from_user.id}.')
        await SettingsForm.change_currency.set()
        currencies = []
        now_currency = await db_functions.get_user_currency(str(call.from_user.id))
        for cur in config.currency.keys():
            if cur != now_currency:
                currencies.append(cur)
        await call.message.answer(
            "Выберете валюту\, которую мы будем использовать\.\n*Внимание\: пересчитает все данные"
            " по текущему курсу валют\!*",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.generate_currency_choice_keyboard(currencies), disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{change_currency_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='settings:add:limit', state=SettingsForm.start)
async def change_limit_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за смену текущей валюты.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Меняем лимит для пользователя. Пользователь с id {call.from_user.id}.')
        await SettingsForm.change_limit.set()
        await call.message.answer(
            "Отправьте число\, которое представляет ваш лимит по средствам на месяц\.\n"
            "Пример: *30000* или *45000\.20*",
            parse_mode="MarkdownV2",
            reply_markup=inline_keybords.refuse_to_input, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{change_currency_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='settings:add:goal', state=SettingsForm.start)
async def change_goal_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за смену текущей валюты.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Меняем цель для пользователя. Пользователь с id {call.from_user.id}.')
        await SettingsForm.change_goal.set()
        await call.message.answer(
            "Отправьте число\, которое представляет вашу цель по сэкономленным средствам на месяц\.\n"
            "Пример: *30000* или *45000\.20*",
            parse_mode="MarkdownV2",
            reply_markup=inline_keybords.refuse_to_input, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{change_currency_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:currency:'),
                           state=SettingsForm.change_currency)
async def change_currency_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за смену текущей валюты.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Меняем валюту для пользователя. Пользователь с id {call.from_user.id}.')
        new_currency = call.data[16:]
        await call.message.delete()
        status = await db_functions.recount_values_in_new_currency(str(call.from_user.id), new_currency)
        if status:
            await call.answer(
                f"Смена валюты на {new_currency} прошла успешно!", )
        else:
            await call.answer(
                f"Проблема! Смена валюты на {new_currency} не удалась!", )
        await state.set_state(SettingsForm.start)
    except Exception as e:
        logging.error(f"{change_currency_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.answer(
            f"Ошибка при смене валюты!", )
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='settings:delete',
                           state=[SettingsForm.change_currency, SettingsForm.delete_event, SettingsForm.add_event,
                                  SettingsForm.delete_event_spend, SettingsForm.delete_event_income])
async def cancel_element_of_settings_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет действие в настройках, возвращая к старту.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем действие в настройках. Пользователь с id {call.from_user.id}.')
        await call.answer("Назад!")
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(SettingsForm.start)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_element_of_settings_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='input::stop', state=[SettingsForm.change_limit, SettingsForm.change_goal])
async def cancel_input_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет действие в настройках, возвращая к старту.
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем действие в настройках. Пользователь с id {call.from_user.id}.')
        await call.answer("Отменяем ввод!")
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(SettingsForm.start)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_input_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='settings:transfer:remainer', state=SettingsForm.start)
async def transfer_remainer_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за перенос остатка.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Переносим остаток с прошлого месяца для пользователя. Пользователь с id {call.from_user.id}.')
        status = await db_functions.transfer_remained_from_past_months(str(call.from_user.id))
        if status:
            await call.answer("Удалось перенести остаток!")
        else:
            await call.answer("Либо остаток неположительный, либо вы его уже переносили!")
    except Exception as e:
        logging.error(f"{transfer_remainer_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.message_handler(state=SettingsForm.change_limit)
async def process_sum_from_user_limit(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая работает со всеми сообщениями, в статусе изменения лимита.
    :param message: Экземпляр сообщения.
    :param state: Состояние.
    """
    try:
        is_value, value = await helpers.helpers.check_if_string_is_sum(message.text)
        print(value)
        if is_value:
            try:
                await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except Exception as e:
                logging.debug(e)
            await message.delete()
            status = await db_functions.set_limit(str(message.from_user.id), value)
            if status:
                await message.answer(f"Сумма: {value} успешно установлена как лимит!", disable_notification=True)
            else:
                await message.answer(f"Ну удалось установить {value} как лимит!", disable_notification=True)
            await SettingsForm.start.set()
        else:
            try:
                await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except Exception as e:
                logging.debug(e)
            await message.delete()
            await message.answer(
                "Ошибка, введите число по примеру или откажитесь от ввода\.\n"
                "Пример: *30000* или *45000\.20*",
                parse_mode="MarkdownV2",
                reply_markup=inline_keybords.refuse_to_input, disable_notification=True)
    except Exception as e:
        logging.error(f"{process_sum_from_user_limit.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await SettingsForm.start.set()


@dp.message_handler(state=SettingsForm.change_goal)
async def process_sum_from_user_goal(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая работает со всеми сообщениями, в статусе изменения цели.
    :param message: Экземпляр сообщения.
    :param state: Состояние.
    """
    try:
        is_value, value = await helpers.helpers.check_if_string_is_sum(message.text)
        print(value)
        if is_value:
            try:
                await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except Exception as e:
                logging.debug(e)
            await message.delete()
            status = await db_functions.set_goal(str(message.from_user.id), value)
            if status:
                await message.answer(f"Сумма: {value} успешно установлена как цель!", disable_notification=True)
            else:
                await message.answer(f"Ну удалось установить {value} как цель!", disable_notification=True)
            await SettingsForm.start.set()
        else:
            try:
                await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except Exception as e:
                logging.debug(e)
            await message.delete()
            await message.answer(
                "Ошибка, введите число по примеру или откажитесь от ввода\.\n"
                "Пример: *30000* или *45000\.20*",
                parse_mode="MarkdownV2",
                reply_markup=inline_keybords.refuse_to_input, disable_notification=True)
    except Exception as e:
        logging.error(f"{process_sum_from_user_goal.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await SettingsForm.start.set()


@dp.callback_query_handler(text_contains='settings:add:event', state=SettingsForm.start)
async def add_event_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за добавление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Добавляем событие. Пользователь с id {call.from_user.id}.')
        await SettingsForm.add_event.set()
        await call.message.answer(
            "Выберите\, какой тип события вы хотите добавить\?\n",
            parse_mode="MarkdownV2",
            reply_markup=inline_keybords.event_income_spend_inline, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{add_event_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='settings:delete:event', state=SettingsForm.start)
async def delete_event_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Удаляем событие. Пользователь с id {call.from_user.id}.')
        await SettingsForm.delete_event.set()
        await call.message.answer(
            "Выберите\, какой тип события вы хотите удалить\?\n",
            parse_mode="MarkdownV2",
            reply_markup=inline_keybords.event_income_spend_inline, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{delete_event_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='event:income', state=SettingsForm.delete_event)
async def delete_event_income_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Удаляем событие доходов. Пользователь с id {call.from_user.id}.')
        await SettingsForm.delete_event_income.set()
        data_dict = await db_functions.return_all_events_income(str(call.from_user.id))
        if len(data_dict.keys()) == 0:
            page = 0
        else:
            if len(data_dict.keys()) % 5 == 0:
                page = int(len(data_dict.keys()) / 5) - 1
            else:
                page = int(len(data_dict.keys()) / 5)
        if page < 0:
            page = 0
        await call.message.answer(
            "Выберите\, какое событие дохода хотите удалить\?\n",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_inline_keyboard_events(data_dict, page),
            disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{delete_event_income_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='event:spend', state=SettingsForm.delete_event)
async def delete_event_spend_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события траты.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Удаляем событие траты. Пользователь с id {call.from_user.id}.')
        await SettingsForm.delete_event_spend.set()
        data_dict = await db_functions.return_all_events_spends(str(call.from_user.id))
        if len(data_dict.keys()) == 0:
            page = 0
        else:
            if len(data_dict.keys()) % 5 == 0:
                page = int(len(data_dict.keys()) / 5) - 1
            else:
                page = int(len(data_dict.keys()) / 5)
        if page < 0:
            page = 0
        await call.message.answer(
            "Выберите\, какое событие траты хотите удалить\?\n",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_inline_keyboard_events(data_dict, page),
            disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{delete_event_spend_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='event:current_page:',
                           state=SettingsForm.delete_event_income)
async def change_page_income_handler(call: CallbackQuery) -> None:
    """
    Функция, которая перестраивает меню удаления доходов.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Переходи на другую страницу удаления события дохода. Пользователь с id {call.from_user.id}.")
        await call.answer()
        data_dict = await db_functions.return_all_events_income(str(call.from_user.id))
        page = call.data.split(':')
        page = int(page[2])
        keyboard = await inline_keybords.create_inline_keyboard_events(data_dict, page)
        await call.message.edit_text("Выберите\, какое событие дохода хотите удалить\?\n",
                                     parse_mode="MarkdownV2", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"{change_page_income_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await SettingsForm.start.set()


@dp.callback_query_handler(text_contains='event:current_page:',
                           state=SettingsForm.delete_event_spend)
async def change_page_spend_handler(call: CallbackQuery) -> None:
    """
    Функция, которая перестраивает меню удаления трат.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Переходи на другую страницу удаления трат. Пользователь с id {call.from_user.id}.")
        await call.answer()
        data_dict = await db_functions.return_all_events_spends(str(call.from_user.id))
        page = call.data.split(':')
        page = int(page[2])
        keyboard = await inline_keybords.create_inline_keyboard_events(data_dict, page)
        await call.message.edit_text("Выберите\, какое событие траты хотите удалить\?",
                                     parse_mode="MarkdownV2", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"{change_page_spend_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await SettingsForm.start.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('delete:event:'),
                           state=SettingsForm.delete_event_spend)
async def delete_event_spend_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку удаления события траты.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Удаляем событие траты. Пользователь с id {call.from_user.id}.")
        id_to_delete = call.data.split(':')
        id_to_delete = id_to_delete[2]
        status = await db_functions.delete_event_spend(str(call.from_user.id), id_to_delete)
        if status:
            await call.answer("Событие траты удалено!")
        else:
            await call.answer("Не удалось удалить событие траты!")
        await call.message.delete()
        await SettingsForm.start.set()
    except Exception as e:
        logging.error(f"{delete_event_spend_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.answer("Произошла непредвиденная ошибка, попробуйте удалить доход снова!")
        await call.message.delete()
        await SettingsForm.start.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('delete:event:'),
                           state=SettingsForm.delete_event_income)
async def delete_event_income_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку удаления события дохода.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Удаляем событие дохода. Пользователь с id {call.from_user.id}.")
        id_to_delete = call.data.split(':')
        id_to_delete = id_to_delete[2]
        status = await db_functions.delete_event_income(str(call.from_user.id), id_to_delete)
        if status:
            await call.answer("Событие дохода удалено!")
        else:
            await call.answer("Не удалось удалить событие траты!")
        await call.message.delete()
        await SettingsForm.start.set()
    except Exception as e:
        logging.error(f"{delete_event_income_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.answer("Произошла непредвиденная ошибка, попробуйте удалить доход снова!")
        await call.message.delete()
        await SettingsForm.start.set()
