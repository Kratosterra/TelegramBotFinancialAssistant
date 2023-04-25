import logging
from calendar import monthrange

from database import db_functions
from texts.ru_RU import messages
import datetime


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
            days = start + datetime.timedelta(days=day_i)
            dates.append(days)
    else:
        delta = end - start
        for day_i in range(delta.days + 1):
            days = start + datetime.timedelta(days=day_i)
            dates.append(days)
    return dates


async def get_day_string(user_id, currency):
    year = datetime.datetime.now().year
    month = messages.months[int(datetime.datetime.now().month)]
    return f"\n_За *{month} {year}*_"


async def get_budget_of_user(user_id: str) -> str:
    await db_functions.count_remained(user_id)
    currency = await db_functions.get_user_currency(user_id)
    string = f"{await get_day_string(user_id, currency)}\n\n" \
             f"{await get_remained_on_day_string(user_id, currency)}\n\n" \
             f"{await get_limit_string(user_id, currency)}\n\n" \
             f"{await get_goal_string(user_id, currency)}\n\n" \
             f"{await get_income_string(user_id, currency)}\n" \
             f"{await get_spend_string(user_id, currency)}\n\n" \
             f"{await get_remainer_string(user_id, currency)}\n"
    return string


async def get_limit_string(user_id: str, currency: str) -> str:
    try:
        is_limit = await db_functions.check_limit(user_id)
        if is_limit:
            is_limit = "✅ соблюдён"
        elif is_limit is None:
            is_limit = "❔ не установлен"
            return f"💰 Лимит трат:\n{is_limit}"
        else:
            is_limit = "❌ превышен"
        limit = str(await db_functions.get_limit(user_id)).replace('.', '\.')
        all_spends = str(round(await db_functions.return_sum_spend(user_id, None, None, True), 2)).replace('.', '\.')
        string = f"💰 Лимит трат:\n{is_limit} _\({all_spends}\/{limit}\)_"
    except Exception as e:
        string = f"💰 Лимит трат:\n*Ошибка*"
        logging.error(f"{get_limit_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def get_goal_string(user_id: str, currency: str) -> str:
    try:
        is_goal = await db_functions.check_goal(user_id)
        if is_goal:
            is_goal = "✅ достигнута"
        elif is_goal is None:
            is_goal = "❔ не установлена"
            return f"📩 Цель по экономии:\n{is_goal}"
        else:
            is_goal = "❌ не достигнута"
        remained = str(await db_functions.get_remained(user_id)).replace('.', '\.')
        goal = str(await db_functions.get_goal(user_id)).replace('.', '\.')
        string = f"📩 Цель по экономии:\n{is_goal} _\({remained}\/{goal}\)_"
    except Exception as e:
        string = f"📩 Цель по экономии:\n*Ошибка*"
        logging.error(f"{get_goal_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def get_remained_on_day_string(user_id: str, currency: str) -> str:
    try:
        days = monthrange(datetime.date.today().year, datetime.date.today().month)[1]
        days_remain = days - len(get_dates_of_period(None, None, True))
        if days_remain < 0:
            days_remain = 0
        remained = str(round((await db_functions.get_remained(user_id)) / float(days_remain + 1), 2)).replace('.', '\.')
        string = f"💵 На сегодня\: *{remained}* {currency}"
    except Exception as e:
        string = f"💵 На сегодня\: *Ошибка*"
        logging.error(f"{get_remained_on_day_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def get_income_string(user_id: str, currency: str) -> str:
    try:
        all_incomes = str(round(await db_functions.return_sum_income(user_id, None, None, True), 2)).replace('.', '\.')
        string = f"📈 Доходы\: *{all_incomes}* {currency}"
    except Exception as e:
        string = f"📈 Доходы\: *Ошибка*"
        logging.error(f"{get_income_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def get_spend_string(user_id: str, currency: str) -> str:
    try:
        all_spends = str(round(await db_functions.return_sum_spend(user_id, None, None, True), 2)).replace('.', '\.')
        string = f"📉 Траты\: *{all_spends}* {currency}"
    except Exception as e:
        string = f"📉 Траты\: *Ошибка*"
        logging.error(f"{get_spend_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def get_remainer_string(user_id: str, currency: str) -> str:
    try:
        all_spends = str(round(await db_functions.get_remained(user_id), 2)).replace('.', '\.')
        string = f"💰 Остаток\: *{all_spends}* {currency}"
    except Exception as e:
        string = f"💰 Остаток\: *Ошибка*"
        logging.error(f"{get_remainer_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string
