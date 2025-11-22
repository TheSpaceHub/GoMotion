from src.meteo import daily_weather_summary
from src.intensities import process_df
import pandas as pd

# Creación del archivo para entrenar al modelo

data = pd.read_csv('data/movilidad_barrios.csv')
intensities = process_df(data)
meteo = daily_weather_summary()

df = pd.merge(
    left=intensities, 
    right=meteo, 
    on='day', 
    how='left'
)

df['year'] = df['day'].dt.year
df['month'] = df['day'].dt.month
df['day_of_the_month'] = df['day'].dt.day
df['day_of_the_week'] = df['day'].dt.day_name(locale='es_ES')
df.to_csv('data/final_data.csv', index = False)