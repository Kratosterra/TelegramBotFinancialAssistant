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
            InlineKeyboardButton(text="📎 Категория", callback_data="category:spend_sum"),
            InlineKeyboardButton(text="🖇 Подкатегория", callback_data="sub:spend_sum"),
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
        InlineKeyboardButton("⬅️ Прошлый месяц", callback_data=f"previous_month:{year}:{month}"),
        InlineKeyboardButton("Следующий месяц ➡️", callback_data=f"next_month:{year}:{month}")
    )
    keyboard.row(
        InlineKeyboardButton("❌ Назад", callback_data="calendar:delete")
    )
    return keyboard
