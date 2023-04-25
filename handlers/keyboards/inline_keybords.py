from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура, которая появляется, когда пользователь вводит число.
income_spend_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Доход", callback_data="income:income_spend_sum"),
            InlineKeyboardButton(text="📉 Трата", callback_data="spend:income_spend_sum"),
        ],
        [
            InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel"),
        ]
    ]
)

# Клавиатура, которая появляется, когда пользователь выбирает для суммы статус дохода.
income_sum_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Имя дохода", callback_data="name:sum"),
            InlineKeyboardButton(text="📆 Изменить дату", callback_data="change_date:sum"),
        ],
        [
            InlineKeyboardButton(text="✅ Добавить доход", callback_data="proceed:sum"),
            InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel"),
        ]
    ]
)

# Клавиатура, которая появляется, когда пользователь выбирает для суммы статус траты.
spend_sum_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Имя траты", callback_data="name:sum"),
            InlineKeyboardButton(text="📆 Изменить дату", callback_data="change_date:sum"),
        ],
        [
            InlineKeyboardButton(text="📂 Категория", callback_data="category:spend_sum"),
            InlineKeyboardButton(text="🗂️ Подкатегория", callback_data="sub:spend_sum"),
        ],
        [
            InlineKeyboardButton(text="✅ Добавить трату", callback_data="proceed:sum"),
            InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel"),
        ]
    ]
)


async def generate_category_keyboard(buttons: list) -> InlineKeyboardMarkup:
    """
    Функция, которая генерирует клавиатуру для выбора категории.
    :param buttons: Лист строк, которые будут представлять категории
    :return: Разметку клавиатуры.
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    check = 0
    for button_text in buttons:
        keyboard.insert(InlineKeyboardButton(button_text, callback_data=f"choice:category:{button_text}"))
        check += 1
        if check == 2:
            keyboard.row()
            check = 0
    keyboard.row(
        InlineKeyboardButton("❌ Назад", callback_data="category:delete")
    )
    return keyboard


async def generate_subcategory_keyboard(buttons: list) -> InlineKeyboardMarkup:
    """
    Функция, которая генерирует клавиатуру для выбора подкатегории.
    :param buttons: Лист строк, которые будут представлять подкатегории.
    :return: Разметку клавиатуры.
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    check = 0
    for button_text in buttons:
        keyboard.insert(InlineKeyboardButton(button_text, callback_data=f"choice:subcategory:{button_text}"))
        check += 1
        if check == 2:
            keyboard.row()
            check = 0
    keyboard.row(
        InlineKeyboardButton("❌ Назад", callback_data="subcategory:delete")
    )
    return keyboard


async def generate_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    """
    Функция, которая генерирует клавиатуру-календарь.
    :param year: Год.
    :param month: Месяц.
    :return: Разметку клавиатуры.
    """
    keyboard = InlineKeyboardMarkup(row_width=7)
    days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    keyboard.insert(InlineKeyboardButton(f"{year}.{month}", callback_data='ignore'))
    keyboard.row()
    for day in days_of_week:
        keyboard.insert(InlineKeyboardButton(day, callback_data='ignore'))
    keyboard.row()
    import calendar
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        for day in week:
            if day == 0:
                keyboard.insert(InlineKeyboardButton(" ", callback_data='ignore'))
            else:
                keyboard.insert(InlineKeyboardButton(str(day), callback_data=f'date:{year}:{month}:{day}'))
        keyboard.row()
    keyboard.row(
        InlineKeyboardButton("⬅️ Прошл. месяц", callback_data=f"previous_month:{year}:{month}"),
        InlineKeyboardButton("След. месяц ➡️", callback_data=f"next_month:{year}:{month}")
    )
    keyboard.row(
        InlineKeyboardButton("❌ Назад", callback_data="calendar:delete")
    )
    return keyboard


# Клавиатура, которая появляется, когда пользователь выбирает кнопку Траты и Доходы.
income_spend_category_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Удалить Доход 📈", callback_data="delete:income:button"),
            InlineKeyboardButton(text="Удалить Трату 📉", callback_data="delete:spend:button"),
        ],
        [
            InlineKeyboardButton(text="📝 Категория", callback_data="add:category:button"),
            InlineKeyboardButton(text="📝 Подкатегория", callback_data="add:subcategory:button"),
        ],
        [
            InlineKeyboardButton(text="🗑 Категория", callback_data="delete:category:button"),
            InlineKeyboardButton(text="🗑 Подкатегория", callback_data="delete:subcategory:button"),
        ],
        [
            InlineKeyboardButton(text="❌ Назад", callback_data="cancel"),
        ]
    ]
)


async def generate_category_choice_keyboard(buttons: list) -> InlineKeyboardMarkup:
    """
    Функция, которая генерирует клавиатуру для выбора категории.
    :param buttons: Лист строк, которые будут представлять категории
    :return: Разметку клавиатуры.
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    check = 0
    for button_text in buttons:
        keyboard.insert(InlineKeyboardButton(button_text, callback_data=f"choice:category:{button_text}"))
        check += 1
        if check == 2:
            keyboard.row()
            check = 0
    keyboard.row(
        InlineKeyboardButton("❌ Назад", callback_data="category:delete")
    )
    return keyboard


async def create_inline_keyboard_sums(data_dict: dict, current_page: int) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для выбора сумм из базы данных для пользователя.
    :param data_dict: Словарь с сумами.
    :param current_page: Текущая страница.
    :return: Клавиатуру
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    page_size = 5
    start_index = current_page * page_size
    end_index = start_index + page_size
    for item in list(data_dict.keys())[start_index:end_index]:
        text = ""
        if 'name_of_income' in data_dict[item].keys():
            text += f"[{data_dict[item]['name_of_income']}] {data_dict[item]['value_of_income']} [{data_dict[item]['date_of_income']}]"
        else:
            text += f"[{data_dict[item]['name_of_spend']}] {data_dict[item]['value_of_spend']} [{data_dict[item]['date_of_spend']}]"
        inline_keyboard.add(InlineKeyboardButton(text=str(text), callback_data=f"delete:sum:{item}"))
    pagination_row = []
    if current_page > 0:
        pagination_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"current_page:{current_page - 1}"))
    if end_index < len(data_dict):
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"current_page:{current_page + 1}"))
    pagination_row.append(InlineKeyboardButton("❌ Назад", callback_data="category:delete"))
    inline_keyboard.row(*pagination_row)
    return inline_keyboard


# Клавиатура, которая появляется, когда пользователь выбирает настройки.
settings_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💱 Сменить валюту и пересчитать", callback_data="settings:change:currency"),
        ],
        [
            InlineKeyboardButton(text="📝 Cобытие", callback_data="settings:add:event"),
            InlineKeyboardButton(text="🗑 Cобытие", callback_data="settings:delete:event"),
        ],
        [
            InlineKeyboardButton(text="💰 Лимит", callback_data="settings:add:limit"),
            InlineKeyboardButton(text="📩 Цель", callback_data="settings:add:goal"),
        ],
        [
            InlineKeyboardButton(text="💸 Перенести остаток", callback_data="settings:transfer:remainer"),
        ]
        ,
        [
            InlineKeyboardButton(text="❌ Назад", callback_data="cancel"),
        ]
    ]
)

# Клавиатура, которая появляется, когда пользователь выбирает отчеты и экспорт.
report_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 Краткий отчет", callback_data="report:small"),
        ],
        [
            InlineKeyboardButton(text="📊 Подробный отчет", callback_data="report:full"),
        ],
        [
            InlineKeyboardButton(text="📤 Экспорт", callback_data="report:export"),
        ],
        [
            InlineKeyboardButton(text="❌ Назад", callback_data="cancel"),
        ]
    ]
)


async def generate_currency_choice_keyboard(buttons: list) -> InlineKeyboardMarkup:
    """
    Функция, которая генерирует клавиатуру для выбора категории.
    :param buttons: Лист строк, которые будут представлять категории
    :return: Разметку клавиатуры.
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    check = 0
    for button_text in buttons:
        keyboard.insert(InlineKeyboardButton(button_text, callback_data=f"choice:currency:{button_text}"))
        check += 1
        if check == 2:
            keyboard.row()
            check = 0
    keyboard.row(
        InlineKeyboardButton("❌ Назад", callback_data="settings:delete")
    )
    return keyboard


refuse_to_input = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Не хочу вводить", callback_data="input::stop"),
        ],
    ]
)

event_income_spend_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Событие Доход", callback_data="event:income"),
            InlineKeyboardButton(text="📉 Событие Трата", callback_data="event:spend"),
        ],
        [
            InlineKeyboardButton(text="❌ Назад", callback_data="settings:delete"),
        ]
    ]
)


async def create_inline_keyboard_events(data_dict: dict, current_page: int) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для выбора сумм из базы данных для пользователя.
    :param data_dict: Словарь с событиями.
    :param current_page: Текущая страница.
    :return: Клавиатуру
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    page_size = 5
    start_index = current_page * page_size
    end_index = start_index + page_size
    for item in list(data_dict.keys())[start_index:end_index]:
        text = ""
        if 'name_of_income' in data_dict[item].keys():
            text += f"[{data_dict[item]['name_of_income']}] {data_dict[item]['value_of_income']} [{data_dict[item]['day_of_income']} числа]"
        else:
            text += f"[{data_dict[item]['name_of_spending']}] {data_dict[item]['value_of_spending']} [{data_dict[item]['day_of_spending']} числа]"
        inline_keyboard.add(InlineKeyboardButton(text=str(text), callback_data=f"delete:event:{item}"))
    pagination_row = []
    if current_page > 0:
        pagination_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"event:current_page:{current_page - 1}"))
    if end_index < len(data_dict):
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"event:current_page:{current_page + 1}"))
    pagination_row.append(InlineKeyboardButton("❌ Назад", callback_data="settings:delete"))
    inline_keyboard.row(*pagination_row)
    return inline_keyboard


# Клавиатура, которая появляется, когда пользователь выбирает для суммы статус дохода.
income_event_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Имя события", callback_data="name:event"),
            InlineKeyboardButton(text="📆 Установить день", callback_data="day:event"),
        ],
        [
            InlineKeyboardButton(text="✅ Добавить событие", callback_data="proceed:event"),
            InlineKeyboardButton(text="🚫 Отмена", callback_data="settings:delete"),
        ]
    ]
)

# Клавиатура, которая появляется, когда пользователь выбирает для суммы статус траты.
spend_event_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Имя события", callback_data="name:event"),
            InlineKeyboardButton(text="📆 Установить день", callback_data="day:event"),
        ],
        [
            InlineKeyboardButton(text="📂 Категория", callback_data="category:event"),
            InlineKeyboardButton(text="🗂️ Подкатегория", callback_data="sub:event"),
        ],
        [
            InlineKeyboardButton(text="✅ Добавить событие", callback_data="proceed:event"),
            InlineKeyboardButton(text="🚫 Отмена", callback_data="settings:delete"),
        ]
    ]
)


async def get_day_choice_keyboard() -> InlineKeyboardMarkup:
    """
    Функция, которая генерирует клавиатуру для выбора дня.
    :return: Разметку клавиатуры.
    """
    keyboard = InlineKeyboardMarkup(row_width=7)
    check = 0
    for i in range(1, 29):
        keyboard.insert(InlineKeyboardButton(str(i), callback_data=f"choice:day:{i}"))
        check += 1
        if check == 7:
            keyboard.row()
            check = 0
    keyboard.row(
        InlineKeyboardButton("❌ Отменить", callback_data="input::stop")
    )
    return keyboard
