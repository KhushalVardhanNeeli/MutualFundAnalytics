import pandas as pd
import shutil
import os

print("=" * 80)
print("DATA CLEANING STARTED")
print("=" * 80)

# Create processed folder
os.makedirs("data/processed", exist_ok=True)

# ==================================================
# 1. CLEAN NAV HISTORY
# ==================================================

print("\nCleaning 02_nav_history.csv...")

nav = pd.read_csv("data/raw/02_nav_history.csv")

# Convert date column
nav["date"] = pd.to_datetime(nav["date"])

# Sort values
nav = nav.sort_values(["amfi_code", "date"])

# Remove duplicates
nav = nav.drop_duplicates()

# Forward fill NAV values within each scheme
nav["nav"] = nav.groupby("amfi_code")["nav"].ffill()

# Keep only valid NAV values
nav = nav[nav["nav"] > 0]

# Save
nav.to_csv(
    "data/processed/02_nav_history.csv",
    index=False
)

print("✓ NAV History cleaned")

# ==================================================
# 2. CLEAN INVESTOR TRANSACTIONS
# ==================================================

print("\nCleaning 08_investor_transactions.csv...")

tx = pd.read_csv(
    "data/raw/08_investor_transactions.csv"
)

# Convert date
tx["transaction_date"] = pd.to_datetime(
    tx["transaction_date"]
)

# Standardize transaction types
tx["transaction_type"] = (
    tx["transaction_type"]
    .astype(str)
    .str.upper()
    .str.strip()
)

# Amount must be positive
tx = tx[
    tx["amount_inr"] > 0
]

# Standardize KYC status
tx["kyc_status"] = (
    tx["kyc_status"]
    .astype(str)
    .str.upper()
    .str.strip()
)

valid_kyc = [
    "VERIFIED",
    "PENDING",
    "REJECTED"
]

tx = tx[
    tx["kyc_status"].isin(valid_kyc)
]

# Save
tx.to_csv(
    "data/processed/08_investor_transactions.csv",
    index=False
)

print("✓ Investor Transactions cleaned")

# ==================================================
# 3. CLEAN SCHEME PERFORMANCE
# ==================================================

print("\nCleaning 07_scheme_performance.csv...")

perf = pd.read_csv(
    "data/raw/07_scheme_performance.csv"
)

numeric_cols = [
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct",
    "expense_ratio_pct"
]

for col in numeric_cols:
    perf[col] = pd.to_numeric(
        perf[col],
        errors="coerce"
    )

# Expense ratio validation
perf = perf[
    (perf["expense_ratio_pct"] >= 0.1)
    &
    (perf["expense_ratio_pct"] <= 2.5)
]

# Save
perf.to_csv(
    "data/processed/07_scheme_performance.csv",
    index=False
)

print("✓ Scheme Performance cleaned")

# ==================================================
# 4. COPY REMAINING FILES
# ==================================================

print("\nCopying remaining files...")

remaining_files = [
    "01_fund_master.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

for file in remaining_files:
    shutil.copy(
        f"data/raw/{file}",
        f"data/processed/{file}"
    )

print("✓ Remaining files copied")

# ==================================================
# COMPLETE
# ==================================================

print("\n" + "=" * 80)
print("DATA CLEANING COMPLETED")
print("=" * 80)