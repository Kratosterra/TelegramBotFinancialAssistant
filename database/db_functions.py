import datetime
import json
import logging
import sqlite3
import time
from sqlite3 import Connection, Cursor

import helpers.helpers

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.DEBUG)
currency = {'rubles': 'RUB', 'euro': 'EUR', 'Yen': 'JPY', 'yuan': 'CNY'}


def initialize_user(user_id):
    logging.debug(f"Инициализация пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        # Создаём таблицу с информацией о пользователе.
        sql.execute("""CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY,
        'limit' REAL,
        'goal' REAL,
        remainer REAL,
        currency TEXT,
        last_indexed TEXT)""")
        db.commit()
        # Добавляем запись о пользователе только при первом создании таблицы.
        sql.execute("SELECT currency FROM user_data")
        if sql.fetchone() is None:
            utctime = time.strftime("%Y-%m-%d", time.gmtime())
            sql.execute("INSERT INTO user_data VALUES (?, ?, ?, ?, ?, ?)",
                        (1, None, None, None, currency['rubles'], utctime))
            db.commit()
        # Создаём таблицу доходов.
        sql.execute("""CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY,
        name_of_income TEXT,
        type_of_income TEXT,
        value_of_income REAL,
        date_of_income TEXT
        )""")
        db.commit()
        # Создаём таблицу расходов.
        sql.execute("""CREATE TABLE IF NOT EXISTS spend (
        id INTEGER PRIMARY KEY,
        name_of_spend TEXT,
        type_of_spend TEXT,
        value_of_spend REAL,
        category TEXT,
        sub_category TEXT,
        date_of_spend TEXT
        )""")
        db.commit()
        # Создаём таблицу событий доходов, повторяющихся каждый месяц.
        sql.execute("""CREATE TABLE IF NOT EXISTS event_income (
        name_of_income TEXT UNIQUE,
        value_of_income REAL,
        day_of_income INTEGER,
        last_indexed TEXT,
        created TEXT
        )""")
        db.commit()
        # Создаём таблицу расходов, повторяющихся каждый месяц
        sql.execute("""CREATE TABLE IF NOT EXISTS event_spend (
        name_of_spending TEXT UNIQUE,
        value_of_spending REAL,
        category TEXT,
        sub_category TEXT,
        day_of_spending INTEGER,
        last_indexed TEXT,
        created TEXT
        )""")
        db.commit()
        # Создаём таблицу категорий и подкатегорий.
        sql.execute("""CREATE TABLE IF NOT EXISTS categories (
        name_of_category TEXT UNIQUE,
        sub_categories TEXT
        )""")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    logging.debug(f"Инициализация пользователя с id: {user_id} закончена.")
    return True


def set_limit(user_id, limit):
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    logging.debug(f"Устанавливаем лимит средств для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"UPDATE user_data SET 'limit' = {limit} WHERE id = 1")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def set_remained(user_id, remained):
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    logging.debug(f"Устанавливаем остаток средств для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"UPDATE user_data SET 'remainer' = {remained} WHERE id = 1")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def set_goal(user_id, goal):
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    logging.debug(f"Устанавливаем цель для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"UPDATE user_data SET 'goal' = {goal} WHERE id = 1")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def add_income(user_id, value, name=None, type_of_income=None, date=time.strftime("%Y-%m-%d", time.gmtime())):
    logging.debug(f"Добавляем запись о доходе пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(
            "INSERT INTO income(name_of_income, type_of_income, value_of_income, date_of_income) VALUES (?, ?, ?, ?)",
            (name, type_of_income, value, date))
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def add_event_income(user_id, value, name, day_of_income):
    logging.debug(f"Добавляем запись о СОБЫТИИ дохода пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        utctime = time.strftime("%Y-%m-%d", time.gmtime())
        sql.execute("INSERT INTO event_income VALUES (?, ?, ?, ?, ?)", (name, value, day_of_income, None, utctime))
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def add_spend(user_id, value, name=None, type_of_spend=None, category=None, subcategory=None,
              date=time.strftime("%Y-%m-%d", time.gmtime())):
    logging.debug(f"Добавляем запись о тратах пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(
            "INSERT INTO spend(name_of_spend, type_of_spend, value_of_spend, category, sub_category, date_of_spend) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, type_of_spend, value, category, subcategory, date))
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def add_event_spend(user_id, value, name, day_of_spending, category=None, subcategory=None):
    logging.debug(f"Добавляем запись о СОБЫТИИ трат пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        utctime = time.strftime("%Y-%m-%d", time.gmtime())
        sql.execute("INSERT INTO event_spend VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, value, category, subcategory, day_of_spending, None, utctime))
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def add_new_category(user_id, category):
    logging.debug(f"Добавляем новую категорию пользователю с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute("INSERT INTO categories VALUES (?, ?)", (category, "{}"))
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def add_new_subcategory(user_id, category, subcategory):
    logging.debug(f"Добавляем новую подкатегорию в категорию пользователю с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT sub_categories FROM categories WHERE name_of_category = '{category}'")
        tuple_data = sql.fetchone()
        if tuple_data is None:
            logging.error(f"Нет родительской категории. Пользователь с id: '{user_id}'")
            return False

        subcategories = json.loads(str(tuple_data[0]))
        if subcategory in subcategories.keys():
            logging.error(f"Такая подкатегория уже есть! Пользователь с id: '{user_id}'")
            return False
        subcategories[subcategory] = 0
        to_write = json.dumps(subcategories)

        sql.execute("UPDATE categories SET sub_categories = ? WHERE name_of_category = ?", (str(to_write), category))
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    except Exception as e:
        logging.error(f"Ошибка при работе с базой данных: '{e}'. Не на стороне базы. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def delete_event_spend(user_id, name_of_spending):
    logging.debug(f"Удаляем СОБЫТИЕ трат у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from event_spend where name_of_spending = '{name_of_spending}'")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def delete_event_income(user_id, name_of_income):
    logging.debug(f"Удаляем СОБЫТИЕ получения средств у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from event_income where name_of_income = '{name_of_income}'")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def delete_category(user_id, name_of_category):
    logging.debug(f"Удаляем категорию у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from categories where name_of_category = '{name_of_category}'")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def delete_subcategory(user_id, category, subcategory):
    logging.debug(f"Удаляем подкатегорию в категории пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT sub_categories FROM categories WHERE name_of_category = '{category}'")
        tuple_data = sql.fetchone()
        if tuple_data is None:
            logging.error(f"Нет родительской категории. Пользователь с id: '{user_id}'")
            return False

        subcategories = json.loads(str(tuple_data[0]))
        if subcategory not in subcategories.keys():
            logging.error(f"Такой подкатегории нет! Пользователь с id: '{user_id}'")
            return False
        del subcategories[subcategory]
        to_write = json.dumps(subcategories)
        sql.execute("UPDATE categories SET sub_categories = ? WHERE name_of_category = ?", (str(to_write), category))
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    except Exception as e:
        logging.error(f"Ошибка при работе с базой данных: '{e}'. Не на стороне базы. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def execute_events(user_id):
    utctime_str = time.strftime("%Y-%m-%d", time.gmtime())
    utctime = datetime.datetime.now()
    logging.debug(f"Исполняем события пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        all_events_spend = {}
        all_events_income = {}
        num_of_spend = 0
        for row in sql.execute(f"SELECT * FROM event_spend"):
            if row[5] is None:
                time_of_reg = datetime.datetime.strptime(row[6], '%Y-%m-%d')
                execution_date = helpers.helpers.get_dates_with_date(int(row[4]), time_of_reg, utctime)
                for i in execution_date:
                    time_event = datetime.datetime.strftime(i, '%Y-%m-%d')
                    all_events_spend[num_of_spend] = (
                        user_id, row[1], row[0], "event", row[2], row[3], time_event)
            else:
                time_last_execution = datetime.datetime.strptime(row[5], '%Y-%m-%d')
                execution_date = helpers.helpers.get_dates_with_date(int(row[4]), time_last_execution, utctime, False)
                for i in execution_date:
                    time_event = datetime.datetime.strftime(i, '%Y-%m-%d')
                    all_events_spend[num_of_spend] = (user_id, row[1], row[0], "event", row[2], row[3], time_event)
            num_of_spend += 1
        num_of_spend = 0
        for row in sql.execute(f"SELECT * FROM event_income"):
            if row[3] is None:
                time_of_reg = datetime.datetime.strptime(row[4], '%Y-%m-%d')
                execution_date = helpers.helpers.get_dates_with_date(int(row[2]), time_of_reg, utctime)
                for i in execution_date:
                    time_event = datetime.datetime.strftime(i, '%Y-%m-%d')
                    all_events_income[num_of_spend] = (user_id, row[1], row[0], "event", time_event)
            else:
                time_last_execution = datetime.datetime.strptime(row[3], '%Y-%m-%d')
                execution_date = helpers.helpers.get_dates_with_date(int(row[2]), time_last_execution, utctime, False)
                for i in execution_date:
                    time_event = datetime.datetime.strftime(i, '%Y-%m-%d')
                    all_events_income[num_of_spend] = (user_id, row[1], row[0], "event", time_event)
            num_of_spend += 1
        for i in all_events_spend.keys():
            spend = str(all_events_spend[i][2])
            sql.execute("UPDATE event_spend SET last_indexed = ? WHERE name_of_spending = ?", (utctime_str, spend))
            db.commit()
        for i in all_events_income.keys():
            income = str(all_events_income[i][2])
            sql.execute("UPDATE event_income SET last_indexed = ? WHERE name_of_income = ?", (utctime_str, income))
            db.commit()
        db.close()
        for i in all_events_spend.keys():
            spend = all_events_spend[i]
            add_spend(spend[0], spend[1], spend[2], spend[3], spend[4], spend[5], spend[6])
        for i in all_events_income.keys():
            income = all_events_income[i]
            add_income(income[0], income[1], income[2], income[3], income[4])
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    except Exception as e:
        logging.error(f"Ошибка при работе с базой данных: '{e}'. Не на стороне базы. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def return_all_spends(user_id):
    logging.debug(f"Возвращаем все траты пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    all_spend = {}
    try:
        sql: Cursor = db.cursor()
        for row in sql.execute(f"SELECT * FROM spend"):
            all_spend[row[0]] = {}
            all_spend[row[0]]["name_of_spend"] = row[1]
            all_spend[row[0]]["type_of_spend"] = row[2]
            all_spend[row[0]]["value_of_spend"] = row[3]
            all_spend[row[0]]["category"] = row[4]
            all_spend[row[0]]["sub_category"] = row[5]
            all_spend[row[0]]["date_of_spend"] = row[6]
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return {}
    finally:
        if db:
            db.close()
    return all_spend


def return_all_incomes(user_id):
    logging.debug(f"Возвращаем все доходы пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    all_spend = {}
    try:
        sql: Cursor = db.cursor()
        for row in sql.execute(f"SELECT * FROM income"):
            all_spend[row[0]] = {}
            all_spend[row[0]]["name_of_income"] = row[1]
            all_spend[row[0]]["type_of_income"] = row[2]
            all_spend[row[0]]["value_of_income"] = row[3]
            all_spend[row[0]]["date_of_income"] = row[4]
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return {}
    finally:
        if db:
            db.close()
    return all_spend


def return_spend_of_period(user_id, start, end, this_moths=False):
    logging.debug(f"Возвращаем траты в заданном периоде пользователя с id: {user_id}.")
    all_spends = return_all_spends(user_id)
    time_points = helpers.helpers.get_dates_of_period(start, end, this_moths)
    spends_of_period = {}
    for time_point in time_points:
        time_of_check = datetime.datetime.strftime(time_point, '%Y-%m-%d')
        for spend in all_spends.keys():
            if all_spends[spend]['date_of_spend'] == time_of_check:
                spends_of_period[spend] = all_spends[spend]
    return spends_of_period


def return_incomes_of_period(user_id, start, end, this_moths=False):
    logging.debug(f"Возвращаем доходы в заданном периоде пользователя с id: {user_id}.")
    all_incomes = return_all_incomes(user_id)
    time_points = helpers.helpers.get_dates_of_period(start, end, this_moths)
    incomes_of_period = {}
    for time_point in time_points:
        time_of_check = datetime.datetime.strftime(time_point, '%Y-%m-%d')
        for spend in all_incomes.keys():
            if all_incomes[spend]['date_of_income'] == time_of_check:
                incomes_of_period[spend] = all_incomes[spend]
    return incomes_of_period


def return_sum_income(user_id, start, end, this_moths=False):
    logging.debug(f"Возвращаем сумму доходов пользователя с id: {user_id}.")
    sum_income = 0.00
    incomes = return_incomes_of_period(user_id, start, end, this_moths)
    for i in incomes.keys():
        sum_income += incomes[i]['value_of_income']
    return sum_income


def return_sum_spend(user_id, start, end, this_moths=False):
    logging.debug(f"Возвращаем сумму трат пользователя с id: {user_id}.")
    sum_spend = 0.00
    spends = return_spend_of_period(user_id, start, end, this_moths)
    for i in spends.keys():
        sum_spend += spends[i]['value_of_spend']
    return sum_spend


def return_all_categories(user_id):
    logging.debug(f"Возвращаем все категории пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    all_categories = {}
    try:
        sql: Cursor = db.cursor()
        for row in sql.execute(f"SELECT * FROM categories"):
            sub_categories_list = []
            sub_categories = dict(json.loads(row[1]))
            for key in sub_categories.keys():
                sub_categories_list.append(key)
            all_categories[row[0]] = sub_categories_list
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return {}
    finally:
        if db:
            db.close()
    return all_categories


def delete_spend_by_id(user_id, spend_id):
    logging.debug(f"Удаляем тарату у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from spend where id = {spend_id}")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def delete_income_by_id(user_id, income_id):
    logging.debug(f"Удаляем доход у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from income where id = {income_id}")
        db.commit()
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


def count_remained(user_id):
    sum_of_spends = return_sum_spend(user_id, None, None, True)
    sum_of_incomes = return_sum_income(user_id, None, None, True)
    remained = sum_of_incomes - sum_of_spends
    set_remained(user_id, remained)


def get_goal(user_id):
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    logging.debug(f"Получаем цель средств для пользователя с id: {user_id}.")
    goal = 0.00
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT * FROM user_data WHERE id = 1")
        goal = sql.fetchone()[2]
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return goal
    finally:
        if db:
            db.close()
    return goal


def get_limit(user_id):
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    logging.debug(f"Получаем лимит средств для пользователя с id: {user_id}.")
    limit = 0.00
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT * FROM user_data WHERE id = 1")
        limit = sql.fetchone()[1]
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return limit
    finally:
        if db:
            db.close()
    return limit


def get_remained(user_id):
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'data/{user_id}.db')
    logging.debug(f"Получаем остаток средств для пользователя с id: {user_id}.")
    remained = 0.00
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT * FROM user_data WHERE id = 1")
        remained = sql.fetchone()[3]
    except sqlite3.Error as error:
        logging.error(f"Ошибка при работе с базой данных: '{error}'.Пользователь с id: '{user_id}'")
        return remained
    finally:
        if db:
            db.close()
    return remained


def check_goal(user_id):
    goal = get_goal(user_id)
    if goal is None:
        return None
    remained = get_remained(user_id)
    if remained is None:
        return None
    if remained < 0:
        return False
    if remained < goal:
        return False
    else:
        return True


def check_limit(user_id):
    limit = get_limit(user_id)
    if limit is None:
        return None
    spend_sum = return_sum_spend(user_id, None, None, True)
    if spend_sum <= limit:
        return True
    else:
        return False


initialize_user("test")
add_new_category('test', "Еда")
add_new_category('test', "да")
add_new_category('test', "Умммм")
add_new_category('test', "У")
add_new_subcategory('test', "Еда", "d")
add_new_subcategory('test', "Еда", "s")
add_new_subcategory('test', "Еда", "k")
add_new_subcategory('test', "Еда", "f")
add_new_subcategory('test', "да", "f")
add_new_subcategory('test', "У", "фыф")
add_event_spend('test', 10.1, "Музыка", 10)
add_event_spend('test', 10.4, "GAMES", 10)
add_event_income('test', 10.12, "Зарплата", 10)
add_event_income('test', 10.2, "Музыка", 9)
add_event_income('test', 10.4, "GAMES", 9)
delete_event_income('test', 'GAMES')
delete_event_income('test', 'Музыка')
delete_category('test', 'да')
delete_subcategory('test', 'Еда', 'd')

execute_events('test')

print(return_sum_income('test', datetime.datetime(2023, 1, 10), datetime.datetime(2023, 1, 10)))
print(return_incomes_of_period('test', datetime.datetime(2012, 2, 10), datetime.datetime(2023, 3, 12)))
print(return_sum_spend('test', datetime.datetime(2023, 1, 10), datetime.datetime(2023, 1, 10)))
print(return_spend_of_period('test', datetime.datetime(2023, 1, 10), datetime.datetime(2023, 1, 10)))

print(return_all_categories('test'))

count_remained('test')
delete_spend_by_id('test', 25)
add_spend('test', 11, "EW")
delete_income_by_id('test', 1)
set_limit('test', 600)
set_remained('test', 99)
set_goal('test', 100)
print(get_limit('test'))
print(get_goal('test'))
print(check_limit('test'))
print(check_goal('test'))
