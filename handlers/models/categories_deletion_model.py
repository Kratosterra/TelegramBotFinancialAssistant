from aiogram.dispatcher.filters.state import State, StatesGroup


class CategoriesAddingForm(StatesGroup):
    """
    Класс, отвечающий за хранение состояний меню Траты и Доходы.
    """
    # Стартовое значение
    start = State()
    # Удаление дохода
    delete_income = State()
    # Удаление траты
    delete_spend = State()
    # Добавление категории
    add_category = State()
    # Добавление подкатегории
    add_subcategory_by_category = State()
    add_subcategory = State()
    # Удаление категории
    delete_category = State()
    # Удаление подкатегории траты
    delete_subcategory_by_category = State()
    delete_subcategory = State()
