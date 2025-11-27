import pandas as pd
import numpy as np
import xgb_model as xgb_model
from peak_classifier import classify_peaks, z_score
from sklearn.metrics import mean_absolute_error
import joblib


def peak_loss(df: pd.DataFrame):
    count = 0
    under_count = 0

    for b in df["barri"].unique():
        df2 = df[df["barri"] == b]
        mean = df2["true"].mean()
        std = df2["true"].std()
        prediction_p = list(classify_peaks(df2, "prediction")["peak_value"])
        prediction_z = list(z_score(df2["prediction"], mean, std))
        true_p = list(classify_peaks(df2, "true")["peak_value"])
        true_z = list(z_score(df2["true"]))

        for i in range(len(df2)):
            if prediction_p[i] != true_p[i]:
                count += 1
                if true_z[i] > prediction_z[i]:
                    under_count += 1
    return count + under_count


min_loss = 1e9


def hyperwalk(
    hyperspace: list[list[any]],
    index: int,
    hyperparameters: list[any],
    processed_data: pd.DataFrame,
    features: list[str],
) -> None:

    if index != len(hyperspace):
        # we need to select more hyperparams
        for param in hyperspace[index]:
            hyperwalk(
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


def calculate_sample_weights(df, base):
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

    df["day_of_the_week"] = [day_to_num[x] for x in df["day_of_the_week"]]

    for lag in [7, 14, 21]:
        df[f"lag_{lag}"] = df.groupby("barri")["intensity"].shift(lag)

    # absolute madness, but cool
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["day_sin"] = np.sin(2 * np.pi * df["day_of_the_week"] / 7)
    df["day_cos"] = np.cos(2 * np.pi * df["day_of_the_week"] / 7)

    # add some derivatives
    df["dt_7_w1"] = (df["lag_7"] - df["lag_14"]) / 7
    df["dt_7_w2"] = (df["lag_14"] - df["lag_21"]) / 7
    df["dt^2"] = df["dt_7_w1"] - df["dt_7_w2"]

    df["day_num"] = [x.day for x in df["day"]]

    df.drop(inplace=True, columns=["impact", "category"])
    df.drop_duplicates(inplace=True)

    encoded_events = pd.read_csv("data/encoded_events.csv")
    encoded_events["day"] = pd.to_datetime(encoded_events["day"])
    df = df.merge(encoded_events, on=["day", "barri"], how="left")

    return df


data = pd.read_csv("data/final_data.csv")
data["day"] = pd.to_datetime(data["day"])

# sort by barri and day (probably already done, just in case)
data = data.sort_values(["barri", "day"])

# remove bad data
data = data.dropna()

# process data
data_processed = create_features(data)

# set types
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
]

hyperspace = []
# add search spaces to hyperspace

# weights base
hyperspace.append([2, 5, 10])
# learning rate
hyperspace.append([0.01, 0.001, 0.0005])
# tree depth
hyperspace.append([5, 6, 7, 8, 9])

hyperwalk(hyperspace, 0, [], data_processed, features)
