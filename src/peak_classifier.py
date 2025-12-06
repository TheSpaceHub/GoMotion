import pandas as pd


def z_score(x: pd.Series, mean: float = None, std: float = None) -> pd.Series:
    """Returns a Pandas Series with the z-scores of the specified column. If a mean and standard deviation are provided (in case the data is part of a larger set), it uses those to calculate the z-scores"""
    if mean is None:
        mean = x.mean()
    if std is None:
        std = x.std()
    return (x - mean) / std


def classify_peaks(z_scores: pd.Series) -> list:
    """Returns the Series, whose values may take values Large peak, Peak and No peak"""
    threshold_peak = 1
    threshold_large_peak = 1.5

    def find_threshold(x: float) -> str:
        if x >= threshold_large_peak:
            return "Pico masivo"
        elif x >= threshold_peak:
            return "Pico"
        else:
            return "No pico"
    return [find_threshold(x) for x in z_scores]


def peak_loss(data: pd.DataFrame, day=None) -> int:
    """Returns a custom loss which takes into account the number of entries where the predicted peak does not match the real peak"""
    df = data.copy()
    
    df["pred_z"] = df.groupby("barri")["prediction"].transform(lambda x: (x - x.mean()) / x.std())
    df["true_z"] = df.groupby("barri")["true"].transform(lambda x: (x - x.mean()) / x.std())
    

    if day is not None:
        df = df[df["day"] == day]
        
    
    return (classify_peaks(df["pred_z"]) != classify_peaks(df["true_z"])).sum() / len(df)