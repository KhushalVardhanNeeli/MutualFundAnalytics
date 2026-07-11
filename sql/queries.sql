-- 1. Top 5 Funds by AUM
SELECT
    df.scheme_name,
    df.fund_house,
    fp.aum_crore,
    fp.return_3yr_pct,
    fp.sharpe_ratio
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
ORDER BY fp.aum_crore DESC
LIMIT 5;

-- 2. Average NAV by Month (2024)
SELECT
    d.year,
    d.month,
    ROUND(AVG(fn.nav), 4) AS avg_nav
FROM fact_nav fn
JOIN dim_date d ON fn.date_id = d.date_id
WHERE d.year = 2024
GROUP BY d.year, d.month
ORDER BY d.month;

-- 3. SIP Inflows YoY Growth
SELECT
    month,
    sip_inflow_crore,
    yoy_growth_pct,
    active_sip_accounts_crore
FROM fact_sip_inflows
ORDER BY month DESC;

-- 4. Transactions by State (Top 10)
SELECT
    state,
    COUNT(*) AS total_transactions,
    ROUND(AVG(amount_inr), 2) AS avg_amount,
    SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC
LIMIT 10;

-- 5. Funds with Expense Ratio < 1%
SELECT
    df.scheme_name,
    df.fund_house,
    fp.expense_ratio_pct,
    fp.return_5yr_pct
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
WHERE fp.expense_ratio_pct < 1.0
ORDER BY fp.expense_ratio_pct ASC;

-- 6. Fund Count by Category
SELECT
    category,
    sub_category,
    COUNT(*) AS fund_count,
    ROUND(AVG(CAST(amfi_code AS REAL)), 0) AS avg_code
FROM dim_fund
GROUP BY category, sub_category
ORDER BY category, sub_category;

-- 7. Average AUM by Fund House (Latest Quarter)
SELECT
    fa.fund_house,
    ROUND(AVG(fa.aum_crore), 0) AS avg_aum_crore,
    ROUND(AVG(fa.aum_lakh_crore), 2) AS avg_aum_lakh_crore,
    MAX(fa.num_schemes) AS total_schemes
FROM fact_aum fa
JOIN dim_date d ON fa.date_id = d.date_id
WHERE d.full_date = (SELECT MAX(full_date) FROM dim_date)
GROUP BY fa.fund_house
ORDER BY avg_aum_crore DESC;

-- 8. Top 10 Funds by Sharpe Ratio
SELECT
    df.scheme_name,
    df.fund_house,
    df.sub_category,
    fp.sharpe_ratio,
    fp.sortino_ratio,
    fp.return_3yr_pct,
    fp.std_dev_ann_pct
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
WHERE fp.sharpe_ratio IS NOT NULL
ORDER BY fp.sharpe_ratio DESC
LIMIT 10;

-- 9. Highest Alpha Funds
SELECT
    df.scheme_name,
    df.fund_house,
    fp.alpha,
    fp.beta,
    fp.return_3yr_pct,
    fp.benchmark_3yr_pct
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
WHERE fp.alpha IS NOT NULL
ORDER BY fp.alpha DESC
LIMIT 10;

-- 10. Transaction Volume by Month
SELECT
    strftime('%Y-%m', transaction_date) AS month,
    transaction_type,
    COUNT(*) AS tx_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_amount_inr
FROM fact_transactions
GROUP BY month, transaction_type
ORDER BY month, transaction_type;

-- 11. Net Category Inflows (FY25)
SELECT
    category,
    ROUND(SUM(net_inflow_crore), 2) AS total_net_inflow_crore,
    COUNT(*) AS months_reported
FROM fact_category_inflows
WHERE month >= '2024-04-01' AND month <= '2025-03-31'
GROUP BY category
ORDER BY total_net_inflow_crore DESC;

-- 12. Investor Demographics Summary
SELECT
    age_group,
    gender,
    city_tier,
    COUNT(*) AS investor_count,
    ROUND(AVG(amount_inr), 2) AS avg_tx_amount,
    ROUND(AVG(annual_income_lakh), 2) AS avg_income_lakh
FROM fact_transactions
GROUP BY age_group, gender, city_tier
ORDER BY age_group, city_tier, gender;

-- 13. Folio Count Growth (YoY)
SELECT
    month,
    total_folios_crore,
    equity_folios_crore,
    debt_folios_crore
FROM fact_folio_count
ORDER BY month;

-- 14. Sector Concentration (Top 5 Sectors by Weight)
SELECT
    sector,
    ROUND(AVG(weight_pct), 2) AS avg_weight_pct,
    COUNT(DISTINCT amfi_code) AS fund_count
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY avg_weight_pct DESC
LIMIT 5;

-- 15. Max Drawdown vs Sharpe (Risk-Return)
SELECT
    df.scheme_name,
    df.risk_category,
    fp.max_drawdown_pct,
    fp.sharpe_ratio,
    fp.return_5yr_pct
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
WHERE fp.max_drawdown_pct IS NOT NULL
ORDER BY fp.max_drawdown_pct ASC
LIMIT 10;
