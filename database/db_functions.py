import datetime
import json
import logging
import sqlite3
import time
from sqlite3 import Connection, Cursor

import config.config
import helpers.helpers
# Получаем доступ к дополнительным функциям
import helpers.parser


async def initialize_user(user_id: str) -> bool:
    """
    Инициализирует пользователя с определенным id. Создаёт db если ее нет для пользователя.
    Устанавливает начальные категории, если их нет у пользователя.
    :param user_id: ID пользователя в Telegram.
    :return: Boolean значение удалось ли произвести действие.
    """
    logging.debug(f"Инициализация пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
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
                        (1, None, None, None, 'RUB', utctime))
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
        await add_init_categories(str(user_id))
    except sqlite3.Error as error:
        logging.error(
            f"{initialize_user.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    logging.debug(f"Инициализация пользователя с id: {user_id} закончена.")
    return True


async def add_init_categories(user_id: str) -> bool:
    """
    Добавляет лист категорий пользователю, если он пуст.
    :param user_id: ID пользователя в Telegram.
    :return: Boolean значение удалось ли произвести действие.
    """
    logging.debug(f"Пытаемся добавить начальные категории для пользователя с id: {user_id}.")
    try:
        categories = config.config.INIT_DICT_OF_CATEGORIES
        check = (await return_all_categories(user_id)).keys()
        if len(check) == 0:
            for category in categories.keys():
                await add_new_category(user_id, category)
                for subcategory in categories[category]:
                    await add_new_subcategory(user_id, category, subcategory)
            return True
        return False
    except Exception as error:
        logging.error(
            f"{add_init_categories.__name__}: Ошибка при добавлении init категорий: '{error}'. "
            f"Пользователь с id: '{user_id}'")
        return False


async def set_limit(user_id: str, limit: float) -> bool:
    """
    Устанавливает лимит по средствам для определённого пользователя.
    :param user_id: ID пользователя в Telegram.
    :param limit: Лимит по средствам.
    :return: Boolean значение удалось ли произвести действие.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Устанавливаем лимит средств для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"UPDATE user_data SET 'limit' = ? WHERE id = 1", (limit,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{set_limit.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def set_remained(user_id: str, remained: float) -> bool:
    """
    Устанавливает остаток по средствам для определённого пользователя.
    :param user_id: ID пользователя в Telegram.
    :param remained: Лимит по средствам.
    :return: Boolean значение удалось ли произвести действие.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Устанавливаем остаток средств для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"UPDATE user_data SET remainer = ? WHERE id = 1", (remained,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{set_remained.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def set_goal(user_id: str, goal: float) -> bool:
    """
    Устанавливает цель по средствам для определённого пользователя.
    :param user_id: ID пользователя в Telegram.
    :param goal: Цель по средствам.
    :return: Boolean значение удалось ли произвести действие.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Устанавливаем цель для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"UPDATE user_data SET goal = ? WHERE id = 1", (goal,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{set_goal.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def add_income(user_id: str, value: float, name: str = None, type_of_income: str = None,
                     date: str = time.strftime("%Y-%m-%d", time.gmtime())) -> bool:
    """
    Добавляет доход пользователю.
    :param user_id: ID пользователя в Telegram.
    :param value: Значение полученных средств в текущей валюте.
    :param name: Имя дохода.
    :param type_of_income: Тип дохода.
    :param date: Время дохода.
    :return: Удалось ли добавить доход.
    """
    logging.debug(f"Добавляем запись о доходе пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(
            "INSERT INTO income(name_of_income, type_of_income, value_of_income, date_of_income) VALUES (?, ?, ?, ?)",
            (name, type_of_income, value, date))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{add_income.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def add_event_income(user_id: str, value: float, name: str, day_of_income: int) -> bool:
    """
    Добавляет событие дохода пользователю.
    :param user_id: ID пользователя в Telegram.
    :param value: Значение дохода.
    :param name: Название дохода события.
    :param day_of_income: Дата месяца.
    :return: Удалось ли произвести действие.
    """
    logging.debug(f"Добавляем запись о СОБЫТИИ дохода пользователя с id: {user_id}.")
    if day_of_income < 1 or day_of_income > 28:
        logging.error(
            f"{add_event_income.__name__}: Дата не лежит в переделе от 1 до 28. Пользователь с id: '{user_id}'")
        return False
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        utctime = time.strftime("%Y-%m-%d", time.gmtime())
        sql.execute("INSERT INTO event_income VALUES (?, ?, ?, ?, ?)", (name, value, day_of_income, None, utctime))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{add_event_income.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def add_spend(user_id: str, value: float, name: str = None, type_of_spend: str = None, category: str = None,
                    subcategory: str = None, date: str = time.strftime("%Y-%m-%d", time.gmtime())) -> bool:
    """
    Добавляет трату пользователю.
    :param subcategory: Подкатегория траты.
    :param category: Категория траты.
    :param user_id: ID пользователя в Telegram.
    :param value: Значение потраченных средств в текущей валюте.
    :param name: Имя траты.
    :param type_of_spend: Тип траты.
    :param date: Время траты.
    :return: Удалось ли добавить трату.
    """
    logging.debug(f"Добавляем запись о тратах пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(
            "INSERT INTO spend(name_of_spend, type_of_spend, value_of_spend, category, sub_category, date_of_spend) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, type_of_spend, value, category, subcategory, date))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{add_spend.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def add_event_spend(user_id: str, value: float, name: str, day_of_spending: int, category: str = None,
                          subcategory: str = None) -> bool:
    """
    Добавляет событие траты пользователю.
    :param subcategory: Подкатегория траты.
    :param category: Категория траты.
    :param user_id: ID пользователя в Telegram.
    :param value: Значение потраченных средств в текущей валюте.
    :param name: Имя траты.
    :param day_of_spending: Число месяца траты.
    :return: Удалось ли добавить событие траты.
    """
    logging.debug(f"Добавляем запись о СОБЫТИИ трат пользователя с id: {user_id}.")
    if day_of_spending < 1 or day_of_spending > 28:
        logging.error(
            f"{add_event_spend.__name__}: Дата не лежит в переделе от 1 до 28. Пользователь с id: '{user_id}'")
        return False
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        utctime = time.strftime("%Y-%m-%d", time.gmtime())
        sql.execute("INSERT INTO event_spend VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, value, category, subcategory, day_of_spending, None, utctime))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{add_event_spend.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def add_new_category(user_id: str, category: str) -> bool:
    """
    Добавляет пользователю новую категорию.
    :param user_id: ID пользователя в Telegram.
    :param category: Название категории.
    :return: Удалось ли добавить категорию.
    """
    logging.debug(f"Добавляем новую категорию пользователю с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute("INSERT INTO categories VALUES (?, ?)", (category, "{}"))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{add_new_category.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def add_new_subcategory(user_id: str, category: str, subcategory: str) -> bool:
    """
    Добавляет пользователю в категорию подкатегорию.
    :param user_id: ID пользователя в Telegram.
    :param category: Название уже существующей категории.
    :param subcategory: Название новой подкатегории.
    :return: Удалось ли добавить подкатегорию.
    """
    logging.debug(f"Добавляем новую подкатегорию в категорию пользователю с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT sub_categories FROM categories WHERE name_of_category = ?", (category,))
        tuple_data = sql.fetchone()
        if tuple_data is None:
            db.close()
            logging.error(f"{add_new_subcategory.__name__}: Нет родительской категории. Пользователь с id: '{user_id}'")
            return False

        subcategories = json.loads(str(tuple_data[0]))
        if subcategory in subcategories.keys():
            db.close()
            logging.error(
                f"{add_new_subcategory.__name__}: Такая подкатегория уже есть! Пользователь с id: '{user_id}'")
            return False
        subcategories[subcategory] = 0
        to_write = json.dumps(subcategories)

        sql.execute("UPDATE categories SET sub_categories = ? WHERE name_of_category = ?", (str(to_write), category))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{add_new_subcategory.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return False
    except Exception as e:
        logging.error(
            f"{add_new_subcategory.__name__}: Ошибка при работе с базой данных: '{e}'. Не на стороне базы."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def delete_event_spend(user_id: str, name_of_spending: str) -> bool:
    """
    Удаляет событие трат у пользователя по имени события.
    :param user_id: ID пользователя в Telegram.
    :param name_of_spending: Имя события трат.
    :return: Удалось ли удалить событие трат.
    """
    logging.debug(f"Удаляем СОБЫТИЕ трат у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from event_spend where name_of_spending = ?", (name_of_spending,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{delete_event_spend.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def delete_event_income(user_id: str, name_of_income: str) -> bool:
    """
    Удаляет событие дохода у пользователя по имени события.
    :param user_id: ID пользователя в Telegram.
    :param name_of_income: Имя события дохода.
    :return: Удалось ли удалить событие дохода.
    """
    logging.debug(f"Удаляем СОБЫТИЕ получения средств у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from event_income where name_of_income = ?", (name_of_income,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{delete_event_income.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def delete_category(user_id: str, name_of_category: str) -> bool:
    """
    Удаляет категорию по ее имени.
    :param user_id: ID пользователя в Telegram.
    :param name_of_category: Имя категории.
    :return: Удалось ли удалить категорию без ошибок.
    """
    logging.debug(f"Удаляем категорию у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from categories where name_of_category = ?", (name_of_category,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{delete_category.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def delete_subcategory(user_id: str, category: str, subcategory: str) -> bool:
    """
    Удаляет подкатегорию по имени в категории пользователя.
    :param user_id: ID пользователя в Telegram.
    :param category: Имя категории в которой будем производить удаление.
    :param subcategory: Имя подкатегории, которую будем удалять.
    :return: Удалось ли произвести удаление без ошибок.
    """
    logging.debug(f"Удаляем подкатегорию в категории пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT sub_categories FROM categories WHERE name_of_category = ?", (category,))
        tuple_data = sql.fetchone()
        if tuple_data is None:
            logging.error(f"{delete_subcategory.__name__}: Нет родительской категории. Пользователь с id: '{user_id}'")
            return False

        subcategories = json.loads(str(tuple_data[0]))
        if subcategory not in subcategories.keys():
            logging.error(f"{delete_subcategory.__name__}: Такой подкатегории нет! Пользователь с id: '{user_id}'")
            return False
        del subcategories[subcategory]
        to_write = json.dumps(subcategories)
        sql.execute("UPDATE categories SET sub_categories = ? WHERE name_of_category = ?", (str(to_write), category))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{delete_subcategory.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return False
    except Exception as e:
        logging.error(
            f"{delete_subcategory.__name__}: Ошибка при работе с базой данных: '{e}'. Не на стороне базы."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def execute_events(user_id: str) -> bool:
    """
    Исполняет события трат и доходов пользователя с учетом прошедшего с последнего исполнения времени.
    :param user_id: ID пользователя в Telegram.
    :return: Удалось ли выполнить события.
    """
    utctime_str = time.strftime("%Y-%m-%d", time.gmtime())
    utctime = datetime.datetime.now()
    logging.debug(f"Исполняем события пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
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
                    num_of_spend += 1
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
                    num_of_spend += 1
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
            await add_spend(spend[0], spend[1], spend[2], spend[3], spend[4], spend[5], spend[6])
        for i in all_events_income.keys():
            income = all_events_income[i]
            await add_income(income[0], income[1], income[2], income[3], income[4])
    except sqlite3.Error as error:
        logging.error(
            f"{execute_events.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return False
    except Exception as e:
        logging.error(
            f"{execute_events.__name__}: Ошибка при работе с базой данных: '{e}'. Не на стороне базы."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def return_all_spends(user_id: str) -> dict:
    """
    Возвращает все траты пользователя из db в виде словаря.
    :param user_id: ID пользователя в Telegram.
    :return: Словарь трат.
    """
    logging.debug(f"Возвращаем все траты пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    all_spend = {}
    try:
        sql: Cursor = db.cursor()
        for row in sql.execute(f"SELECT * FROM spend"):
            all_spend[row[0]] = {}
            all_spend[row[0]]["id"] = row[0]
            all_spend[row[0]]["name_of_spend"] = row[1]
            all_spend[row[0]]["type_of_spend"] = row[2]
            all_spend[row[0]]["value_of_spend"] = row[3]
            all_spend[row[0]]["category"] = row[4]
            all_spend[row[0]]["sub_category"] = row[5]
            all_spend[row[0]]["date_of_spend"] = row[6]
    except sqlite3.Error as error:
        logging.error(
            f"{return_all_spends.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return {}
    finally:
        if db:
            db.close()
    return all_spend


async def return_all_incomes(user_id: str) -> dict:
    """
    Возвращает все доходы пользователя из db в виде словаря.
    :param user_id: ID пользователя в Telegram.
    :return: Словарь доходов.
    """
    logging.debug(f"Возвращаем все доходы пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    all_incomes = {}
    try:
        sql: Cursor = db.cursor()
        for row in sql.execute(f"SELECT * FROM income"):
            all_incomes[row[0]] = {}
            all_incomes[row[0]]["id"] = row[0]
            all_incomes[row[0]]["name_of_income"] = row[1]
            all_incomes[row[0]]["type_of_income"] = row[2]
            all_incomes[row[0]]["value_of_income"] = row[3]
            all_incomes[row[0]]["date_of_income"] = row[4]
    except sqlite3.Error as error:
        logging.error(
            f"{return_all_incomes.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return {}
    finally:
        if db:
            db.close()
    return all_incomes


async def return_spend_of_period(user_id: str, start: datetime, end: datetime, this_moths: bool = False) -> dict:
    """
    Возвращает словарь с тратами за определенный период или за текущий месяц.
    :param user_id: ID пользователя в Telegram.
    :param start: Время начала периода.
    :param end: Конец временного отрезка.
    :param this_moths: В этом ли месяце возвращать траты.
    :return: Словарь с тратами.
    """
    logging.debug(f"Возвращаем траты в заданном периоде пользователя с id: {user_id}.")
    all_spends = await return_all_spends(user_id)
    time_points = helpers.helpers.get_dates_of_period(start, end, this_moths)
    spends_of_period = {}
    for time_point in time_points:
        time_of_check = datetime.datetime.strftime(time_point, '%Y-%m-%d')
        for spend in all_spends.keys():
            if all_spends[spend]['date_of_spend'] == time_of_check:
                spends_of_period[spend] = all_spends[spend]
    return spends_of_period


async def return_incomes_of_period(user_id: str, start: datetime, end: datetime, this_moths: bool = False) -> dict:
    """
    Возвращает словарь с доходами за определенный период или за текущий месяц.
    :param user_id: ID пользователя в Telegram.
    :param start: Время начала периода.
    :param end: Конец временного отрезка.
    :param this_moths: В этом ли месяце возвращать доходы.
    :return: Словарь с доходами.
    """
    logging.debug(f"Возвращаем доходы в заданном периоде пользователя с id: {user_id}.")
    all_incomes = await return_all_incomes(user_id)
    time_points = helpers.helpers.get_dates_of_period(start, end, this_moths)
    incomes_of_period = {}
    for time_point in time_points:
        time_of_check = datetime.datetime.strftime(time_point, '%Y-%m-%d')
        for spend in all_incomes.keys():
            if all_incomes[spend]['date_of_income'] == time_of_check:
                incomes_of_period[spend] = all_incomes[spend]
    return incomes_of_period


async def return_sum_income(user_id: str, start: datetime, end: datetime, this_moths: bool = False) -> float:
    """
    Возвращает сумму доходов за определенный период или текущий месяц.
    :param user_id: ID пользователя в Telegram.
    :param start: Время начала периода.
    :param end: Конец временного отрезка.
    :param this_moths: В этом ли месяце возвращать сумму доходов.
    :return: Сумма доходов.
    """
    logging.debug(f"Возвращаем сумму доходов пользователя с id: {user_id}.")
    sum_income = 0.00
    incomes = await return_incomes_of_period(user_id, start, end, this_moths)
    for i in incomes.keys():
        sum_income += incomes[i]['value_of_income']
    return sum_income


async def return_sum_spend(user_id: str, start: datetime, end: datetime, this_moths: bool = False) -> float:
    """
    Возвращает сумму трат за определенный период или текущий месяц.
    :param user_id: ID пользователя в Telegram.
    :param start: Время начала периода.
    :param end: Конец временного отрезка.
    :param this_moths: В этом ли месяце возвращать сумму трат.
    :return: Сумма трат.
    """
    logging.debug(f"Возвращаем сумму трат пользователя с id: {user_id}.")
    sum_spend = 0.00
    spends = await return_spend_of_period(user_id, start, end, this_moths)
    for i in spends.keys():
        sum_spend += spends[i]['value_of_spend']
    return sum_spend


async def return_all_categories(user_id: str) -> dict:
    """
    Возвращает все категории пользователя в виде словаря.
    :param user_id: ID пользователя в Telegram.
    :return: Словарь со всеми категориями.
    """
    logging.debug(f"Возвращаем все категории пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
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
        logging.error(
            f"{return_all_categories.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return {}
    finally:
        if db:
            db.close()
    return all_categories


async def delete_spend_by_id(user_id: str, spend_id: int) -> bool:
    """
    Удаляет трату по id у пользователя.
    :param user_id: ID пользователя в Telegram.
    :param spend_id: ID траты в db пользователя.
    :return: Удалось ли удалить трату без ошибок.
    """
    logging.debug(f"Удаляем трату у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from spend where id = ?", (spend_id,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{delete_spend_by_id.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def delete_income_by_id(user_id: str, income_id: int) -> bool:
    """
    Удаляет доход по id у пользователя.
    :param user_id: ID пользователя в Telegram.
    :param income_id: ID дохода в db пользователя.
    :return: Удалось ли удалить доход без ошибок.
    """
    logging.debug(f"Удаляем доход у пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"DELETE from income where id = ?", (income_id,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{delete_income_by_id.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def count_remained(user_id: str) -> bool:
    """
    Считает и устанавливает остаток на текущий месяц.
    :param user_id: ID пользователя Telegram.
    :return: Удалось ли установить остаток.
    """
    sum_of_spends = await return_sum_spend(user_id, None, None, True)
    sum_of_incomes = await return_sum_income(user_id, None, None, True)
    remained = sum_of_incomes - sum_of_spends
    if remained < 0:
        remained = 0
    return await set_remained(user_id, remained)


async def get_goal(user_id: str) -> float or None:
    """
    Возвращает цель по средствам.
    :param user_id: ID пользователя Telegram.
    :return: Сумму цели по средствам.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Получаем цель средств для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT * FROM user_data WHERE id = 1")
        goal = sql.fetchone()[2]
    except sqlite3.Error as error:
        logging.error(
            f"{get_goal.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return None
    finally:
        if db:
            db.close()
    return goal


async def get_limit(user_id: str) -> float or None:
    """
    Возвращает лимит по средствам.
    :param user_id: ID пользователя Telegram.
    :return: Сумму лимита по средствам.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Получаем лимит средств для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT * FROM user_data WHERE id = 1")
        limit = sql.fetchone()[1]
    except sqlite3.Error as error:
        logging.error(
            f"{get_limit.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return None
    finally:
        if db:
            db.close()
    return limit


async def get_remained(user_id: str) -> float or None:
    """
    Получает остаток по средствам и возвращает его.
    :param user_id: ID пользователя в Telegram.
    :return: Сумму остатка по средствам.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Получаем остаток средств для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT * FROM user_data WHERE id = 1")
        remained = sql.fetchone()[3]
    except sqlite3.Error as error:
        logging.error(
            f"{get_remained.__name__}: Ошибка при работе с базой данных: '{error}'. Пользователь с id: '{user_id}'")
        return None
    finally:
        if db:
            db.close()
    return remained


async def check_goal(user_id: str) -> bool or None:
    """
    Выполнена ли цель по средствам.
    :param user_id: ID пользователя Telegram.
    :return: Выполнена ли цель по средствам.
    """
    goal = await get_goal(user_id)
    if goal is None:
        return None
    remained = await get_remained(user_id)
    if remained is None:
        return None
    if remained < 0:
        return False
    if remained < goal:
        return False
    else:
        return True


async def check_limit(user_id: str) -> bool or None:
    """
    Выполнен ли лимит по средствам.
    :param user_id: ID пользователя Telegram.
    :return: Выполнена ли цель по средствам.
    """
    limit = await get_limit(user_id)
    if limit is None:
        return None
    spend_sum = await return_sum_spend(user_id, None, None, True)
    if spend_sum <= limit:
        return True
    else:
        return False


async def get_user_currency(user_id: str) -> str:
    """
    Возвращает текущую валюту пользователя.
    :param user_id: ID пользователя Telegram.
    :return: Валюта в трехбуквенном представлении.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Получаем валюту для пользователя с id: {user_id}.")
    currency = ""
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"SELECT * FROM user_data WHERE id = 1")
        currency = sql.fetchone()[4]
    except sqlite3.Error as error:
        logging.error(
            f"{get_user_currency.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return currency
    finally:
        if db:
            db.close()
    return currency


async def _set_user_currency(user_id: str, new_currency: str) -> bool:
    """
    Устанавливает текущую валюту пользователя в информационное поле.
    :param user_id: ID пользователя Telegram.
    :param new_currency: Название новой валюты.
    :return: Удалось ли установить новую валюту без ошибок.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Меняем валюту для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        sql.execute(f"UPDATE user_data SET currency = ? WHERE id = 1", (new_currency,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{_set_user_currency.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True


async def _recount_all_values_of_user(user_id: str, exchange_rate: float) -> bool:
    """
    Пересчитывает все значения в db в новую валюту, получая соотношения текущей валюты к новой.
    :param user_id: ID пользователя Telegram.
    :param exchange_rate: Обменный курс. Соотношение старой валюты к новой.
    :return: Удалось ли пересчитать значения.
    """
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    logging.debug(f"Меняем валюту для пользователя с id: {user_id}.")
    try:
        sql: Cursor = db.cursor()
        # Обновляем значения в таблице event_income
        sql.execute("UPDATE event_income SET value_of_income = round(value_of_income * ?, 2)", (exchange_rate,))
        # Обновляем значения в таблице event_spend
        sql.execute("UPDATE event_spend SET value_of_spending = round(value_of_spending * ?, 2)", (exchange_rate,))
        # Обновляем значения в таблице income
        sql.execute("UPDATE income SET value_of_income = round(value_of_income * ?, 2)", (exchange_rate,))
        # Обновляем значения в таблице spend
        sql.execute("UPDATE spend SET value_of_spend = round(value_of_spend * ?, 2)", (exchange_rate,))
        # Обновляем значения в таблице user_data
        sql.execute("UPDATE user_data SET goal = round(goal * ?, 2)", (exchange_rate,))
        lim = (await get_limit(user_id))
        if lim is not None:
            lim = lim * exchange_rate
            sql.execute("UPDATE user_data SET 'limit' = round(?, 2)", (lim,))
        sql.execute("UPDATE user_data SET remainer = round(remainer * ?, 2)", (exchange_rate,))
        db.commit()
    except sqlite3.Error as error:
        logging.error(
            f"{_recount_all_values_of_user.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return False
    finally:
        if db:
            db.close()
    return True
    pass


async def recount_values_in_new_currency(user_id: str, to_currency: str) -> bool:
    """
    Пересчитывает все значения в db согласно текущему курсу валют.
    :param user_id: ID пользователя в Telegram
    :param to_currency: Строка из трех букв, представляющая новую валюту
    :return: Удалось ли пересчитать значения и установить информацию.
    """
    logging.debug(f"Пересчитываем валюту для пользователя с id: {user_id}.")
    now_currency = await get_user_currency(user_id)
    if now_currency == to_currency:
        logging.debug(f"{recount_values_in_new_currency.__name__}: Предупреждение! Смена на ту же валюту для "
                      f"пользователя с id: {user_id}.")
        return False
    try:
        exchange_rate = helpers.parser.get_exchange_rate(now_currency, to_currency)
        status = await _recount_all_values_of_user(user_id, exchange_rate)
        status = status and await _set_user_currency(user_id, to_currency)
        return status
    except Exception as e:
        logging.error(f"{recount_values_in_new_currency.__name__}: {e} для "
                      f"пользователя с id: {user_id}.")
        return False


async def transfer_remained_from_past_months(user_id: str) -> bool:
    """
    Переносит остаток у пользователя с предыдущего месяца как доход.
    :param user_id: ID пользователя в Telegram.
    :return: Удалось ли перенести остаток с прошлого месяца.
    """
    logging.debug(f"Переносим остаток с прошлого месяца для пользователя с id: {user_id}.")
    past_months = helpers.helpers.get_past_months()
    sum_of_spends = await return_sum_spend(user_id, past_months[0], past_months[1])
    sum_of_incomes = await return_sum_income(user_id, past_months[0], past_months[1])
    remained = sum_of_incomes - sum_of_spends
    flag_is_used_this_months = False
    incomes = await return_incomes_of_period(user_id, None, None, True)
    for row in incomes:
        if incomes[row]['type_of_income'] == 'remained':
            flag_is_used_this_months = True
            break
    if flag_is_used_this_months:
        logging.debug(f"{transfer_remained_from_past_months.__name__}: Предупреждение! Перенос уже использован для "
                      f"пользователя с id: {user_id} в этом месяце.")
        return False
    if remained > 0:
        status = await add_income(user_id, remained, f"Остаток с прошлого месяца", type_of_income="remained",
                                  date=time.strftime("%Y-%m-%d", time.gmtime()))
    else:
        logging.debug(f"{transfer_remained_from_past_months.__name__}: Предупреждение! Неположительный остаток для "
                      f"пользователя с id: {user_id}.")
        status = False
    return status


async def return_all_events_spends(user_id: str) -> dict:
    """
    Возвращает все события трат пользователя из db в виде словаря.
    :param user_id: ID пользователя в Telegram.
    :return: Словарь трат.
    """
    logging.debug(f"Возвращаем все траты пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    all_spend = {}
    try:
        sql: Cursor = db.cursor()
        for row in sql.execute(f"SELECT * FROM event_spend"):
            all_spend[row[0]] = {}
            all_spend[row[0]]["name_of_spending"] = row[0]
            all_spend[row[0]]["value_of_spending"] = row[1]
            all_spend[row[0]]["category"] = row[2]
            all_spend[row[0]]["sub_category"] = row[3]
            all_spend[row[0]]["day_of_spending"] = row[4]
            all_spend[row[0]]["last_indexed"] = row[5]
    except sqlite3.Error as error:
        logging.error(
            f"{return_all_events_spends.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return {}
    finally:
        if db:
            db.close()
    return all_spend


async def return_all_events_income(user_id: str) -> dict:
    """
    Возвращает все события доходов пользователя из db в виде словаря.
    :param user_id: ID пользователя в Telegram.
    :return: Словарь трат.
    """
    logging.debug(f"Возвращаем все траты пользователя с id: {user_id}.")
    # Подключаем базу данных определённого пользователя.
    db: Connection = sqlite3.connect(f'database/data/{user_id}.db')
    all_income = {}
    try:
        sql: Cursor = db.cursor()
        for row in sql.execute(f"SELECT * FROM event_income"):
            all_income[row[0]] = {}
            all_income[row[0]]["name_of_income"] = row[0]
            all_income[row[0]]["value_of_income"] = row[1]
            all_income[row[0]]["day_of_income"] = row[2]
            all_income[row[0]]["last_indexed"] = row[3]
    except sqlite3.Error as error:
        logging.error(
            f"{return_all_events_income.__name__}: Ошибка при работе с базой данных: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return {}
    finally:
        if db:
            db.close()
    return all_income


async def get_spends_of_user_by_categories(user_id: str, start: datetime, end: datetime) -> dict:
    """
    Функция, которая возвращает траты пользователя по категориям в виде словаря сумм.
    :param user_id: ID пользователя в Telegram.
    :param start: Начало периода.
    :param end: Конец периода.
    :return: Словарь с суммами трат по всем категориям.
    """
    try:
        categories = await return_all_categories(user_id)
        spends = await return_spend_of_period(user_id, start, end)
        answer_sum = {'$no_category': {"$all": 0.0}}
        for id_spend in spends.keys():
            if spends[id_spend]['category'] is None or spends[id_spend]['category'] not in categories.keys():
                answer_sum['$no_category']['$all'] += spends[id_spend]['value_of_spend']
        for category in categories.keys():
            answer_sum[category] = {"$no_subcategory": 0.0, "$all": 0.0}
            for sub in categories[category]:
                answer_sum[category][sub] = 0.0
            for id_spend in spends.keys():
                if spends[id_spend]['category'] == category:
                    answer_sum[category]["$all"] += spends[id_spend]['value_of_spend']
                    if spends[id_spend]['sub_category'] in categories[category]:
                        answer_sum[category][spends[id_spend]['sub_category']] += spends[id_spend]['value_of_spend']
                    else:
                        answer_sum[category]['$no_subcategory'] += spends[id_spend]['value_of_spend']
        return answer_sum
    except Exception as error:
        logging.error(
            f"{return_all_events_income.__name__}: Ошибка при получении сумм по категориям: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return {}


async def get_full_spends_of_user_by_categories(user_id: str, start: datetime, end: datetime) -> dict:
    """
    Функция, которая возвращает траты пользователя по категориям в виде словаря с тратами.
    :param user_id: ID пользователя в Telegram.
    :param start: Начало периода.
    :param end: Конец периода.
    :return: Словарь со списками трат по всем категориям.
    """
    try:
        categories = await return_all_categories(user_id)
        spends = await return_spend_of_period(user_id, start, end)
        answer_sum = {'$no_category': {"$all": []}}
        for id_spend in spends.keys():
            if spends[id_spend]['category'] is None or spends[id_spend]['category'] not in categories.keys():
                answer_sum['$no_category']['$all'].append(spends[id_spend])
        for category in categories.keys():
            answer_sum[category] = {"$no_subcategory": [], "$all": []}
            for sub in categories[category]:
                answer_sum[category][sub] = []
            for id_spend in spends.keys():
                if spends[id_spend]['category'] == category:
                    answer_sum[category]["$all"].append(spends[id_spend])
                    if spends[id_spend]['sub_category'] in categories[category]:
                        answer_sum[category][spends[id_spend]['sub_category']].append(spends[id_spend])
                    else:
                        answer_sum[category]['$no_subcategory'].append(spends[id_spend])
        return answer_sum
    except Exception as error:
        logging.error(
            f"{get_full_spends_of_user_by_categories.__name__}: Ошибка при получении сумм по категориям: '{error}'."
            f" Пользователь с id: '{user_id}'")
        return {}


async def return_sum_income_ignore_remained(user_id: str, start: datetime, end: datetime,
                                            this_moths: bool = False) -> float:
    """
    Возвращает сумму доходов за определенный период или текущий месяц игнорируя остатки.
    :param user_id: ID пользователя в Telegram.
    :param start: Время начала периода.
    :param end: Конец временного отрезка.
    :param this_moths: В этом ли месяце возвращать сумму доходов.
    :return: Сумма доходов.
    """
    logging.debug(f"Возвращаем сумму доходов (без остатков) пользователя с id: {user_id}.")
    sum_income = 0.00
    incomes = await return_incomes_of_period(user_id, start, end, this_moths)
    for i in incomes.keys():
        if incomes[i]['type_of_income'] != 'remained':
            sum_income += incomes[i]['value_of_income']
    return sum_income
