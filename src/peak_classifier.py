import pandas as pd


def z_score(x: pd.Series, mean: float = None, std: float = None) -> pd.Series:
    if mean is None:
        mean = x.mean()
    if std is None:
        std = x.std()
    return (x - mean) / std


def classify_peaks(data: pd.DataFrame, column: str) -> pd.DataFrame:
    df = data.copy()
    threshold_increased_mobility = 0.75
    threshold_peak = 1
    threshold_large_peak = 1.25

    def find_threshold(x: float) -> str:
        if x >= threshold_large_peak:
            return "Large peak"
        elif x >= threshold_peak:
            return "Peak"
        elif x >= threshold_increased_mobility:
            return "Increased mobility"
        else:
            return "No peak"

    df["peak_value"] = [find_threshold(x) for x in z_score(df[column])]
    return df
