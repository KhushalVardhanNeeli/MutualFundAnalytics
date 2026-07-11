import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/db/bluestock_mf.db")


def _get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH.resolve()}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def compute_var_cvar(returns, confidence=0.95):
    if len(returns) == 0:
        return np.nan, np.nan
    var = np.percentile(returns, (1 - confidence) * 100)
    cvar = returns[returns <= var].mean()
    return var, cvar


def compute_rolling_sharpe(daily_returns, window=252, risk_free_rate=0.0):
    daily_rf = risk_free_rate / 252
    excess = daily_returns - daily_rf
    roll_mean = excess.rolling(window=window).mean()
    roll_std = excess.rolling(window=window).std()
    sharpe = (roll_mean / roll_std) * np.sqrt(252)
    return sharpe


def compute_hhi(market_shares):
    shares = np.asarray(market_shares)
    if len(shares) == 0:
        return np.nan
    return np.sum(shares ** 2)


def get_nav_dataframe(amfi_codes=None):
    conn = _get_connection()
    query = """
        SELECT
            fn.amfi_code,
            d.full_date AS date,
            fn.nav,
            df.scheme_name,
            df.category,
            df.sub_category
        FROM fact_nav fn
        JOIN dim_date d ON fn.date_id = d.date_id
        JOIN dim_fund df ON fn.amfi_code = df.amfi_code
    """
    if amfi_codes is not None:
        placeholders = ",".join("?" for _ in amfi_codes)
        query += f" WHERE fn.amfi_code IN ({placeholders})"

    params = amfi_codes if amfi_codes is not None else []
    df = pd.read_sql_query(query, conn, params=params)
    df["date"] = pd.to_datetime(df["date"])
    conn.close()
    return df


def get_performance_df(amfi_codes=None):
    conn = _get_connection()
    query = """
        SELECT
            fp.*,
            df.scheme_name,
            df.fund_house,
            df.category,
            df.sub_category
        FROM fact_performance fp
        JOIN dim_fund df ON fp.amfi_code = df.amfi_code
    """
    if amfi_codes is not None:
        placeholders = ",".join("?" for _ in amfi_codes)
        query += f" WHERE fp.amfi_code IN ({placeholders})"

    params = amfi_codes if amfi_codes is not None else []
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_fund_list():
    conn = _get_connection()
    query = """
        SELECT amfi_code, scheme_name, fund_house, category, sub_category
        FROM dim_fund
        ORDER BY fund_house, scheme_name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def compute_all_var_cvar():
    """Compute VaR and CVaR for all 40 schemes and save report."""
    nav_df = get_nav_dataframe()
    results = []
    for code in nav_df["amfi_code"].unique():
        fund_nav = nav_df[nav_df["amfi_code"] == code].sort_values("date")
        returns = fund_nav["nav"].pct_change().dropna()
        var95, cvar95 = compute_var_cvar(returns, 0.95)
        name = fund_nav["scheme_name"].iloc[0]
        results.append({
            "amfi_code": code,
            "scheme_name": name,
            "var_95_pct": round(var95 * 100, 4) if not np.isnan(var95) else None,
            "cvar_95_pct": round(cvar95 * 100, 4) if not np.isnan(cvar95) else None,
            "volatility_daily": round(returns.std(), 6) if not returns.empty else None,
            "n_observations": len(returns),
        })

    df = pd.DataFrame(results)
    df = df.sort_values("var_95_pct")
    return df


def compute_all_hhi():
    """Compute HHI concentration for all funds from portfolio holdings."""
    conn = _get_connection()
    query = "SELECT amfi_code, weight_pct FROM fact_portfolio_holdings"
    df = pd.read_sql_query(query, conn)
    conn.close()

    results = []
    for code in df["amfi_code"].unique():
        weights = df[df["amfi_code"] == code]["weight_pct"]
        hhi = compute_hhi(weights)
        n_stocks = len(weights)
        concentration = "Low" if hhi < 1000 else ("Moderate" if hhi < 1500 else "High")
        results.append({
            "amfi_code": code,
            "hhi": round(hhi, 2),
            "n_holdings": n_stocks,
            "concentration": concentration,
        })

    df = pd.DataFrame(results).sort_values("hhi", ascending=False)
    return df


def compute_rolling_sharpe_for_funds(amfi_codes, window=90, risk_free_rate=0.065):
    """Compute rolling 90-day Sharpe ratio for specified funds."""
    nav_df = get_nav_dataframe(amfi_codes)
    results = {}
    for code in amfi_codes:
        fund_nav = nav_df[nav_df["amfi_code"] == code].sort_values("date")
        returns = fund_nav["nav"].pct_change().dropna()
        if len(returns) > window:
            sharpe = compute_rolling_sharpe(returns, window=window, risk_free_rate=risk_free_rate)
            results[code] = sharpe
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("COMPUTING VaR / CVaR FOR ALL 40 SCHEMES")
    print("=" * 70)

    var_df = compute_all_var_cvar()
    print(f"\nTop 5 lowest VaR (least risky):")
    print(var_df.head(5).to_string(index=False))

    print(f"\nTop 5 highest VaR (most risky):")
    print(var_df.tail(5).to_string(index=False))

    var_df.to_csv("reports/var_cvar_report.csv", index=False)
    print("\n✓ VaR/CVaR report saved to reports/var_cvar_report.csv")

    print("\n" + "=" * 70)
    print("COMPUTING HHI CONCENTRATION")
    print("=" * 70)

    hhi_df = compute_all_hhi()
    print(f"\nTop 5 most concentrated funds:")
    print(hhi_df.head(5).to_string(index=False))

    print(f"\nTop 5 most diversified funds:")
    print(hhi_df.tail(5).to_string(index=False))

    print("\n✓ All metrics computed")
