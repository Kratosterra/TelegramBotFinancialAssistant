from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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
