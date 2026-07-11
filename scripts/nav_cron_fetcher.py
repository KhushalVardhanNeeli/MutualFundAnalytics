#!/usr/bin/env python3

import os
import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

SCHEMES = {
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_LargeCap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841",
}

API_BASE = "https://api.mfapi.in/mf"
OUTPUT_DIR = Path("data/raw/api")


def main():
    start_time = datetime.now(timezone.utc)
    print(f"[{start_time.isoformat()}] NAV Cron Fetcher started")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {}

    for scheme_name, amfi_code in SCHEMES.items():
        url = f"{API_BASE}/{amfi_code}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            json_filename = f"{scheme_name}_{timestamp}.json"
            json_filepath = OUTPUT_DIR / json_filename
            with open(json_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            nav_df = pd.DataFrame(data["data"])
            csv_filename = f"{scheme_name}.csv"
            csv_filepath = OUTPUT_DIR / csv_filename
            nav_df.to_csv(csv_filepath, index=False)

            nav_entries = len(nav_df)
            latest_nav = data.get("data", [{}])[0].get("nav", "N/A")
            results[scheme_name] = f"OK ({nav_entries} records, latest NAV: {latest_nav})"
            print(f"  [{datetime.now().isoformat()}] {scheme_name} ({amfi_code}): OK - {nav_entries} records saved")

        except requests.exceptions.RequestException as e:
            results[scheme_name] = f"FAILED: {e}"
            print(f"  [{datetime.now().isoformat()}] {scheme_name} ({amfi_code}): FAILED - {e}")

    end_time = datetime.now(timezone.utc)
    print(f"\n[{end_time.isoformat()}] NAV Cron Fetcher finished")
    print(f"Duration: {(end_time - start_time).total_seconds():.1f}s")
    print("\nSummary:")
    for name, status in results.items():
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()
