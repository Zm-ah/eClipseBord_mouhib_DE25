import pandas as pd
from backend.constants import DATA_PATH


def load_lunar_data() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_PATH}/lunar.csv")
    df = df.astype(object)
    return df.where(df.notna(), None)


def load_solar_data() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_PATH}/solar.csv")
    df = df.astype(object)
    return df.where(df.notna(), None)
