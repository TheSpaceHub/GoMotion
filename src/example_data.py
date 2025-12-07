import pandas as pd
import numpy as np

barri_coefs = {
    "el Raval": 1.5,
    "el Barri Gòtic": 1.4,
    "la Barceloneta": 0.3,
    "Sant Pere, Santa Caterina i la Ribera": 1.5,
    "el Fort Pienc": 1.7,
    "la Sagrada Família": 3.4,
    "la Dreta de l'Eixample": 5.3,
    "l'Antiga Esquerra de l'Eixample": 3.0,
    "la Nova Esquerra de l'Eixample": 2.5,
    "Sant Antoni": 2.1,
    "el Poble-sec": 0.9,
    "la Marina del Prat Vermell": 0.3,
    "la Marina de Port": 0.5,
    "la Font de la Guatlla": 0.5,
    "Hostafrancs": 1.1,
    "la Bordeta": 0.6,
    "Sants - Badal": 0.4,
    "Sants": 1.5,
    "les Corts": 2.2,
    "la Maternitat i Sant Ramon": 0.5,
    "Pedralbes": 0.4,
    "Vallvidrera, el Tibidabo i les Planes": 0.1,
    "Sarrià": 0.7,
    "les Tres Torres": 0.9,
    "Sant Gervasi - la Bonanova": 1.1,
    "Sant Gervasi - Galvany": 2.6,
    "el Putxet i el Farró": 1.2,
    "Vallcarca i els Penitents": 1.4,
    "el Coll": 0.8,
    "la Salut": 1.3,
    "la Vila de Gràcia": 2.4,
    "el Camp d'en Grassot i Gràcia Nova": 2.3,
    "el Baix Guinardó": 1.7,
    "Can Baró": 0.6,
    "el Guinardó": 2.2,
    "la Font d'en Fargues": 0.4,
    "el Carmel": 1.1,
    "la Teixonera": 0.8,
    "Sant Genís dels Agudells": 0.2,
    "Montbau": 0.2,
    "la Vall d'Hebron": 0.4,
    "la Clota": 0.4,
    "Horta": 0.8,
    "Vilapicina i la Torre Llobeta": 1.8,
    "Porta": 0.8,
    "el Turó de la Peira": 0.7,
    "Can Peguera": 0.3,
    "la Guineueta": 0.6,
    "Canyelles": 0.1,
    "les Roquetes": 0.2,
    "Verdun": 0.2,
    "la Prosperitat": 0.4,
    "la Trinitat Nova": 0.2,
    "Torre Baró": 0.1,
    "Ciutat Meridiana": 0.1,
    "Vallbona": 0.0,
    "la Trinitat Vella": 0.1,
    "Baró de Viver": 0.1,
    "el Bon Pastor": 0.3,
    "Sant Andreu": 0.9,
    "la Sagrera": 1.3,
    "el Congrés i els Indians": 0.9,
    "Navas": 1.1,
    "el Camp de l'Arpa del Clot": 1.4,
    "el Clot": 1.4,
    "el Parc i la Llacuna del Poblenou": 1.7,
    "la Vila Olímpica del Poblenou": 0.6,
    "el Poblenou": 0.7,
    "Diagonal Mar i el Front Marítim del Poblenou": 0.3,
    "el Besòs i el Maresme": 0.2,
    "Provençals del Poblenou": 0.9,
    "Sant Martí de Provençals": 0.6,
    "la Verneda i la Pau": 0.4,
}

dotw_coefs = {
    0: 1.0,
    1: 1.2,
    2: 1.2,
    3: 1.2,
    4: 1.1,
    5: 0.8,
    6: 0.6,
}

month_coefs = {
    1: 1.0,
    2: 1.1,
    3: 1.1,
    4: 1.0,
    5: 1.1,
    6: 1.0,
    7: 1.0,
    8: 0.7,
    9: 1.0,
    10: 1.1,
    11: 1.1,
    12: 1.0,
}

model_const = 96000


def generate_day(day: pd.Timestamp, barri: str) -> float:
    """Generate the intensity for a day"""
    return (
        month_coefs[day.month]
        * dotw_coefs[day.dayofweek]
        * barri_coefs[barri]
        * model_const
        * (1 + np.random.normal(0, 0.1, 1))
    )


def generate_data(start: str, end: str) -> pd.DataFrame:
    """Generates example data that follows the structure of the confidential data. Steps have been taken in order to ensure it is impossible to replicate the original numbers"""
    days = []
    barris = []
    intensities = []

    for day in pd.date_range(start=start, end=end):
        if day.day == 1:
            print(day.year, day.month)
        for barri in barri_coefs.keys():
            days.append(day)
            barris.append(barri)
            intensities.append(generate_day(day, barri)[0])
            
    return pd.DataFrame({"day" : days, "barri" : barris, "intensity" : intensities})
        


def main():
    df = generate_data(start="2023-01-01", end="2025-08-01")
    df.to_csv("data/intensities.csv", index=None)


if __name__ == "__main__":
    main()
