# Data Quality Summary

## Overview
All 10 datasets were loaded, inspected, and validated through the data ingestion and cleaning pipeline.

---

## 01_fund_master.csv
- **Shape:** (40, 15)
- **Duplicate Rows:** 0
- **Missing Values:** 0
- **Data Types:** amfi_code (int64), fund_house (object), scheme_name (object), category (object), sub_category (object), plan (object), launch_date (datetime64), benchmark (object), expense_ratio_pct (float64), exit_load_pct (float64), min_sip_amount (int64), min_lumpsum_amount (int64), fund_manager (object), risk_category (object), sebi_category_code (object)
- **Remarks:** Unique AMFI codes per scheme. 10 fund houses, 2 categories (Equity/Debt), 10 sub-categories. Risk categories: Low, Moderate, Moderately High, High, Very High.

---

## 02_nav_history.csv
- **Shape:** (46,000, 3)
- **Duplicate Rows:** Removed
- **Missing Values:** 0 after forward-fill
- **Data Types:** date (datetime64), amfi_code (int64), nav (float64)
- **Remarks:** Daily NAV values for 40 schemes. Forward-filled for non-trading days. All NAV values > 0. Date range: 2022-01-03 to 2025-12-31.

---

## 03_aum_by_fund_house.csv
- **Shape:** (90, 5)
- **Duplicate Rows:** 0
- **Missing Values:** 0
- **Data Types:** date (datetime64), fund_house (object), aum_lakh_crore (float64), aum_crore (float64), num_schemes (int64)
- **Remarks:** Quarterly AUM data for 10 fund houses from Q1 2022 to Q4 2025. SBI dominates with ₹12.5L Cr peak AUM.

---

## 04_monthly_sip_inflows.csv
- **Shape:** (48, 6)
- **Duplicate Rows:** 0
- **Missing Values:** yoy_growth_pct has some NaN (early months of 2022)
- **Data Types:** month (datetime64), sip_inflow_crore (float64), active_sip_accounts_crore (float64), new_sip_accounts_lakh (float64), sip_aum_lakh_crore (float64), yoy_growth_pct (float64)
- **Remarks:** Monthly SIP data Jan 2022 – Dec 2025. All-time high inflow ₹31,002 Cr in Dec 2025. Steady growth from ₹11,517 Cr in Jan 2022.

---

## 05_category_inflows.csv
- **Shape:** (144, 3)
- **Duplicate Rows:** 0
- **Missing Values:** 0
- **Data Types:** month (datetime64), category (object), net_inflow_crore (float64)
- **Remarks:** Monthly net inflows by fund category (Large Cap, Mid Cap, Small Cap, ELSS, Index/ETF, Flexi Cap, Value, etc.). Some months show net outflows.

---

## 06_industry_folio_count.csv
- **Shape:** (21, 6)
- **Duplicate Rows:** 0
- **Missing Values:** 0
- **Data Types:** month (datetime64), total_folios_crore (float64), equity_folios_crore (float64), debt_folios_crore (float64), hybrid_folios_crore (float64), others_folios_crore (float64)
- **Remarks:** Quarterly folio counts. Total folios grew from 13.26 Cr (Jan 2022) to 26.12 Cr (Dec 2025). Equity folios dominate (~72%).

---

## 07_scheme_performance.csv
- **Shape:** (40, 13)
- **Duplicate Rows:** 0
- **Missing Values:** Some non-equity funds have NaN for certain metrics
- **Data Types:** All numeric (float64) except amfi_code (int64)
- **Remarks:** Returns (1yr/3yr/5yr), Sharpe/Sortino ratios, alpha, beta, std dev, max drawdown, AUM, expense ratio (0.27%–2.15%), Morningstar rating (1–5). Expense ratios validated in [0.1%, 2.5%] range.

---

## 08_investor_transactions.csv
- **Shape:** (32,779, 14)
- **Duplicate Rows:** 0
- **Missing Values:** 0 after cleaning
- **Data Types:** investor_id (object), transaction_date (datetime64), amfi_code (int64), transaction_type (object), amount_inr (float64), state (object), city (object), city_tier (object), age_group (object), gender (object), annual_income_lakh (float64), payment_mode (object), kyc_status (object)
- **Remarks:** SIP/Lumpsum/Redemption transactions across 28 states. City tiers: T30/B30. Age groups: 18-25, 26-35, 36-45, 46-55, 56+. KYC status: Verified (majority), Pending, Rejected. All amounts > 0.

---

## 09_portfolio_holdings.csv
- **Shape:** (322, 8)
- **Duplicate Rows:** 0
- **Missing Values:** 0
- **Data Types:** amfi_code (int64), stock_symbol (object), stock_name (object), sector (object), weight_pct (float64), market_value_cr (float64), current_price_inr (float64), portfolio_date (datetime64)
- **Remarks:** Holdings for equity schemes as of 2025-12-31. Weights validated to sum to ~100% per fund. 12 sectors represented.

---

## 10_benchmark_indices.csv
- **Shape:** (8,050, 3)
- **Duplicate Rows:** 0
- **Missing Values:** 0 after cleaning
- **Data Types:** date (datetime64), index_name (object), close_value (float64)
- **Remarks:** Daily closing values for NIFTY50 and NIFTY100 (normalized). Date range matching NAV history. All close values > 0.

---

## AMFI Validation
Validation between `01_fund_master.csv` and `02_nav_history.csv`:

| Metric | Value |
|---|---|
| Fund Master Codes | 40 |
| Unique NAV Codes | 40 |
| Missing Codes | 0 |
| Match Rate | 100% |

All 40 AMFI codes in fund_master have corresponding records in nav_history.

---

## Conclusion
- All 10 datasets loaded, cleaned, and validated.
- No critical data quality issues found.
- Dates standardized to datetime64. Amounts validated > 0.
- Category/enum values standardized and validated.
- Data is ready for SQL schema loading and exploratory analysis.
