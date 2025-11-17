import pandas as pd
from barri_manager import get_barri
from typing import *
import requests
import os
from dotenv import load_dotenv
import re
from shapely.geometry import Point

Metro = str
Bus = str
Barri = str
Parades = list[Barri]

load_dotenv()

auth_params = {
    "app_id": os.getenv("TMB_APP_ID"),
    "app_key": os.getenv("TMB_APP_KEY")
}

def barris_metro()->dict[Metro:Parades]:
    """For each metro line, returns an ordered list of the neighbourhoods in the route"""

    pattern = r"L\d+[NS]?"
    barris: dict[Metro:Parades] = {}

    url = "https://api.tmb.cat/v1/transit/estacions"
    r = requests.get(url, params=auth_params)

    if r.status_code != 200:
        print(f"Error al obtener líneas: {r.status_code}")
        exit()

    lines_data = r.json()

    df_lines = pd.json_normalize(lines_data, record_path='features')

    for index, row in df_lines.iterrows():
        lineas = re.findall(pattern, row['properties.PICTO'])

        for linea in lineas:
            coordinates = row['geometry.coordinates']
            barri = get_barri(Point(coordinates[0], coordinates[1]))
            if barri:
                if linea in barris.keys() and barri not in barris[linea]:
                    barris[linea].append(barri)
                else:
                    barris[linea] = [barri]    

    return barris 

print(barris_metro())