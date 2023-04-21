from aiogram.dispatcher.filters.state import State, StatesGroup


class SettingsForm(StatesGroup):
    """
    Класс, отвечающий за хранение состояний настроек.
    """
    # Стартовое значение
    start = State()
