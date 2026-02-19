from metadata_manager import MetadataManager
import llm_scraper
import datetime
import meteo
import database_connection
import pandas as pd
import joblib
import tensorflow as tf
import event_encoder
import sqlalchemy as sql
import numpy as np

def process_scraped_events(df_events: pd.DataFrame, barri_list: list[str]) -> pd.DataFrame:
    """
    Process events DataFrame by creating a new line for each barri affected
    """

    processed_events: list[dict] = []
    
    for _, row in df_events.iterrows():
        clean_date = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")
        impact_val = int(row["impact"])
        if row["barris"] == "all":
            for barri in barri_list:
                processed_events.append({
                    "day": clean_date,
                    "barri": barri,
                    "category": row["category"],
                    "impact": impact_val,
                    "description": row["description"],
                })
        else:
            for barri in row["barris"].split("|"):
                processed_events.append({
                    "day": clean_date,
                    "barri": barri,
                    "category": row["category"],
                    "impact": impact_val,
                    "description": row["description"],
                })
                
    return pd.DataFrame(processed_events)

def get_lag_features(date: datetime.datetime, barri: str, engine) -> tuple[float, float, float, float]:
    """
    Returns tuples with the intensity 7, 14, 21 and 28 days back
    """
    target = date.strftime("%Y-%m-%d")
    
    query = f"""
                select intensity
                from display_data 
                where DATE(day) in (
                    DATE('{target}') - INTERVAL '1 week', 
                    DATE('{target}') - INTERVAL '2 weeks',
                    DATE('{target}') - INTERVAL '3 weeks',
                    DATE('{target}') - INTERVAL '4 weeks'
                ) and barri = :barri
                order by day desc;
                """
                
    df_lag_fearures = pd.read_sql_query(sql.text(query), con=engine, params={"barri": barri})
    lags = tuple(df_lag_fearures["intensity"].to_list())
    
    if len(lags) != 4:
        print(f"Error! Missing lags from DB for {barri} on {target}")
        mean = 0 if len(lags) == 0 else sum(lags) / len(lags)
        return tuple(mean for _ in range(4))
    
    return lags


def main() -> None:
    """
    Executes pipeline, made to be executed daily, updates data in DB
    """
    
    engine = database_connection.connect_to_db()
    manager = MetadataManager(engine)
    TODAY = datetime.datetime.today()
    WEEK_AHEAD = TODAY + datetime.timedelta(days=7)
    weekdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    regressor = joblib.load("../models/regressor.joblib")
    encoder = tf.keras.models.load_model("../models/encoder.keras")
    max_len = int(pd.read_sql_query(sql.text("select value from metadata where key='encoder_max_len'"), con=engine).iloc[0, 0])
    latent_dim = 5
    
    features = [
        "barri",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "is_holiday",
        "month_cat",
        "day_cat",
        "lag_7",
        "lag_14",
        "lag_21",
        "lag_28",
        "dt_7_w1",
        "dt_7_w2",
        "enc1",
        "enc2",
        "enc3",
        "enc4",
        "enc5",
    ]

    
    df_barri = pd.read_sql_query(sql.text("select nom_barri from geospatial_data"), con=engine)
    barri_list = df_barri['nom_barri'].to_list()
    last_predicted_date = datetime.datetime.strptime(manager.get("last_predicted_day"), "%Y-%m-%d")
    df_events, df_festius = llm_scraper.scrape_week_ahead()
    df_events_processed = process_scraped_events(df_events, barri_list)
    
    # ------------------- EVENTS ------------------
    
    if datetime.datetime.strptime(manager.get("last_day_event_checked"), "%Y-%m-%d").date() < WEEK_AHEAD.date():
        
        database_connection.upload_df_to_db(df_events_processed, "events", engine)
        print("Events uploaded")
        manager.set("last_day_event_checked", (WEEK_AHEAD).strftime("%Y-%m-%d"))
        print("Metadata manager updated")
    
    # ----------------------- MAKE PREDICTIONS / METEO / FESTIUS -----------------
    
    if last_predicted_date.date() < WEEK_AHEAD.date():
    
        start_str = last_predicted_date.strftime("%Y-%m-%d")
        end_str = WEEK_AHEAD.strftime("%Y-%m-%d")
        df_weather = meteo.weather_forecast_1_week(start=start_str, end=end_str)
        print(df_weather)
        if df_weather.empty:
            print("Error! Unable to retrieve weather data.")
            
        df_weather.columns = [col.split(" ")[0] for col in df_weather.columns]
    
        all_display_data_frames: list[dict] = []
        
        last_date = last_predicted_date
        while last_date.date() < WEEK_AHEAD.date():
            
            next_date = last_date + pd.Timedelta(days=1)
            is_holiday = int(next_date in df_festius["date"].values)
            
            current_month = str(next_date.month)
            current_day = weekdays[next_date.weekday()]
            
            daily_t_max = df_weather.loc[df_weather['day'] == next_date, 'temperature_2m_max'].values[0]
            daily_t_min = df_weather.loc[df_weather['day'] == next_date, 'temperature_2m_min'].values[0]
            daily_precip = df_weather.loc[df_weather['day'] == next_date, 'precipitation_sum'].values[0]

            daily_data: list[dict] = []
            
            for barri in barri_list:
                
                lag_7, lag_14, lag_21, lag_28 = get_lag_features(next_date, barri, engine)
                
                dt_7_w1 = (lag_7 - lag_14) / 7
                dt_7_w2 = (lag_14 - lag_21) / 7
                
                daily_data.append({
                    "day": next_date.strftime("%Y-%m-%d"),
                    "barri": barri,
                    "temperature_2m_max": daily_t_max,
                    "temperature_2m_min": daily_t_min,
                    "precipitation_sum": daily_precip,
                    "month_cat": current_month,
                    "day_cat": current_day,
                    "lag_7": lag_7,
                    "lag_14": lag_14,
                    "lag_21": lag_21,
                    "lag_28": lag_28,
                    "dt_7_w1": dt_7_w1,
                    "dt_7_w2": dt_7_w2,
                    "is_holiday": is_holiday,
                        
                })
                
            df_daily = pd.DataFrame(daily_data)
            
            if not df_events_processed.empty:
                encoded_events = event_encoder.predict(df_events_processed, encoder, max_len, latent_dim)   
            else:
                empty_cols = ["day", "barri"] + [f"enc{i+1}" for i in range(latent_dim)]
                encoded_events = pd.DataFrame(columns=empty_cols)
                
            df_pred = pd.merge(df_daily, encoded_events, on=['day', 'barri'], how='left')
            
            enc_cols = ["enc1", "enc2", "enc3", "enc4", "enc5"]
            for col in enc_cols:
                if col not in df_pred.columns:
                    df_pred[col] = 0.0
                    
            df_pred[enc_cols] = df_pred[enc_cols].fillna(0.0).infer_objects(copy=False)
            
            df_pred["barri"] = df_pred["barri"].astype(str).astype("category")
            df_pred["month_cat"] = df_pred["month_cat"].astype(str).astype("category")
            df_pred["day_cat"] = df_pred["day_cat"].astype(str).astype("category")
            
            print(df_pred)
            prediction = np.expm1(regressor.predict(df_pred[features]))
            
            df_daily["intensity"] = prediction
            all_display_data_frames.append(df_daily)
            last_date = next_date
            
        final_display_data = pd.concat(all_display_data_frames, ignore_index=True)    
        database_connection.upload_df_to_db(final_display_data, "display_data", engine)
        print("Display data table updated")
        manager.set("last_predicted_day", (WEEK_AHEAD).strftime("%Y-%m-%d"))
        print("Metadata manager updated")
    
    
if __name__ == "__main__":
    main()