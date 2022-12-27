import pandas as pd
from math import isnan


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
    с датой в файле currency.csv

    Args:
        row (Series): Строка в data_file
    Returns:
        float: Значение для ячейки 'salary' в рублях
    """
    convert = pd.read_csv("currency.csv")
    if row["salary_currency"] in convert.columns:
        answer = row["salary"] * float(convert[convert["date"] == row["published_at"][:7]][row["salary_currency"]])
        return round(answer, 2)
    return row["salary"]


def currency_conversion(file_name):
    """Обрабатывает данные из колонок salary_from, salary_to, salary_currency и объединяет в колонку salary

    Args:
        file_name: Путь к файлу vacancies_dif_currencies.csv
    """
    data_file = pd.read_csv(file_name)
    answer = data_file.loc[0:99].copy()
    answer["salary"] = answer.apply(lambda row: get_average_salary(row), axis=1)
    answer["salary"] = answer.apply(lambda row: converting_salaries_into_rubles(row), axis=1)
    answer.drop(labels=["salary_from", "salary_to", "salary_currency"], axis=1, inplace=True)
    answer = answer[["name", "salary", "area_name", "published_at"]]
    answer.to_csv("100_vacancies.csv", index=False)


currency_conversion('data\\vacancies_dif_currencies.csv')