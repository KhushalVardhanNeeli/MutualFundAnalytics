import sys
import pandas as pd
import sqlite3
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.config import (
    PROJECT_ROOT, DATA_PROCESSED, DB_PATH, SCHEMA_SQL, DB_TABLES,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("LOADING DATA INTO SQLITE")
logger.info("=" * 80)

engine = None
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(f"sqlite:///{DB_PATH}")
    logger.info("Using SQLAlchemy engine")
except ImportError:
    logger.warning("SQLAlchemy not available, falling back to sqlite3")

# --------------------------------------------------
# Execute schema.sql
# --------------------------------------------------
with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
    schema_sql = f.read()

conn = sqlite3.connect(str(DB_PATH))
conn.executescript(schema_sql)
conn.commit()
conn.close()
logger.info("✓ Schema created from %s", SCHEMA_SQL.name)

# --------------------------------------------------
# Load dim_fund
# --------------------------------------------------
fund_master = pd.read_csv(DATA_PROCESSED / "01_fund_master.csv")
dim_fund_cols = [
    "amfi_code", "scheme_name", "fund_house", "category", "sub_category",
    "plan", "launch_date", "benchmark", "expense_ratio_pct",
    "exit_load_pct", "min_sip_amount", "min_lumpsum_amount",
    "fund_manager", "risk_category", "sebi_category_code",
]
dim_fund = fund_master[dim_fund_cols].copy()

if engine:
    dim_fund.to_sql("dim_fund", engine, if_exists="replace", index=False)
else:
    conn = sqlite3.connect(str(DB_PATH))
    dim_fund.to_sql("dim_fund", conn, if_exists="replace", index=False)
    conn.close()

logger.info("✓ dim_fund loaded (%d rows)", len(dim_fund))

# --------------------------------------------------
# Create dim_date from all date-bearing tables
# --------------------------------------------------
nav = pd.read_csv(DATA_PROCESSED / "02_nav_history.csv")
nav["date"] = pd.to_datetime(nav["date"])

all_dates = pd.DataFrame({"full_date": sorted(nav["date"].unique())})

aum = pd.read_csv(DATA_PROCESSED / "03_aum_by_fund_house.csv")
aum_dates = pd.to_datetime(aum["date"].dropna().unique())
all_dates = pd.concat([all_dates, pd.DataFrame({"full_date": aum_dates})])

all_dates["full_date"] = pd.to_datetime(all_dates["full_date"])
all_dates = all_dates.drop_duplicates().sort_values("full_date").reset_index(drop=True)

all_dates["date_id"] = all_dates.index + 1
all_dates["year"] = all_dates["full_date"].dt.year
all_dates["month"] = all_dates["full_date"].dt.month
all_dates["quarter"] = all_dates["full_date"].dt.quarter
all_dates["is_month_end"] = (
    all_dates["full_date"] == all_dates["full_date"] + pd.offsets.MonthEnd(0)
).astype(int)
all_dates["is_year_end"] = (
    all_dates["full_date"] == all_dates["full_date"] + pd.offsets.YearEnd(0)
).astype(int)

dim_date = all_dates[["date_id", "full_date", "year", "month", "quarter",
                       "is_month_end", "is_year_end"]]

if engine:
    dim_date.to_sql("dim_date", engine, if_exists="replace", index=False)
else:
    conn = sqlite3.connect(str(DB_PATH))
    dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
    conn.close()

logger.info("✓ dim_date loaded (%d rows)", len(dim_date))

# --------------------------------------------------
# Load fact_nav with date_id FK
# --------------------------------------------------
date_map = dim_date.set_index("full_date")["date_id"].to_dict()
nav["date_id"] = nav["date"].map(date_map)
fact_nav = nav[["amfi_code", "date_id", "nav"]].copy()

if engine:
    fact_nav.to_sql("fact_nav", engine, if_exists="replace", index=False)
else:
    conn = sqlite3.connect(str(DB_PATH))
    fact_nav.to_sql("fact_nav", conn, if_exists="replace", index=False)
    conn.close()

logger.info("✓ fact_nav loaded (%d rows)", len(fact_nav))

# --------------------------------------------------
# Load fact_transactions — preserve investor_id as column, auto-increment PK
# --------------------------------------------------
tx = pd.read_csv(DATA_PROCESSED / "08_investor_transactions.csv")
tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])

tx_cols = [
    "investor_id", "transaction_date", "amfi_code", "transaction_type",
    "amount_inr", "state", "city", "city_tier", "age_group", "gender",
    "annual_income_lakh", "payment_mode", "kyc_status",
]

fact_tx = tx[tx_cols].copy()
fact_tx["transaction_id"] = range(1, len(fact_tx) + 1)

if engine:
    fact_tx.to_sql("fact_transactions", engine, if_exists="replace", index=False)
else:
    conn = sqlite3.connect(str(DB_PATH))
    fact_tx.to_sql("fact_transactions", conn, if_exists="replace", index=False)
    conn.close()

logger.info("✓ fact_transactions loaded (%d rows)", len(fact_tx))

# --------------------------------------------------
# Load fact_performance
# --------------------------------------------------
perf = pd.read_csv(DATA_PROCESSED / "07_scheme_performance.csv")

if engine:
    perf.to_sql("fact_performance", engine, if_exists="replace", index=False)
else:
    conn = sqlite3.connect(str(DB_PATH))
    perf.to_sql("fact_performance", conn, if_exists="replace", index=False)
    conn.close()

logger.info("✓ fact_performance loaded (%d rows)", len(perf))

# --------------------------------------------------
# Load fact_aum with date_id FK
# --------------------------------------------------
aum = pd.read_csv(DATA_PROCESSED / "03_aum_by_fund_house.csv")
aum["date"] = pd.to_datetime(aum["date"])

aum_date_map = dim_date.set_index("full_date")["date_id"].to_dict()
aum["date_id"] = aum["date"].map(aum_date_map)

fact_aum = aum[["date_id", "fund_house", "aum_lakh_crore", "aum_crore", "num_schemes"]].copy()
fact_aum = fact_aum.dropna(subset=["date_id"])

if engine:
    fact_aum.to_sql("fact_aum", engine, if_exists="replace", index=False)
else:
    conn = sqlite3.connect(str(DB_PATH))
    fact_aum.to_sql("fact_aum", conn, if_exists="replace", index=False)
    conn.close()

logger.info("✓ fact_aum loaded (%d rows)", len(fact_aum))

# --------------------------------------------------
# Load additional tables
# --------------------------------------------------
additional = {
    "fact_category_inflows": ("05_category_inflows.csv", ["month", "category", "net_inflow_crore"]),
    "fact_sip_inflows": ("04_monthly_sip_inflows.csv", None),
    "fact_folio_count": ("06_industry_folio_count.csv", None),
    "fact_portfolio_holdings": ("09_portfolio_holdings.csv", None),
    "fact_benchmark_indices": ("10_benchmark_indices.csv", None),
}

for table_name, (csv_file, cols) in additional.items():
    df = pd.read_csv(DATA_PROCESSED / csv_file)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    if "month" in df.columns:
        df["month"] = pd.to_datetime(df["month"])
    if "portfolio_date" in df.columns:
        df["portfolio_date"] = pd.to_datetime(df["portfolio_date"])

    if cols:
        df = df[cols].copy()

    if engine:
        df.to_sql(table_name, engine, if_exists="replace", index=False)
    else:
        conn = sqlite3.connect(str(DB_PATH))
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()

    logger.info("✓ %s loaded (%d rows)", table_name, len(df))

# --------------------------------------------------
# Verify Row Counts
# --------------------------------------------------
logger.info("")
logger.info("=" * 80)
logger.info("ROW COUNT VERIFICATION")
logger.info("=" * 80)

all_tables = DB_TABLES + [
    "fact_category_inflows", "fact_sip_inflows", "fact_folio_count",
    "fact_portfolio_holdings", "fact_benchmark_indices",
]

conn = sqlite3.connect(str(DB_PATH))
for table in all_tables:
    try:
        result = conn.execute(f"SELECT COUNT(*) FROM {table}")
        count = result.fetchone()[0]
        logger.info("  %-30s : %6d", table, count)
    except Exception as e:
        logger.warning("  %-30s : ERROR (%s)", table, e)
conn.close()

logger.info("")
logger.info("=" * 80)
logger.info("DATABASE LOAD COMPLETED")
logger.info("=" * 80)
