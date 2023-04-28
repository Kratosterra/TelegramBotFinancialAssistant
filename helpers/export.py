import csv
import os

from database import db_functions


async def get_export_table(user_id):
    if not os.path.exists('temporary'):
        os.makedirs('temporary')
    if not os.path.exists('temporary\\export'):
        os.makedirs('temporary\\export')

    incomes = await db_functions.return_all_incomes(user_id)
    spends = await db_functions.return_all_spends(user_id)

    with open(f"temporary\\export\\{user_id}.csv", mode="w", encoding='windows-1251') as w_file:
        file_writer = csv.writer(w_file, delimiter=";", lineterminator="\r")
        file_writer.writerow(["windows-1251", "", " ", " ", " "])
        file_writer.writerow(["$Incomes", " ", " ", " ", " "])
        file_writer.writerow(["$Name", "$Sum", "$Date", " ", " "])
        for inc_id in incomes:
            if incomes[inc_id]['type_of_income'] == "remained":
                continue
            name = incomes[inc_id]['name_of_income']
            value = incomes[inc_id]['value_of_income']
            date = incomes[inc_id]['date_of_income']
            file_writer.writerow([name, value, date, " ", " "])
        file_writer.writerow(["$Spends", " ", " ", " ", " "])
        file_writer.writerow(["$Name", "$Sum", "$Category", "$Subcategory", "$Date"])
        for spend_id in spends:
            name = spends[spend_id]['name_of_spend']
            value = spends[spend_id]['value_of_spend']
            category = spends[spend_id]['category']
            subcategory = spends[spend_id]['sub_category']
            date = spends[spend_id]['date_of_spend']
            file_writer.writerow([name, value, category, subcategory, date])

    return f"temporary\\export\\{user_id}.csv"
