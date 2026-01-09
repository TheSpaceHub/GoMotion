import os
import dotenv
import sqlalchemy as sql
import pandas as pd

dotenv.load_dotenv()


def connect_to_db() -> sql.Engine:
    """Generates a connection to the Supabase pool. Returns engine object.

    Returns:
        sql.Engine: Engine object.
    """
    try:
        db_url = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        engine = sql.create_engine(db_url)
        print("Engine connection successful.")
        return engine
    except Exception as e:
        print("Could not connect to pool.")
        raise e


def upload_to_database():
    """Uploads and updates necessary data to database."""
    print("Uploading data to database...")
    engine = connect_to_db()

    # upload data_extended
    try:
        data_extended = pd.read_csv("data/data_extended.csv")
        data_extended.to_sql(
            name="display_data", con=engine, if_exists="append", index=False
        )
    except:
        print("data_extended.csv could not be loaded")
        exit()

    # upload geo data
    try:
        geo_data = pd.read_csv("data/barris.csv")
        geo_data.to_sql(
            name="geospatial_data", con=engine, if_exists="replace", index=False
        )
    except:
        print("barris.csv could not be loaded")
        exit()

    # upload model importances and features
    try:
        i_and_f = pd.read_csv("data/importances_and_features.csv")
        i_and_f.to_sql(
            name="importances_and_features",
            con=engine,
            if_exists="replace",
            index=False,
        )
    except:
        print("importances_and_features.csv could not be loaded")
        exit()

    # upload events
    try:
        events = pd.read_csv("data/all_events.csv")
        events.to_sql(name="events", con=engine, if_exists="append", index=False)
    except:
        print("all_events.csv could not be loaded")
        exit()
