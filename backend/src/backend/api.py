from fastapi import FastAPI
from backend.data_processing import load_lunar_data, load_solar_data

app = FastAPI(title="eClipseBord API")

lunar_df = load_lunar_data()
solar_df = load_solar_data()


@app.get("/")
def root():
    return {"message": "eClipseBord API is running"}


@app.get("/eclipses/{eclipse_type}")
def get_eclipses(eclipse_type: str):
    if eclipse_type == "lunar":
        return lunar_df.to_dict(orient="records")
    elif eclipse_type == "solar":
        return solar_df.to_dict(orient="records")
    return {"error": "eclipse_type must be 'lunar' or 'solar'"}


@app.get("/eclipses/{eclipse_type}/filter")
def filter_eclipses(eclipse_type: str, year: int | None = None, type_filter: str | None = None):
    df = lunar_df if eclipse_type == "lunar" else solar_df
    result = df.copy()
    if year:
        result = result[result["Calendar Date"].str.contains(str(year))]
    if type_filter:
        result = result[result["Eclipse Type"] == type_filter]
    return result.to_dict(orient="records")


@app.get("/eclipses/{eclipse_type}/map")
def get_map_data(eclipse_type: str):
    df = lunar_df if eclipse_type == "lunar" else solar_df
    columns = ["Calendar Date", "Eclipse Type", "Latitude", "Longitude"]
    return df[columns].to_dict(orient="records")


@app.get("/eclipses/{eclipse_type}/stats")
def get_stats(eclipse_type: str):
    df = lunar_df if eclipse_type == "lunar" else solar_df
    return df["Eclipse Type"].value_counts().to_dict()