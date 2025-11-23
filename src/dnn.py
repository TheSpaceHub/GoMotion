import keras
import pandas as pd
from sklearn.model_selection import train_test_split


def define_model(input_num: int) -> keras.Model:
    inputs = keras.Input(shape=(input_num,))

    x = keras.layers.Dense(256)(inputs)
    x = keras.layers.Dropout(0.01)(x)
    x = keras.layers.Dense(256, activation="swish")(x)
    x = keras.layers.Dropout(0.01)(x)
    x = keras.layers.Dense(128, activation="swish")(x)
    x = keras.layers.Dense(128, activation="swish")(x)

    outputs = keras.layers.Dense(1)(x)

    opt = keras.optimizers.Adam(learning_rate=0.001)
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=opt, loss="mean_squared_error")

    return model


data = pd.read_csv("data/final_data.csv")
data.dropna(inplace=True)

data["year"] = data["year"] - 2022  # normalization
data["intensity"] = data["intensity"]
data = pd.get_dummies(data, columns=["barri"])
data = pd.get_dummies(data, columns=["day_of_the_week"])
data.drop(columns=["day"], inplace=True)

y = data.pop("intensity") / 10000  # normalize by 10000
X = data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)


model = define_model(len(X.columns))
pd.set_option("display.max_columns", None)

lr_scheduler = keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss", factor=0.5, patience=10, min_lr=1e-7
)

early_stopper = keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=25, restore_best_weights=True
)
model.fit(
    X_train,
    y_train,
    epochs=400,
    batch_size=64,
    validation_data=(X_test, y_test),
    callbacks=[lr_scheduler, early_stopper],
)
model.save("data/model.keras")
