import datetime
from datetime import timedelta


def get_dates_with_date(date_of_months: int, start: datetime, end: datetime, need_first_date=True) -> list:
    """
    Возвращает все даты во временном отрезке, которые совпадают с датой переданной в функцию.
    :param date_of_months: Дата.
    :param start: Начало временного периода.
    :param end: Конецу временного периода.
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
