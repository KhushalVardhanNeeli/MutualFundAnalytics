# Data Dictionary

Here's what each column in our datasets actually means, in plain terms.

---

## 01_fund_master.csv — Fund Reference Sheet

This is the master lookup — one row per scheme, 40 funds across 10 AMCs.

| Column | What It Means |
|---|---|
| `amfi_code` | The 6-digit code that AMFI uses to identify every scheme. Our primary key throughout the entire project. |
| `fund_house` | The AMC — SBI, HDFC, ICICI Pru, etc. |
| `scheme_name` | Full scheme name including plan and option. E.g. "SBI Bluechip Fund - Direct Plan - Growth". |
| `category` | Broad bucket: Equity or Debt. Simple. |
| `sub_category` | More specific — Large Cap, Mid Cap, Small Cap, Flexi Cap, ELSS, Value, Index/ETF, Gilt, Short Duration, Liquid. |
| `plan` | Regular (via distributor) or Direct (bought straight from AMC, lower expense ratio). |
| `launch_date` | When the scheme was born. |
| `benchmark` | The index the fund measures itself against — usually something from NIFTY or BSE. |
| `expense_ratio_pct` | TER — what the AMC charges you annually as a % of AUM. Direct plans are cheaper. |
| `exit_load_pct` | Penalty for redeeming too early (usually within 12 months). |
| `min_sip_amount` | Minimum you can put in via SIP each month. Typically ₹500. |
| `min_lumpsum_amount` | Minimum for a one-shot investment. ₹100 to ₹5,000 depending on the fund. |
| `fund_manager` | The person or team running the show. |
| `risk_category` | SEBI's risk bucket: Low, Moderate, Moderately High, High, Very High. |
| `sebi_category_code` | SEBI's internal classification. E.g. EC01 = Large Cap Equity. |

---

## 02_nav_history.csv — Daily NAV Snapshots

Bread and butter of performance analysis. One row per scheme per trading day.

| Column | What It Means |
|---|---|
| `date` | Trading date. We forward-filled weekends and holidays so you never see gaps. |
| `amfi_code` | Links back to fund_master. |
| `nav` | Price of one unit in rupees. Always positive. |

Roughly 46,000 rows covering 2022 through 2025. About 1,150 trading days per scheme.

---

## 03_aum_by_fund_house.csv — AMC-Level AUM

Quarterly snapshots of how much money each fund house manages.

| Column | What It Means |
|---|---|
| `date` | Quarter-end date. |
| `fund_house` | AMC name. |
| `aum_lakh_crore` | AUM in Lakh Crore. Handy for top-level numbers — SBI hit ₹12.5 L Cr. |
| `aum_crore` | Same number in plain Crore. More useful for charts and calculations. |
| `num_schemes` | How many schemes the AMC runs. |

---

## 04_monthly_sip_inflows.csv — Industry SIP Data

Monthly data from AMFI on systematic investment plan flows.

| Column | What It Means |
|---|---|
| `month` | Month (first of the month). |
| `sip_inflow_crore` | Total money coming in via SIPs that month. Grew from ~₹11.5K Cr to ₹31K Cr over the period. |
| `active_sip_accounts_crore` | Number of active SIP accounts in Crore. |
| `new_sip_accounts_lakh` | New accounts opened that month (Lakh). |
| `sip_aum_lakh_crore` | Cumulative AUM sitting in SIP accounts (Lakh Crore). |
| `yoy_growth_pct` | Year-over-year growth in inflows. |

---

## 05_category_inflows.csv — Where The Money Flows

Net inflows by fund category, month by month.

| Column | What It Means |
|---|---|
| `month` | Month of the flow data. |
| `category` | Large Cap, Mid Cap, Small Cap, ELSS, etc. |
| `net_inflow_crore` | Inflows minus outflows. Negative means more money left than came in. |

---

## 06_industry_folio_count.csv — Investor Accounts

Quarterly folio (investor account) counts across the industry.

| Column | What It Means |
|---|---|
| `month` | Reporting month. |
| `total_folios_crore` | All folios combined. Went from 13.26 Cr to 26.12 Cr — doubled in 4 years. |
| `equity_folios_crore` | Equity-oriented folios (the bulk of it, ~72%). |
| `debt_folios_crore` | Debt fund folios. |
| `hybrid_folios_crore` | Hybrid fund folios. |
| `others_folios_crore` | Everything else (solution-oriented, ETFs, etc.). |

---

## 07_scheme_performance.csv — How Each Fund Did

All the risk and return numbers for every scheme. This is our analytics sweet spot.

| Column | What It Means |
|---|---|
| `amfi_code` | Links to fund_master. |
| `return_1yr_pct` | Absolute return over the last year. |
| `return_3yr_pct` | CAGR over 3 years — annualised. |
| `return_5yr_pct` | CAGR over 5 years — annualised. |
| `benchmark_3yr_pct` | What the benchmark returned over 3 years, for comparison. |
| `alpha` | Jensen's Alpha — how much extra return the fund delivered vs what beta alone would predict. Higher is better. |
| `beta` | Sensitivity to benchmark. 1.0 means it moves with the market, >1 means amplified moves. |
| `sharpe_ratio` | Risk-adjusted return. (Return − RiskFree) / Std Dev. Our primary ranking metric. |
| `sortino_ratio` | Like Sharpe but only penalises downside volatility. Better for funds with asymmetric risk. |
| `std_dev_ann_pct` | Annualised volatility of daily returns. |
| `max_drawdown_pct` | Worst peak-to-trough drop. How much you'd have lost if you bought at the worst time. |
| `aum_crore` | Scheme-level AUM in Crore. Different from the fund-house-level AUM in dataset 03. |
| `expense_ratio_pct` | TER for the scheme. Same as fund_master but verified during cleaning. |
| `morningstar_rating` | 1 to 5 stars. 5 = top dog. |

---

## 08_investor_transactions.csv — Who's Buying What

Individual investor-level transaction data. Simulated but based on realistic patterns.

| Column | What It Means |
|---|---|
| `investor_id` | Unique ID per investor. INV prefix. |
| `transaction_date` | When the transaction happened. |
| `amfi_code` | Which fund they bought/sold. |
| `transaction_type` | SIP, LUMPSUM, or REDEMPTION. |
| `amount_inr` | Money involved, in rupees. |
| `state` | State of residence. |
| `city` | City. |
| `city_tier` | T30 (top 30 cities) or B30 (beyond). SEBI's classification. |
| `age_group` | 18-25, 26-35, 36-45, 46-55, or 56+. |
| `gender` | Male or Female. |
| `annual_income_lakh` | Annual income in Lakh rupees. |
| `payment_mode` | How they paid — UPI, Cheque, Netbanking, etc. |
| `kyc_status` | Verified, Pending, or Rejected. |

---

## 09_portfolio_holdings.csv — What's Inside Each Fund

The stocks each equity fund actually holds, with weights.

| Column | What It Means |
|---|---|
| `amfi_code` | Links to fund_master. |
| `stock_symbol` | Ticker. RELIANCE, HDFCBANK, etc. |
| `stock_name` | Full company name. |
| `sector` | Banking, IT, Pharma, Utilities, etc. |
| `weight_pct` | How much of the fund's money is in this stock. |
| `market_value_cr` | Market value of the holding in Crore. |
| `current_price_inr` | Stock price per share. |
| `portfolio_date` | Snapshot date — as of when this holding list was current. |

---

## 10_benchmark_indices.csv — Market Benchmarks

Daily closing values for NIFTY indices, for benchmarking fund performance.

| Column | What It Means |
|---|---|
| `date` | Trading date. |
| `index_name` | NIFTY50 or NIFTY100. |
| `close_value` | Where the index closed that day. |

---

## Database — How It All Connects

The SQLite database uses a star schema with two dimension tables and nine fact tables.

**Dimension Tables**
- `dim_fund` — Scheme master data (fund name, house, category, risk, manager). Keyed on `amfi_code`.
- `dim_date` — Calendar dimension with year, month, quarter, and month-end/year-end flags. Keyed on `date_id`.

**Fact Tables**
- `fact_nav` — Daily NAVs. Links to `dim_fund` and `dim_date`.
- `fact_transactions` — 32K+ investor transactions. Links to `dim_fund`.
- `fact_performance` — Risk/return metrics per scheme. Links to `dim_fund`.
- `fact_aum` — Fund-house-level AUM by quarter. Links to `dim_date`.
- `fact_sip_inflows` — Monthly SIP aggregates from AMFI.
- `fact_category_inflows` — Category-wise net flows.
- `fact_folio_count` — Industry folio statistics.
- `fact_portfolio_holdings` — Stock-level holdings per fund.
- `fact_benchmark_indices` — Daily index values.
