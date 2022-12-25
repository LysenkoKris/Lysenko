import pandas as pd
import sqlite3


def get_sql():
    """
    Переводит csv-файл в таблицу sqlite.
    """
    df = pd.read_csv('currency.csv')
    df.to_sql('currency', sqlite3.connect('currency.sqlite'), if_exists='replace', index=False)


get_sql()