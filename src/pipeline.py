import os
import pandas as pd
import intensities
import event_encoder
import llm_scraper
import datetime
import data_filler
import hyperparameter_optimizer


def check_and_load_data(save_file: bool = True) -> pd.DataFrame:
    """Checks that all data is present and stores merged data"""
    # geodata
    if not os.path.exists("data/barris.csv"):
        raise Exception("Geographical barri data is missing")

    # event data
    if not os.path.exists("data/events_final.csv"):
        raise Exception("Past event data is missing")

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


def process_scraped_events(df: pd.DataFrame, barri_list: list[str]) -> pd.DataFrame:
    """Takes a DataFrame from the scraper and spreads out the barris"""
    processed_events = pd.DataFrame(
        columns=["day", "barri", "category", "impact", "description"]
    )
    for _, row in df.iterrows():
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
    return processed_events


def main():
    # run the whole pipeline

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

    # ----------------------------------------------
    # EVENT DATA
    # ----------------------------------------------
    encoder_created = False
    if not os.path.exists("data/encoded_events.csv"):
        # get all events using the scraper and run event_encoder.py
        # the second file creates an encoder (which takes existing events and projects them to a 5-dimensional latent space conserving all information) and processes all events for given data
        all_events = process_scraped_events(
            llm_scraper.scrape_week_ahead(
                datetime.datetime(year=2023, month=1, day=1), datetime.date.today()
            ),
            intensities_df["barri"].unique(),
        )
        # store them
        all_events.to_csv("data/all_events.csv", index=None)

        # create and train encoder, then encode
        event_encoder.main()

        # keep track of this; if the encoder is rebuilt, the weights might have changed, so we need to retrain XGB model
        encoder_created = True

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

        # weights base
        hyperspace.append([10])
        # learning rate
        hyperspace.append([0.01])
        # tree depth
        hyperspace.append([9])

        hyperparameter_optimizer.grid_search(
            hyperspace, 0, [], hyperparameter_optimizer.features, train, test
        )


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    main()
