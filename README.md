# Bluestock — Mutual Fund Analytics

A complete mutual fund analytics project built from the ground up. Covers everything from raw data ingestion through SQL analytics, EDA, performance metrics, advanced risk modelling, and interactive dashboards.

---

## What's Inside

```
bluestock_mf_capstone/
├── data/
│   ├── raw/              ← Original CSVs (10 datasets)
│   ├── raw/api/          ← Live NAV from MFAPI
│   ├── processed/        ← Cleaned, analysis-ready
│   └── db/               ← SQLite database
├── scripts/
│   ├── config.py         ← Shared config — paths, codes, constants
│   ├── etl_pipeline.py   ← One command to run it all
│   ├── data_ingestion.py ← Load & explore raw data
│   ├── validate_amfi.py  ← Cross-check fund master vs NAV
│   ├── explore_fund_master.py ← Quick fund master look
│   ├── live_nav_fetch.py ← Hit mfapi.in for current NAV
│   ├── nav_cron_fetcher.py    ← Scheduled NAV fetcher (JSON + CSV)
│   ├── data_cleaning.py  ← Clean all 10 datasets
│   ├── load_to_sqlite.py ← Star schema into SQLite
│   ├── compute_metrics.py     ← VaR, CVaR, HHI, rolling Sharpe
│   ├── recommender.py         ← Risk-based fund picker
│   ├── monte_carlo_nav.py     ← 10K-path NAV projection
│   ├── markowitz_efficient_frontier.py ← Efficient frontier
│   └── email_report_generator.py      ← Weekly HTML reports
├── sql/
│   ├── schema.sql        ← Full star schema (dim + fact)
│   └── queries.sql       ← 15 analytical queries
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── dashboard/
│   ├── bluestock_mf.pbix        ← Power BI (4 pages)
│   └── streamlit_app.py        ← Streamlit alternative
├── charts/                ← Exported PNG/HTML outputs
├── reports/
│   ├── data_quality_summary.md
│   ├── data_dictionary.md
│   ├── fund_scorecard.csv
│   ├── alpha_beta.csv
│   ├── var_cvar_report.csv
│   └── weekly_report_*.html
└── requirements.txt
```

---

## Database at a Glance

Two dimensions, nine facts. Everything ties back to `amfi_code` and `date_id`.

| Table | What It Holds |
|---|---|
| `dim_fund` | Scheme names, fund houses, categories, risk grades |
| `dim_date` | Calendar with year/month/quarter flags |
| `fact_nav` | Daily NAV for all 40 schemes |
| `fact_transactions` | 32K+ investor transactions |
| `fact_performance` | Returns, Sharpe, Alpha, Beta, AUM |
| `fact_aum` | Quarterly AUM by fund house |
| `fact_sip_inflows` | Monthly SIP aggregates |
| `fact_category_inflows` | Category-wise net flows |
| `fact_folio_count` | Industry folio stats |
| `fact_portfolio_holdings` | Stock-level holdings |
| `fact_benchmark_indices` | NIFTY50/NIFTY100 daily values |

---

## Getting Started

```bash
pip install -r requirements.txt        # Dependencies

python scripts/etl_pipeline.py         # Run everything
# or step by step:
python scripts/data_ingestion.py
python scripts/data_cleaning.py
python scripts/load_to_sqlite.py
python scripts/validate_amfi.py

python scripts/live_nav_fetch.py       # Live NAV from MFAPI
python scripts/compute_metrics.py      # VaR + HHI
python scripts/recommender.py Moderate # Fund picks by risk
python scripts/email_report_generator.py
streamlit run dashboard/streamlit_app.py
jupyter notebook notebooks/
```

---

## Deliverables

| What | Where | Weight |
|---|---|---|
| ETL Pipeline | `scripts/*.py` | 15% |
| SQLite DB + Queries | `data/db/`, `sql/` | 10% |
| EDA Notebook | `notebooks/03_eda_analysis.ipynb` | 15% |
| Performance Metrics | `notebooks/04_performance_analytics.ipynb` | 15% |
| Dashboard | `dashboard/` | 20% |
| Advanced Analytics | `notebooks/05_advanced_analytics.ipynb` | 10% |
| Report + Slides | `reports/` | 15% |

### Bonus
- B1: Cron NAV fetcher — `scripts/nav_cron_fetcher.py`
- B2: Streamlit app — `dashboard/streamlit_app.py`
- B3: Monte Carlo — `scripts/monte_carlo_nav.py`
- B4: Markowitz Frontier — `scripts/markowitz_efficient_frontier.py`
- B5: Email reports — `scripts/email_report_generator.py`

---

## Stack

Python 3 · Pandas · NumPy · SciPy · StatsModels · Matplotlib · Seaborn · Plotly · SQLite · SQLAlchemy · Jupyter · Power BI · Streamlit · mfapi.in

---

Mutual fund investments are subject to market risks. This is an educational project — not financial advice.
