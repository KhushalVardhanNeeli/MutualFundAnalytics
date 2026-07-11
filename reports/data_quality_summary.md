# Data Quality Summary

Quick rundown of each dataset — what's in it, what shape it's in, and anything worth noting before we start analysing.

---

## 01_fund_master.csv

40 schemes, 15 columns. Clean with no duplicates and no missing values.

The AMFI codes are all unique and span 10 fund houses (SBI, HDFC, ICICI Pru, Nippon, Kotak, Axis, Aditya Birla, UTI, Mirae, DSP). Categories split evenly-ish between Equity and Debt. Risk grades go from Low (liquid funds) to Very High (small caps). The expense ratios range from 0.55% (debt funds) to 1.64% (regular equity plans), with direct plans consistently cheaper — that all checks out.

---

## 02_nav_history.csv

46,000 rows, 3 columns. All 40 schemes present with daily NAV from Jan 2022 through Dec 2025.

Forward-filled for weekends and holidays so the time series is continuous. A handful of schemes have shorter histories (funds that launched in 2023 or later), but the forward-fill handles that gracefully. No negative or zero NAV values — that'd be a serious red flag and we don't have it.

---

## 03_aum_by_fund_house.csv

90 rows (quarterly, 10 fund houses), 5 columns.

Covers March 2022 through December 2025. SBI's dominance is real — they peak at ₹12.5 Lakh Crore, nearly double the nearest competitor. The `aum_lakh_crore` and `aum_crore` columns are just the same number expressed differently; we kept both for convenience.

---

## 04_monthly_sip_inflows.csv

48 months, 6 columns.

SIP inflows grew from ₹11,517 Cr (Jan 2022) to ₹31,002 Cr (Dec 2025). That's nearly 3x growth. The `yoy_growth_pct` column is empty for the first 12 months (obviously — no prior year to compare with for 2022), which is expected.

---

## 05_category_inflows.csv

144 rows (12 months × ~12 categories), 3 columns.

Some categories go negative in certain months — that's normal, it just means redemptions exceeded fresh inflows. Equity categories dominate the positive side, which matches what you'd expect from a bull market.

---

## 06_industry_folio_count.csv

21 rows (quarterly), 6 columns.

Total folios doubled from 13.26 Cr to 26.12 Cr over the 4-year period. Equity makes up about 72% of all folios. Nothing surprising here, data is clean.

---

## 07_scheme_performance.csv

40 schemes, 19 columns.

This is where the action is. Returns, Sharpe/Sortino ratios, alpha, beta, max drawdown, etc. A few debt funds have NaN for equity-specific metrics like beta or Morningstar rating — that's expected. Expense ratios all validated in the 0.1%–2.5% range. AUM here is scheme-level, not fund-house-level — important distinction.

---

## 08_investor_transactions.csv

32,778 transactions, 14 columns.

Transaction types are standardised (SIP/LUMPSUM/REDEMPTION), all amounts are positive, KYC status is clean (most are Verified, some Pending, very few Rejected). Covers most Indian states with realistic T30/B30 splits. Age distribution is sensible — peak in the 26-45 range, tapering off on the older end.

One thing: `investor_id` values aren't unique per row — the same investor can have multiple transactions. That's by design. The database handles this with an auto-increment `transaction_id` primary key.

---

## 09_portfolio_holdings.csv

322 holdings across equity funds, 8 columns.

Weights per fund add up to roughly 100% (within ±5% tolerance, allowing for cash holdings). Sectors represented: Banking, IT, Pharma, Auto, Oil & Gas, FMCG, Construction, Metals, Utilities, Power, Chemicals, Telecom. Top-heavy on Banking and IT, which reflects real-world large-cap funds.

---

## 10_benchmark_indices.csv

8,050 daily values, 3 columns.

NIFTY50 and NIFTY100 from Jan 2022 to Dec 2025. No gaps, all values positive. Same date range as NAV data so benchmarking is apples-to-apples.

---

## AMFI Code Validation

Quick and dirty check: all 40 `amfi_code` values from `fund_master` appear in `nav_history`. Zero mismatches. Every scheme has NAV data.

| Check | Result |
|---|---|
| Fund master codes | 40 |
| Unique NAV codes | 40 |
| Missing | 0 |
| Match rate | 100% |

---

## Bottom Line

Data is solid. No deal-breaking issues. Dates are parsed, duplicates removed, amounts validated, categories standardised. Ready for analysis, SQL loading, and dashboarding.
