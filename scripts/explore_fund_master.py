import pandas as pd

# Load dataset
fund_master = pd.read_csv("data/raw/01_fund_master.csv")

print("=" * 70)
print("FUND MASTER EXPLORATION")
print("=" * 70)

print("\nDataset Shape:")
print(fund_master.shape)

print("\nColumns:")
print(fund_master.columns.tolist())

print("\nUnique Fund Houses:")
print(fund_master["fund_house"].unique())

print("\nUnique Categories:")
print(fund_master["category"].unique())

print("\nUnique Sub Categories:")
print(fund_master["sub_category"].unique())

print("\nUnique Risk Categories:")
print(fund_master["risk_category"].unique())

print("\nAMFI Code Sample:")
print(fund_master[["amfi_code", "scheme_name"]].head())

print("\nAMFI Code Information:")
print(f"- Total Schemes: {fund_master['amfi_code'].nunique()}")
print(f"- Minimum AMFI Code: {fund_master['amfi_code'].min()}")
print(f"- Maximum AMFI Code: {fund_master['amfi_code'].max()}")

