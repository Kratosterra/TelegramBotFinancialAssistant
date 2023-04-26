import datetime
import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from bot import dp
from handlers.keyboards import inline_keybords
from handlers.models.income_spend_model import IncomeSpendForm
from handlers.models.report_model import ReportForm
from helpers import report


@dp.callback_query_handler(text_contains='report:small', state=[ReportForm.start])
async def small_report_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет действие в настройках, возвращая к старту.
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Получаем маленький отчет. Пользователь с id {call.from_user.id}.')
        await ReportForm.small_report.set()
        now = datetime.date.today()
        await call.message.answer(
            f"📄 *Краткий отчет*\n{await report.get_small_text_report(str(call.from_user.id), datetime.date.today())}",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_report_keyboard_small(now))
    except Exception as e:
        logging.error(f"{small_report_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)


@dp.callback_query_handler(text_contains='more:', state=ReportForm.small_report)
async def expand_small_report_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Делаем маленький отчет подробнее. Пользователь с id {call.from_user.id}.')
        date = call.data.split(':')
        now = datetime.datetime.strptime(date[1], "%Y-%m-%d")
        await call.message.edit_text(
            f"📄 *Краткий отчет*\n{await report.get_small_text_report(str(call.from_user.id), now, True)}",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_report_keyboard_small(now, False))
        await call.answer()
    except Exception as e:
        logging.error(f"{expand_small_report_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)


@dp.callback_query_handler(text_contains='less:', state=ReportForm.small_report)
async def expand_small_report_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Делаем маленький отчет менее подробным. Пользователь с id {call.from_user.id}.')
        date = call.data.split(':')
        now = datetime.datetime.strptime(date[1], "%Y-%m-%d")
        await call.message.edit_text(
            f"📄 *Краткий отчет*\n{await report.get_small_text_report(str(call.from_user.id), now)}",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_report_keyboard_small(now))
        await call.answer()
    except Exception as e:
        logging.error(f"{expand_small_report_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)


@dp.callback_query_handler(text_contains='change:', state=ReportForm.small_report)
async def change_small_report_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за удаление события.
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Меняем маленький отчет менее подробным. Пользователь с id {call.from_user.id}.')
        date = call.data.split(':')
        now = datetime.datetime.strptime(date[1], "%Y-%m-%d")
        await call.message.edit_text(
            f"📄 *Краткий отчет*\n{await report.get_small_text_report(str(call.from_user.id), now)}",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_report_keyboard_small(now))
        await call.answer()
    except Exception as e:
        logging.error(f"{change_small_report_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)
