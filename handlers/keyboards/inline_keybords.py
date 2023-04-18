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
