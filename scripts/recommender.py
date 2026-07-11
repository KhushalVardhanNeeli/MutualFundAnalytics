#!/usr/bin/env python3
"""Fund recommender based on risk appetite, Sharpe ratio, and performance metrics."""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/db/bluestock_mf.db")

RISK_TO_CATEGORIES = {
    "Low": ["Debt"],
    "Moderate": ["Equity"],
    "High": ["Equity"],
}

RISK_TO_SUBCATEGORIES = {
    "Low": ["Liquid", "Short Duration", "Gilt"],
    "Moderate": ["Large Cap", "Index/ETF", "Index"],
    "High": ["Mid Cap", "Small Cap", "Flexi Cap", "ELSS", "Value", "Large & Mid Cap"],
}


def get_recommendations(risk_appetite, top_n=3):
    risk = risk_appetite.strip().title()
    if risk not in RISK_TO_CATEGORIES:
        valid = ", ".join(RISK_TO_CATEGORIES.keys())
        raise ValueError(f"Invalid risk appetite '{risk_appetite}'. Choose from: {valid}")

    categories = RISK_TO_CATEGORIES[risk]
    subcategories = RISK_TO_SUBCATEGORIES[risk]

    conn = sqlite3.connect(str(DB_PATH))

    cat_placeholders = ",".join("?" for _ in categories)
    sub_placeholders = ",".join("?" for _ in subcategories)

    query = f"""
        SELECT
            df.scheme_name,
            df.fund_house,
            df.sub_category,
            df.risk_category,
            fp.sharpe_ratio,
            fp.sortino_ratio,
            fp.return_3yr_pct,
            fp.return_5yr_pct,
            fp.alpha,
            fp.expense_ratio_pct,
            fp.morningstar_rating,
            fp.aum_crore
        FROM fact_performance fp
        JOIN dim_fund df ON fp.amfi_code = df.amfi_code
        WHERE df.category IN ({cat_placeholders})
          AND df.sub_category IN ({sub_placeholders})
          AND fp.sharpe_ratio IS NOT NULL
        ORDER BY fp.sharpe_ratio DESC
        LIMIT ?
    """

    params = [*categories, *subcategories, top_n]
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


def print_recommendations(risk_appetite, top_n=3):
    print(f"\n{'=' * 80}")
    print(f"  FUND RECOMMENDATIONS — Risk Appetite: {risk_appetite.upper()}")
    print(f"{'=' * 80}")

    try:
        df = get_recommendations(risk_appetite, top_n)
    except ValueError as e:
        print(f"  Error: {e}")
        return

    if df.empty:
        print("  No funds found matching criteria.")
        return

    print(f"\n  Top {len(df)} funds by Sharpe Ratio:\n")
    for i, row in df.iterrows():
        print(f"  {i+1}. {row['scheme_name']}")
        print(f"     Fund House   : {row['fund_house']}")
        print(f"     Category     : {row['sub_category']} | Risk: {row['risk_category']}")
        print(f"     Sharpe Ratio : {row['sharpe_ratio']:.2f}")
        print(f"     Sortino Ratio: {row['sortino_ratio']:.2f}")
        print(f"     3Y Return    : {row['return_3yr_pct']:.2f}%")
        print(f"     5Y Return    : {row['return_5yr_pct']:.2f}%")
        print(f"     Alpha        : {row['alpha']:.2f}")
        print(f"     Expense Ratio: {row['expense_ratio_pct']:.2f}%")
        print(f"     Morningstar  : {row['morningstar_rating']}★")
        print(f"     AUM          : ₹{row['aum_crore']:,.0f} Cr")
        print()

    return df


def compare_all_risks():
    """Print recommendations for all risk levels."""
    for risk in ["Low", "Moderate", "High"]:
        print_recommendations(risk, top_n=3)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        risk = sys.argv[1]
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        print_recommendations(risk, top_n=n)
    else:
        print("Usage: python recommender.py <Low|Moderate|High> [top_n]")
        print("       python recommender.py all")
        if len(sys.argv) == 1:
            print("\nShowing recommendations for all risk levels:\n")
            compare_all_risks()
