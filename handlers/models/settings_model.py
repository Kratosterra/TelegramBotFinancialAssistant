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
