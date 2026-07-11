-- =====================================================
-- BLUESTOCK MUTUAL FUND ANALYTICS — STAR SCHEMA
-- =====================================================

DROP TABLE IF EXISTS fact_benchmark_indices;
DROP TABLE IF EXISTS fact_portfolio_holdings;
DROP TABLE IF EXISTS fact_folio_count;
DROP TABLE IF EXISTS fact_sip_inflows;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

-- =====================================================
-- DIMENSION TABLES
-- =====================================================

CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    plan TEXT,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE INDEX idx_dim_fund_house ON dim_fund(fund_house);
CREATE INDEX idx_dim_fund_category ON dim_fund(category);
CREATE INDEX idx_dim_fund_subcategory ON dim_fund(sub_category);
CREATE INDEX idx_dim_fund_risk ON dim_fund(risk_category);

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    is_month_end INTEGER,
    is_year_end INTEGER
);

CREATE INDEX idx_dim_date_full ON dim_date(full_date);
CREATE INDEX idx_dim_date_year ON dim_date(year);

-- =====================================================
-- FACT TABLES
-- =====================================================

CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    nav REAL NOT NULL,
    FOREIGN KEY(amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY(date_id) REFERENCES dim_date(date_id)
);

CREATE INDEX idx_fact_nav_amfi ON fact_nav(amfi_code);
CREATE INDEX idx_fact_nav_date ON fact_nav(date_id);
CREATE UNIQUE INDEX idx_fact_nav_unique ON fact_nav(amfi_code, date_id);

CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code INTEGER,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY(amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX idx_fact_txn_amfi ON fact_transactions(amfi_code);
CREATE INDEX idx_fact_txn_date ON fact_transactions(transaction_date);
CREATE INDEX idx_fact_txn_type ON fact_transactions(transaction_type);
CREATE INDEX idx_fact_txn_state ON fact_transactions(state);
CREATE INDEX idx_fact_txn_age ON fact_transactions(age_group);

CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    FOREIGN KEY(amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX idx_fact_perf_sharpe ON fact_performance(sharpe_ratio);
CREATE INDEX idx_fact_perf_aum ON fact_performance(aum_crore);
CREATE INDEX idx_fact_perf_rating ON fact_performance(morningstar_rating);

CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id INTEGER,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    FOREIGN KEY(date_id) REFERENCES dim_date(date_id)
);

CREATE INDEX idx_fact_aum_date ON fact_aum(date_id);
CREATE INDEX idx_fact_aum_house ON fact_aum(fund_house);

-- =====================================================
-- ADDITIONAL TABLES FOR ANALYSIS
-- =====================================================

CREATE TABLE fact_category_inflows (
    inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE,
    category TEXT,
    net_inflow_crore REAL
);

CREATE INDEX idx_fact_catflow_month ON fact_category_inflows(month);
CREATE INDEX idx_fact_catflow_cat ON fact_category_inflows(category);

CREATE TABLE fact_sip_inflows (
    sip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

CREATE INDEX idx_fact_sip_month ON fact_sip_inflows(month);

CREATE TABLE fact_folio_count (
    folio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

CREATE INDEX idx_fact_folio_month ON fact_folio_count(month);

CREATE TABLE fact_portfolio_holdings (
    holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    stock_symbol TEXT,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date DATE,
    FOREIGN KEY(amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX idx_fact_holding_amfi ON fact_portfolio_holdings(amfi_code);
CREATE INDEX idx_fact_holding_sector ON fact_portfolio_holdings(sector);

CREATE TABLE fact_benchmark_indices (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    index_name TEXT,
    close_value REAL
);

CREATE INDEX idx_fact_bench_date ON fact_benchmark_indices(date);
CREATE INDEX idx_fact_bench_name ON fact_benchmark_indices(index_name);
