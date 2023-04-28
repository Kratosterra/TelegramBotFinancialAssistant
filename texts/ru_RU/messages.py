# Стартовое сообщение, которое видит пользователь, используя /start
start_message = "*Добро пожаловать*\! ❤️\n\nОтправьте *число*\, чтобы добавить его в отчет\!\n" \
                "Отправьте *фото вашего чека* и я смогу понять, какую сумму добавить в отчет\!\n" \
                "Отправьте файлик в формате *\.csv* или *\.xlsx* и я его добавлю к себе\!\n" \
                "И не забывайте пользоваться *клавиатурой внизу экрана*\!\n"
# Сообщение о помощи, которое видит пользователь, используя /help
help_message = "*Помощь\!* 🆘\n\n*Добавление записей*\n" \
               "Чтобы добавить траты или доходы \- воспользуйтесь чатом, просто отправте число или фото своего чека\," \
               " далее действуйте по указаниям\.\n\n*Добавление категорий у удаление записей*" \
               "\nЧтобы управлять категориями и записями\, воспользуйтесь кнопкой\n*🛠 Категории*\.\n\n" \
               "*Валюта, лимиты и цели*\nЧтобы настроить лимиты, цели, события, изменить валюту," \
               " перенсти остаток по средствам\," \
               " воспользуйтесь ⚙️ *Настройки*\.\n\n" \
               "*Импорт*\nПросто отправьте файл в формате \.csv в чат и я" \
               " добавлю эту информацию к себе\!\n\n*Отчеты и экспорт*\n" \
               "Чтобы получить отчеты или экспортные данные\," \
               " воспользуйтесь кнопкой 📊 *Отчёты и экспорт*\.\n\n" \
               "*Бюджет*\nЕсли вы хотите быстро узнать" \
               " состояние бюджета\, состояние лимита и цели\," \
               " воспользуйтесь кнопкой ℹ️ *Бюджет*\.\n\n*Как работают цели и лимиты*\n" \
               "*Цель* \- это то\, сколько вы хотите экономить в месяц в текущей валюте\.\n" \
               "*Лимит* \- это то\, сколько вы хотите тратить в месяц в текущей валюте\." \
               "\n\n*Как работают события*\n*События* учитываются в установленный день месяца\," \
               " автоматически добавляясь как трата или доход\."

# Сообщение, которое видит пользователь, когда отправляет что-то, что бот не умеет распознавать!
not_in_bot_message = "*К сожалению\, я пока так не умею*\! 😥\n\nНо надеюсь когда\-то научится\!"
# Сообщение, которое видит пользователь, когда отправляет что-то, что бот не может принять как трату/доход!
hint_message = "*Введите неотрицательное число*\n_Чтобы добавить сумму траты или дохода\._"
# Сообщение, предупреждающее пользователя о том, что стоит закончить работу с прошлой суммой.
error = "*Завершите работу с текущей командой*\n_Или просто нажмите_ 🚫 *Отмена* _или_ ❌ *Назад*_\._"
# Сообщение, которое появляется перед пользователем после отправки сообщения, если бот выходил из сети и потерял состояние.
repair_of_functional = "💤 Я случайно уснул\.\.\.\n\n" \
                       "Восстановление функционала произведено\!\n" \
                       "Можете отправлять число или команды\!"
# Названия месяцев по номерам
months = {
    1: "январь",
    2: "февраль",
    3: "март",
    4: "апрель",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "август",
    9: "сентябрь",
    10: "октябрь",
    11: "ноябрь",
    12: "декабрь",
}
