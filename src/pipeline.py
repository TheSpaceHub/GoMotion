import os
#shut tensorflow up if it doesn't need to say anything
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import pandas as pd
import intensities
import event_encoder
import llm_scraper
import datetime
import data_filler
import hyperparameter_optimizer
import keras
from metadata_manager import MetadataManager


def check_and_load_data(save_file: bool = True) -> pd.DataFrame:
    """Checks that all data is present and stores merged data"""
    # geodata
    if not os.path.exists("data/barris.csv"):
        raise Exception("Geographical barri data is missing")

    # data provided by challenge setters
    dates = (
        pd.date_range(start="2023-01-01", end="2025-08-01", freq="MS")
        .strftime("%Y-%m")
        .tolist()
    )

    # if file already exists no need to do this again
    if not os.path.exists("data/merged_data.csv"):
        all_dataframes: list[pd.DataFrame] = []
        for date in dates:
            if not os.path.exists("data/output_limite_legal/" + date):
                raise Exception("Data for " + date + " is missing")
            else:
                # load month data
                month_data = pd.read_csv(
                    f"data/output_limite_legal/{date}/movilidad_barrios_{date}_origen.csv"
                )

                # keep only useful columns
                month_data = month_data[
                    ["day", "barrio_origen_name", "barrio_destino_name", "viajes"]
                ]

                print("Loaded month " + date)
                all_dataframes.append(month_data)

        merged_data = pd.concat(all_dataframes)
        if save_file:
            merged_data.to_csv("data/merged_data.csv", index=None)

    else:
        merged_data = pd.read_csv("data/merged_data.csv")
    print("Data loaded")
    return merged_data


def process_scraped_events(
    df_tuple: tuple[pd.DataFrame], barri_list: list[str]
) -> tuple[pd.DataFrame]:
    """Takes two DataFrames from the scraper and spreads out the barris for events"""
    (df_events, df_holidays) = df_tuple

    # events
    processed_events = pd.DataFrame(
        columns=["day", "barri", "category", "impact", "description"]
    )
    for _, row in df_events.iterrows():
        if row["barris"] == "all":
            for barri in barri_list:
                processed_events.loc[len(processed_events)] = {
                    "day": row["date"],
                    "barri": barri,
                    "category": row["category"],
                    "impact": row["impact"],
                    "description": row["description"],
                }
        else:
            for barri in row["barris"].split("|"):
                processed_events.loc[len(processed_events)] = {
                    "day": row["date"],
                    "barri": barri,
                    "category": row["category"],
                    "impact": row["impact"],
                    "description": row["description"],
                }
    processed_events = processed_events.sort_values(["day", "barri"])

    # holidays
    processed_holidays = pd.DataFrame()
    processed_holidays["day"] = df_holidays["date"]
    processed_holidays["description"] = df_holidays["description"]

    return (processed_events, processed_holidays)


def main():
    # run the whole pipeline
    # metadata manager
    manager = MetadataManager()

    # useful vars
    TODAY = datetime.datetime.today()
    

    # ----------------------------------------------
    # MATHEMATICAL FRAMEWROK
    # ----------------------------------------------
    if not os.path.exists("data/intensities.csv"):
        # we only load the merged data if we do not have the intensities, as once we have them there is no need to load this (big file)
        merged_data = check_and_load_data(False)
        # calculate the intensities for each day-barri pair according to the mathematical formulation of the task
        intensities_df = intensities.process_df(merged_data, download=True, verbose=1)
    else:
        intensities_df = pd.read_csv("data/intensities.csv")

    # keep this (its useful)
    barri_list = intensities_df["barri"].unique()

    # ----------------------------------------------
    # EVENT AND HOLIDAY DATA
    # ----------------------------------------------

    # deal with encoder
    encoder_created = False
    if not os.path.exists("data/encoded_events.csv"):
        if not os.path.exists("data/events.csv"):
            raise Exception("Event data is missing")
        if not os.path.exists("data/holidays.csv"):
            raise Exception("Event data is missing")

        # load precomputed events and holidays, rename them and keep track of it in metadata
        all_events = pd.read_csv("data/events.csv")
        all_events.to_csv("data/all_events.csv", index=None)
        all_holidays = pd.read_csv("data/holidays.csv")
        all_holidays.to_csv("data/all_holidays.csv", index=None)

        # run event_encoder.py
        # the file creates an encoder (which takes existing events and projects them to a 5-dimensional latent space conserving all information) and processes all events for given data
        event_encoder.main(manager)

        # keep track of this; if the encoder is rebuilt, the weights might have changed, so we need to retrain XGB model
        encoder_created = True

    # this part only matters if the pipeline is run multiple times: since the day might be different, we need to check new events
    if (
        datetime.datetime.strptime(
            manager.get("last_day_event_checked"), "%Y-%m-%d"
        ).date()
        < TODAY.date()
    ):
        # there might be new events
        (new_events, new_holidays) = process_scraped_events(
            llm_scraper.scrape_week_ahead(),
            barri_list,
        )

        # load old events and holidays, concatenate new ones and metadata
        all_events = pd.read_csv("data/all_events.csv")
        all_holidays = pd.read_csv("data/all_holidays.csv")

        # cut events and holidays that might already be loaded
        event_cutoff = max(all_events["day"])
        holiday_cutoff = max(all_holidays["day"])

        new_events = new_events[new_events["day"] > event_cutoff]
        new_holidays = new_holidays[new_holidays["day"] > holiday_cutoff]

        all_events = pd.concat([all_events, new_events])
        all_holidays = pd.concat([all_holidays, new_holidays])
        all_events.to_csv("data/all_events.csv", index=None)
        all_holidays.to_csv("data/all_holidays.csv", index=None)
        manager.set("last_day_event_checked", TODAY.strftime("%Y-%m-%d"))

        # need to encode new events
        encoder = keras.models.load_model("models/encoder.keras")
        encoder_max_len = int(manager.get("encoder_max_len"))

        # predict no events (need bias)
        if len(new_events) > 0:
            encoded_events = pd.read_csv("data/encoded_events.csv")
            new_encoded_events = event_encoder.predict(
                new_events, encoder, encoder_max_len, 5
            )
            encoded_events = pd.concat([encoded_events, new_encoded_events])
            encoded_events.to_csv("data/encoded_events.csv", index=None)

    # ----------------------------------------------
    # PREDICTION MODEL
    # ----------------------------------------------
    if encoder_created or not os.path.exists("models/regressor.joblib"):
        # we need to train a model. For that, we first prepare the data
        data = intensities_df
        data["day"] = pd.to_datetime(data["day"])

        # add meteo first
        data = data_filler.add_weather_features(
            data, datetime.datetime(year=2022, month=12, day=31), datetime.date.today()
        )

        # add rest of features
        data_processed = hyperparameter_optimizer.create_features(data)

        # store features for all
        df_to_save = hyperparameter_optimizer.create_features(data, False)
        df_to_save.drop(inplace=True, columns=["enc1", "enc2", "enc3", "enc4", "enc5"])
        df_to_save.to_csv(
            "data/data_processed.csv", index=None
        )

        # training portion
        # choose where to split the dataset
        split_date = datetime.datetime(year=2025, month=1, day=1)

        # split data
        train = data_processed.loc[data_processed["day"] < split_date].copy()
        test = data_processed.loc[data_processed["day"] >= split_date].copy()

        # remove nans
        train = train.dropna()

        # define empty hyperspace; adding values next
        hyperspace = []

        hyperspace.append([10])
        # learning rate
        hyperspace.append([0.0005])
        # tree depth
        hyperspace.append([9])
        hyperparameter_optimizer.grid_search(
            hyperspace, 0, [], hyperparameter_optimizer.features, train, test
        )
        
    os.system("streamlit run src/dashboard.py")


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    main()
