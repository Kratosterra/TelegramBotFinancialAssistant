import datetime
import logging

from database import db_functions

import xlwt as xlwt


async def get_report_table(user_id, start: datetime, end: datetime):
    try:
        currency = await db_functions.get_user_currency(user_id)
        spends_sums = await db_functions.get_spends_of_user_by_categories(user_id, start, end)
        spends = await db_functions.get_full_spends_of_user_by_categories(user_id, start, end)
        incomes = await db_functions.return_incomes_of_period(user_id, start, end)
        sum_income = await db_functions.return_sum_income_ignore_remained(user_id, start, end)
        sum_spend = await db_functions.return_sum_spend(user_id, start, end)

        book = xlwt.Workbook()
        sheet_report = book.add_sheet("Отчёт")
        row_name = sheet_report.row(0)
        row_name.write(0, "Подробный отчёт")
        row_date = sheet_report.row(2)
        row_date.write(0, "C")
        row_date.write(1, f"{start.strftime('%Y-%m-%d')}")
        row_date.write(2, f"по")
        row_date.write(3, f"{end.strftime('%Y-%m-%d')}")

        row_incomes = sheet_report.row(5)
        row_spend = sheet_report.row(6)

        row_incomes.write(0, "Всего доходов:")
        row_incomes.write(1, sum_income)

        row_spend.write(0, "Всего трат:")
        row_spend.write(1, sum_spend)

        row_info = sheet_report.row(9)
        row_info.write(0, "По категориям трат:")

        row = 11
        for category in spends_sums.keys():
            now = sheet_report.row(row)
            if category == "$no_category":
                all = spends_sums[category]['$all']
                now.write(0, "Без категории:")
                now.write(1, str(all))
                now.write(2, f"{currency}")
                row += 2
                continue
            all = spends_sums[category]['$all']
            no_category = spends_sums[category]['$no_subcategory']
            now.write(0, f"{category}:")
            now.write(1, all)
            now.write(2, currency)
            row += 2
            now = sheet_report.row(row)
            now.write(1, "Без подкатегории:")
            now.write(2, no_category)
            now.write(3, currency)
            row += 1
            for sub_category in (spends_sums[category].keys()):
                now = sheet_report.row(row)
                if sub_category == "$all" or sub_category == "$no_subcategory":
                    row += 1
                    continue
                sum = spends_sums[category][sub_category]
                now.write(1, f"{sub_category}:")
                now.write(2, sum)
                now.write(3, currency)
                row += 1
            row += 2

        sheet_spends = book.add_sheet("Траты")

        row = 1
        for category in spends.keys():
            now = sheet_spends.row(row)
            if category == "$no_category":
                now.write(0, "Имя категории")
                now.write(1, "Имя Траты")
                now.write(2, "Дата Траты")
                now.write(3, "Сумма")
                now.write(4, "Валюта")
                row += 1
                now = sheet_spends.row(row)
                all = spends[category]['$all']
                now.write(0, "Без категории:")
                row += 1
                for spend in all:
                    now = sheet_spends.row(row)
                    if spend['name_of_spend'] is None:
                        now.write(1, "Безымянный")
                    else:
                        now.write(1, spend['name_of_spend'])
                    now.write(2, spend['date_of_spend'])
                    now.write(3, spend['value_of_spend'])
                    now.write(4, currency)
                    row += 1
                row += 2
                now = sheet_spends.row(row)
                now.write(0, "Имя категории")
                now.write(1, "Имя подкатегории")
                now.write(2, "Имя Траты")
                now.write(3, "Дата Траты")
                now.write(4, "Сумма")
                now.write(5, "Валюта")
                row += 1
                continue
            no_category = spends[category]['$no_subcategory']
            now.write(0, f"{category}:")
            row += 2
            now = sheet_spends.row(row)
            now.write(1, "Без подкатегории:")
            row += 1
            for spend in no_category:
                now = sheet_spends.row(row)
                if spend['name_of_spend'] is None:
                    now.write(2, "Безымянный")
                else:
                    now.write(2, spend['name_of_spend'])
                now.write(3, spend['date_of_spend'])
                now.write(4, spend['value_of_spend'])
                now.write(5, currency)
                row += 1
            row += 1
            for sub_category in (spends[category].keys()):
                now = sheet_spends.row(row)
                if sub_category == "$all" or sub_category == "$no_subcategory":
                    row += 1
                    continue
                sum = spends[category][sub_category]
                now.write(1, sub_category)
                row += 1
                for spend in sum:
                    now = sheet_spends.row(row)
                    if spend['name_of_spend'] is None:
                        now.write(2, "Безымянный")
                    else:
                        now.write(2, spend['name_of_spend'])
                    now.write(3, spend['date_of_spend'])
                    now.write(4, spend['value_of_spend'])
                    now.write(5, currency)
                    row += 1
                row += 1
            row += 2

        sheet_incomes = book.add_sheet("Доходы")

        row = 0
        now = sheet_incomes.row(row)
        now.write(0, "Id")
        now.write(1, "Имя дохода")
        now.write(2, "Дата дохода")
        now.write(3, "Сумма")
        now.write(4, "Валюта")
        row = 2
        for income_id in incomes.keys():
            now = sheet_incomes.row(row)
            if incomes[income_id]['type_of_income'] == "remained":
                continue
            now.write(0, row - 1)
            if incomes[income_id]['name_of_income'] is None:
                now.write(1, "Безымянный")
            else:
                now.write(1, incomes[income_id]['name_of_income'])
            now.write(2, incomes[income_id]['date_of_income'])
            now.write(3, incomes[income_id]['value_of_income'])
            now.write(4, currency)
            row += 1

        path = f'temporary\\report\\{user_id}.xls'
        book.save(path)
        return path
    except Exception as e:
        logging.error(f"{get_report_table.__name__}: {e}. Пользователь с id {user_id}.")
