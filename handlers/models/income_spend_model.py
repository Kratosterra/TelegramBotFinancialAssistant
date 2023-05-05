from aiogram.dispatcher.filters.state import State, StatesGroup


class IncomeSpendForm(StatesGroup):
    """
    Класс, отвечающий за хранение состояний добавления сумм как доходов или трат.
    """
    # Хранит значение
    value = State()
    # Является ли сумма тратой
    is_spend = State()
    # Имя суммы
    name = State()
    # Категория траты
    category = State()
    # Подкатегория траты
    subcategory = State()
    # Дата суммы
    date = State()
