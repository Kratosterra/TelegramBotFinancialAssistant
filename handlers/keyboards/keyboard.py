from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Клавиатура главного меню.
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📝 Траты и доходы'),
        ],
        [
            KeyboardButton(text='ℹ️ Бюджет'),
            KeyboardButton(text='🛠 Категории'),
            KeyboardButton(text='📊 Отчёты и экспорт'),
        ],
        [
            KeyboardButton(text='⚙️ Настройки'),
            KeyboardButton(text='🆘 Помощь'),
        ]
    ],
    resize_keyboard=True
)
