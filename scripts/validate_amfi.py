import pandas as pd

# Load datasets
fund_master = pd.read_csv("data/raw/01_fund_master.csv")
nav_history = pd.read_csv("data/raw/02_nav_history.csv")

# Find missing AMFI codes
missing_codes = fund_master[
    ~fund_master["amfi_code"].isin(nav_history["amfi_code"])
]

print("=" * 60)
print("AMFI CODE VALIDATION")
print("=" * 60)

print(f"\nTotal Fund Master Codes : {len(fund_master)}")
print(f"Total Unique NAV Codes  : {nav_history['amfi_code'].nunique()}")

print(f"\nMissing Codes : {len(missing_codes)}")

if len(missing_codes) == 0:
    print("\n✅ All AMFI codes are present in nav_history.")
else:
    print("\n❌ Missing AMFI Codes")
    print(missing_codes[["amfi_code", "scheme_name"]])