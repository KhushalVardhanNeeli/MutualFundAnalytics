import pandas as pd
from pathlib import Path

# Path to raw data
DATA_FOLDER = Path("data/raw")

# Get all CSV files
csv_files = sorted(DATA_FOLDER.glob("*.csv"))

print("=" * 80)
print("MUTUAL FUND ANALYTICS - DATA INGESTION")
print("=" * 80)

for file in csv_files:
    print("\n" + "=" * 80)
    print(f"FILE: {file.name}")
    print("=" * 80)

    try:
        df = pd.read_csv(file)

        print("\nShape:")
        print(df.shape)

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nDuplicate Rows:")
        print(df.duplicated().sum())

        print("\nFirst 5 Rows:")
        print(df.head())

    except Exception as e:
        print(f"Error reading {file.name}: {e}")

print("\n")
print("=" * 80)
print("ALL FILES LOADED SUCCESSFULLY")
print("=" * 80)