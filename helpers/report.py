import datetime
import logging

from dateutil.relativedelta import relativedelta

from database import db_functions
from texts.ru_RU import messages


def get_past_months_from_date(date: datetime) -> list:
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


async def get_small_text_report(user_id: str, date: datetime, need_subcategories=False) -> str:
    string = "*Ошибка*"
    print(date)
    try:
        currency = await db_functions.get_user_currency(user_id)
        start = datetime.date(date.year, date.month, 1)
        end = start.replace(day=28) + datetime.timedelta(days=4)
        end = end - datetime.timedelta(days=end.day)
        print(f"{start} {end}")
        string = f"{await get_day_string(user_id, currency, start, end)}\n\n" \
                 f"{await better_string(user_id, currency, start, end)}\n" \
                 f"{await get_income_string(user_id, currency, start, end)}\n" \
                 f"{await get_spend_string(user_id, currency, start, end)}\n\n" \
                 f"{await get_categories_report(user_id, currency, start, end, need_subcategories)}"
        if len(string) > 3800:
            return string[:3800] + "\.\.\. *Воспользуйтесь отчетом \.xlsx*"
        print(string)
    except Exception as e:
        logging.error(f"{get_small_text_report.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def get_categories_report(user_id, currency, start, end, need_subcategories):
    data = await db_functions.get_spends_of_user_by_categories(user_id, start, end)
    string = "*По категориям трат:*\n\n"
    for category in data.keys():
        if category == "$no_category":
            all = str(round(data[category]['$all'], 2)).replace('.', '\.')
            string += f"*Без категории*: _{all}_ {currency}\n\n"
            continue
        all = str(round(data[category]['$all'], 2)).replace('.', '\.')
        no_category = str(round(data[category]['$no_subcategory'], 2)).replace('.', '\.')
        if need_subcategories:
            string += f"*{category}*: _{all}_ {currency}\n\t\> _Без подкатегории_: {no_category} {currency}\n"
        else:
            string += f"*{category}*: _{all}_ {currency}\n"
        if need_subcategories:
            for sub_category in (data[category].keys()):
                if sub_category == "$all" or sub_category == "$no_subcategory":
                    continue
                now = str(round(data[category][sub_category], 2)).replace('.', '\.')
                string += f"\t\> _{sub_category}_: {now} {currency}\n"
        string += "\n"
    return string


async def better_string(user_id, currency, start, end):
    print("/better_string")
    list_dates_past = get_past_months_from_date(start)
    print(list_dates_past)
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
    print("/better_string end")
    return f"_По сравнению с прошлым месяцем:_\n📈 Доходы\: {income_string}\n📉 Траты\: {spend_string}\n"


async def get_day_string(user_id, currency, start, end):
    year = start.year
    month = messages.months[int(start.month)]
    return f"\n_За *{month} {year}*_"


async def get_income_string(user_id: str, currency: str, start, end) -> str:
    try:
        all_incomes = str(round(await db_functions.return_sum_income(user_id, start, end), 2)).replace('.', '\.')
        string = f"📈 Доходы\: *{all_incomes}* {currency}"
    except Exception as e:
        string = f"📈 Доходы\: *Ошибка*"
        logging.error(f"{get_income_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string


async def get_spend_string(user_id: str, currency: str, start, end) -> str:
    try:
        all_spends = str(round(await db_functions.return_sum_spend(user_id, start, end), 2)).replace('.', '\.')
        string = f"📉 Траты\: *{all_spends}* {currency}"
    except Exception as e:
        string = f"📉 Траты\: *Ошибка*"
        logging.error(f"{get_spend_string.__name__}: {e}. Пользователь с id {user_id}.")
    return string
