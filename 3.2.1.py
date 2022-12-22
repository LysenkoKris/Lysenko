from pandas import set_option, read_csv

set_option("display.max_columns", False)
set_option("expand_frame_repr", False)


def split_by_year(path_to_file):
    """
    Разделяет входной файл на меньшие, группирует по годам

    Args:
        path_to_file (str): Путь к входному csv-файлу
    """
    data_of_file = read_csv(path_to_file)
    data_of_file["year"] = data_of_file["published_at"].apply(lambda x: x[:4])
    data_of_file = data_of_file.groupby("year")
    for year, data in data_of_file:
        data[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]].\
            to_csv(rf"data\csv_by_years\year_number_{year}.csv", index=False)


split_by_year("data\\vacancies.csv")