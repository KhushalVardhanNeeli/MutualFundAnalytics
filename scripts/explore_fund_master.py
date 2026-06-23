import pandas as pd

df = pd.read_csv("data/raw/01_fund_master.csv")

print("=" * 70)
print("FUND MASTER ANALYSIS")
print("=" * 70)

print("\nColumns")
print(df.columns.tolist())

print("\nDataset Shape")
print(df.shape)

print("\nFirst 5 Rows")
print(df.head())

print("\nData Types")
print(df.dtypes)

print("\nUnique Values")

for column in df.columns:
    if df[column].dtype == object:
        print(f"\n{column}")
        print(df[column].unique())