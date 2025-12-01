import requests
import pandas as pd
import io
from datetime import datetime, timedelta

TODAY = datetime.today()
ONE_WEEK = TODAY+ timedelta(weeks=1)

# Coordenadas de Barcelona
LATITUDE = 41.38
LONGITUDE = 2.17

# Rango de fechas
START_DATE = "2023-01-01"
END_DATE = "2025-08-31"

API_URL_PAST = "https://archive-api.open-meteo.com/v1/archive"
API_URL_FUTURE = "https://api.open-meteo.com/v1/forecast"


def daily_weather_summary(lat = LATITUDE, lon = LONGITUDE, start = START_DATE, end = END_DATE) -> pd.DataFrame | None:
    """Obtains historic Barcelona meteorological data (precipitation + temperature)"""
   
    parametros = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "format": "csv"
    }


    response = requests.get(API_URL_PAST, params=parametros)
    
    if response.status_code == 200:
        # Usar skiprows=2 para ignorar las líneas de metadatos (coordenadas y unidades)
        # Se renombra la columna 'time' a 'day' para claridad
        df = pd.read_csv(io.StringIO(response.text), skiprows=2)
        df = df.rename(columns={'time': 'day'})
        df['day'] = pd.to_datetime(df['day'])
        return df
    else:
        print(f"Error obtaining data. Response status code: {response.status_code}")
        print(response.text)
        return None

def weather_forecast_1_week(lat = LATITUDE, lon = LONGITUDE, start = TODAY.strftime('%Y-%m-%d')  , end = ONE_WEEK.strftime('%Y-%m-%d')  ) -> pd.DataFrame | None:
    """Obtains historic Barcelona meteorological data (precipitation + temperature)"""
   
    parametros = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "format": "csv"
    }


    response = requests.get(API_URL_FUTURE, params=parametros)
    
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text), skiprows=2)
        df = df.rename(columns={'time': 'day'})
        df['day'] = pd.to_datetime(df['day'])
        return df
    else:
        print(f"Error obtaining data. Response status code: {response.status_code}")
        print(response.text)
        return None
    
