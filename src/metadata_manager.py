import os
import sqlalchemy as sql
import pandas as pd


class MetadataManager:
    engine: sql.Engine

    def __init__(self, engine: sql.Engine):
        """Stores engine and creates table if it doesn't exist

        Args:
            engine (sql.Engine): sqlalchemy engine.
        """
        inspector = sql.inspect(engine)
        self.engine = engine
        if not inspector.has_table("metadata"):
            with self.engine.connect() as conn:
                pd.DataFrame(
                    {
                        # default values
                        "key": [
                            "encoder_max_len",
                            "last_day_event_checked",
                            "model_accuracy",
                            "model_error_over",
                            "model_error_under",
                            "last_predicted_day",
                            "best_learning_rate",
                            "best_base",
                            "best_depth",
                        ],
                        "value": [
                            0,
                            "2022-12-31",
                            0,
                            0,
                            0,
                            None,
                            0,
                            0,
                            0,
                        ],
                    }
                ).to_sql(name="metadata", con=engine, if_exists="fail", index=False)

    def get(self, key: str) -> str | None:
        """Returns the value of the key if found.

        Args:
            key (str)

        Returns:
            str | None: Value.
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                sql.text("SELECT * FROM metadata WHERE key=:key"), {"key": key}
            ).all()
            if len(result) == 0:
                return None
            else:
                # result is a list of tuples (key, value)
                return result[0][1]

    def set(self, key: str, value: str):
        """Updates the value of a key.

        Args:
            key (str)
            value (str)

        Raises:
            Exception: If the key was not found
        """
        # Execute SQL
        with self.engine.connect() as conn:
            result = conn.execute(
                sql.text("UPDATE metadata SET value = :value WHERE key = :key"),
                {"key": key, "value": value},
            )
            conn.commit()

            # Check if any row was modified
            if result.rowcount == 0:
                raise Exception(f"The key {key} was not found in the metadata.")
