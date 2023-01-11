import datetime
from datetime import timedelta


def get_dates_with_date(date_of_months, start, end, need_first_date=True):
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


def get_dates_of_period(start, end, this_moths=False):
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
