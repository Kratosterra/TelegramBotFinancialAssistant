import datetime
import logging
import os

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile

from bot import dp
from handlers.keyboards import inline_keybords
from handlers.models.income_spend_model import IncomeSpendForm
from handlers.models.report_model import ReportForm
from helpers import report, full_report, export


@dp.callback_query_handler(text_contains='report:small', state=ReportForm.start)
async def small_report_menu_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отправляет пользователю отчёт по месяцам как сообщение.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Получаем маленький отчет по нажатию на кнопку. Пользователь с id {call.from_user.id}.')
        await ReportForm.small_report.set()
        now = datetime.date.today()
        await call.message.answer(
            f"📄 *Отчёт*\n{await report.get_small_text_report(str(call.from_user.id), datetime.date.today())}",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_report_keyboard_small(now))
        await call.answer()
    except Exception as e:
        logging.error(f"{small_report_menu_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)


@dp.callback_query_handler(text_contains='more:', state=ReportForm.small_report)
async def expand_small_report_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за расширение текущего отчёта, показывает статистику с подкатегориями.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Делаем маленький отчёт подробнее. Пользователь с id {call.from_user.id}.')
        date = call.data.split(':')
        now = datetime.datetime.strptime(date[1], "%Y-%m-%d")
        await call.message.edit_text(
            f"📄 *Отчёт*\n{await report.get_small_text_report(str(call.from_user.id), now, True)}",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_report_keyboard_small(now, False))
        await call.answer()
    except Exception as e:
        logging.error(f"{expand_small_report_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)

@dp.callback_query_handler(text_contains='picture:', state=ReportForm.small_report)
async def send_graphics_report_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за расширение текущего отчёта, показывает статистику с подкатегориями.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Делаем графику для маленького отчёта. Пользователь с id {call.from_user.id}.')
        date = call.data.split(':')
        now = datetime.datetime.strptime(date[1], "%Y-%m-%d")
        path = InputFile(await report.get_graphics_in_photo(call.from_user.id, now))
        await call.message.answer_photo(photo=path, reply_markup=inline_keybords.clear_inline)
        await call.answer()
        try:
            os.remove(f"temporary\\graphics\\{str(call.from_user.id)}.png")
        except Exception as io_error:
            logging.debug(f"{send_graphics_report_button_handler.__name__}: {io_error}."
                          f" Пользователь с id {call.from_user.id}.")
            pass
    except Exception as e:
        logging.error(f"{expand_small_report_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)

@dp.callback_query_handler(text_contains='less:', state=ReportForm.small_report)
async def reduce_small_report_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за уменьшение текущего отчёта, показывает статистику только с категориями.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Делаем маленький отчёт менее подробным. Пользователь с id {call.from_user.id}.')
        date = call.data.split(':')
        now = datetime.datetime.strptime(date[1], "%Y-%m-%d")
        await call.message.edit_text(
            f"📄 *Отчёт*\n{await report.get_small_text_report(str(call.from_user.id), now)}",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_report_keyboard_small(now))
        await call.answer()
    except Exception as e:
        logging.error(f"{reduce_small_report_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)


@dp.callback_query_handler(text_contains='change:', state=ReportForm.small_report)
async def change_moths_small_report_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за изменение текущего месяца отчёта.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Меняем маленький отчёт на другой месяц. Пользователь с id {call.from_user.id}.')
        date = call.data.split(':')
        now = datetime.datetime.strptime(date[1], "%Y-%m-%d")
        await call.message.edit_text(
            f"📄 *Отчёт*\n{await report.get_small_text_report(str(call.from_user.id), now)}",
            parse_mode="MarkdownV2",
            reply_markup=await inline_keybords.create_report_keyboard_small(now))
        await call.answer()
    except Exception as e:
        logging.error(f"{change_moths_small_report_button_handler.__name__}: {e}."
                      f" Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)


@dp.callback_query_handler(text_contains='report:full', state=[ReportForm.start])
async def big_report_menu_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отправляет сообщения с выбором параметров для большого отчёта.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Отправляем сообщение с выбором параметров для большого отчёта.'
                      f' Пользователь с id {call.from_user.id}.')
        await ReportForm.big_report.set()
        await call.message.answer(
            f"📊 *Отчет Excel*\n\n_Выберете период с помощью кнопок и подтвердите создание_",
            parse_mode="MarkdownV2",
            reply_markup=inline_keybords.big_report_inline)
        await call.answer()
    except Exception as e:
        logging.error(f"{big_report_menu_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(IncomeSpendForm.value)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('date:'), state=[ReportForm.report_start,
                                                                                   ReportForm.report_end])
async def date_select_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на нажатие кнопки в календаре, в зависимости от текущего состояния устанавливает дату
    как начало или конец периода.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Получаем дату для выбора периода отчёта. Пользователь с id {call.from_user.id}.")
        year, month, day = map(int, call.data.split(':')[1:])
        data = datetime.datetime(year, month, day)
        if await state.get_state() == ReportForm.report_end.state:
            await state.update_data(report_end=data)
            await call.answer(f"Конец: {data.strftime('%Y-%m-%d')}")
        else:
            await state.update_data(report_start=data)
            await call.answer(f"Начало: {data.strftime('%Y-%m-%d')}")
        await call.message.delete()
        await ReportForm.big_report.set()
    except Exception as e:
        logging.error(f"{date_select_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте создать отчет снова!",
                                  reply_markup=inline_keybords.clear_inline)
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='change_date:', state=ReportForm.big_report)
async def send_date_picker_button_handler(call: CallbackQuery) -> None:
    """
    Функция, которая отвечает за обработку нажатия на кнопку изменения даты суммы, отправляя сообщение с календарём.
    :type call: CallbackQuery
    :param call: Вызов от кнопки.
    """
    try:
        logging.debug(f"Отправляем календарь для выбора даты. Пользователь с id {call.from_user.id}.")
        year = datetime.datetime.today().year
        month = datetime.datetime.today().month
        calendar_keyboard = await inline_keybords.generate_calendar(year, month)
        type_of_date = call.data.split(':')
        if type_of_date[1] == 'start':
            await ReportForm.report_start.set()
        else:
            await ReportForm.report_end.set()
        await call.message.answer("Выберите дату:", reply_markup=calendar_keyboard, disable_notification=True)
        await call.answer()
    except Exception as e:
        logging.error(f"{send_date_picker_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('previous_month'), state=[ReportForm.report_start,
                                                                                            ReportForm.report_end])
async def process_previous_month_button_handler(call: CallbackQuery) -> None:
    """
    Функция, реагирующая на нажатие на кнопку в календаре, переносящую на прошлый месяц, изменяет календарь.
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Пересоздаём календарь за предыдущий месяц. Пользователь с id {call.from_user.id}.")
        year, month = map(int, call.data.split(':')[1:])
        new_month = month - 1
        new_year = year
        if new_month < 1:
            new_month = 12
            new_year = year - 1
        keyboard = await inline_keybords.generate_calendar(new_year, new_month)
        await dp.bot.edit_message_reply_markup(call.message.chat.id,
                                               call.message.message_id,
                                               reply_markup=keyboard)

        await dp.bot.answer_callback_query(call.id)
        await call.answer()
    except Exception as e:
        logging.error(f"{process_previous_month_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await ReportForm.big_report.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('next_month'), state=[ReportForm.report_start,
                                                                                        ReportForm.report_end])
async def process_next_month_callback(call: CallbackQuery) -> None:
    """
    Функция, реагирующая на нажатие на кнопку в календаре, переносящую на следующий месяц, изменяет календарь.
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Пересоздаём календарь за следующий месяц. Пользователь с id {call.from_user.id}.")
        year, month = map(int, call.data.split(':')[1:])
        new_month = month + 1
        new_year = year
        if new_month > 12:
            new_month = 1
            new_year = year + 1
        keyboard = await inline_keybords.generate_calendar(new_year, new_month)
        await dp.bot.edit_message_reply_markup(call.message.chat.id,
                                               call.message.message_id,
                                               reply_markup=keyboard)
        await dp.bot.answer_callback_query(call.id)
        await call.answer()
    except Exception as e:
        logging.error(f"{process_next_month_callback.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await ReportForm.big_report.set()


@dp.callback_query_handler(text_contains='calendar:delete', state=[ReportForm.report_start,
                                                                   ReportForm.report_end])
async def cancel_calendar_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор даты, возвращая в прошлое состояние с сохранением данных.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем выбор даты при создании большого отчёта. Пользователь с id {call.from_user.id}.')
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(ReportForm.big_report)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_calendar_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(ReportForm.big_report)


@dp.callback_query_handler(text_contains='proceed', state=ReportForm.big_report)
async def proceed_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за подтверждение данных от пользователя при создании большого отчёта.
    Если с данными все данные подходят под формат, отправляет сообщение с отчётом как документ.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(f"Подтверждение. Отправляем большой отчёт. Пользователь с id {call.from_user.id}.")
        data = (await state.get_data())
        if 'report_end' not in data.keys() or 'report_start' not in data.keys():
            await call.answer("Установите даты!")
            return
        if data["report_end"] <= data["report_start"]:
            await call.answer("Дата старта должна быть раньше!")
            return
        start = data['report_start'].strftime('%Y-%m-%d').replace('-', '\-')
        end = data['report_end'].strftime('%Y-%m-%d').replace('-', '\-')
        path_to_file = await full_report.get_report_table(str(call.from_user.id), data['report_start'],
                                                          data['report_end'])
        await call.message.answer_document(open(path_to_file, 'rb'),
                                           caption=f"📊 *Отчёт Excel*\nC _{start}_ по _{end}_",
                                           parse_mode="MarkdownV2")
        await call.message.delete()
        await state.finish()
        await IncomeSpendForm.value.set()
        try:
            os.remove(path_to_file)
        except Exception as io_error:
            logging.debug(f"{proceed_button_handler.__name__}: {io_error}. Пользователь с id {call.from_user.id}.")
            pass
    except Exception as e:
        logging.error(f"{proceed_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.answer("При создании отчета произошла ошибка, попробуйте еще раз!")
        await IncomeSpendForm.value.set()


@dp.callback_query_handler(text_contains='report:export', state=[ReportForm.start])
async def export_menu_button_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отвечает за отправку пользователю экспортных данных.
    :type state: FSMContext
    :type call: CallbackQuery
    :param call: Запрос от кнопки.
    :param state: Состояние.
    """
    try:
        await call.message.delete()
        logging.debug(f'Получаем файл для экспорта и отправляем пользователю. Пользователь с id {call.from_user.id}.')
        await ReportForm.export.set()
        path_to_file = await export.get_export_table(str(call.from_user.id))
        await call.message.answer_document(open(path_to_file, 'rb'),
                                           caption=f"📤 *Экспорт*\n\n_Данные за все время в формате \.csv_",
                                           parse_mode="MarkdownV2")
        await call.answer()
        await state.set_state(IncomeSpendForm.value)
        try:
            os.remove(path_to_file)
        except Exception as io_error:
            logging.debug(f"{export_menu_button_handler.__name__}: {io_error}. Пользователь с id {call.from_user.id}.")
            pass
    except Exception as e:
        logging.error(f"{export_menu_button_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.answer(
            f"📤 *Экспорт*\n\n_Произошла ошибка_",
            parse_mode="MarkdownV2", reply_markup=inline_keybords.clear_inline)
        await state.set_state(IncomeSpendForm.value)
