import datetime
import logging
from calendar import monthrange

from database import db_functions
from texts.ru_RU import messages


def _get_dates_of_period(start: datetime, end: datetime, this_moths: bool = False) -> list:
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


async def _get_day_string() -> str:
    """
    Функция, которая возвращает строку, представляющую текущую дату в виде месяца и года.
    :return: Строку для бюджета, представляющую текущую дату в виде месяца и года.
    """
    year = datetime.datetime.now().year
    month = messages.months[int(datetime.datetime.now().month)]
    return f"\n_За *{month} {year}*_"


async def _get_event_spend_string(user_id: str, currency: str) -> str:
    """
    Функция, которая возвращает строку представления состояний событий трат для сообщения с бюджетом.
    :param user_id: ID пользователя Telegram.
    :param currency: Валюта в строковом представлении.
    :return: Строку представления состояний событий трат пользователя.
    """
    try:
        event_spend = await db_functions.return_all_events_spends(user_id)
        data = "*События*\n\n✅ \- учтено\n⭕ \- ожидает учёта\n\n*События трат*\n\n"
        month = messages.months_events[int(datetime.datetime.now().month)]
        if len(event_spend) == 0:
            data += "*Пока отсутствуют\.*\n\n"
            return data
        for spend_name in event_spend:
            sum_spend = str(event_spend[spend_name]['value_of_spending']).replace('.', '\.')
            day = event_spend[spend_name]["day_of_spending"]
            today = event_spend[spend_name]["last_indexed"]
            check = today
            if today is not None:
                today = datetime.datetime.strptime(today, "%Y-%m-%d").day
                if datetime.datetime.strptime(check, "%Y-%m-%d").month < datetime.date.today().month\
                        or datetime.datetime.strptime(check, "%Y-%m-%d").year < datetime.date.today().year:
                    today = None
            if today is not None and day <= today:
                data += f"*{spend_name}*\t✅\nСумма _{sum_spend} {currency}_ за _{day} {month}_\n\n"
            else:
                data += f"*{spend_name}*\t⭕\nСумма _{sum_spend} {currency}_ за _{day} {month}_\n\n"
    except Exception as e:
        data = f"*События*\n\n✅ \- учтено\n⭕ \- ожидает учёта\n\n*События трат*\n\n*Ошибка*\n\n"
        logging.error(f"{_get_event_spend_string.__name__}: {e}. Пользователь с id {user_id}.")
    return data


async def _get_event_income_string(user_id: str, currency: str) -> str:
    """
    Функция, которая возвращает строку представления состояний событий доходов для сообщения с бюджетом.
    :param user_id: ID пользователя Telegram.
    :param currency: Валюта в строковом представлении.
    :return: Строку представления состояний событий доходов пользователя.
    """
    try:
        event_income = await db_functions.return_all_events_income(user_id)
        data = "*События доходов*\n\n"
        month = messages.months_events[int(datetime.datetime.now().month)]
        if len(event_income) == 0:
            data += "*Пока отсутствуют\.*\n\n"
            return data
        for income in event_income:
            sum_spend = str(event_income[income]['value_of_income']).replace('.', '\.')
            day = event_income[income]["day_of_income"]
            today = event_income[income]["last_indexed"]
            check = today
            if today is not None:
                today = datetime.datetime.strptime(today, "%Y-%m-%d").day
                if datetime.datetime.strptime(check, "%Y-%m-%d").month < datetime.date.today().month\
                        or datetime.datetime.strptime(check, "%Y-%m-%d").year < datetime.date.today().year:
                    today = None
            if today is not None and day <= today:
                data += f"*{income}*\t✅\nСумма _{sum_spend} {currency}_ за _{day} {month}_\n\n"
            else:
                data += f"*{income}*\t⭕\nСумма _{sum_spend} {currency}_ за _{day} {month}_\n\n"
    except Exception as e:
        data = f"*События доходов*\n\n*Ошибка*\n\n"
        logging.error(f"{_get_event_income_string.__name__}: {e}. Пользователь с id {user_id}.")
    return data


async def get_budget_of_user(user_id: str) -> str:
    """
    Функция, которая возвращает строку для сообщения с бюджетом.
    :param user_id: ID пользователя Telegram.
    :return: Строка для сообщения с бюджетом.
    """
    await db_functions.count_remained(user_id)
    currency = await db_functions.get_user_currency(user_id)
    string = f"{await _get_day_string()}\n\n" \
             f"{await _get_remained_on_day_string(user_id, currency)}\n\n" \
             f"{await _get_limit_string(user_id, currency)}\n\n" \
             f"{await _get_goal_string(user_id, currency)}\n\n" \
             f"{await _get_income_string(user_id, currency)}\n" \
             f"{await _get_spend_string(user_id, currency)}\n\n" \
             f"{await _get_remainer_string(user_id, currency)}\n\n" \
             f"{await _get_event_spend_string(user_id, currency)}" \
             f"{await _get_event_income_string(user_id, currency)}\n"
    if len(string) > 3900:
        string = f"{await _get_day_string()}\n\n" \
                 f"{await _get_remained_on_day_string(user_id, currency)}\n\n" \
                 f"{await _get_limit_string(user_id, currency)}\n\n" \
                 f"{await _get_goal_string(user_id, currency)}\n\n" \
                 f"{await _get_income_string(user_id, currency)}\n" \
                 f"{await _get_spend_string(user_id, currency)}\n\n" \
                 f"{await _get_remainer_string(user_id, currency)}\n\n"
    return string


async def _get_limit_string(user_id: str, currency: str) -> str:
    """
    Функция, которая возвращает строку лимита.
    :param user_id: ID пользователя Telegram.
    :param currency: Валюта в строковом представлении.
    :return: Строку представления лимита.
    """
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
        string = f"💰 Лимит трат:\n{is_limit}\n_\({all_spends} {currency} из {limit} {currency}\)_"
    except Exception as e:
        string = f"💰 Лимит трат:\n*Ошибка*"
        logging.error(f"{_get_limit_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def _get_goal_string(user_id: str, currency: str) -> str:
    """
    Функция, которая возвращает строку цели.
    :param user_id: ID пользователя Telegram.
    :param currency: Валюта в строковом представлении.
    :return: Строку представления цели.
    """
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
        string = f"📩 Цель по экономии:\n{is_goal}\n_\({remained} {currency} из {goal} {currency}\)_"
    except Exception as e:
        string = f"📩 Цель по экономии:\n*Ошибка*"
        logging.error(f"{_get_goal_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def _get_remained_on_day_string(user_id: str, currency: str) -> str:
    """
    Функция, которая возвращает строку оставшегося на день остатка.
    :param currency: Валюта в строковом представлении.
    :param user_id: ID пользователя Telegram.
    :return: Строку представления остатка на день.
    """
    try:
        days = monthrange(datetime.date.today().year, datetime.date.today().month)[1]
        days_remain = days - len(_get_dates_of_period(None, None, True))
        if days_remain < 0:
            days_remain = 0
        remained = str(round((await db_functions.get_remained(user_id)) / float(days_remain + 1), 2)).replace('.', '\.')
        string = f"💵 На сегодня\: *{remained}* {currency}"
    except Exception as e:
        string = f"💵 На сегодня\: *Ошибка*"
        logging.error(f"{_get_remained_on_day_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def _get_income_string(user_id: str, currency: str) -> str:
    """
    Функция, которая возвращает строку представления доходов.
    :param currency: Валюта в строковом представлении.
    :param user_id: ID пользователя Telegram.
    :return: Строку представления дохода.
    """
    try:
        all_incomes = str(round(await db_functions.return_sum_income(user_id, None, None, True), 2)).replace('.', '\.')
        string = f"📈 Доходы\: *{all_incomes}* {currency}"
    except Exception as e:
        string = f"📈 Доходы\: *Ошибка*"
        logging.error(f"{_get_income_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def _get_spend_string(user_id: str, currency: str) -> str:
    """
    Функция, которая возвращает строку представления трат.
    :param currency: Валюта в строковом представлении.
    :param user_id: ID пользователя Telegram.
    :return: Строку представления траты.
    """
    try:
        all_spends = str(round(await db_functions.return_sum_spend(user_id, None, None, True), 2)).replace('.', '\.')
        string = f"📉 Траты\: *{all_spends}* {currency}"
    except Exception as e:
        string = f"📉 Траты\: *Ошибка*"
        logging.error(f"{_get_spend_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def _get_remainer_string(user_id: str, currency: str) -> str:
    """
    Функция, которая возвращает строку представления остатка.
    :param currency: Валюта в строковом представлении.
    :param user_id: ID пользователя Telegram.
    :return: Строку представления остатка.
    """
    try:
        all_spends = str(round(await db_functions.get_remained(user_id), 2)).replace('.', '\.')
        string = f"💰 Остаток\: *{all_spends}* {currency}"
    except Exception as e:
        string = f"💰 Остаток\: *Ошибка*"
        logging.error(f"{_get_remainer_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string
