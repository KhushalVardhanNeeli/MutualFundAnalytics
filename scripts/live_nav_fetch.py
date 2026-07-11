import os
import sys
import requests
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

API_BASE = "https://api.mfapi.in/mf"
OUTPUT_DIR = Path("data/raw/api")

schemes = {
    "HDFC_Top100": "125497",
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_LargeCap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841",
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("FETCHING LIVE NAV DATA FROM MFAPI")
print("=" * 70)

for scheme_name, amfi_code in schemes.items():
    url = f"{API_BASE}/{amfi_code}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        json_data = response.json()

        nav_df = pd.DataFrame(json_data["data"])

        csv_path = OUTPUT_DIR / f"{scheme_name}.csv"
        nav_df.to_csv(csv_path, index=False)

        print(f"\n{scheme_name}")
        print(f"AMFI Code : {amfi_code}")
        print(f"Records   : {len(nav_df)}")
        print(f"Saved To  : {csv_path}")

    except Exception as e:
        print(f"\nFailed to fetch {scheme_name}")
        print(e)

print("\n" + "=" * 70)
print("ALL REQUESTS COMPLETED")
print("=" * 70)
