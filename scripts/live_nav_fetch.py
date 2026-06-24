import os
import requests
import pandas as pd

# Create API folder if it doesn't exist
os.makedirs("data/raw/api", exist_ok=True)

# Dictionary of schemes and their AMFI codes
schemes = {
    "HDFC_Top100": "125497",
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_LargeCap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}

print("=" * 70)
print("FETCHING LIVE NAV DATA FROM MFAPI")
print("=" * 70)

for scheme_name, amfi_code in schemes.items():

    url = f"https://api.mfapi.in/mf/{amfi_code}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        json_data = response.json()

        # Convert NAV history to DataFrame
        nav_df = pd.DataFrame(json_data["data"])

        # Save CSV
        file_path = f"data/raw/api/{scheme_name}.csv"
        nav_df.to_csv(file_path, index=False)

        print(f"\n✅ {scheme_name}")
        print(f"AMFI Code : {amfi_code}")
        print(f"Records   : {len(nav_df)}")
        print(f"Saved To  : {file_path}")

    except Exception as e:
        print(f"\n❌ Failed to fetch {scheme_name}")
        print(e)

print("\n" + "=" * 70)
print("ALL REQUESTS COMPLETED")
print("=" * 70)