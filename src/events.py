import pandas as pd
 

df_holidays = pd.read_csv("data/festius.csv")
df_holidays["day"] = pd.to_datetime(df_holidays["day"])
df_holidays_dates = df_holidays["day"]


df = pd.read_csv("data/partidos.csv")
df["day"] = pd.to_datetime(df["day"], format="%d-%m-%Y")
df_fcbarcelona = df[df["home"] == "Barcelona"].copy()
df_fcbarcelona = df_fcbarcelona[["day"]].copy()
df_fcbarcelona["category"] = "Evento Deportivo"
df_fcbarcelona["impact"] = 7


data = [
    ("2023-09-19", "UEFA Champions League — Barça vs Antwerp (home)", 9, "Evento Deportivo"),
    ("2023-10-25", "UEFA Champions League — Barça vs Shakhtar Donetsk (home)", 9, "Evento Deportivo"),
    ("2023-11-28", "UEFA Champions League — Barça vs Porto (home)", 9, "Evento Deportivo"),
    ("2024-10-01", "UEFA Champions League — Barça vs Young Boys (home)", 9, "Evento Deportivo"),
    ("2024-10-23", "UEFA Champions League — Barça vs Bayern Munich (home)", 10, "Evento Deportivo"),
    ("2024-11-26", "UEFA Champions League — Barça vs Brest (home)", 9, "Evento Deportivo"),
    ("2025-01-29", "UEFA Champions League — Barça vs Atalanta (home)", 9, "Evento Deportivo")
]

df_champions = pd.DataFrame(data, columns=["day", "event_description", "impact", "category"])
df_champions["day"] = pd.to_datetime(df_champions["day"])

df_events = pd.read_csv("data/events.csv")
df_events["day"] = pd.to_datetime(df_events["day"])

