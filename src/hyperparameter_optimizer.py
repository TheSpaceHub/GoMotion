import pandas as pd
import numpy as np
import xgb_model as xgb_model
from peak_classifier import peak_loss, peak_loss_over_under
from sklearn.metrics import mean_absolute_error
import metadata_manager
import joblib
import sqlalchemy as sql
import keras


# min_loss stores the smallest loss seen in the grid search
min_loss = 1e9


def grid_search(
    manager: metadata_manager.MetadataManager,
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
                manager,
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

            # store accuracies in metadata
            manager.set("model_accuracy", 1 - loss)
            over, under = peak_loss_over_under(peak_loss_df)
            manager.set("model_error_over", over)
            manager.set("model_error_under", under)

            # store best hyperparameters
            manager.set("best_base", base)
            manager.set("best_learning_rate", learning_rate)
            manager.set("best_depth", depth)


def train_best(
    manager: metadata_manager.MetadataManager,
    features: list[str],
    train: pd.DataFrame,
    test: pd.DataFrame,
) -> xgb_model.Multiregressor:
    """Trains model with best chosen hyperparameters"""
    # unpack
    base = int(manager.get("best_base"))
    learning_rate = manager.get("best_learning_rate")
    depth = manager.get("best_depth")

    print(f"Training with base = {base}, l_rate = {learning_rate}, depth = {depth}")

    # calculate weights
    weights = calculate_sample_weights(train, base)

    X_train = train[features]
    y_train = np.log1p(train["intensity"])
    X_test = test[features]
    y_test = np.log1p(test["intensity"])

    model = xgb_model.Multiregressor()
    model.fit_multiregressor(
        3,
        X_train,
        y_train,
        X_test,
        y_test,
        weights,
        learning_rate,
        depth,
    )

    # save model
    joblib.dump(model, "models/regressor.joblib")
    return model


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


def load_events(df: pd.DataFrame, manager: metadata_manager.MetadataManager) -> pd.DataFrame:
    """Returns DataFrame with all events and holidays added"""
    encoder = keras.models.load_model("models/encoder.keras")
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


def create_features(
    data: pd.DataFrame,
    manager: metadata_manager.MetadataManager,
    drop_empty: bool = True,
) -> pd.DataFrame:
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
    df = load_events(df, manager)
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
