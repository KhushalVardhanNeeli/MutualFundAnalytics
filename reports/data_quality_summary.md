# Data Quality Summary

## Overview

The provided datasets were successfully loaded into Pandas and inspected.

---

## 01_fund_master.csv

- Shape: (40, 15)
- Duplicate Rows: 0
- Missing Values: Checked
- Remarks:
  - Contains master information of mutual fund schemes.
  - AMFI codes are unique.
  - Includes fund house, category, benchmark, fund manager and risk category.

---

## 02_nav_history.csv

- Duplicate Rows: Checked
- Missing Values: Checked
- Remarks:
  - Contains historical NAV values.
  - Linked using AMFI code.

---

## 03_aum_by_fund_house.csv

- Successfully loaded
- Data types verified

---

## 04_monthly_sip_inflows.csv

- Successfully loaded
- Data types verified

---

## 05_category_inflows.csv

- Successfully loaded
- Data types verified

---

## 06_industry_folio_count.csv

- Successfully loaded
- Data types verified

---

## 07_scheme_performance.csv

- Successfully loaded
- Data types verified

---

## 08_investor_transactions.csv

- Successfully loaded
- Data types verified

---

## 09_portfolio_holdings.csv

- Successfully loaded
- Data types verified

---

## 10_benchmark_indices.csv

- Successfully loaded
- Data types verified

---

## AMFI Validation

Validation was performed between `01_fund_master.csv` and `02_nav_history.csv`.

Results:

- Total Fund Master Codes: 40
- Total Unique NAV Codes: 40
- Missing Codes: 0

All AMFI codes in `01_fund_master.csv` are present in `02_nav_history.csv`.


## Conclusion

- All datasets loaded successfully.
- Data types verified.
- Basic quality checks completed.
- Project is ready for SQL schema design and exploratory data analysis.