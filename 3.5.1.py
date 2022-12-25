import pandas as pd
import sqlite3

df = pd.read_csv('currency.csv')
df.to_sql('currency', sqlite3.connect('currency.sqlite'), if_exists='replace', index=False)