from src.meteo import daily_weather_summary
from src.intensities import process_df
from src.events import load_events_df, load_holidays_df
import pandas as pd

# Creación del archivo para entrenar al modelo

data = pd.read_csv('data/movilidad_barrios.csv')
intensities = process_df(data)
meteo = daily_weather_summary()
events = load_events_df()
holidays = load_holidays_df()

df_to_merge: list[pd.DataFrame] = [meteo, events, holidays]
df = intensities.copy()

for other in df_to_merge:
    df = df.merge(other, on="day", how="left")

df['year'] = df['day'].dt.year
df['month'] = df['day'].dt.month
df['day_of_the_month'] = df['day'].dt.day
df['day_of_the_week'] = df['day'].dt.day_name(locale='es_ES')
df["impact"] = df["impact"].fillna(0)
df["category"] = df["category"].fillna(0)
df["is_holiday"] = df["is_holiday"].fillna(0)
df.to_csv('data/final_data.csv', index = False)