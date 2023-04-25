from aiogram.dispatcher.filters.state import State, StatesGroup


class ReportForm(StatesGroup):
    """
    Класс, отвечающий за хранение состояний отчетов.
    """
    # Стартовое значение
    start = State()
    # Экспорт
    export = State()
    # Большой отчет
    big_report = State()
    # От даты
    report_start = State()
    # До даты
    report_end = State()
    # маленький отчет
    small_report = State()
