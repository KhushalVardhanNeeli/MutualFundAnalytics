# Data Dictionary — Bluestock Mutual Fund Analytics

---

## 01_fund_master.csv — Mutual Fund Scheme Master

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | amfi_code | INTEGER | Unique AMFI-assigned code identifying a mutual fund scheme |
| 2 | fund_house | TEXT | Name of the Asset Management Company (AMC), e.g. SBI Mutual Fund |
| 3 | scheme_name | TEXT | Full scheme name including plan and option, e.g. "SBI Bluechip Fund - Regular Plan - Growth" |
| 4 | category | TEXT | Broad classification: Equity or Debt |
| 5 | sub_category | TEXT | Specific category: Large Cap, Mid Cap, Small Cap, Flexi Cap, Index/ETF, ELSS, Value, Gilt, Short Duration, Liquid |
| 6 | plan | TEXT | Plan type: Regular or Direct |
| 7 | launch_date | DATE | Scheme inception date |
| 8 | benchmark | TEXT | Benchmark index for performance comparison, e.g. NIFTY 100 TRI |
| 9 | expense_ratio_pct | REAL | Total Expense Ratio as percentage of AUM charged annually |
| 10 | exit_load_pct | REAL | Exit load percentage charged on redemption within specified period |
| 11 | min_sip_amount | INTEGER | Minimum Systematic Investment Plan amount in INR |
| 12 | min_lumpsum_amount | INTEGER | Minimum lump-sum investment amount in INR |
| 13 | fund_manager | TEXT | Name of the primary fund manager managing the scheme |
| 14 | risk_category | TEXT | SEBI-mandated risk grade: Low, Moderate, Moderately High, High, Very High |
| 15 | sebi_category_code | TEXT | SEBI category classification code, e.g. EC01 (Large Cap Equity) |
| **Source:** | AMFI / fund house disclosures | | |

---

## 02_nav_history.csv — Historical NAV Data

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | date | DATE | Trading date (business day); weekends/holidays forward-filled |
| 2 | amfi_code | INTEGER | Foreign key to fund_master.amfi_code |
| 3 | nav | REAL | Net Asset Value per unit in INR. Validated > 0 |
| **Source:** | AMFI historical NAV data | | |
| **Note:** | Missing dates (weekends/holidays) are forward-filled within each amfi_code group | | |

---

## 03_aum_by_fund_house.csv — Assets Under Management

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | date | DATE | Quarter-end date (e.g. 2022-03-31) |
| 2 | fund_house | TEXT | Name of the Asset Management Company |
| 3 | aum_lakh_crore | REAL | Total AUM in Lakh Crore INR (1 Lakh Crore = ₹1,000,000,000,000) |
| 4 | aum_crore | REAL | Total AUM in Crore INR (1 Crore = ₹10,000,000) |
| 5 | num_schemes | INTEGER | Number of active schemes managed by the fund house |
| **Source:** | AMFI quarterly AUM disclosures | | |

---

## 04_monthly_sip_inflows.csv — SIP Inflows

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | month | DATE | Month identifier (first day of month) |
| 2 | sip_inflow_crore | REAL | Total SIP inflow amount for the month in Crore INR |
| 3 | active_sip_accounts_crore | REAL | Number of active SIP accounts in Crore |
| 4 | new_sip_accounts_lakh | REAL | New SIP accounts registered during the month in Lakh |
| 5 | sip_aum_lakh_crore | REAL | Cumulative AUM from SIP investments in Lakh Crore INR |
| 6 | yoy_growth_pct | REAL | Year-over-year growth percentage in SIP inflows |
| **Source:** | AMFI monthly SIP data | | |

---

## 05_category_inflows.csv — Category-wise Inflows

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | month | DATE | Month identifier |
| 2 | category | TEXT | Fund category: Large Cap, Mid Cap, Small Cap, ELSS, Index/ETF, Flexi Cap, Value, etc. |
| 3 | net_inflow_crore | REAL | Net inflow (gross inflow − gross outflow) for the category in Crore INR |
| **Source:** | AMFI monthly category flow data | | |

---

## 06_industry_folio_count.csv — Industry Folio Statistics

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | month | DATE | Month identifier |
| 2 | total_folios_crore | REAL | Total folio (investor account) count across all categories in Crore |
| 3 | equity_folios_crore | REAL | Equity-oriented folio count in Crore |
| 4 | debt_folios_crore | REAL | Debt-oriented folio count in Crore |
| 5 | hybrid_folios_crore | REAL | Hybrid fund folio count in Crore |
| 6 | others_folios_crore | REAL | Other category folio count in Crore |
| **Source:** | AMFI folio statistics | | |

---

## 07_scheme_performance.csv — Scheme Performance Metrics

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | amfi_code | INTEGER | Foreign key to fund_master.amfi_code |
| 2 | return_1yr_pct | REAL | Trailing 1-year absolute return as percentage |
| 3 | return_3yr_pct | REAL | Trailing 3-year CAGR return as percentage |
| 4 | return_5yr_pct | REAL | Trailing 5-year CAGR return as percentage |
| 5 | benchmark_3yr_pct | REAL | Benchmark 3-year CAGR return as percentage |
| 6 | alpha | REAL | Jensen's Alpha — excess return over benchmark (annualised) |
| 7 | beta | REAL | Beta — sensitivity to benchmark movements. >1 = more volatile |
| 8 | sharpe_ratio | REAL | Sharpe Ratio = (Rp − Rf) / σp. Risk-adjusted return metric |
| 9 | sortino_ratio | REAL | Sortino Ratio — Sharpe using only downside deviation |
| 10 | std_dev_ann_pct | REAL | Annualised standard deviation of returns as percentage |
| 11 | max_drawdown_pct | REAL | Maximum drawdown — worst peak-to-trough decline as percentage |
| 12 | aum_crore | REAL | Scheme-level AUM in Crore INR |
| 13 | expense_ratio_pct | REAL | Total Expense Ratio as percentage (validated 0.1%–2.5%) |
| 14 | morningstar_rating | INTEGER | Morningstar star rating (1–5); 5 = top rating |
| **Source:** | Computed from NAV data and benchmark indices | | |

---

## 08_investor_transactions.csv — Investor Transactions

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | investor_id | TEXT | Unique identifier for each investor (INV prefix) |
| 2 | transaction_date | DATE | Date of transaction |
| 3 | amfi_code | INTEGER | Fund scheme identifier |
| 4 | transaction_type | TEXT | Type: SIP, LUMPSUM, or REDEMPTION (standardised uppercase) |
| 5 | amount_inr | REAL | Transaction amount in INR. Validated > 0 |
| 6 | state | TEXT | Investor's state of residence |
| 7 | city | TEXT | Investor's city |
| 8 | city_tier | TEXT | SEBI city classification: T30 (top 30 cities) or B30 (beyond top 30) |
| 9 | age_group | TEXT | Age bracket: 18-25, 26-35, 36-45, 46-55, 56+ |
| 10 | gender | TEXT | Male / Female |
| 11 | annual_income_lakh | REAL | Annual income in Lakh INR |
| 12 | payment_mode | TEXT | Payment method: UPI, Cheque, Netbanking, etc. |
| 13 | kyc_status | TEXT | KYC compliance status: Verified, Pending, Rejected |
| **Source:** | Simulated investor transaction data | | |

---

## 09_portfolio_holdings.csv — Portfolio Holdings

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | amfi_code | INTEGER | Fund scheme identifier |
| 2 | stock_symbol | TEXT | Stock ticker symbol, e.g. RELIANCE |
| 3 | stock_name | TEXT | Full company name |
| 4 | sector | TEXT | Industry sector classification |
| 5 | weight_pct | REAL | Portfolio weight of the holding as percentage of total AUM |
| 6 | market_value_cr | REAL | Market value of the holding in Crore INR |
| 7 | current_price_inr | REAL | Stock price per share in INR |
| 8 | portfolio_date | DATE | As-of date of the portfolio snapshot |
| **Source:** | Fund house monthly portfolio disclosures | | |

---

## 10_benchmark_indices.csv — Benchmark Index Values

| # | Column | Type | Business Definition |
|---|---|---|---|
| 1 | date | DATE | Trading date |
| 2 | index_name | TEXT | Index identifier: NIFTY50 or NIFTY100 |
| 3 | close_value | REAL | Closing value of the index on that date. Validated > 0 |
| **Source:** | NSE historical index data | | |

---

## Database Schema (bluestock_mf.db)

### Dimension Tables
| Table | Primary Key | Description |
|---|---|---|
| dim_fund | amfi_code | Fund master reference data |
| dim_date | date_id | Date dimension with year/month/quarter flags |

### Fact Tables
| Table | Primary Key | Foreign Keys | Description |
|---|---|---|---|
| fact_nav | nav_id (auto) | amfi_code → dim_fund, date_id → dim_date | Daily NAV snapshots |
| fact_transactions | transaction_id (auto) | amfi_code → dim_fund | Investor transactions |
| fact_performance | amfi_code | amfi_code → dim_fund | Scheme performance metrics |
| fact_aum | aum_id (auto) | date_id → dim_date | Fund house AUM by quarter |
| fact_category_inflows | inflow_id (auto) | — | Monthly category net inflows |
| fact_sip_inflows | sip_id (auto) | — | Monthly SIP inflow aggregates |
| fact_folio_count | folio_id (auto) | — | Industry folio counts |
| fact_portfolio_holdings | holding_id (auto) | amfi_code → dim_fund | Fund portfolio holdings |
| fact_benchmark_indices | benchmark_id (auto) | — | Daily benchmark index values |
