# Mutual Fund Analytics Capstone

Complete end-to-end mutual fund analytics project covering data ingestion, SQL analytics, exploratory data analysis,
performance metrics, advanced analytics, and interactive dashboarding.

---

## Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/              ← Original downloaded CSV files (10 datasets)
│   ├── raw/api/          ← Live NAV data fetched from MFAPI
│   ├── processed/        ← Cleaned datasets ready for analysis
│   └── db/               ← bluestock_mf.db (SQLite database)
├── scripts/
│   ├── config.py         ← Shared configuration (paths, codes, constants)
│   ├── etl_pipeline.py   ← Master pipeline runner (all steps)
│   ├── data_ingestion.py ← Load and explore all 10 raw CSVs
│   ├── validate_amfi.py  ← Validate AMFI codes between datasets
│   ├── explore_fund_master.py ← Fund master exploration
│   ├── live_nav_fetch.py ← Fetch live NAV from mfapi.in
│   ├── nav_cron_fetcher.py    ← Cron-ready NAV fetcher (JSON + CSV)
│   ├── data_cleaning.py  ← Clean all 10 datasets
│   ├── load_to_sqlite.py ← Load cleaned data into SQLite star schema
│   ├── compute_metrics.py     ← VaR/CVaR, HHI, rolling Sharpe
│   ├── recommender.py         ← Fund recommender by risk appetite
│   ├── monte_carlo_nav.py     ← Monte Carlo NAV projection (5 years)
│   ├── markowitz_efficient_frontier.py ← Efficient Frontier optimisation
│   └── email_report_generator.py      ← Weekly HTML email reports
├── sql/
│   ├── schema.sql        ← Database star schema (dim + fact tables)
│   └── queries.sql       ← 15 analytical SQL queries
├── notebooks/
│   ├── 01_data_ingestion.ipynb         ← Load & explore all 10 raw CSVs
│   ├── 02_data_cleaning.ipynb          ← Clean & validate datasets
│   ├── 03_eda_analysis.ipynb           ← Exploratory Data Analysis (15+ charts)
│   ├── 04_performance_analytics.ipynb  ← CAGR, Sharpe, Alpha/Beta, Scorecard
│   └── 05_advanced_analytics.ipynb     ← VaR, Cohorts, Recommender, HHI
├── dashboard/
│   ├── bluestock_mf.pbix        ← Power BI 4-page dashboard
│   └── streamlit_app.py        ← Streamlit web app alternative
├── charts/                ← Exported PNG/HTML chart outputs
├── reports/
│   ├── data_quality_summary.md  ← Data quality findings
│   ├── data_dictionary.md       ← Full column-level documentation
│   ├── fund_scorecard.csv       ← Composite fund ranking (0-100)
│   ├── alpha_beta.csv           ← Alpha/Beta for all 40 funds
│   └── weekly_report_*.html     ← Generated weekly email reports
└── requirements.txt       ← Python dependencies
```

---

## Database Tables (bluestock_mf.db)

### Dimension Tables
| Table | Key | Description |
|---|---|---|
| dim_fund | amfi_code | Scheme master data (name, house, category, risk, manager) |
| dim_date | date_id | Calendar dimension with year/month/quarter flags |

### Fact Tables
| Table | Key | FKs | Description |
|---|---|---|---|
| fact_nav | nav_id (auto) | amfi_code, date_id | Daily NAV for all 40 schemes |
| fact_transactions | transaction_id (auto) | amfi_code | 32K+ investor transactions |
| fact_performance | amfi_code | amfi_code | Returns, Sharpe, Alpha, Beta, AUM |
| fact_aum | aum_id (auto) | date_id | Quarterly AUM by fund house |
| fact_sip_inflows | sip_id (auto) | — | Monthly SIP industry data |
| fact_category_inflows | inflow_id (auto) | — | Category-wise net inflows |
| fact_folio_count | folio_id (auto) | — | Industry folio statistics |
| fact_portfolio_holdings | holding_id (auto) | amfi_code | Fund portfolio stock holdings |
| fact_benchmark_indices | benchmark_id (auto) | — | NIFTY50 / NIFTY100 daily values |

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run ETL Pipeline
```bash
python scripts/data_ingestion.py          # Explore raw data
python scripts/data_cleaning.py           # Clean all 10 datasets
python scripts/load_to_sqlite.py          # Load into SQLite DB
python scripts/validate_amfi.py           # Validate AMFI codes
```

### 3. Live NAV Fetch
```bash
python scripts/live_nav_fetch.py
```

### 4. Run Notebooks
```bash
jupyter notebook notebooks/
```

### 5. Compute Performance Metrics
```bash
python scripts/compute_metrics.py         # VaR/CVaR + HHI
python scripts/monte_carlo_nav.py         # Monte Carlo projection
python scripts/markowitz_efficient_frontier.py  # Portfolio optimisation
```

### 6. Generate Weekly Report
```bash
# Set env vars for email: SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO
python scripts/email_report_generator.py
```

### 7. Streamlit Dashboard
```bash
streamlit run dashboard/streamlit_app.py
```

### 8. Cron Job (Bonus)
```bash
# Add to crontab:
# 0 20 * * 1-5 cd /path/to/project && python3 scripts/nav_cron_fetcher.py
```

---

## Key Deliverables

| ID | Deliverable | Format | Status |
|---|---|---|---|
| D1 | ETL Pipeline | scripts/*.py | Done |
| D2 | SQLite Database | bluestock_mf.db | Done |
| D3 | EDA Notebook | notebooks/03_eda_analysis.ipynb | Done |
| D4 | Performance Metrics | notebooks/04_performance_analytics.ipynb | Done |
| D5 | Interactive Dashboard | dashboard/ | Done |
| D6 | Advanced Analytics | notebooks/05_advanced_analytics.ipynb | Done |
| D7 | Final Report + Slides | reports/ | Done |
| B1 | Cron NAV Fetcher | scripts/nav_cron_fetcher.py | Done |
| B2 | Streamlit App | dashboard/streamlit_app.py | Done |
| B3 | Monte Carlo Simulation | scripts/monte_carlo_nav.py | Done |
| B4 | Markowitz Frontier | scripts/markowitz_efficient_frontier.py | Done |
| B5 | Email Report Generator | scripts/email_report_generator.py | Done |

---

## Technologies

- Python 3, Pandas, NumPy, SciPy, StatsModels
- Matplotlib, Seaborn, Plotly (visualisation)
- SQLite + SQLAlchemy (database)
- Jupyter Notebook (analysis)
- Power BI + Streamlit (dashboarding)
- MFAPI.in (live NAV integration)

---

## License

This project is for educational/capstone purposes. Mutual fund investments are subject to market risks.
