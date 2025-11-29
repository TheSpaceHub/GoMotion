import pandas as pd


def z_score(x: pd.Series, mean: float = None, std: float = None) -> pd.Series:
    """Returns a Pandas Series with the z-scores of the specified column. If a mean and standard deviation are provided (in case the data is part of a larger set), it uses those to calculate the z-scores"""
    if mean is None:
        mean = x.mean()
    if std is None:
        std = x.std()
    return (x - mean) / std


def classify_peaks(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """Returns the DataFrame with the peak_value column added, which may take values Large peak, Peak and No peak"""
    df = data.copy()
    threshold_peak = 1
    threshold_large_peak = 1.5

    def find_threshold(x: float) -> str:
        if x >= threshold_large_peak:
            return "Large peak"
        elif x >= threshold_peak:
            return "Peak"
        else:
            return "No peak"

    df["peak_value"] = [find_threshold(x) for x in z_score(df[column])]
    return df


def peak_loss(df: pd.DataFrame) -> int:
    """Returns a custom loss which takes into account the number of entries where the predicted peak does not match the real peak"""
    count = 0

    for barri in df["barri"].unique():
        df_barri = df[df["barri"] == barri]
        prediction_peak = list(classify_peaks(df_barri, "prediction")["peak_value"])
        true_peak = list(classify_peaks(df_barri, "true")["peak_value"])

        for i in range(len(df_barri)):
            if prediction_peak[i] != true_peak[i]:
                # if the peaks are not the same we add 1 to the count
                count += 1
    return count / len(df)
