import pandas as pd
import numpy as np
import xgb_model as xgb_model
from peak_classifier import peak_loss
from sklearn.metrics import mean_absolute_error
import metadata_manager
import joblib
from datetime import datetime
import keras


# min_loss stores the smallest loss seen in the grid search
min_loss = 1e9


def grid_search(
    hyperspace: list[
        list[any]
    ],  # hyperspace is a list which contains the values to test for each hyperparameter
    index: int,
    hyperparameters: list[any],
    features: list[str],
    train: pd.DataFrame,
    test: pd.DataFrame,
) -> None:
    """Performs a grid search. Custom function in order to implement custom hyperparameters"""
    if index != len(hyperspace):
        # we need to select more hyperparams
        for param in hyperspace[index]:
            grid_search(
                hyperspace,
                index + 1,
                hyperparameters + [param],
                features,
                train,
                test,
            )

    else:
        # we have selected all hyperparameters, time to test out a model

        # unpack
        base = hyperparameters[0]
        learning_rate = hyperparameters[1]
        depth = hyperparameters[2]

        print(f"Testing base = {base}, l_rate = {learning_rate}, depth = {depth}")

        # calculate weights
        train_weights = calculate_sample_weights(train, base)

        X_train = train[features]
        y_train = np.log1p(train["intensity"])
        X_test = test[features]
        y_test = np.log1p(test["intensity"])

        model = xgb_model.Multiregressor()
        model.fit_multiregressor(
            3, X_train, y_train, X_test, y_test, train_weights, learning_rate, depth
        )
        prediction = np.expm1(model.predict(X_test))
        y_test = np.expm1(y_test)
        print("MAE FOR:")
        print(hyperparameters)
        print(mean_absolute_error(prediction, y_test))

        # check if model is current best and save
        global min_loss
        peak_loss_df = pd.DataFrame(
            {
                "day": test["day"],
                "barri": test["barri"],
                "prediction": prediction,
                "true": y_test,
            }
        )
        loss = peak_loss(peak_loss_df)
        if loss < min_loss:
            min_loss = loss
            print("New minimum loss achieved:", min_loss)
            joblib.dump(model, "models/regressor.joblib")

            for i, x in enumerate(model.get_feature_importances()):
                print(features[i] + ":", x)


def calculate_sample_weights(df: pd.DataFrame, base: float) -> pd.Series:
    """Given intensities and a base, calculates weights proportional to base^(max(z_score, 0)) for the regressor, highlighting the importance of predicting correctly more intense peaks"""
    stats = df.groupby("barri")["intensity"].agg(["mean", "std"]).reset_index()
    stats.columns = ["barri", "barri_mean", "barri_std"]

    # merge stats back
    df = pd.merge(df, stats, on="barri", how="left")

    df["z_score"] = (df["intensity"] - df["barri_mean"]) / (df["barri_std"] + 1)
    df["sample_weight"] = np.where(
        df["z_score"] > 0,
        base ** (df["z_score"]),
        1.0,
    )

    return df["sample_weight"]


def load_events(df: pd.DataFrame) -> pd.DataFrame:
    """Returns DataFrame with all events and holidays added"""
    encoder = keras.models.load_model("models/encoder.keras")
    manager = metadata_manager.MetadataManager()
    encoder_max_len = int(manager.get("encoder_max_len"))

    # predict no events (need bias)
    zero_prediction = encoder.predict(
        x={
            "input_event": np.zeros((1, encoder_max_len), dtype="int32"),
            "input_impact": np.zeros((1, encoder_max_len, 1), dtype="int32"),
        },
    )

    # load existing events
    encoded_events = pd.read_csv("data/encoded_events.csv")
    encoded_events["day"] = pd.to_datetime(encoded_events["day"])
    encoded_events["barri"] = encoded_events["barri"].astype("category")
    df = df.merge(encoded_events, on=["day", "barri"], how="left")

    # set empty events for the rest
    df.loc[df["enc1"].isna(), "enc1"] = zero_prediction[0][0]
    df.loc[df["enc2"].isna(), "enc2"] = zero_prediction[0][1]
    df.loc[df["enc3"].isna(), "enc3"] = zero_prediction[0][2]
    df.loc[df["enc4"].isna(), "enc4"] = zero_prediction[0][3]
    df.loc[df["enc5"].isna(), "enc5"] = zero_prediction[0][4]

    # set holidays
    # load holiday csv
    holiday_df = pd.read_csv("data/all_holidays.csv")
    holiday_df["day"] = pd.to_datetime(holiday_df["day"])
    df["is_holiday"] = 0
    df.loc[df["day"].isin(list(holiday_df["day"])), "is_holiday"] = 1

    return df


def create_features(data: pd.DataFrame, drop_empty: bool = True) -> pd.DataFrame:
    """Returns a DataFrame with the additional features"""
    df = data.copy()

    # add day of the week
    day_int_to_name = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo",
    }

    df["month_cat"] = pd.Series([str(x.month) for x in df["day"]]).astype("category")
    # we use known monday as reference
    df["day_cat"] = pd.Series(
        [
            day_int_to_name[(x - pd.Timestamp(day=4, month=1, year=1982)).days % 7]
            for x in df["day"]
        ]
    ).astype("category")

    # add lags (intensities {1, 2, 3, 4} weeks ago)
    for lag in [7, 14, 21, 28]:
        df[f"lag_{lag}"] = df.groupby("barri")["intensity"].shift(lag)

    # add some derivatives
    df["dt_7_w1"] = (df["lag_7"] - df["lag_14"]) / 7
    df["dt_7_w2"] = (df["lag_14"] - df["lag_21"]) / 7

    # remove nans from rows without lags
    if drop_empty:
        df.dropna(inplace=True)

    # add holidays and encoded events
    df = load_events(df)
    df["barri"] = df["barri"].astype("category")

    return df


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


def main():
    # read data
    data = pd.read_csv("data/final_data.csv")
    data["day"] = pd.to_datetime(data["day"])

    # sort by barri and day (probably already done, just in case)
    data = data.sort_values(["barri", "day"])

    # remove bad data
    data = data.dropna()

    # process data
    data_processed = create_features(data)

    # choose where to split the dataset
    split_date = datetime(year=2025, month=1, day=1)

    # split data
    train = data_processed.loc[data_processed["day"] < split_date].copy()
    test = data_processed.loc[data_processed["day"] >= split_date].copy()

    # remove nans
    train = train.dropna()

    # define empty hyperspace; adding values next
    hyperspace = []

    # weights base
    hyperspace.append([5, 10, 20])
    # learning rate
    hyperspace.append([0.01, 0.0005])
    # tree depth
    hyperspace.append([5, 9, 10])

    grid_search(hyperspace, 0, [], features, train, test)


if __name__ == "__main__":
    main()
