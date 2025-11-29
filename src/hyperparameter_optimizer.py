import pandas as pd
import numpy as np
import xgb_model as xgb_model
from peak_classifier import peak_loss
from sklearn.metrics import mean_absolute_error
import joblib
import math


# min_loss stores the smallest loss seen in the grid search
min_loss = 1e9


def grid_search(
    hyperspace: list[
        list[any]
    ],  # hyperspace is a list which contains the values to test for each hyperparameter
    index: int,
    hyperparameters: list[any],
    processed_data: pd.DataFrame,
    features: list[str],
) -> None:
    """Performs a grid search. Custom function in order to implement custom hyperparameters"""
    if index != len(hyperspace):
        # we need to select more hyperparams
        for param in hyperspace[index]:
            grid_search(
                hyperspace,
                index + 1,
                hyperparameters + [param],
                processed_data,
                features,
            )

    else:
        # we have selected all hyperparameters, time to test out a model

        # unpack
        base = hyperparameters[0]
        learning_rate = hyperparameters[1]
        depth = hyperparameters[2]

        print(f"Testing base = {base}, l_rate = {learning_rate}, depth = {depth}")

        # split data and calculate weights
        train = data_processed.loc[data_processed["day"] < split_date].copy()
        test = data_processed.loc[data_processed["day"] >= split_date].copy()

        # remove nans
        train = train.dropna()
        train_weights = calculate_sample_weights(train, base)

        X_train = train[features]
        y_train = np.log1p(train["intensity"])
        X_test = test[features]
        y_test = np.log1p(test["intensity"])

        model = xgb_model.create_and_fit_regressor(
            X_train, y_train, X_test, y_test, train_weights, learning_rate, depth
        )
        prediction = model.predict(X_test)
        print("MAE FOR:")
        print(hyperparameters)
        print(mean_absolute_error(np.exp(prediction) - 1, np.exp(y_test) - 1))

        # check if model is current best and save
        global min_loss
        loss = peak_loss(
            pd.DataFrame(
                {"barri": X_test["barri"], "prediction": prediction, "true": y_test}
            )
        )
        if loss < min_loss:
            min_loss = loss
            print("New minimum loss achieved:", min_loss)
            joblib.dump(model, "data/regressor.joblib")


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


def create_features(data: pd.DataFrame) -> pd.DataFrame:
    """Returns a DataFrame with the additional features"""
    df = data.copy()

    day_to_num = {
        "Lunes": 0,
        "Martes": 1,
        "Miércoles": 2,
        "Jueves": 3,
        "Viernes": 4,
        "Sábado": 5,
        "Domingo": 6,
    }

    # add day of the week
    df["day_of_the_week"] = [day_to_num[x] for x in df["day_of_the_week"]]

    # add day of the month
    df["day_num"] = [x.day for x in df["day"]]

    # add lags (intensities {1, 2, 3, 4} weeks ago)
    for lag in [7, 14, 21, 28]:
        df[f"lag_{lag}"] = df.groupby("barri")["intensity"].shift(lag)

    # absolute madness, but cool: simulate periodicity of months in a year and days in a month
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["day_sin"] = np.sin(2 * np.pi * df["day_of_the_week"] / 7)
    df["day_cos"] = np.cos(2 * np.pi * df["day_of_the_week"] / 7)

    # add some derivatives
    df["dt_7_w1"] = (df["lag_7"] - df["lag_14"]) / 7
    df["dt_7_w2"] = (df["lag_14"] - df["lag_21"]) / 7
    df["dt^2"] = df["dt_7_w1"] - df["dt_7_w2"]

    # get rid of old event columns
    df.drop(inplace=True, columns=["impact", "category"])
    df.drop_duplicates(inplace=True)

    # add encoded events
    encoded_events = pd.read_csv("data/encoded_events.csv")
    encoded_events["day"] = pd.to_datetime(encoded_events["day"])
    df = df.merge(encoded_events, on=["day", "barri"], how="left")

    # add exponential smoothing (useful predictor)
    alpha = 0.8
    df["exp"] = (
        alpha * df["lag_7"]
        + alpha * (1 - alpha) * df["lag_14"]
        + alpha * (1 - alpha) ** 2 * df["lag_21"]
        + (1 - alpha) ** 3 * df["lag_28"]
    )

    return df


# read data
data = pd.read_csv("data/final_data.csv")
data["day"] = pd.to_datetime(data["day"])

# sort by barri and day (probably already done, just in case)
data = data.sort_values(["barri", "day"])

# remove bad data
data = data.dropna()

# process data
data_processed = create_features(data)

# set types (need dtype to be category to avoid problems when feeding to model)
data_processed["barri"] = data_processed["barri"].astype("category")

# choose where to split the dataset
split_date = "2025-01-01"

features = [
    "barri",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "is_holiday",
    "month_sin",
    "month_cos",
    "day_num",
    "day_sin",
    "day_cos",
    "lag_7",
    "lag_14",
    "dt_7_w1",
    "dt_7_w2",
    "dt^2",
    "enc1",
    "enc2",
    "enc3",
    "enc4",
    "enc5",
    # "exp",
]

# define empty hyperspace; adding values next
hyperspace = []

# weights base
hyperspace.append([10])
# learning rate
hyperspace.append([0.01])
# tree depth
hyperspace.append([9])

grid_search(hyperspace, 0, [], data_processed, features)
