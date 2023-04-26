import datetime
import logging
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

import helpers.helpers
from bot import dp
from config import config
from database import db_functions
from helpers import report
from handlers.keyboards import inline_keybords
from handlers.models.report_model import ReportForm
from handlers.models.income_spend_model import IncomeSpendForm


@dp.callback_query_handler(text_contains='report:small', state=[ReportForm.start])
async def small_report_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет действие в настройках, возвращая к старту.
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f'Получаем маленький отчет. Пользователь с id {call.from_user.id}.')
        await ReportForm.small_report.set()
        await call.message.answer(
            f"📄 *Краткий отчет*\n{await report.get_small_text_report(str(call.from_user.id), datetime.date.today())}",
            parse_mode="MarkdownV2")
        await state.set_state(IncomeSpendForm.value)
    except Exception as e:
        logging.error(f"{small_report_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)
