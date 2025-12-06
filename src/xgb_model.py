import pandas as pd
import numpy as np
import xgboost as xgb


class Multiregressor:
    def __init__(self):
        self.regressors = []
        self.prediction_length = 0
        self.features = []

    def fit_multiregressor(
        self,
        n: int,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        train_weights,
        learning_rate: float,
        depth: int,
    ) -> None:
        """Creates n XGB regressors with the hyperparameters provided and fits them with the data provided"""
        self.features = X_train.columns

        for i in range(n):
            print(f"Fitting regressor {i + 1} of {n}")
            self.regressors.append(
                create_and_fit_regressor(
                    X_train,
                    y_train,
                    X_test,
                    y_test,
                    train_weights,
                    learning_rate,
                    depth,
                )
            )

    def predict(self, X: pd.DataFrame) -> np.array:
        """Returns the average of all predictions"""
        prediction = np.zeros(len(X))
        for model in self.regressors:
            prediction += model.predict(X) / len(self.regressors)
        return prediction

    def get_feature_importances(self) -> np.array:
        """Returns the average of all model importances"""
        feature_importances = np.zeros(len(self.features))
        for model in self.regressors:
            feature_importances += model.feature_importances_ / len(self.regressors)
        return feature_importances


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
        verbose=1,
        sample_weight=train_weights,
    )

    return model
