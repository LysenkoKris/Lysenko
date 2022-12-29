import multiprocessing
import cProfile
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader
import pathlib
import pdfkit

list_print1 = ['Динамика уровня зарплат по годам: ','Динамика количества вакансий по годам: ',
               'Динамика уровня зарплат по годам для выбранной профессии: ', 'Динамика количества вакансий по годам для выбранной профессии: ',
               'Уровень зарплат по городам (в порядке убывания): ', 'Доля вакансий по городам (в порядке убывания): ',
               'Динамика уровня зарплат по годам для выбранной профессии и региона: ',
               'Динамика количества вакансий по годам для выбранной профессии и региона: ']


class Solution:
    """Класс для получения и печати статистик

    Attributes:
        path_to_file (str): Путь к входному csv-файлу
        name_vacancy (str): Название выбранной профессии
        area_name (str): Название выбранного региона
        dynamics1 (dict): Динамика уровня зарплат по годам
        dynamics2 (dict): Динамика количества вакансий по годам
        dynamics3 (dict): Динамика уровня зарплат по годам для выбранной профессии
        dynamics4 (dict): Динамика количества вакансий по годам для выбранной профессии
        dynamics5 (dict): Уровень зарплат по городам (в порядке убывания)
        dynamics6 (dict): Доля вакансий по городам (в порядке убывания)
        dynamics7 (dict): Динамика уровня зарплат по годам для выбранной профессии и региона
        dynamics8 (dict): Динамика количества вакансий по годам для выбранной профессии и региона
    """
    def __init__(self, path_to_file, name_vacancy, area_name):
        """Инициализирует объект Solution.

        Args:
            name_vacancy (str): Название выбранной профессии
            path_to_file (str): Путь к входному csv-файлу
            area_name (str): Название выбранного региона
        """
        self.path_to_file = path_to_file
        self.name_vacancy = name_vacancy
        self.area_name = area_name
        self.dynamics1 = {}
        self.dynamics2 = {}
        self.dynamics3 = {}
        self.dynamics4 = {}
        self.dynamics5 = {}
        self.dynamics6 = {}
        self.dynamics7 = {}
        self.dynamics8 = {}

    def split_by_year(self):
        """Разделяет входной файл на меньшие, группирует по годам
        """
        data_of_file = pd.read_csv(self.path_to_file)
        data_of_file["year"] = data_of_file["published_at"].apply(lambda x: x[:4])
        data_of_file = data_of_file.groupby("year")
        for year, data in data_of_file:
            data[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]]. \
                to_csv(rf"data\csv_by_years_dif_currencies\year_number_{year}.csv", index=False)

    def get_dynamics(self):
        """Получение динамик
        """
        self.get_dynamics_by_year_with_multiprocessing()
        self.get_dynamics_by_city()
        return self.dynamics1, self.dynamics2, self.dynamics3, self.dynamics4, self.dynamics5, self.dynamics6, self.dynamics7, self.dynamics8

    def get_statistic_by_year(self, file_csv):
        """Составляет статистику по году
        Args:
            file_csv (str): Название файла с данными о вакансиях за год
        Returns:
            str, [int, int, int, int, int, int]: год, [ср. зп, всего вакансий, ср. зп для профессии,
            вакансий по профессии, ср. зп для профессии и региона, вакансий по профессии и региону]
        """
        data_of_file = pd.read_csv(file_csv)
        data_of_file["salary"] = data_of_file[["salary_from", "salary_to"]].mean(axis=1)
        data_of_file["published_at"] = data_of_file["published_at"].apply(lambda s: int(s[:4]))
        data_of_file_vacancy = data_of_file[data_of_file["name"].str.contains(self.name_vacancy, case=False)]
        data_of_file_vacancy_area = data_of_file_vacancy[data_of_file_vacancy["area_name"].str.contains(self.area_name)]

        return data_of_file["published_at"].values[0], [int(data_of_file["salary"].mean()), len(data_of_file),
                                                        int(data_of_file_vacancy["salary"].mean() if len(data_of_file_vacancy) != 0 else 0),
                                                        len(data_of_file_vacancy),
                                                        int(data_of_file_vacancy_area["salary"].mean() if len(data_of_file_vacancy_area) != 0 else 0),
                                                        len(data_of_file_vacancy_area)]

    def get_dynamics_by_year_with_multiprocessing(self):
        """Получает статистики по годам с использованием нескольких процессов
        """
        files = [rf"data\csv_by_years_dif_currencies\{file_name}" for file_name in os.listdir(rf"data\csv_by_years_dif_currencies")]
        pool = multiprocessing.Pool(4)
        result = pool.starmap(self.get_statistic_by_year, [(file,) for file in files])
        pool.close()
        for year, data_dynamics in result:
            self.dynamics1[year] = data_dynamics[0]
            self.dynamics2[year] = data_dynamics[1]
            self.dynamics3[year] = data_dynamics[2]
            self.dynamics4[year] = data_dynamics[3]
            self.dynamics7[year] = data_dynamics[4]
            self.dynamics8[year] = data_dynamics[5]

    def get_dynamics_by_city(self):
        """Получает статистики по городам
        """
        data_of_file = pd.read_csv(self.path_to_file)
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
        list_print2 = [self.dynamics1, self.dynamics2, self.dynamics3, self.dynamics4, self.dynamics5, self.dynamics6, self.dynamics7, self.dynamics8]
        for i in range(len(list_print1)):
            print(list_print1[i] + '{0}'.format(list_print2[i]))
        InputConnect(self.path_to_file, self.name_vacancy, self.dynamics1, self.dynamics2, self.dynamics3, self.dynamics4, self.dynamics5, self.dynamics6)


class InputConnect:
    """ Класс для получения контента

    Attributes:
        path_to_file (str): Путь к входному csv-файлу
        name_vacancy (str): Название выбранной профессии
    """
    def __init__(self,path_to_file, name_vacancy, dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6):
        """Инициализирует объект InputConnect.

        Args:
            path_to_file (str): Путь к входному csv-файлу
            name_vacancy (str): Название выбранной профессии
            dynamics1 (dict): Динамика уровня зарплат по годам
            dynamics2 (dict): Динамика количества вакансий по годам
            dynamics3 (dict): Динамика уровня зарплат по годам для выбранной профессии
            dynamics4 (dict): Динамика количества вакансий по годам для выбранной профессии
            dynamics5 (dict): Уровень зарплат по городам (в порядке убывания)
            dynamics6 (dict): Доля вакансий по городам (в порядке убывания)
        """
        self.path_to_file, self.name_vacancy = path_to_file, name_vacancy
        dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6 = dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6
        new_graphic = Report(self.name_vacancy, dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6)
        new_graphic.generate_image()
        new_graphic.generate_pdf()


class Report:
    """ Класс для генерации гистрограмм и итогового pdf

    Attributes:
        name_vacancy (str): Название выбранной профессии
        dynamics1 (dict): Динамика уровня зарплат по годам
        dynamics2 (dict): Динамика количества вакансий по годам
        dynamics3 (dict): Динамика уровня зарплат по годам для выбранной профессии
        dynamics4 (dict): Динамика количества вакансий по годам для выбранной профессии
        dynamics5 (dict): Уровень зарплат по городам (в порядке убывания)
        dynamics6 (dict): Доля вакансий по городам (в порядке убывания)
    """
    def __init__(self, name_vacancy, dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6):
        """Инициализирует объект Report.

        Args:
            name_vacancy (str): Название выбранной профессии
            dynamics1 (dict): Динамика уровня зарплат по годам
            dynamics2 (dict): Динамика количества вакансий по годам
            dynamics3 (dict): Динамика уровня зарплат по годам для выбранной профессии
            dynamics4 (dict): Динамика количества вакансий по годам для выбранной профессии
            dynamics5 (dict): Уровень зарплат по городам (в порядке убывания)
            dynamics6 (dict): Доля вакансий по городам (в порядке убывания)
        """
        self.name_vacancy = name_vacancy
        self.dynamics1 = dynamics1
        self.dynamics2 = dynamics2
        self.dynamics3 = dynamics3
        self.dynamics4 = dynamics4
        self.dynamics5 = dynamics5
        self.dynamics6 = dynamics6

    def generate_image(self):
        """Генерирует 4 гистрограммы и сохраняет в png файл:
        1) Диаграмма - уровень зарплат по годам для вывода динамики уровня зарплат по годам как общий,
        так и для выбранной профессии
        2) Диаграмма - количество вакансий по годам как общий, так и для выбранной профессии
        3) Горизонтальная диаграмма - уровень зарплат по городам
        4) Круговая диаграмма - количество вакансий по городам
        """
        x = np.arange(len(self.dynamics1.keys()))
        width = 0.35

        fig, axs = plt.subplots(ncols=2, nrows=2)
        axs[0, 0].bar(x - width / 2, self.dynamics1.values(), width, label='средняя з/п')
        axs[0, 0].bar(x + width / 2, self.dynamics3.values(), width, label='з/п {0}'.format(self.name_vacancy))
        plt.rcParams['font.size'] = '8'
        for label in (axs[0, 0].get_xticklabels() + axs[0, 0].get_yticklabels()):
            label.set_fontsize(7)
        axs[0, 0].set_title('Уровень зарплат по годам')
        axs[0, 0].set_xticks(x, self.dynamics1.keys(), rotation=90)
        axs[0, 0].grid(axis='y')
        axs[0, 0].legend(fontsize=7)

        axs[0, 1].bar(x - width / 2, self.dynamics2.values(), width, label='количество вакансий')
        axs[0, 1].bar(x + width / 2, self.dynamics4.values(), width,
                      label='количество вакансий {0}'.format(self.name_vacancy))
        for label in (axs[0, 1].get_xticklabels() + axs[0, 1].get_yticklabels()):
            label.set_fontsize(7)
        axs[0, 1].set_title('Количество вакансий по годам')
        axs[0, 1].set_xticks(x, self.dynamics2.keys(), rotation=90)
        axs[0, 1].grid(axis='y')
        axs[0, 1].legend(fontsize=7)
        fig.tight_layout()

        areas = []
        for area in self.dynamics5.keys():
            areas.append(str(area).replace(' ', '\n').replace('-', '-\n'))
        y_pos = np.arange(len(areas))
        performance = self.dynamics5.values()
        error = np.random.rand(len(areas))
        axs[1, 0].barh(y_pos, performance, xerr=error, align='center')
        for label in (axs[1, 0].get_xticklabels() + axs[1, 0].get_yticklabels()):
            label.set_fontsize(7)
        axs[1, 0].set_yticks(y_pos, labels=areas, size=7)
        axs[1, 0].invert_yaxis()
        axs[1, 0].grid(axis='x')
        axs[1, 0].set_title('Уровень зарплат по городам')

        val = list(self.dynamics6.values()) + [1 - sum(list(self.dynamics6.values()))]
        k = list(self.dynamics6.keys()) + ['Другие']
        axs[1, 1].pie(val, labels=k, startangle=150)
        axs[1, 1].set_title('Доля вакансий по городам')

        plt.tight_layout()
        plt.savefig('graph.png', dpi=300)

    def generate_pdf(self):
        """Генерация pdf файла, в котором содержатся таблицы и png файл
        """
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template.html")
        dynamics = []
        for year in self.dynamics2.keys():
            dynamics.append([year, self.dynamics1[year], self.dynamics2[year], self.dynamics3[year], self.dynamics4[year]])

        for key in self.dynamics6:
            self.dynamics6[key] = round(self.dynamics6[key] * 100, 2)

        pdf_template = template.render({'name': self.name_vacancy,
                                        'path': '{0}/{1}'.format(pathlib.Path(__file__).parent.resolve(), 'graph.png'),
                                        'dynamics': dynamics, 'dynamics5': self.dynamics5, 'dynamics6': self.dynamics6})

        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report_3_4_3.pdf', configuration=config, options={"enable-local-file-access": ""})


if __name__ == '__main__':
    filename = input('Введите название файла: ')
    name_vacancy = input('Введите название профессии: ')
    area_name = input('Введите название региона: ')
    solve = Solution(filename, name_vacancy, area_name)
    solve.split_by_year()
    solve.get_dynamics()
    solve.print_statistic()