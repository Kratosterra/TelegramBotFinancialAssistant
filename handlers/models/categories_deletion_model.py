from aiogram.dispatcher.filters.state import State, StatesGroup


class CategoriesAddingForm(StatesGroup):
    """
    Класс, отвечающий за хранение состояний меню Категории.
    """
    # Стартовое значение
    start = State()
    # Удаление дохода
    delete_income = State()
    # Удаление траты
    delete_spend = State()
    # Добавление категории
    add_category = State()
    # Добавление подкатегории (информация о категории)
    add_subcategory_by_category = State()
    # Добавление подкатегории
    add_subcategory = State()
    # Удаление категории
    delete_category = State()
    # Удаление подкатегории траты (информация о категории)
    delete_subcategory_by_category = State()
    # Удаление подкатегории траты
    delete_subcategory = State()
