import time
from pathlib import Path

import pandas as pd
import requests

from locations import LOCATIONS


OUTPUT_DIR = Path("data/raw/osm")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "heatwave-datawarehouse-student-project/1.0"
}


records = []

for name, details in LOCATIONS.items():

    print(f"Fetching OpenStreetMap data for {name}...")

    params = {
        "q": f"{name}, India",
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 1
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        print(f"WARNING: No result found for {name}")
        continue

    result = results[0]
    address = result.get("address", {})

    records.append({
        "location": name,
        "osm_latitude": float(result["lat"]),
        "osm_longitude": float(result["lon"]),
        "display_name": result.get("display_name"),
        "city": address.get("city")
                or address.get("town")
                or address.get("municipality"),
        "state": address.get("state"),
        "country": address.get("country"),
        "country_code": address.get("country_code")
    })

    # Nominatim requires no more than 1 request per second.
    time.sleep(1)


df = pd.DataFrame(records)

output_file = OUTPUT_DIR / "locations_raw.csv"

df.to_csv(output_file, index=False)

print()
print("OpenStreetMap extraction complete.")
print(f"Records: {len(df)}")
print(f"Saved to: {output_file}")