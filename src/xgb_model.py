import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error


def create_and_fit_regressor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    train_weights,
    learning_rate: float,
    depth: int,
) -> xgb.XGBRegressor:
    """Creates an XGB regressor with the hyperparameters provided and fits it with the data provided. Returns the trained model"""
    model = xgb.XGBRegressor(
        tree_method="hist",
        n_estimators=20000,
        learning_rate=learning_rate,
        early_stopping_rounds=150,
        max_depth=depth,
        enable_categorical=True,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=100,
        sample_weight=train_weights,
    )

    return model
