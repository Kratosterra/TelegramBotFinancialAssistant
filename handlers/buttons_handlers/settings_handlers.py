import logging
import re

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
                                  SettingsForm.delete_event_spend, SettingsForm.delete_event_income,
                                  SettingsForm.event_menu])
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


@dp.callback_query_handler(text_contains='input::stop',
                           state=[SettingsForm.change_limit, SettingsForm.change_goal, SettingsForm.value])
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
                await message.answer(f"Сумма: {value} успешно установлена как лимит!", disable_notification=True,
                                     reply_markup=inline_keybords.clear_inline)
            else:
                await message.answer(f"Не удалось установить {value} как лимит!", disable_notification=True,
                                     reply_markup=inline_keybords.clear_inline)
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
                await message.answer(f"Сумма: {value} успешно установлена как цель!", disable_notification=True,
                                     reply_markup=inline_keybords.clear_inline)
            else:
                await message.answer(f"Не удалось установить {value} как цель!", disable_notification=True,
                                     reply_markup=inline_keybords.clear_inline)
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


@dp.callback_query_handler(text_contains='event:income', state=SettingsForm.add_event)
async def add_event_income_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Удаляем событие доходов. Пользователь с id {call.from_user.id}.')
        await state.update_data(isSpend=False)
        await SettingsForm.value.set()
        await call.message.answer(
            "Отправьте число\, которое представляет средства, которые будут добавляться в бюджет\.\n"
            "Пример: *30000* или *45000\.20*",
            parse_mode="MarkdownV2",
            reply_markup=inline_keybords.refuse_to_input, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{add_event_income_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='event:spend', state=SettingsForm.add_event)
async def add_event_spend_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Добавляем событие трат. Пользователь с id {call.from_user.id}.')
        await state.update_data(isSpend=True)
        await SettingsForm.value.set()
        await call.message.answer(
            "Отправьте число\, которое представляет средства, которые будут учтены как траты в бюджет\.\n"
            "Пример: *30000* или *45000\.20*",
            parse_mode="MarkdownV2",
            reply_markup=inline_keybords.refuse_to_input, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{add_event_spend_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.message_handler(state=SettingsForm.value)
async def process_sum_from_user_event(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая работает со всеми сообщениями, в статусе изменения цели.
    :param message: Экземпляр сообщения.
    :param state: Состояние.
    """
    try:
        is_value, value = await helpers.helpers.check_if_string_is_sum(message.text)
        if is_value:
            try:
                await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except Exception as e:
                logging.debug(e)
            await message.delete()
            await state.update_data(value=value)
            await SettingsForm.event_menu.set()
            if (await state.get_data())['isSpend']:
                await message.answer(
                    f"Событие траты на {value} {await db_functions.get_user_currency(str(message.from_user.id))}\n"
                    "Обязательно добавьте имя и день события!",
                    reply_markup=inline_keybords.spend_event_inline, disable_notification=True)
            else:
                await message.answer(
                    f"Событие дохода на {value} {await db_functions.get_user_currency(str(message.from_user.id))}\n"
                    "Обязательно добавьте имя и день события!",
                    reply_markup=inline_keybords.income_event_inline, disable_notification=True)
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
        logging.error(f"{process_sum_from_user_event.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await SettingsForm.start.set()


@dp.callback_query_handler(text_contains='name:event', state=SettingsForm.event_menu)
async def add_name_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку имени, отправляя запрос на предоставление имени суммы.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Изменяем имя. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await SettingsForm.name.set()
        await call.message.answer("Отправьте имя суммы события.", reply_markup=inline_keybords.refuse_to_input,
                                  disable_notification=True)
    except Exception as e:
        logging.error(f"{add_name_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await SettingsForm.event_menu.set()


@dp.message_handler(state=SettingsForm.name)
async def add_name_message_handler(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая реагирует на отправление любого сообщения, после нажатия на кнопку добавления имени.
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
            await SettingsForm.name.set()
        else:
            await message.delete()
            name = str(message.text)
            name = re.sub(r'[^\w\s]', '', name)
            if (await state.get_data())['isSpend']:
                if name in (await db_functions.return_all_events_spends(str(message.from_user.id))):
                    await message.answer(
                        "Имя суммы не должно быть уже использовано в событии трат!",
                        reply_markup=inline_keybords.refuse_to_input)
                    await SettingsForm.name.set()
                    return
            else:
                if name in (await db_functions.return_all_events_income(str(message.from_user.id))):
                    await message.answer(
                        "Имя суммы не должно быть уже использовано в событии дохода!",
                        reply_markup=inline_keybords.refuse_to_input)
                    await SettingsForm.name.set()
                    return
            if len(name) < 3:
                await message.answer(
                    "Имя суммы не должно быть меньше 3 символов, повторите ввод, снова отправьте имя)",
                    reply_markup=inline_keybords.refuse_to_input)
                await SettingsForm.name.set()
                return
            await state.update_data(name=name)
            await message.answer(f"Имя: {name} установлено!", disable_notification=True,
                                 reply_markup=inline_keybords.clear_inline)
            await SettingsForm.event_menu.set()
    except Exception as e:
        logging.error(f"{add_name_message_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await message.delete()
        await message.answer("Произошла непредвиденная ошибка, попробуйте изменить имя снова!",
                             reply_markup=inline_keybords.refuse_to_input)
        await SettingsForm.event_menu.set()


@dp.callback_query_handler(text_contains='input::stop', state=[SettingsForm.date, SettingsForm.name])
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
        await state.set_state(SettingsForm.event_menu)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_input_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='delete', state=[SettingsForm.category, SettingsForm.subcategory])
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
        await state.set_state(SettingsForm.event_menu)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_input_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='day:event', state=SettingsForm.event_menu)
async def add_day_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку имени, отправляя запрос на предоставление имени суммы.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Добавляем день событию. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await SettingsForm.date.set()
        await call.message.answer("Выберете день, в который будет происходить событие:",
                                  reply_markup=await inline_keybords.get_day_choice_keyboard(),
                                  disable_notification=True)
    except Exception as e:
        logging.error(f"{add_day_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await SettingsForm.event_menu.set()


@dp.callback_query_handler(text_contains='choice:day:', state=SettingsForm.date)
async def on_day_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Получаем день для события. Пользователь с id {call.from_user.id}.')
        day = call.data.split(':')
        day = int(day[2])
        await call.answer(f"Событие установлено на {day} число!")
        await state.update_data(date=day)
        await SettingsForm.event_menu.set()
    except Exception as e:
        logging.error(f"{on_day_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='proceed:event', state=SettingsForm.event_menu)
async def on_day_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Подтверждаем событие. Пользователь с id {call.from_user.id}.')
        main_data = await state.get_data()
        if 'name' not in main_data.keys() or 'date' not in main_data.keys():
            await call.answer(f"Установите имя и дату события!")
            await SettingsForm.event_menu.set()
            return
        value = main_data['value']
        name = main_data['name']
        date = main_data['date']
        if not main_data['isSpend']:
            st = await db_functions.add_event_income(user_id=str(call.from_user.id), value=value, name=name,
                                                     day_of_income=date)
        else:
            category = None
            subcategory = None
            if 'category' in main_data.keys():
                category = (await state.get_data())['category']
            if 'subcategory' in main_data.keys():
                subcategory = (await state.get_data())['subcategory']
            st = await db_functions.add_event_spend(user_id=str(call.from_user.id), category=category,
                                                    subcategory=subcategory, value=value, name=name,
                                                    day_of_spending=date)
        await call.message.delete()
        if st:
            await call.answer(f"Добавление завершено успешно!")
        else:
            await call.answer(f"Добавление не завершено, повторите попытку!")
        await state.finish()
        await SettingsForm.start.set()
    except Exception as e:
        logging.error(f"{on_day_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(SettingsForm.start)


@dp.callback_query_handler(text_contains='category:event', state=SettingsForm.event_menu)
async def send_category_picker(call: CallbackQuery) -> None:
    """
    Функция, которая отвечает за обработку нажатия на кнопку категории, отсылая сообщение с кнопками для выбора.
    :param call: Вызов от кнопки.
    """
    try:
        logging.debug(f"Отправляем сообщение с кнопками для выбора категории. Пользователь с id {call.from_user.id}.")
        categories_raw = await db_functions.return_all_categories(str(call.from_user.id))
        categories = list(categories_raw.keys())
        keyboard = await inline_keybords.generate_category_keyboard(categories)
        await SettingsForm.category.set()
        if len(categories) == 0:
            await call.message.answer("У вас нет категорий, добавьте их в настройках.", reply_markup=keyboard,
                                      disable_notification=True)
        else:
            await call.message.answer("Выберите категорию:", reply_markup=keyboard, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{send_category_picker.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await SettingsForm.event_menu.set()


@dp.callback_query_handler(text_contains='sub:event', state=SettingsForm.event_menu)
async def send_sub_category_picker(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за обработку нажатия на кнопку подкатегории, отсылая сообщение для выбора.
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
                await call.message.answer("Выберете подкатегорию:",
                                          reply_markup=keyboard, disable_notification=True)
            else:
                keyboard = await inline_keybords.generate_subcategory_keyboard([])
                await call.message.answer("Сначала добавьте подкатегории в свою категорию:",
                                          reply_markup=keyboard, disable_notification=True)
        await call.answer()
        await SettingsForm.subcategory.set()
    except Exception as e:
        logging.error(f"{send_sub_category_picker.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await SettingsForm.event_menu.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:category:'), state=SettingsForm.category)
async def add_category_message_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на выбор категории кнопкой, добавляя информацию в состояние.
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
        await SettingsForm.event_menu.set()
    except Exception as e:
        logging.error(f"{add_category_message_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.answer("Произошла непредвиденная ошибка, попробуйте присвоить категорию снова!")
        await call.message.delete()
        await SettingsForm.event_menu.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:subcategory:'),
                           state=SettingsForm.subcategory)
async def add_subcategory_message_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на выбор подкатегории кнопкой, добавляя информацию в состояние.
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Получаем подкатегорию. Пользователь с id {call.from_user.id}.")
        category = call.data[19:]
        await call.message.delete()
        await state.update_data(subcategory=str(category))
        await call.answer(f"Подкатегория: {category} установлена!")
        await SettingsForm.event_menu.set()
    except Exception as e:
        logging.error(f"{add_subcategory_message_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.answer("Произошла непредвиденная ошибка, попробуйте присвоить категорию снова!")
        await SettingsForm.event_menu.set()
