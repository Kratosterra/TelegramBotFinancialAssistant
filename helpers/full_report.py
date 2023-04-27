import datetime
import logging
import os

import xlsxwriter as xlwt

from database import db_functions


async def get_report_table(user_id, start: datetime, end: datetime):
    try:
        if not os.path.exists('temporary'):
            os.makedirs('temporary')
        if not os.path.exists('temporary\\report'):
            os.makedirs('temporary\\report')

        currency = await db_functions.get_user_currency(user_id)
        spends_sums = await db_functions.get_spends_of_user_by_categories(user_id, start, end)
        spends = await db_functions.get_full_spends_of_user_by_categories(user_id, start, end)
        incomes = await db_functions.return_incomes_of_period(user_id, start, end)
        sum_income = await db_functions.return_sum_income_ignore_remained(user_id, start, end)
        sum_spend = await db_functions.return_sum_spend(user_id, start, end)

        book = xlwt.Workbook(f'temporary\\report\\{user_id}.xlsx')

        category_format, date_format, income_format, name_format, spend_format, subcategory_format, up_format = await create_formats(
            book)
        sheet_report = book.add_worksheet("Отчёт")
        await create_report_worksheet(category_format, currency, date_format, end, income_format, name_format,
                                      sheet_report, spend_format, spends_sums, start, subcategory_format, sum_income,
                                      sum_spend)
        sheet_spends = book.add_worksheet("Траты")
        await create_spend_worksheet(category_format, currency, sheet_spends, spends, subcategory_format, up_format)
        sheet_incomes = book.add_worksheet("Доходы")
        await create_income_worksheet(currency, incomes, sheet_incomes, subcategory_format, up_format)

        book.close()

        return f'temporary\\report\\{user_id}.xlsx'
    except Exception as e:
        logging.error(f"{get_report_table.__name__}: {e}. Пользователь с id {user_id}.")


async def create_formats(book):
    name_format = book.add_format()
    name_format.set_left(1)
    name_format.set_right(1)
    name_format.set_top(1)
    name_format.set_bottom(1)
    name_format.set_bg_color('orange')
    name_format.set_bold()
    name_format.set_font_size(14)
    name_format.set_align('center')
    date_format = book.add_format()
    date_format.set_bg_color('orange')
    date_format.set_font_size(13)
    date_format.set_bold()
    date_format.set_left(1)
    date_format.set_right(1)
    date_format.set_top(1)
    date_format.set_bottom(1)
    category_format = book.add_format()
    category_format.set_bold()
    category_format.set_font_color('black')
    category_format.set_align('center')
    category_format.set_font_size(13)
    category_format.set_bg_color(bg_color='cyan')
    subcategory_format = book.add_format()
    subcategory_format.set_italic()
    subcategory_format.set_font_color('black')
    subcategory_format.set_align('right')
    subcategory_format.set_font_size(12)
    subcategory_format.set_bg_color(bg_color='silver')
    income_format = book.add_format()
    income_format.set_font_size(13)
    income_format.set_bold()
    income_format.set_bg_color(bg_color='red')
    up_format = book.add_format()
    up_format.set_font_size(13)
    up_format.set_align('center')
    up_format.set_bold()
    up_format.set_bg_color(bg_color='yellow')
    spend_format = book.add_format()
    spend_format.set_font_size(13)
    spend_format.set_bold()
    spend_format.set_bg_color(bg_color='cyan')
    return category_format, date_format, income_format, name_format, spend_format, subcategory_format, up_format


async def create_report_worksheet(category_format, currency, date_format, end, income_format, name_format, sheet_report,
                                  spend_format, spends_sums, start, subcategory_format, sum_income, sum_spend):
    sheet_report.set_column(0, 2, 30)
    sheet_report.set_column(3, 3, 12)
    sheet_report.write(0, 0, "Подробный отчёт", name_format)
    sheet_report.write(2, 0, f"Период", date_format)
    sheet_report.write(2, 1, f"C {start.strftime('%Y-%m-%d')}", date_format)
    sheet_report.write(2, 2, f"по {end.strftime('%Y-%m-%d')}", date_format)
    row_incomes = 5
    row_spend = 6
    sheet_report.write(row_incomes, 0, "Всего доходов:", income_format)
    sheet_report.write(row_incomes, 1, sum_income, income_format)
    sheet_report.write(row_incomes, 2, currency, income_format)
    sheet_report.write(row_spend, 0, "Всего трат:", spend_format)
    sheet_report.write(row_spend, 1, sum_spend, spend_format)
    sheet_report.write(row_spend, 2, currency, spend_format)
    row = 9
    for category in spends_sums.keys():
        if category == "$no_category":
            all = spends_sums[category]['$all']
            sheet_report.write(row, 0, "Без категории:", category_format)
            sheet_report.write(row, 1, all, category_format)
            sheet_report.write(row, 2, f"{currency}", category_format)
            row += 2
            continue
        all = spends_sums[category]['$all']
        no_category = spends_sums[category]['$no_subcategory']
        sheet_report.write(row, 0, f"{category}:", category_format)
        sheet_report.write(row, 1, all, category_format)
        sheet_report.write(row, 2, currency, category_format)
        row += 2
        sheet_report.write(row, 1, "Без подкатегории:", subcategory_format)
        sheet_report.write(row, 2, no_category, subcategory_format)
        sheet_report.write(row, 3, currency, subcategory_format)
        row += 1
        for sub_category in (spends_sums[category].keys()):
            if sub_category == "$all" or sub_category == "$no_subcategory":
                continue
            sum = spends_sums[category][sub_category]
            sheet_report.write(row, 1, f"{sub_category}:", subcategory_format)
            sheet_report.write(row, 2, sum, subcategory_format)
            sheet_report.write(row, 3, currency, subcategory_format)
            row += 1
        row += 2


async def create_income_worksheet(currency, incomes, sheet_incomes, subcategory_format, up_format):
    sheet_incomes.set_column(1, 3, 30)
    sheet_incomes.set_column(4, 4, 8)
    row = 0
    sheet_incomes.write(row, 0, "Id", up_format)
    sheet_incomes.write(row, 1, "Имя дохода", up_format)
    sheet_incomes.write(row, 2, "Дата дохода", up_format)
    sheet_incomes.write(row, 3, "Сумма", up_format)
    sheet_incomes.write(row, 4, "Валюта", up_format)
    row = 1
    for income_id in incomes.keys():
        if incomes[income_id]['type_of_income'] == "remained":
            continue
        sheet_incomes.write(row, 0, row, subcategory_format)
        if incomes[income_id]['name_of_income'] is None:
            sheet_incomes.write(row, 1, "Безымянный", subcategory_format)
        else:
            sheet_incomes.write(row, 1, incomes[income_id]['name_of_income'], subcategory_format)
        sheet_incomes.write(row, 2, incomes[income_id]['date_of_income'], subcategory_format)
        sheet_incomes.write(row, 3, incomes[income_id]['value_of_income'], subcategory_format)
        sheet_incomes.write(row, 4, currency, subcategory_format)
        row += 1


async def create_spend_worksheet(category_format, currency, sheet_spends, spends, subcategory_format, up_format):
    sheet_spends.set_column(0, 4, 30)
    sheet_spends.set_column(5, 5, 12)
    row = 1
    for category in spends.keys():
        if category == "$no_category":
            sheet_spends.write(row, 0, "Имя категории", up_format)
            sheet_spends.write(row, 1, "Имя Траты", up_format)
            sheet_spends.write(row, 2, "Дата Траты", up_format)
            sheet_spends.write(row, 3, "Сумма", up_format)
            sheet_spends.write(row, 4, "Валюта", up_format)
            row += 1
            all = spends[category]['$all']
            sheet_spends.write(row, 0, "Без категории:", category_format)
            row += 1
            for spend in all:
                if spend['name_of_spend'] is None:
                    sheet_spends.write(row, 1, "Безымянный", subcategory_format)
                else:
                    sheet_spends.write(row, 1, spend['name_of_spend'], subcategory_format)
                sheet_spends.write(row, 2, spend['date_of_spend'], subcategory_format)
                sheet_spends.write(row, 3, spend['value_of_spend'], subcategory_format)
                sheet_spends.write(row, 4, currency, subcategory_format)
                row += 1
            row += 2
            sheet_spends.write(row, 0, "Имя категории", up_format)
            sheet_spends.write(row, 1, "Имя подкатегории", up_format)
            sheet_spends.write(row, 2, "Имя Траты", up_format)
            sheet_spends.write(row, 3, "Дата Траты", up_format)
            sheet_spends.write(row, 4, "Сумма", up_format)
            sheet_spends.write(row, 5, "Валюта", up_format)
            row += 1
            continue
        no_category = spends[category]['$no_subcategory']
        sheet_spends.write(row, 0, f"{category}:", category_format)
        row += 2
        sheet_spends.write(row, 1, "Без подкатегории:", subcategory_format)
        row += 1
        for spend in no_category:
            if spend['name_of_spend'] is None:
                sheet_spends.write(row, 2, "Безымянный", subcategory_format)
            else:
                sheet_spends.write(row, 2, spend['name_of_spend'], subcategory_format)
            sheet_spends.write(row, 3, spend['date_of_spend'], subcategory_format)
            sheet_spends.write(row, 4, spend['value_of_spend'], subcategory_format)
            sheet_spends.write(row, 5, currency, subcategory_format)
            row += 1
        row += 1
        for sub_category in (spends[category].keys()):
            if sub_category == "$all" or sub_category == "$no_subcategory":
                continue
            sum = spends[category][sub_category]
            sheet_spends.write(row, 1, sub_category, subcategory_format)
            row += 1
            for spend in sum:
                if spend['name_of_spend'] is None:
                    sheet_spends.write(row, 2, "Безымянный", subcategory_format)
                else:
                    sheet_spends.write(row, 2, spend['name_of_spend'], subcategory_format)
                sheet_spends.write(row, 3, spend['date_of_spend'], subcategory_format)
                sheet_spends.write(row, 4, spend['value_of_spend'], subcategory_format)
                sheet_spends.write(row, 5, currency, subcategory_format)
                row += 1
            row += 1
        row += 2
