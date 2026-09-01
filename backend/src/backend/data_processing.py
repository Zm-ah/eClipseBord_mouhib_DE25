import pandas as pd 
from backend.constants import DATA_PATH


def load_lunar_data() -> pd.DataFrame: 
    return pd.read_csv(f"{DATA_PATH}/lunar.csv") 

def load_solar_data() -> pd.DataFrame: 
    return pd.read_csv(f"{DATA_PATH}/solar.csv")

 