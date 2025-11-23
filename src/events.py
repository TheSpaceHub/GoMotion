import pandas as pd

def load_events_df(download: bool = False) -> pd.DataFrame | None:
    """Returns main Barcelona events from 2023 to 31-08-2025 in a DataFrame with columns: day, category, impact.
    Expects laliga.csv, city_events.csv files to exist"""
    
    try:
        df_laliga = pd.read_csv("data/laliga.csv")
        df_events = pd.read_csv("data/city_events.csv")
    except:
        raise FileNotFoundError("File not found laliga.csv or city_events.csv")
    
    champions_data = [
    ("2023-09-19", "UEFA Champions League — Barça vs Antwerp (home)", 9, "Evento Deportivo"),
    ("2023-10-25", "UEFA Champions League — Barça vs Shakhtar Donetsk (home)", 9, "Evento Deportivo"),
    ("2023-11-28", "UEFA Champions League — Barça vs Porto (home)", 9, "Evento Deportivo"),
    ("2024-10-01", "UEFA Champions League — Barça vs Young Boys (home)", 9, "Evento Deportivo"),
    ("2024-10-23", "UEFA Champions League — Barça vs Bayern Munich (home)", 10, "Evento Deportivo"),
    ("2024-11-26", "UEFA Champions League — Barça vs Brest (home)", 9, "Evento Deportivo"),
    ("2025-01-29", "UEFA Champions League — Barça vs Atalanta (home)", 9, "Evento Deportivo")
    ]
    
    df_champions = pd.DataFrame(champions_data, columns=["day", "description", "impact", "category"])
    df_champions["day"] = pd.to_datetime(df_champions["day"], format="%Y-%m-%d")

    df_laliga["day"] = pd.to_datetime(df_laliga["day"], format="%d-%m-%Y")

    df_fcbarcelona = df_laliga[df_laliga["home"] == "Barcelona"].copy()
    df_fcbarcelona = df_fcbarcelona[["day"]]
    df_fcbarcelona["description"] = "Partido LaLiga — Barça (home)"
    df_fcbarcelona["category"] = "Evento Deportivo"
    df_fcbarcelona["impact"] = 7

    df_events["day"] = pd.to_datetime(df_events["day"])

    df = pd.concat([df_champions, df_fcbarcelona, df_events], ignore_index=True)
    df = df[["day","impact", "category"]]
    if download: df.to_csv("data/events.csv")
    return df

def load_holidays_df() -> pd.DataFrame:
    """Returns a DataFrame with holidays from 1-1-2023 to 31-8-2025. Expects festius.csv yo exist"""
    try: 
        df_holidays = pd.read_csv("data/festius.csv")
    except:
        raise FileNotFoundError("File data/festius.csv not found")
    
    df_holidays["day"] = pd.to_datetime(df_holidays["day"])
    df_holidays = df_holidays.drop(columns=["description"])
    df_holidays["is_holiday"] = 1

    return df_holidays