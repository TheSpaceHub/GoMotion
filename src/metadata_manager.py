import os
import pandas as pd


class MetadataManager:
    def __init__(self):
        """Loads metadata file or creates it if it doesnt exist"""
        if os.path.exists("data/metadata.csv"):
            self.df = pd.read_csv("data/metadata.csv")
        else:
            self.df = pd.DataFrame(
                {
                    # default values
                    "key": ["encoder_max_len", "last_day_event_checked", "model_accuracy", "model_error_over", "model_error_under", "last_predicted_day"],
                    "value": [0, "2022-12-31", 0, 0, 0, None],
                }
            )
            self.save()

    def get(self, key: str) -> str | None:
        """Returns the value associated to the key (or None)"""
        row = self.df[self.df["key"] == key]
        if len(row) == 0:
            return None
        else:
            return row.iloc[0]["value"]

    def set(self, key: str, value: str) -> None:
        """Sets the value of the key"""
        try:
            self.df.loc[self.df["key"] == key, "value"] = value
        except:
            raise Exception(f"Metadata error: could not assign {key} to {value}")

        self.save()

    def save(self) -> None:
        """Saves metadata file"""
        try:
            self.df.to_csv("data/metadata.csv", index=None)
        except:
            raise Exception(f"Metadata error: could not save file")
