import logging
import os
from pathlib import Path

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import dp
from database import db_functions
from handlers.keyboards import inline_keybords
from handlers.models.income_spend_model import IncomeSpendForm
from helpers import import_data, qr_scanner


async def on_import_from_user_handler(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая отвечает за импорт данных при получении нужного документа.
     Добавляет записи о тратах и доходах в базу данных.
    :type state: FSMContext
    :type message: Message
    :param message: Сообщение от пользователя.
    :param state: Состояние.
    """
    try:
        file_id = message.document.file_id
        file = await dp.bot.get_file(file_id)
        file_path = file.file_path
        if Path(file_path).suffix != '.csv':
            await message.answer("*Такой тип файлов недоступен для импорта\.*\n_Используйте файлы в формате"
                                 "* \.csv*_", parse_mode="MarkdownV2", reply_markup=inline_keybords.clear_inline)
        else:
            await message.answer("*Приступаю к импорту\.\.\.*", parse_mode="MarkdownV2")
            if not os.path.exists('temporary'):
                os.makedirs('temporary')
            if not os.path.exists('temporary\\import'):
                os.makedirs('temporary\\import')
            await dp.bot.download_file(file_path, f"temporary\\import\\{str(message.from_user.id)}.csv")
            num_of_incomes, num_of_spends, status = \
                await import_data.import_table(str(message.from_user.id),
                                               path=f"temporary\\import\\{str(message.from_user.id)}.csv")
            if status:
                await message.answer(f"*Импорт прошёл успешно*\n\n_Добавлено доходов\:_ {num_of_incomes}\n"
                                     f"_Добавлено трат\:_ {num_of_spends}\n", parse_mode="MarkdownV2",
                                     reply_markup=inline_keybords.clear_inline)
            else:
                await message.answer("*При импорте произошли ошибки\, пожалуйста проверьте содержание файла\!*\n"
                                     "_Содержание файла должно быть в таком же формате\, что и экспорт\._\n"
                                     "_Воспользуйтесь экспортом из бота, чтобы прояснить для себя формат\._",
                                     parse_mode="MarkdownV2", reply_markup=inline_keybords.clear_inline)
            await state.set_state(IncomeSpendForm.value)
            try:
                os.remove(f"temporary\\import\\{str(message.from_user.id)}.csv")
            except Exception as io_error:
                logging.debug(f"{on_import_from_user_handler.__name__}: {io_error}."
                              f" Пользователь с id {message.from_user.id}.")
                pass
    except Exception as e:
        logging.error(f"{on_import_from_user_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)


async def on_photo_from_user_handler(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая отвечает за сканирование данных из фото. Если сканирование прошло успешно,
     отправляет пользователя в меню сумм.
    :type state: FSMContext
    :type message: Message
    :param message: Сообщение от пользователя.
    :param state: Состояние.
    """
    try:
        if not os.path.exists('temporary'):
            os.makedirs('temporary')
        if not os.path.exists('temporary\\photo'):
            os.makedirs('temporary\\photo')
        paths = f"temporary\\photo\\{str(message.from_user.id)}.jpg"
        await message.photo[-1].download(destination_file=paths)
        data_qrs = await qr_scanner.get_qr_codes(paths)
        if len(data_qrs) > 0:
            data = str(data_qrs[0])
            if data.count("&s=") != 1 or data.count("&fn=") != 1:
                await message.answer(
                    f"*QR код не содержит требуемой информации*\n\n_Код был считан\, вероятно\, он не с чека\._",
                    parse_mode="MarkdownV2",
                    reply_markup=inline_keybords.clear_inline)
                return
            sum_value = float(data[data.find("&s=") + 3:data.find("&fn=")])
            await IncomeSpendForm.isSpend.set()
            if float(sum_value) > 10000000000 or float(sum_value) < 0.01:
                await message.answer("*Это уже слишком для меня!*\n\n"
                                     "_Полученная сумма либо крайне маленькая\, либо большая\!_",
                                     parse_mode="MarkdownV2", reply_markup=inline_keybords.clear_inline)
                await IncomeSpendForm.value.set()
                return
            await state.update_data(value=round(float(sum_value), 2))
            await message.answer(
                f"Сумма: {round(float(sum_value), 2)}"
                f" {await db_functions.get_user_currency(str(message.from_user.id))}",
                reply_markup=inline_keybords.income_spend_inline, disable_notification=True)
        else:
            await message.answer(
                f"*На фото не было обнаружено QR кода*\n\n_QR\-код должен быть хорошо виден и не размыт\._",
                parse_mode="MarkdownV2",
                reply_markup=inline_keybords.clear_inline)
            await state.set_state(IncomeSpendForm.value)
    except Exception as e:
        logging.error(f"{on_photo_from_user_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await message.answer(
            f"*Произошла ошибка при считывании QR кода\.*",
            parse_mode="MarkdownV2",
            reply_markup=inline_keybords.clear_inline)
        await state.set_state(IncomeSpendForm.value)
    finally:
        try:
            os.remove(f"temporary\\photo\\{str(message.from_user.id)}.jpg")
        except Exception as io_error:
            logging.debug(f"{on_photo_from_user_handler.__name__}: {io_error}."
                          f" Пользователь с id {message.from_user.id}.")
