import pandas as pd
import shutil
import os
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROCESSED = PROJECT_ROOT / "data" / "processed"

logger.info("=" * 80)
logger.info("DATA CLEANING STARTED")
logger.info(f"Source      : {RAW}")
logger.info(f"Destination : {PROCESSED}")
logger.info("=" * 80)

PROCESSED.mkdir(parents=True, exist_ok=True)

logger.info("Cleaning 01_fund_master.csv ...")

fm = pd.read_csv(RAW / "01_fund_master.csv")

fm["launch_date"] = pd.to_datetime(fm["launch_date"], errors="coerce")
fm = fm.drop_duplicates(subset=["amfi_code"])
fm["plan"] = fm["plan"].astype(str).str.strip()

valid_risk = ["Low", "Moderate", "Moderately High", "High", "Very High"]
for risk_val in fm["risk_category"].unique():
    if risk_val not in valid_risk:
        logger.warning(f"  Unknown risk_category: {risk_val}")

fm["expense_ratio_pct"] = pd.to_numeric(fm["expense_ratio_pct"], errors="coerce")
fm["exit_load_pct"] = pd.to_numeric(fm["exit_load_pct"], errors="coerce")

fm.to_csv(PROCESSED / "01_fund_master.csv", index=False)
logger.info("  ✓ Fund master cleaned (%d rows)", len(fm))

logger.info("Cleaning 02_nav_history.csv ...")

nav = pd.read_csv(RAW / "02_nav_history.csv")
nav["date"] = pd.to_datetime(nav["date"])
nav = nav.sort_values(["amfi_code", "date"])
nav = nav.drop_duplicates()
nav["nav"] = nav.groupby("amfi_code")["nav"].ffill()
nav = nav[nav["nav"] > 0]

nav.to_csv(PROCESSED / "02_nav_history.csv", index=False)
logger.info("  ✓ NAV history cleaned (%d rows)", len(nav))

logger.info("Cleaning 03_aum_by_fund_house.csv ...")

aum = pd.read_csv(RAW / "03_aum_by_fund_house.csv")
aum["date"] = pd.to_datetime(aum["date"])
aum = aum.sort_values(["fund_house", "date"])
aum = aum.drop_duplicates()
aum["aum_lakh_crore"] = pd.to_numeric(aum["aum_lakh_crore"], errors="coerce")
aum["aum_crore"] = pd.to_numeric(aum["aum_crore"], errors="coerce")
aum["num_schemes"] = pd.to_numeric(aum["num_schemes"], errors="coerce")
aum = aum[aum["aum_crore"] > 0]

aum.to_csv(PROCESSED / "03_aum_by_fund_house.csv", index=False)
logger.info("  ✓ AUM cleaned (%d rows)", len(aum))

logger.info("Cleaning 04_monthly_sip_inflows.csv ...")

sip = pd.read_csv(RAW / "04_monthly_sip_inflows.csv")
sip["month"] = pd.to_datetime(sip["month"])
sip = sip.sort_values("month")
sip = sip.drop_duplicates(subset=["month"])
sip["sip_inflow_crore"] = pd.to_numeric(sip["sip_inflow_crore"], errors="coerce")
sip["active_sip_accounts_crore"] = pd.to_numeric(sip["active_sip_accounts_crore"], errors="coerce")
sip["new_sip_accounts_lakh"] = pd.to_numeric(sip["new_sip_accounts_lakh"], errors="coerce")
sip["sip_aum_lakh_crore"] = pd.to_numeric(sip["sip_aum_lakh_crore"], errors="coerce")
sip["yoy_growth_pct"] = pd.to_numeric(sip["yoy_growth_pct"], errors="coerce")

sip.to_csv(PROCESSED / "04_monthly_sip_inflows.csv", index=False)
logger.info("  ✓ SIP inflows cleaned (%d rows)", len(sip))

logger.info("Cleaning 05_category_inflows.csv ...")

cat = pd.read_csv(RAW / "05_category_inflows.csv")
cat["month"] = pd.to_datetime(cat["month"])
cat = cat.sort_values(["category", "month"])
cat = cat.drop_duplicates()
cat["net_inflow_crore"] = pd.to_numeric(cat["net_inflow_crore"], errors="coerce")
cat["category"] = cat["category"].astype(str).str.strip()

cat.to_csv(PROCESSED / "05_category_inflows.csv", index=False)
logger.info("  ✓ Category inflows cleaned (%d rows)", len(cat))

logger.info("Cleaning 06_industry_folio_count.csv ...")

folio = pd.read_csv(RAW / "06_industry_folio_count.csv")
folio["month"] = pd.to_datetime(folio["month"])
folio = folio.sort_values("month")
folio = folio.drop_duplicates(subset=["month"])
for col in ["total_folios_crore", "equity_folios_crore", "debt_folios_crore",
            "hybrid_folios_crore", "others_folios_crore"]:
    folio[col] = pd.to_numeric(folio[col], errors="coerce")

folio.to_csv(PROCESSED / "06_industry_folio_count.csv", index=False)
logger.info("  ✓ Folio count cleaned (%d rows)", len(folio))

logger.info("Cleaning 07_scheme_performance.csv ...")

perf = pd.read_csv(RAW / "07_scheme_performance.csv")
numeric_cols = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "expense_ratio_pct", "alpha", "beta", "sharpe_ratio",
    "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
    "aum_crore", "morningstar_rating", "benchmark_3yr_pct"
]
for col in numeric_cols:
    if col in perf.columns:
        perf[col] = pd.to_numeric(perf[col], errors="coerce")

perf = perf[(perf["expense_ratio_pct"] >= 0.1) & (perf["expense_ratio_pct"] <= 2.5)]

perf.to_csv(PROCESSED / "07_scheme_performance.csv", index=False)
logger.info("  ✓ Scheme performance cleaned (%d rows)", len(perf))

logger.info("Cleaning 08_investor_transactions.csv ...")

tx = pd.read_csv(RAW / "08_investor_transactions.csv")
tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])
tx["transaction_type"] = tx["transaction_type"].astype(str).str.upper().str.strip()
tx = tx[tx["amount_inr"] > 0]

tx["kyc_status"] = tx["kyc_status"].astype(str).str.upper().str.strip()
valid_kyc = ["VERIFIED", "PENDING", "REJECTED"]
tx = tx[tx["kyc_status"].isin(valid_kyc)]

tx["gender"] = tx["gender"].astype(str).str.strip().str.title()
tx["state"] = tx["state"].astype(str).str.strip()
tx["city_tier"] = tx["city_tier"].astype(str).str.strip().str.upper()
tx["payment_mode"] = tx["payment_mode"].astype(str).str.strip().str.title()
tx["age_group"] = tx["age_group"].astype(str).str.strip()

tx.to_csv(PROCESSED / "08_investor_transactions.csv", index=False)
logger.info("  ✓ Investor transactions cleaned (%d rows)", len(tx))

logger.info("Cleaning 09_portfolio_holdings.csv ...")

pf = pd.read_csv(RAW / "09_portfolio_holdings.csv")
pf["portfolio_date"] = pd.to_datetime(pf["portfolio_date"])
pf = pf.drop_duplicates()
pf["weight_pct"] = pd.to_numeric(pf["weight_pct"], errors="coerce")
pf["market_value_cr"] = pd.to_numeric(pf["market_value_cr"], errors="coerce")
pf["current_price_inr"] = pd.to_numeric(pf["current_price_inr"], errors="coerce")

weight_check = pf.groupby("amfi_code")["weight_pct"].sum()
for code, total in weight_check.items():
    if total < 90 or total > 110:
        logger.warning(f"  Weight sum for {code}: {total:.1f}% (expected ~100%)")

pf.to_csv(PROCESSED / "09_portfolio_holdings.csv", index=False)
logger.info("  ✓ Portfolio holdings cleaned (%d rows)", len(pf))

logger.info("Cleaning 10_benchmark_indices.csv ...")

bm = pd.read_csv(RAW / "10_benchmark_indices.csv")
bm["date"] = pd.to_datetime(bm["date"])
bm = bm.sort_values(["index_name", "date"])
bm = bm.drop_duplicates()
bm["close_value"] = pd.to_numeric(bm["close_value"], errors="coerce")
bm = bm[bm["close_value"] > 0]
bm["index_name"] = bm["index_name"].astype(str).str.strip().str.upper()

bm.to_csv(PROCESSED / "10_benchmark_indices.csv", index=False)
logger.info("  ✓ Benchmark indices cleaned (%d rows)", len(bm))

logger.info("")
logger.info("=" * 80)
logger.info("DATA CLEANING COMPLETED — All 10 datasets processed")
logger.info("=" * 80)

for f in sorted(PROCESSED.glob("*.csv")):
    df = pd.read_csv(f)
    logger.info("  %-45s  %5d rows  %2d cols", f.name, len(df), len(df.columns))
