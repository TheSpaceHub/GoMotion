import requests
import pandas as pd
import io

# Coordenadas de Barcelona
LATITUDE = 41.38
LONGITUDE = 2.17

# Rango de fechas
START_DATE = "2023-01-01"
END_DATE = "2025-08-31"

API_URL = "https://archive-api.open-meteo.com/v1/archive"

def daily_resume(lat, lon, start, end):
    """Obtains historic Barcelona meteorological data (precipitation + temperature)"""
   
    parametros = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "format": "csv"
    }
    
    response = requests.get(API_URL, params=parametros)
    
    if response.status_code == 200:
        # Usar skiprows=2 para ignorar las líneas de metadatos (coordenadas y unidades)
        # Se renombra la columna 'time' a 'day' para claridad
        df = pd.read_csv(io.StringIO(response.text), skiprows=2)
        df = df.rename(columns={'time': 'day'})
        df['day'] = pd.to_datetime(df['day'])
        
        return df
    else:
        print(f"Error al obtener datos. Código de estado: {response.status_code}")
        print(response.text)
        return None

df_barcelona = daily_resume(
    LATITUDE, LONGITUDE, START_DATE, END_DATE
)

if df_barcelona is not None:
    df_barcelona.to_csv('data/meteo.csv', index=False)


df1 = pd.read_csv('data/meteo.csv')
df2 = pd.read_csv('data/intensities.csv')

df_combined = pd.merge(
    left=df1, 
    right=df2, 
    on='day', 
    how='left'
)

df_combined.to_csv('data/final_data.csv', index = False)