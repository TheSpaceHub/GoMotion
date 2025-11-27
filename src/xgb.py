import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error


def calculate_sample_weights(df):
    stats = df.groupby("barri")["intensity"].agg(["mean", "std"]).reset_index()
    stats.columns = ["barri", "barri_mean", "barri_std"]

    # merge stats back
    df = pd.merge(df, stats, on="barri", how="left")

    df["z_score"] = (df["intensity"] - df["barri_mean"]) / (df["barri_std"] + 1)
    df["sample_weight"] = np.where(
        df["z_score"] > 0,
        10 ** (df["z_score"]),
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
# data_processed["category"] = data_processed["category"].astype("category")

# choose where to split the dataset
split_date = "2025-01-01"

train = data_processed.loc[data_processed["day"] < split_date].copy()
test = data_processed.loc[data_processed["day"] >= split_date].copy()

# remove nans again
train = train.dropna()
train_weights = calculate_sample_weights(train)

features = [
    "barri",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "is_holiday",
    "month_sin",
    "month_cos",
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


X_train = train[features]
y_train = np.log1p(train["intensity"])
X_test = test[features]
y_test = np.log1p(test["intensity"])

model = xgb.XGBRegressor(
    tree_method="hist",
    n_estimators=5000,
    learning_rate=0.005,
    early_stopping_rounds=150,
    max_depth=9,
    enable_categorical=True,
)

model.fit(
    X_train,
    y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=100,
    sample_weight=train_weights,
)

preds = model.predict(X_test)
print(f"MAE: {mean_absolute_error(np.exp(y_test), np.exp(preds))}")


pd.DataFrame(
    {
        "day": test["day"],
        "barri": test["barri"],
        "val": np.exp(model.predict(X_test)) - 1,
        "check": np.exp(y_test) - 1,
    }
).to_csv("data/checkthings.csv")
