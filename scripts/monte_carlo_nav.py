#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sqlite3


DB_PATH = Path("bluestock_mf.db")
CHARTS_DIR = Path("charts")
OUTPUT = CHARTS_DIR / "monte_carlo_projection.png"

SCHEME_CODES = [119551, 120503, 118632, 119092, 120841]
SCHEME_NAMES = {
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip",
}

N_SIMULATIONS = 10_000
N_DAYS = 252 * 5


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


def compute_returns(df):
    returns = {}
    for code in df["amfi_code"].unique():
        fund_data = df[df["amfi_code"] == code].sort_values("date")
        fund_data = fund_data.set_index("date")
        daily_ret = fund_data["nav"].pct_change().dropna()
        returns[code] = daily_ret
    return returns


def run_simulation(returns):
    results = {}
    params = {}
    for code, ret_series in returns.items():
        mu = ret_series.mean()
        sigma = ret_series.std()
        params[code] = {"mean_daily": mu, "std_daily": sigma}

        last_nav = 1.0
        simulations = np.zeros((N_SIMULATIONS, N_DAYS + 1))
        simulations[:, 0] = last_nav

        for day in range(1, N_DAYS + 1):
            random_returns = np.random.normal(mu, sigma, N_SIMULATIONS)
            simulations[:, day] = simulations[:, day - 1] * (1 + random_returns)

        results[code] = simulations

    return results, params


def plot_results(results, params):
    fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    axes = axes.flatten()

    for idx, (code, simulations) in enumerate(results.items()):
        ax = axes[idx]
        median = np.median(simulations, axis=0)
        lower = np.percentile(simulations, 2.5, axis=0)
        upper = np.percentile(simulations, 97.5, axis=0)
        days = np.arange(N_DAYS + 1)

        years = days / 252

        ax.plot(years, median, color="steelblue", linewidth=2, label="Median Projection")
        ax.fill_between(years, lower, upper, color="steelblue", alpha=0.15, label="95% Confidence Band")
        ax.set_title(SCHEME_NAMES.get(code, f"Fund {code}"), fontsize=13, fontweight="bold")
        ax.set_xlabel("Years")
        ax.set_ylabel("NAV Growth (Start = 1.0)")
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)

        start_val = 1.0
        final_median = median[-1]
        final_lower = lower[-1]
        final_upper = upper[-1]
        cagr = ((final_median / start_val) ** (1 / 5) - 1) * 100

        summary_text = (
            f"5-Year CAGR: {cagr:.2f}%\n"
            f"Median: {final_median:.3f}\n"
            f"Range: [{final_lower:.3f}, {final_upper:.3f}]"
        )
        ax.text(0.98, 0.05, summary_text, transform=ax.transAxes,
                fontsize=9, verticalalignment="bottom", horizontalalignment="right",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="wheat", alpha=0.8))

    if len(results) < 6:
        for idx in range(len(results), len(axes)):
            axes[idx].set_visible(False)

    fig.suptitle("Monte Carlo NAV Projection (10,000 simulations, 5 Years)",
                 fontsize=16, fontweight="bold", y=1.01)
    fig.tight_layout()
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved to {OUTPUT}")


def print_summary(results):
    print("\n" + "=" * 90)
    print("{:<25} {:>12} {:>15} {:>25}".format(
        "Fund", "5-Year CAGR", "Median NAV", "95% Range"))
    print("=" * 90)

    for code in SCHEME_CODES:
        simulations = results[code]
        median = np.median(simulations, axis=0)
        lower = np.percentile(simulations, 2.5, axis=0)
        upper = np.percentile(simulations, 97.5, axis=0)

        cagr = ((median[-1] / 1.0) ** (1 / 5) - 1) * 100
        print("{:<25} {:>10.2f}% {:>12.3f}x {:>12.3f}x - {:.3f}x".format(
            SCHEME_NAMES.get(code, str(code)),
            cagr,
            median[-1],
            lower[-1],
            upper[-1],
        ))
    print("=" * 90)


def main():
    print("=" * 70)
    print("MONTE CARLO NAV PROJECTION")
    print("=" * 70)
    print(f"Funds: {[SCHEME_NAMES[c] for c in SCHEME_CODES]}")
    print(f"Simulations: {N_SIMULATIONS:,}")
    print(f"Projection period: {N_DAYS} trading days (5 years)")
    print()

    print("Loading NAV data from database...")
    nav_df = load_nav_data(SCHEME_CODES)
    print(f"  Loaded {len(nav_df)} records for {nav_df['amfi_code'].nunique()} funds")

    print("\nComputing daily returns...")
    returns = compute_returns(nav_df)
    for code, ret in returns.items():
        print(f"  {SCHEME_NAMES.get(code, code)}: "
              f"mean_daily={ret.mean():.6f}, std_daily={ret.std():.6f}")

    print(f"\nRunning {N_SIMULATIONS:,} Monte Carlo simulations...")
    results, params = run_simulation(returns)
    print("  Simulations complete")

    print_summary(results)
    plot_results(results, params)


if __name__ == "__main__":
    main()
