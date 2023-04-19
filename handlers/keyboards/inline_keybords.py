from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

spend_sum_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Имя траты", callback_data="name:sum"),
            InlineKeyboardButton(text="📆 Изменить дату", callback_data="change_date:sum"),
        ],
        [
            InlineKeyboardButton(text="📎 Добавить категорию", callback_data="name:spend_sum"),
            InlineKeyboardButton(text="🖇 Добавить подкатегорию", callback_data="change_date:spend_sum"),
        ],
        [
            InlineKeyboardButton(text="✅ Добавить трату", callback_data="proceed:sum"),
            InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel"),
        ]
    ]
)


def generate_keyboard(buttons: list):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for button_text in buttons:
        keyboard.add(InlineKeyboardButton(button_text, callback_data=button_text))
    return keyboard


def generate_calendar(year, month):
    # создаем пустую inline клавиатуру
    keyboard = InlineKeyboardMarkup(row_width=7)
    # создаем список дней недели, который будет использоваться для заполнения первого ряда клавиатуры
    days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    keyboard.insert(InlineKeyboardButton(f"{year}.{month}", callback_data='ignore'))
    keyboard.row()
    # заполняем первый ряд клавиатуры кнопками, содержащими дни недели
    for day in days_of_week:
        keyboard.insert(InlineKeyboardButton(day, callback_data='ignore'))
    keyboard.row()
    # находим первый день месяца и день недели, на который он приходится
    import calendar
    month_calendar = calendar.monthcalendar(year, month)
    # добавляем кнопки с днями месяца
    for week in month_calendar:
        for day in week:
            if day == 0:
                keyboard.insert(InlineKeyboardButton(" ", callback_data='ignore'))
            else:
                keyboard.insert(InlineKeyboardButton(str(day), callback_data=f'date:{year}:{month}:{day}'))
        keyboard.row()
    # добавляем кнопки для переключения между месяцами
    keyboard.row(
        InlineKeyboardButton("<", callback_data=f"previous_month:{year}:{month}"),
        InlineKeyboardButton(">", callback_data=f"next_month:{year}:{month}")
    )
    # добавляем кнопку для отмены
    keyboard.row(
        InlineKeyboardButton("Отмена", callback_data="calendar:delete")
    )
    return keyboard
