import time
from pathlib import Path

import pandas as pd
import requests

from locations import LOCATIONS, START_DATE, END_DATE


OUTPUT_DIR = Path("data/raw/open_meteo")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_location(name, details):
    params = {
        "latitude": details["latitude"],
        "longitude": details["longitude"],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "wind_speed_10m_max",
        ]),
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": "Asia/Kolkata",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data["daily"])

    df["time"] = pd.to_datetime(df["time"])
    df = df.rename(columns={"time": "date"})

    df["location"] = name
    df["latitude"] = details["latitude"]
    df["longitude"] = details["longitude"]
    df["state"] = details["state"]
    df["region"] = details["region"]

    return df


all_data = []

for name, details in LOCATIONS.items():
    print(f"Fetching Open-Meteo data for {name}...")

    df = fetch_location(name, details)
    all_data.append(df)

    time.sleep(1)


final_df = pd.concat(all_data, ignore_index=True)

output_file = OUTPUT_DIR / "open_meteo_raw.csv"

final_df.to_csv(output_file, index=False)

print()
print("Open-Meteo extraction complete.")
print(f"Records: {len(final_df):,}")
print(f"Saved to: {output_file}")