from aiogram.dispatcher.filters.state import State, StatesGroup


class SettingsForm(StatesGroup):
    """
    Класс, отвечающий за хранение состояний настроек.
    """
    # Стартовое значение
    start = State()
    # Состояние смены валюты
    change_currency = State()
    # Состояние смены лимита
    change_limit = State()
    # Состояние смены цели
    change_goal = State()
    # Состояние смены остатка.
    transfer_remainer = State()
    # Удаляем событие
    delete_event = State()
    # Удаление событие траты
    delete_event_spend = State()
    # Удаляем событие доходов
    delete_event_income = State()
    # Добавляем событие
    add_event = State()
    # Хранит значение
    value = State()
    # Меню добавления события
    event_menu = State()
    # Является ли сумма тратой
    isSpend = State()
    # Имя суммы
    name = State()
    # Категория траты
    category = State()
    # Подкатегория траты
    subcategory = State()
    # Дата суммы
    date = State()
