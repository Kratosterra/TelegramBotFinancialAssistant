import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta


def get_dates_with_date(date_of_months: int, start: datetime, end: datetime, need_first_date=True) -> list:
    """
    Возвращает все даты во временном отрезке, которые совпадают с датой переданной в функцию.
    :param date_of_months: Дата.
    :param start: Начало временного периода.
    :param end: Конец временного периода.
    :param need_first_date: Нужна ли первая дата.
    :return: Лист дат.
    """
    delta = end - start
    dates_of_one_date = []
    n = 0
    for day_i in range(delta.days + 1):
        days = start + timedelta(days=day_i)
        if days.day == date_of_months:
            if need_first_date:
                dates_of_one_date.append(days)
            else:
                if n > 0:
                    dates_of_one_date.append(days)
        n += 1
    return dates_of_one_date


def get_past_months() -> list:
    """
    Возвращает лист размера 2, с первой датой прошлого месяца и последней датой прошлого месяца
    :return: Лист из двух datetime.
    """
    today = datetime.date.today()
    first_day_prev_month = datetime.date(today.year, today.month, 1)
    first_day_prev_month += relativedelta(months=-1)
    last_day_prev_month = first_day_prev_month.replace(day=28) + datetime.timedelta(days=4)
    last_day_prev_month = last_day_prev_month - datetime.timedelta(days=last_day_prev_month.day)
    return [first_day_prev_month, last_day_prev_month]


def get_dates_of_period(start: datetime, end: datetime, this_moths=False) -> list:
    """
    Возвращает все даты в определенном промежутке либо за текущий месяц.
    :param start: Начало временного промежутка.
    :param end: Конец временного промежутка.
    :param this_moths: В этом ли месяце возвращать даты.
    :return: Лист дат.
    """
    dates = []
    if this_moths:
        end = datetime.datetime.now()
        start = datetime.datetime(end.date().year, end.date().month, 1)
        delta = end - start
        for day_i in range(delta.days + 1):
            days = start + timedelta(days=day_i)
            dates.append(days)
    else:
        delta = end - start
        for day_i in range(delta.days + 1):
            days = start + timedelta(days=day_i)
            dates.append(days)
    return dates


async def check_if_string_is_sum(sum_str: str) -> {bool, float}:
    """
    Проверяет являться ли текстовое значение суммой.
    :param sum_str: Строковое представление.
    :return: Является ли тест суммой.
    """
    if sum_str.replace('.', '', 1).isdigit() or sum_str.replace(',', '', 1).isdigit():
        sum_str = sum_str.replace(',', '.')
        if float(sum_str) > 10000000000 or float(sum_str) < 0.01:
            return False, 0.0
        return True, round(float(sum_str), 2)
    return False, 0.0
