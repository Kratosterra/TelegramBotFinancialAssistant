import datetime
import logging
import os

import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

from database import db_functions
from texts.ru_RU import messages


def _get_past_months_from_date(date: datetime) -> list:
    """
    Возвращает лист размера 2, с первой датой прошлого месяца и последней датой прошлого месяца
    :return: Лист из двух datetime.
    """
    today = date
    first_day_prev_month = datetime.date(today.year, today.month, 1)
    first_day_prev_month += relativedelta(months=-1)
    last_day_prev_month = first_day_prev_month.replace(day=28) + datetime.timedelta(days=4)
    last_day_prev_month = last_day_prev_month - datetime.timedelta(days=last_day_prev_month.day)
    return [first_day_prev_month, last_day_prev_month]


async def get_small_text_report(user_id: str, date: datetime, need_subcategories: bool = False) -> str:
    """
    Функция, которая получает строку с представлением отчёта в строке.
    :param user_id: ID пользователя Telegram.
    :param date: Дата, с которой следует делать отчёт.
    :param need_subcategories: Нужны ли подкатегории.
    :return: Строку с представлением отчёта для сообщения.
    """
    string = "*Ошибка*"
    try:
        currency = await db_functions.get_user_currency(user_id)
        start = datetime.date(date.year, date.month, 1)
        end = start.replace(day=28) + datetime.timedelta(days=4)
        end = end - datetime.timedelta(days=end.day)
        string = f"{await _get_day_string(start)}\n\n" \
                 f"{await _get_better_string(user_id, start, end)}\n" \
                 f"{await _get_income_string(user_id, currency, start, end)}\n" \
                 f"{await _get_spend_string(user_id, currency, start, end)}\n\n" \
                 f"{await _get_categories_report(user_id, currency, start, end, need_subcategories)}"
        if len(string) > 3900:
            return "\.\.\. *Воспользуйтесь отчетом \.xlsx*"
    except Exception as e:
        logging.error(f"{get_small_text_report.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def _get_categories_report(user_id: str, currency: str, start: datetime, end: datetime,
                                 need_subcategories: bool) -> str:
    """
    Функция, которая получает строковое представления отчёта по тратам в категориях.
    :param user_id: ID пользователя Telegram.
    :param currency: Строковое представление валюты.
    :param start: Начало периода отчёта.
    :param end: Конец периода отчёта.
    :param need_subcategories: Нужны ли подкатегории.
    :return:
    """
    data = await db_functions.get_spends_of_user_by_categories(user_id, start, end)
    string = "*По категориям трат:*\n\n"
    for category in data.keys():
        if category == "$no_category":
            all_data = str(round(data[category]['$all'], 2)).replace('.', '\.')
            string += f"*Без категории*: _{all_data}_ {currency}\n\n"
            continue
        all_data = str(round(data[category]['$all'], 2)).replace('.', '\.')
        no_category = str(round(data[category]['$no_subcategory'], 2)).replace('.', '\.')
        if need_subcategories:
            string += f"*{category}*: _{all_data}_ {currency}\n\t\> _Без подкатегории_: {no_category} {currency}\n"
        else:
            string += f"*{category}*: _{all_data}_ {currency}\n"
        if need_subcategories:
            for sub_category in (data[category].keys()):
                if sub_category == "$all" or sub_category == "$no_subcategory":
                    continue
                now = str(round(data[category][sub_category], 2)).replace('.', '\.')
                string += f"\t\> _{sub_category}_: {now} {currency}\n"
        string += "\n"
    return string


async def _get_better_string(user_id: str, start: datetime, end: datetime) -> str:
    """
    Функция, которая возвращает строку с представлением сравнения трат и доходов с прошлым месяцем.
    :param user_id: ID пользователя Telegram.
    :param start: Начало периода отчёта.
    :param end: Конец периода отчёта.
    :return: Строку с представлением сравнения.
    """
    list_dates_past = _get_past_months_from_date(start)
    now_spends = await db_functions.return_sum_spend(user_id, start, end)
    past_spends = await db_functions.return_sum_spend(user_id, list_dates_past[0], list_dates_past[1])
    now_incomes = await db_functions.return_sum_income(user_id, start, end)
    past_incomes = await db_functions.return_sum_income(user_id, list_dates_past[0], list_dates_past[1])

    if past_spends != 0:
        spend_ratio = now_spends / past_spends
    else:
        spend_ratio = 1
    if past_incomes != 0:
        incomes_ratio = now_incomes / past_incomes
    else:
        incomes_ratio = 1

    if spend_ratio >= 1:
        spend_ratio -= 1
        spend_percent = str(round(spend_ratio * 100, 2)).replace('.', '\.')
        spend_string = f"*\+ {spend_percent}\%*"
    else:
        spend_ratio = 1 - spend_ratio
        spend_percent = str(round(spend_ratio * 100, 2)).replace('.', '\.')
        spend_string = f"*\- {spend_percent}\%*"

    if incomes_ratio >= 1:
        incomes_ratio -= 1
        incomes_percent = str(round(incomes_ratio * 100, 2)).replace('.', '\.')
        income_string = f"*\+ {incomes_percent}\%*"
    else:
        incomes_ratio = 1 - incomes_ratio
        incomes_percent = str(round(incomes_ratio * 100, 2)).replace('.', '\.')
        income_string = f"*\- {incomes_percent}\%*"
    return f"_По сравнению с прошлым месяцем:_\n📈 Доходы\: {income_string}\n📉 Траты\: {spend_string}\n"


async def _get_day_string(start: datetime) -> str:
    """
    Функция, которая возвращает строковое представление даты в виде месяца и года.
    :param start: Начало периода отчёта.
    :return: Строка даты.
    """
    year = start.year
    month = messages.months[int(start.month)]
    return f"\n_За *{month} {year}*_"


async def _get_income_string(user_id: str, currency: str, start: datetime, end: datetime) -> str:
    """
    Функция, которая возвращает строковое представление дохода.
    :param user_id: ID пользователя Telegram.
    :param currency: Строковое представление валюты.
    :param start: Начало периода отчёта.
    :param end: Конец периода отчёта.
    :return: Строковое представление дохода.
    """
    try:
        all_incomes = str(round(await db_functions.return_sum_income(user_id, start, end), 2)).replace('.', '\.')
        string = f"📈 Доходы\: *{all_incomes}* {currency}"
    except Exception as e:
        string = f"📈 Доходы\: *Ошибка*"
        logging.error(f"{_get_income_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def _get_spend_string(user_id: str, currency: str, start: datetime, end: datetime) -> str:
    """
    Функция, которая возвращает строковое представление траты.
    :param user_id: ID пользователя Telegram.
    :param currency: Строковое представление валюты.
    :param start: Начало периода отчёта.
    :param end: Конец периода отчёта.
    :return: Строковое представление траты.
    """
    try:
        all_spends = str(round(await db_functions.return_sum_spend(user_id, start, end), 2)).replace('.', '\.')
        string = f"📉 Траты\: *{all_spends}* {currency}"
    except Exception as e:
        string = f"📉 Траты\: *Ошибка*"
        logging.error(f"{_get_spend_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def get_graphics_in_photo(user_id: str, now: datetime) -> str:
    """
    Функция, которая возвращает путь к графику трат.
    :param now: Дата
    :param user_id: ID пользователя Telegram.
    :return: Путь до файла.
    """
    path = f'temporary\\graphics\\{user_id}.png'
    try:
        if not os.path.exists('temporary'):
            os.makedirs('temporary')
        if not os.path.exists('temporary\\graphics'):
            os.makedirs('temporary\\graphics')
        start = datetime.date(now.year, now.month, 1)
        end = start.replace(day=28) + datetime.timedelta(days=4)
        end = end - datetime.timedelta(days=end.day)
        data = await db_functions.get_spends_of_user_by_categories(user_id, start, end)
        spending_by_category = {}
        for category in data.keys():
            if data[category]['$all'] == 0:
                continue
            if category == "$no_category":
                spending_by_category['Без категории'] = data[category]['$all']
                continue
            spending_by_category[category] = data[category]['$all']
        labels = list(spending_by_category.keys())
        sizes = list(spending_by_category.values())
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        plt.title('Расходы по категориям')
        fig1.savefig(path, dpi=300, bbox_inches='tight')
    except Exception as e:
        logging.error(f"{get_graphics_in_photo.__name__}: {e}. Пользователь с id {user_id}.")
    return path
