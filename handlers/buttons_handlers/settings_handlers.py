import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

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
            reply_markup=await inline_keybords.generate_currency_choice_keyboard(currencies))
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


@dp.callback_query_handler(text_contains='settings:delete', state=SettingsForm.change_currency)
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
