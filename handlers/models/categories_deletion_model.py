from aiogram.dispatcher.filters.state import State, StatesGroup


class CategoriesAddingForm(StatesGroup):
    """
    Класс, отвечающий за хранение состояний добавления сумм как доходов или трат.
    """
    # Хранит значение
    start = State()
    # Является ли сумма тратой
    delete_income = State()
    # Имя суммы
    delete_spend = State()
    # Категория траты
    add_category = State()
    # Подкатегория траты
    add_subcategory_by_category = State()
    add_subcategory = State()
    # Дата суммы
    delete_category = State()
    delete_subcategory_by_category = State()
    delete_subcategory = State()
