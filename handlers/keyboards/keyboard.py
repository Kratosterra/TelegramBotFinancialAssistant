from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Клавиатура главного меню.
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='ℹ️ Информация'),
            KeyboardButton(text='📈 Траты и Доходы'),
            KeyboardButton(text='📝 Отчёты и экспорт'),
        ],
        [
            KeyboardButton(text='⚙️ Настройки'),
            KeyboardButton(text='🆘 Помощь'),
        ]
    ],
    resize_keyboard=True
)

report_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📄 Краткий отчет'),
            KeyboardButton(text='📊 Подробный отчет'),
        ],
        [
            KeyboardButton(text='📤 Экспорт'),
        ]
    ],
    resize_keyboard=True
)
