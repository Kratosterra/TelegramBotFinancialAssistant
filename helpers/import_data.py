import csv
import datetime
import logging
import re

from database import db_functions


async def check_if_string_is_sum(sum_str: str) -> {bool, float}:
    """
    Проверяет являться ли текстовое значение суммой.
    :param sum_str: Стрококвое представление.
    :return: Является ли тест суммой.
    """
    if sum_str.replace('.', '', 1).isdigit() or sum_str.replace(',', '', 1).isdigit():
        sum_str = sum_str.replace(',', '.')
        if float(sum_str) > 10000000000 or float(sum_str) < 0.01:
            return False, 0.0
        return True, round(float(sum_str), 2)
    return False, 0.0


async def check_if_string_is_date(date: str):
    if len(date.split('-')) == 3:
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
            return True, date
        except Exception:
            return False, ""
    else:
        return False, ""


async def check_income(row):
    ans = []
    if len(row) != 5:
        return False, []

    name = str(row[0])
    if name.startswith('$'):
        return False, []
    name = re.sub(r'[^\w\s]', '', name)
    if len(name) > 75 or len(name) < 3:
        ans.append(None)
    else:
        ans.append(name)

    sum = str(row[1])
    status, sum = await check_if_string_is_sum(sum)
    if status:
        ans.append(sum)
    else:
        return False, []

    date = str(row[2])
    status, date = await check_if_string_is_date(date)
    if status:
        ans.append(date)
    else:
        return False, []

    return True, ans


async def check_spend(row):
    ans = []
    if len(row) != 5:
        return False, []

    name = str(row[0])
    if name.startswith('$'):
        return False, []
    name = re.sub(r'[^\w\s]', '', name)
    if len(name) > 75 or len(name) < 3:
        ans.append(None)
    else:
        ans.append(name)
    sum = str(row[1])
    status, sum = await check_if_string_is_sum(sum)
    if status:
        ans.append(sum)
    else:
        return False, []
    category = str(row[2])
    category = re.sub(r'[^\w\s]', '', category)
    if len(category) > 40 or len(category) < 3:
        ans.append(None)
    else:
        ans.append(category)

    subcategory = str(row[3])
    subcategory = re.sub(r'[^\w\s]', '', subcategory)
    if len(subcategory) > 40 or len(subcategory) < 3:
        ans.append(None)
    else:
        ans.append(subcategory)

    date = str(row[4])
    status, date = await check_if_string_is_date(date)
    if status:
        ans.append(date)
    else:
        return False, []

    return True, ans


async def import_table(user_id, path):
    try:
        num_of_spends = 0
        num_of_incomes = 0
        is_income_now = False
        is_spend_now = False
        with open(path, 'r', encoding="windows-1251") as csv_file:
            reader = csv.reader(csv_file, delimiter=";")
            for row in reader:
                if len(row) != 5:
                    return 0, 0, False
                if row[0] == "$Incomes":
                    is_income_now = True
                    is_spend_now = False
                    continue
                elif row[0] == "$Spends":
                    is_spend_now = True
                    is_income_now = False
                    continue
                if is_income_now:
                    status, data = await check_income(row)
                    if status and len(data) == 3:
                        good = await db_functions.add_income(user_id=user_id, name=data[0], value=data[1], date=data[2])
                        if good:
                            num_of_incomes += 1
                    else:
                        continue
                elif is_spend_now:
                    status, data = await check_spend(row)
                    if status and len(data) == 5:
                        good = await db_functions.add_spend(user_id=user_id, name=data[0], value=data[1], date=data[4],
                                                            category=data[2], subcategory=data[3])
                        if good:
                            num_of_spends += 1
                    else:
                        continue
        return num_of_incomes, num_of_spends, True
    except Exception as e:
        logging.error(f"{import_table.__name__}: {e}. Пользователь с id {user_id}.")
        return 0, 0, False
