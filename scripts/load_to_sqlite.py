import pandas as pd
from sqlalchemy import create_engine, text

print("=" * 80)
print("LOADING DATA INTO SQLITE")
print("=" * 80)

# --------------------------------------------------
# Create SQLite Database
# --------------------------------------------------

engine = create_engine(
    "sqlite:///bluestock_mf.db"
)

# --------------------------------------------------
# Execute schema.sql
# --------------------------------------------------

import sqlite3

# --------------------------------------------------
# Execute schema.sql
# --------------------------------------------------

with open("sql/schema.sql", "r", encoding="utf-8") as file:
    schema_sql = file.read()

conn = sqlite3.connect("bluestock_mf.db")

conn.executescript(schema_sql)

conn.commit()
conn.close()

print("✓ Schema created")

# --------------------------------------------------
# Load Dimension Tables
# --------------------------------------------------

fund_master = pd.read_csv(
    "data/processed/01_fund_master.csv"
)

dim_fund = fund_master[
    [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "plan",
        "fund_manager",
        "risk_category"
    ]
]

dim_fund.to_sql(
    "dim_fund",
    engine,
    if_exists="replace",
    index=False
)

print("✓ dim_fund loaded")

# --------------------------------------------------
# Create dim_date
# --------------------------------------------------

nav = pd.read_csv(
    "data/processed/02_nav_history.csv"
)

nav["date"] = pd.to_datetime(
    nav["date"]
)

unique_dates = pd.DataFrame({
    "full_date": sorted(
        nav["date"].unique()
    )
})

unique_dates["date_id"] = (
    unique_dates.index + 1
)

unique_dates = unique_dates[
    ["date_id", "full_date"]
]

unique_dates.to_sql(
    "dim_date",
    engine,
    if_exists="replace",
    index=False
)

print("✓ dim_date loaded")

# --------------------------------------------------
# Create fact_nav
# --------------------------------------------------

fact_nav = nav.merge(
    unique_dates,
    left_on="date",
    right_on="full_date"
)

fact_nav = fact_nav[
    [
        "amfi_code",
        "date_id",
        "nav"
    ]
]

fact_nav.to_sql(
    "fact_nav",
    engine,
    if_exists="replace",
    index=False
)

print("✓ fact_nav loaded")

# --------------------------------------------------
# Create fact_transactions
# --------------------------------------------------

transactions = pd.read_csv(
    "data/processed/08_investor_transactions.csv"
)

fact_transactions = transactions.rename(
    columns={
        "investor_id": "transaction_id"
    }
)

fact_transactions.to_sql(
    "fact_transactions",
    engine,
    if_exists="replace",
    index=False
)

print("✓ fact_transactions loaded")

# --------------------------------------------------
# Create fact_performance
# --------------------------------------------------

performance = pd.read_csv(
    "data/processed/07_scheme_performance.csv"
)

performance.to_sql(
    "fact_performance",
    engine,
    if_exists="replace",
    index=False
)

print("✓ fact_performance loaded")

# --------------------------------------------------
# Create fact_aum
# --------------------------------------------------

aum = pd.read_csv(
    "data/processed/03_aum_by_fund_house.csv"
)

aum.to_sql(
    "fact_aum",
    engine,
    if_exists="replace",
    index=False
)

print("✓ fact_aum loaded")

# --------------------------------------------------
# Verify Row Counts
# --------------------------------------------------

print("\n")
print("=" * 80)
print("ROW COUNT VERIFICATION")
print("=" * 80)

tables = [
    "dim_fund",
    "dim_date",
    "fact_nav",
    "fact_transactions",
    "fact_performance",
    "fact_aum"
]

with engine.connect() as conn:

    for table in tables:

        result = conn.execute(
            text(
                f"SELECT COUNT(*) FROM {table}"
            )
        )

        count = result.scalar()

        print(
            f"{table:<20} : {count}"
        )

print("\n")
print("=" * 80)
print("DATABASE LOAD COMPLETED")
print("=" * 80)