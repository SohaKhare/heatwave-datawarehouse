import time
from pathlib import Path

import pandas as pd
import requests

from locations import LOCATIONS, START_DATE, END_DATE


OUTPUT_DIR = Path("data/raw/nasa_power")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

PARAMETERS = "T2M,RH2M,WS2M,ALLSKY_SFC_SW_DWN"


def fetch_location(name, details):
    params = {
        "parameters": PARAMETERS,
        "community": "RE",
        "longitude": details["longitude"],
        "latitude": details["latitude"],
        "start": START_DATE.replace("-", ""),
        "end": END_DATE.replace("-", ""),
        "format": "JSON",
        "time-standard": "UTC",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    records = data["properties"]["parameter"]

    df = pd.DataFrame(records)

    df = df.reset_index()
    df = df.rename(columns={"index": "date"})

    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")

    df["location"] = name
    df["latitude"] = details["latitude"]
    df["longitude"] = details["longitude"]
    df["state"] = details["state"]
    df["region"] = details["region"]

    return df


all_data = []

for name, details in LOCATIONS.items():
    print(f"Fetching NASA POWER data for {name}...")

    df = fetch_location(name, details)
    all_data.append(df)

    time.sleep(1)


final_df = pd.concat(all_data, ignore_index=True)

output_file = OUTPUT_DIR / "nasa_power_raw.csv"

final_df.to_csv(output_file, index=False)

print()
print("NASA POWER extraction complete.")
print(f"Records: {len(final_df):,}")
print(f"Saved to: {output_file}")