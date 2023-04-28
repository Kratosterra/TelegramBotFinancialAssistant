import logging
import os
from pathlib import Path

from bot import dp
from handlers.models.income_spend_model import IncomeSpendForm
from helpers import import_data


async def on_import_from_user_handler(message, state):
    try:
        file_id = message.document.file_id
        file = await dp.bot.get_file(file_id)
        file_path = file.file_path
        if Path(file_path).suffix != '.csv':
            await message.answer("*Такой тип файлов недоступен для импорта\.*\n_Используйте файлы в формате"
                                 "* \.csv*_", parse_mode="MarkdownV2")
        else:
            await message.answer("*Приступаю к импорту\.\.\.*", parse_mode="MarkdownV2")
            if not os.path.exists('temporary'):
                os.makedirs('temporary')
            if not os.path.exists('temporary\\import'):
                os.makedirs('temporary\\import')
            await dp.bot.download_file(file_path, f"temporary\\import\\{str(message.from_user.id)}.csv")
            num_of_incomes, num_of_spends, status = await import_data.import_table(str(message.from_user.id),
                                                                                   path=f"temporary\\import\\{str(message.from_user.id)}.csv")
            if status:
                await message.answer(f"*Импорт прошёл успешно*\n\n_Добавлено доходов\:_ {num_of_incomes}\n"
                                     f"_Добавлено трат\:_ {num_of_spends}\n", parse_mode="MarkdownV2")
            else:
                await message.answer("*При импорте произошли ошибки\, пожалуйста проверьте содержание файла\!*\n"
                                     "_Содержание файла должно быть в таком же формате\, что и экспорт\._\n"
                                     "_Воспользуйтесь экспортом из бота, чтобы прояснить для себя формат\._",
                                     parse_mode="MarkdownV2")
            await state.set_state(IncomeSpendForm.value)
            try:
                os.remove(f"temporary\\import\\{str(message.from_user.id)}.csv")
            except Exception:
                pass
    except Exception as e:
        logging.error(f"{on_import_from_user_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)
