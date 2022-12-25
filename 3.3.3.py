import requests
import time
import pandas as pd
import json


def get_page(page, half):
    """Получает ответ на запрос с api.hh.ru по сто вакансий за страницу

    Args:
        page (int): Номер страницы для выгрузки
        half (int): Вакансии во второй половине дня
    Returns:
        str: Список IT-вакансий в формате .json
    """
    if not half:
        hour, next_hour = '00', '11'
    else:
        hour, next_hour = '12', '23'
    params = {
        "specialization": 1,
        "found": 1,
        "per_page": 100,
        "page": page,
        "date_from": f"2022-12-21T{hour}:00:00+0300",
        "date_to": f"2022-12-21T{next_hour}:59:00+0300"
    }

    try:
        request = requests.get('https://api.hh.ru/vacancies', params)
        data = request.content.decode()
        request.close()
    except:
        return get_page(page)

    return data


def set_vacancies():
    """Собирает и сохраняет в csv-файл данные о вакансиях с api.hh.ru
    """
    data_file = pd.DataFrame(columns=['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'])
    result = []
    for half in range(2):
        for page in range(0, 999):
            js_obj = json.loads(get_page(page, half))
            result += [js_obj]
            if (js_obj['pages'] - page) <= 1:
                break
            time.sleep(1)

    for vacancies in result:
        for row in vacancies['items']:
            if row['salary'] is not None:
                data_file.loc[len(data_file)] = [row['name'], row['salary']['from'],
                                                 row['salary']['to'], row['salary']['currency'],
                                                 row['area']['name'], row['published_at']]
            else:
                data_file.loc[len(data_file)] = [row['name'], '',
                                                 '', '',
                                                 row['area']['name'], row['published_at']]

    data_file.to_csv("hh_vacancies.csv", index=False)


set_vacancies()