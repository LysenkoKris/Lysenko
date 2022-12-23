import multiprocessing
import cProfile
import os
from pandas import read_csv
import concurrent.futures as con_fut

list_print1 = ['Динамика уровня зарплат по годам: ','Динамика количества вакансий по годам: ',
                      'Динамика уровня зарплат по годам для выбранной профессии: ','Динамика количества вакансий по годам для выбранной профессии: ',
                      'Уровень зарплат по городам (в порядке убывания): ','Доля вакансий по городам (в порядке убывания): ']
class Solution:
    """Класс для получения и печати статистик

    Attributes:
        path_to_file (str): Путь к входному csv-файлу
        name_vacancy (str): Название выбранной профессии
        dynamics1 (dict): Динамика уровня зарплат по годам
        dynamics2 (dict): Динамика количества вакансий по годам
        dynamics3 (dict): Динамика уровня зарплат по годам для выбранной профессии
        dynamics4 (dict): Динамика количества вакансий по годам для выбранной профессии
        dynamics5 (dict): Уровень зарплат по городам (в порядке убывания)
        dynamics6 (dict): Доля вакансий по городам (в порядке убывания)
    """
    def __init__(self, path_to_file, name_vacancy):
        """Инициализирует объект Solution.

        Args:
            name_vacancy (str): Название выбранной профессии
            path_to_file (str): Путь к входному csv-файлу
        """
        self.path_to_file = path_to_file
        self.name_vacancy = name_vacancy
        self.dynamics1 = {}
        self.dynamics2 = {}
        self.dynamics3 = {}
        self.dynamics4 = {}
        self.dynamics5 = {}
        self.dynamics6 = {}

    def split_by_year(self):
        """Разделяет входной файл на меньшие, группирует по годам
        """

        data_of_file = read_csv(self.path_to_file)
        data_of_file["year"] = data_of_file["published_at"].apply(lambda x: x[:4])
        data_of_file = data_of_file.groupby("year")
        for year, data in data_of_file:
            data[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]]. \
                to_csv(rf"data\csv_by_years\year_number_{year}.csv", index=False)

    def get_dynamics(self):
        """Получение динамик
        """
        self.get_dynamics_by_year_with_multiprocessing()
        self.get_dynamics_by_city()

    def get_statistic_by_year(self, file_csv):
        """Составляет статистику по году

        Args:
            file_csv (str): Название файла с данными о вакансиях за год
        Returns:
            str, [int, int, int, int]: год, [ср. зп, всего вакансий, ср. зп для профессии, вакансий по профессии]
        """
        data_of_file = read_csv(file_csv)
        data_of_file["salary"] = data_of_file[["salary_from", "salary_to"]].mean(axis=1)
        data_of_file["published_at"] = data_of_file["published_at"].apply(lambda s: int(s[:4]))
        data_of_file_vacancy = data_of_file[data_of_file["name"].str.contains(self.name_vacancy)]

        return data_of_file["published_at"].values[0], [int(data_of_file["salary"].mean()), len(data_of_file),
                                              int(data_of_file_vacancy["salary"].mean() if len(data_of_file_vacancy) != 0 else 0), len(data_of_file_vacancy)]

    def add_elements_to_dynamics(self, result):
        """Добавляет значения в динамики по годам

        Args:
            result (list): Список значений для динамик
        """
        for year, data_dynamics in result:
            self.dynamics1[year] = data_dynamics[0]
            self.dynamics2[year] = data_dynamics[1]
            self.dynamics3[year] = data_dynamics[2]
            self.dynamics4[year] = data_dynamics[3]

    def get_dynamics_by_year_not_with_multiprocessing(self):
        """Получает статистики по годам с использованием только одиного процесса
        """
        result = []
        for filename in os.listdir("data\csv_by_years"):
            with open(os.path.join("data\csv_by_years", filename), "r") as file_csv:
                result.append(self.get_statistic_by_year(file_csv.name))

        self.add_elements_to_dynamics(result)

    def get_dynamics_by_year_with_multiprocessing(self):
        """Получает статистики по годам с использованием нескольких процессов
        """
        files = [rf"data\csv_by_years\{file_name}" for file_name in os.listdir(rf"data\csv_by_years")]
        pool = multiprocessing.Pool(4)
        result = pool.starmap(self.get_statistic_by_year, [(file,) for file in files])
        pool.close()

        self.add_elements_to_dynamics(result)

    def get_dynamics_by_year_with_concurrent_futures(self):
        """Получает статистики по годам с использованием модуля concurrent futures
        """
        files = [rf"data\csv_by_years\{file_name}" for file_name in os.listdir("data\csv_by_years")]
        with con_fut.ProcessPoolExecutor(max_workers=4) as executer:
            res = executer.map(self.get_statistic_by_year, files)
        result = list(res)

        self.add_elements_to_dynamics(result)

    def get_dynamics_by_city(self):
        """Получает статистики по городам
        """
        data_of_file = read_csv(self.path_to_file)
        total = len(data_of_file)
        data_of_file["salary"] = data_of_file[["salary_from", "salary_to"]].mean(axis=1)
        data_of_file["count"] = data_of_file.groupby("area_name")["area_name"].transform("count")
        data_of_file = data_of_file[data_of_file["count"] > total * 0.01]
        data_of_file = data_of_file.groupby("area_name", as_index=False)
        data_of_file = data_of_file[["salary", "count"]].mean().sort_values("salary", ascending=False)
        data_of_file["salary"] = data_of_file["salary"].apply(lambda s: int(s))

        self.dynamics5 = dict(zip(data_of_file.head(10)["area_name"], data_of_file.head(10)["salary"]))

        data_of_file = data_of_file.sort_values("count", ascending=False)
        data_of_file["count"] = round(data_of_file["count"] / total, 4)

        self.dynamics6 = dict(zip(data_of_file.head(10)["area_name"], data_of_file.head(10)["count"]))

    def print_statistic(self):
        """Выводит все динамики с описанием

        Prints:
            Печатать каждой динамики с описанием
        """
        list_print2 = [self.dynamics1, self.dynamics2, self.dynamics3, self.dynamics4, self.dynamics5, self.dynamics6]
        for i in range(len(list_print1)):
            print(list_print1[i] + '{0}'.format(list_print2[i]))


if __name__ == '__main__':
    # solve = Solution(input("Введите название файла: "), input("Введите название профессии: "))
    # solve.split_by_year()
    # solve.get_dynamics()
    # solve.print_statistic()

    solve = Solution("data\\vacancies.csv", "Аналитик")
    solve.split_by_year()
    # cProfile.run("solve.get_dynamics_by_year_not_with_multiprocessing()", sort="cumtime")
    # cProfile.run("solve.get_dynamics_by_year_with_multiprocessing()", sort="cumtime")
    cProfile.run("solve.get_dynamics_by_year_with_concurrent_futures()", sort="cumtime")