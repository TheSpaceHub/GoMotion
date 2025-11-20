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

def daily_resume(lat = LATITUDE, lon = LONGITUDE, start = START_DATE, end = END_DATE):
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
