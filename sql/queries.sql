-- 1. Top 5 Funds by AUM

SELECT *
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV

SELECT AVG(nav) AS average_nav
FROM fact_nav;

-- 3. Average 1-Year Return

SELECT AVG(return_1yr_pct)
FROM fact_performance;

-- 4. Funds With Expense Ratio < 1%

SELECT
amfi_code,
expense_ratio_pct
FROM fact_performance
WHERE expense_ratio_pct < 1;

-- 5. Transaction Count By State

SELECT
state,
COUNT(*) AS total_transactions
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;

-- 6. Average Transaction Amount

SELECT
AVG(amount_inr)
FROM fact_transactions;

-- 7. Fund Count By Category

SELECT
category,
COUNT(*)
FROM dim_fund
GROUP BY category;

-- 8. Average AUM By Fund House

SELECT
fund_house,
AVG(aum_crore)
FROM fact_aum
GROUP BY fund_house;

-- 9. Highest Sharpe Ratio Funds

SELECT
amfi_code,
sharpe_ratio
FROM fact_performance
ORDER BY sharpe_ratio DESC
LIMIT 10;

-- 10. Highest Alpha Funds

SELECT
amfi_code,
alpha
FROM fact_performance
ORDER BY alpha DESC
LIMIT 10;