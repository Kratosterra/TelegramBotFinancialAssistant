from aiogram.dispatcher.filters.state import State, StatesGroup


class IncomeSpendForm(StatesGroup):
    value = State()
    isSpend = State()
    name = State()
    category = State()
    subcategory = State()
    date = State()
