#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sqlite3


DB_PATH = Path("bluestock_mf.db")
CHARTS_DIR = Path("charts")
OUTPUT = CHARTS_DIR / "efficient_frontier.png"

DIVERSE_FUNDS = {
    119551: "SBI Bluechip (Large Cap)",
    100033: "HDFC Mid-Cap (Mid Cap)",
    119598: "SBI Small Cap (Small Cap)",
    120843: "Kotak Flexicap (Flexi Cap)",
    119120: "SBI Magnum Gilt (Debt)",
}

N_PORTFOLIOS = 50_000
TRADING_DAYS = 252
RISK_FREE_RATE = 0.065


def load_nav_data(codes):
    conn = sqlite3.connect(str(DB_PATH))
    query = """
        SELECT fn.amfi_code, d.full_date AS date, fn.nav
        FROM fact_nav fn
        JOIN dim_date d ON fn.date_id = d.date_id
        WHERE fn.amfi_code IN ({})
        ORDER BY fn.amfi_code, d.full_date
    """.format(",".join("?" for _ in codes))

    df = pd.read_sql_query(query, conn, params=codes)
    df["date"] = pd.to_datetime(df["date"])
    conn.close()
    return df


def build_returns_matrix(nav_df, codes):
    pivot = nav_df.pivot(index="date", columns="amfi_code", values="nav")
    pivot = pivot[codes]
    returns = pivot.pct_change().dropna()
    return returns


def generate_random_portfolios(returns, n=N_PORTFOLIOS):
    mean_returns = returns.mean() * TRADING_DAYS
    cov_matrix = returns.cov() * TRADING_DAYS
    n_assets = len(mean_returns)

    np.random.seed(42)
    results = {
        "return": np.zeros(n),
        "volatility": np.zeros(n),
        "sharpe": np.zeros(n),
        "w1": np.zeros(n),
        "w2": np.zeros(n),
        "w3": np.zeros(n),
        "w4": np.zeros(n),
        "w5": np.zeros(n),
    }

    for i in range(n):
        weights = np.random.random(n_assets)
        weights /= weights.sum()

        port_return = np.dot(weights, mean_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = (port_return - RISK_FREE_RATE) / port_vol

        results["return"][i] = port_return
        results["volatility"][i] = port_vol
        results["sharpe"][i] = sharpe
        for j in range(n_assets):
            results[f"w{j+1}"][i] = weights[j]

    return pd.DataFrame(results), mean_returns, cov_matrix


def plot_frontier(portfolios, mean_returns, returns_matrix):
    fig, ax = plt.subplots(figsize=(14, 10))

    scatter = ax.scatter(
        portfolios["volatility"] * 100,
        portfolios["return"] * 100,
        c=portfolios["sharpe"],
        cmap="viridis",
        alpha=0.4,
        s=3,
        edgecolors="none",
    )
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Sharpe Ratio", fontsize=11)

    max_sharpe_idx = portfolios["sharpe"].idxmax()
    max_sharpe = portfolios.iloc[max_sharpe_idx]
    ax.scatter(
        max_sharpe["volatility"] * 100,
        max_sharpe["return"] * 100,
        color="red",
        marker="*",
        s=350,
        edgecolors="black",
        linewidths=1.5,
        zorder=10,
        label="Max Sharpe Ratio Portfolio",
    )

    min_vol_idx = portfolios["volatility"].idxmin()
    min_vol = portfolios.iloc[min_vol_idx]
    ax.scatter(
        min_vol["volatility"] * 100,
        min_vol["return"] * 100,
        color="blue",
        marker="*",
        s=350,
        edgecolors="black",
        linewidths=1.5,
        zorder=10,
        label="Min Volatility Portfolio",
    )

    codes = list(DIVERSE_FUNDS.keys())
    individual_vols = np.sqrt(np.diag(returns_matrix.cov() * TRADING_DAYS))
    for i, code in enumerate(codes):
        ax.scatter(
            individual_vols[i] * 100,
            mean_returns[code] * 100,
            color="orange",
            marker="D",
            s=100,
            edgecolors="black",
            linewidths=1,
            zorder=8,
        )
        ax.text(
            individual_vols[i] * 100 + 0.3,
            mean_returns[code] * 100,
            DIVERSE_FUNDS[code].split(" (")[0],
            fontsize=8,
            fontweight="bold",
        )

    ax.set_xlabel("Annualised Volatility (%)", fontsize=13)
    ax.set_ylabel("Annualised Return (%)", fontsize=13)
    ax.set_title("Markowitz Efficient Frontier - Mutual Fund Portfolios", fontsize=15, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved to {OUTPUT}")

    return max_sharpe, min_vol


def print_weights(portfolio, mean_returns, label):
    codes = list(DIVERSE_FUNDS.keys())
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    print(f"  Expected Return:     {portfolio['return']*100:.2f}%")
    print(f"  Expected Volatility: {portfolio['volatility']*100:.2f}%")
    print(f"  Sharpe Ratio:        {portfolio['sharpe']:.4f}")
    print(f"\n  Portfolio Weights:")
    for i, code in enumerate(codes):
        w = portfolio[f"w{i+1}"]
        print(f"    {DIVERSE_FUNDS[code]:<35s} {w*100:6.2f}%")


def main():
    codes = list(DIVERSE_FUNDS.keys())
    print("=" * 70)
    print("MARKOWITZ EFFICIENT FRONTIER")
    print("=" * 70)
    print(f"Selected funds:")
    for code, name in DIVERSE_FUNDS.items():
        print(f"  {code}: {name}")
    print(f"Portfolios to simulate: {N_PORTFOLIOS:,}")
    print(f"Risk-free rate: {RISK_FREE_RATE*100:.1f}%")
    print()

    print("Loading NAV data...")
    nav_df = load_nav_data(codes)
    print(f"  Loaded {len(nav_df):,} records for {nav_df['amfi_code'].nunique()} funds")

    print("\nBuilding returns matrix...")
    returns_matrix = build_returns_matrix(nav_df, codes)
    print(f"  Shape: {returns_matrix.shape} (dates x funds)")
    for col in returns_matrix.columns:
        ann_ret = returns_matrix[col].mean() * TRADING_DAYS
        ann_vol = returns_matrix[col].std() * np.sqrt(TRADING_DAYS)
        print(f"  {DIVERSE_FUNDS[col]:<35s} | "
              f"Ann Return: {ann_ret*100:7.2f}% | "
              f"Ann Vol: {ann_vol*100:7.2f}%")

    print(f"\nGenerating {N_PORTFOLIOS:,} random portfolios...")
    portfolios, mean_returns, cov = generate_random_portfolios(returns_matrix)
    print("  Done")

    max_sharpe, min_vol = plot_frontier(portfolios, mean_returns, returns_matrix)
    print_weights(max_sharpe, mean_returns, "MAX SHARPE RATIO PORTFOLIO")
    print_weights(min_vol, mean_returns, "MINIMUM VOLATILITY PORTFOLIO")
    print()


if __name__ == "__main__":
    main()
