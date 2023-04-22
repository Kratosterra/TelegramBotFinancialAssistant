import json
import logging

import requests
from bs4 import BeautifulSoup

from config.config import currency


def get_exchange_rate(now_currency: str, new_currency: str) -> float:
    """
    Получает обменный курс для двух валют в виде соотношения текущей валюты к новой.
    :param now_currency: Текущая валюта.
    :param new_currency: Новая валюта.
    :return: Обменный курс в виде соотношения текущей валюты к новой.
    """
    if now_currency not in currency.keys() or new_currency not in currency.keys():
        raise Exception(f"{get_exchange_rate.__name__}: Одна из представленных валют не существует в представлении.")
    return get_exchange_rate_dict(now_currency)[currency[new_currency]]


def get_exchange_rate_dict(currency_str: str) -> dict:
    """
    Возвращает словарь с обменными курсами для валют.
    :param currency_str: Валюта в трехбуквенном строковом представлении
    :return: Словарь с обменным курсом для валют
    """
    exchange_rates = {}
    try:
        full_content = requests.get(f"https://www.x-rates.com/table/?from={currency_str}&amount=1").content
        html_data = BeautifulSoup(full_content, "html.parser")
        exchange_tables = html_data.find_all("table")
        for exchange_table in exchange_tables:
            for tr in exchange_table.find_all("tr"):
                tds = tr.find_all("td")
                if tds:
                    currency_data = tds[0].text
                    exchange_rate = float(tds[1].text)
                    exchange_rates[currency_data] = exchange_rate
        # Сохранить данные
        with open('config/currencies.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        data[currency_str] = exchange_rates
        with open('config/currencies.json', 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"{get_exchange_rate_dict.__name__}: {e}. Используем старые данные!")
        with open('config/currencies.json', 'r') as f:
            json_string = f.read()
            data = json.loads(json_string)
        exchange_rates = data[currency_str]
    return exchange_rates
