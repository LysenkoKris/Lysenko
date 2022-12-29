import pandas as pd
from math import isnan
import sqlite3


def get_average_salary(row):
    """Возращает значение для поля salary в зависимости от заполненности полей salary_from, salary_to
    Args:
        row (Series): Строка в data_file
    Returns:
        float: Значение для ячейки 'salary'
    """
    cell_values = []
    cell_values += [row["salary_from"]] if not isnan(row["salary_from"]) else []
    cell_values += [row["salary_to"]] if not isnan(row["salary_to"]) else []
    if len(cell_values) != 0:
        return sum(cell_values) / len(cell_values)
    return


def converting_salaries_into_rubles(row):
    """Переводит значение salary в рубли после сравнения даты появления вакансии
    с датой в файле currencies.db
    Args:
        row (Series): Строка в data_file
    Returns:
        float: Значение для ячейки 'salary' в рублях
    """
    answer = []
    exchange = sqlite3.connect("currencies.db")
    cur = exchange.cursor()
    cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('currency');")
    for i in cur.fetchall():
        answer.append(i[0])
    if row["salary_currency"] in answer:
        cur.execute(f"SELECT {row['salary_currency']} FROM currency WHERE Date = ?", (row["published_at"][:7],))
        answer = row["salary"] * float(cur.fetchone()[0])
        return round(answer, 2)
    return row["salary"]


def currency_conversion(file_name):
    """Обрабатывает данные из колонок salary_from, salary_to, salary_currency и объединяет в колонку salary
    Args:
        file_name: Путь к файлу vacancies_dif_currencies.csv
    """
    data_file = pd.read_csv(file_name)
    data_file["salary"] = data_file.apply(lambda row: get_average_salary(row), axis=1)
    data_file["salary"] = data_file.apply(lambda row: converting_salaries_into_rubles(row), axis=1)
    data_file.drop(labels=["salary_from", "salary_to", "salary_currency"], axis=1, inplace=True)
    data_file = data_file[["name", "salary", "area_name", "published_at"]]
    cnx = sqlite3.connect("vacancies.db")
    data_file.to_sql("vacancies", con=cnx, index=False)


currency_conversion('data\\vacancies_dif_currencies.csv')