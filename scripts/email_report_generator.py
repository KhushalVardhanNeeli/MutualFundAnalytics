#!/usr/bin/env python3

import sqlite3
import smtplib
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

DB_PATH = Path("data/db/bluestock_mf.db")
REPORTS_DIR = Path("reports")

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "")

CSS_STYLE = """
body {
    font-family: Arial, Helvetica, sans-serif;
    background-color: #f4f6f8;
    margin: 0;
    padding: 0;
    color: #1a1a2e;
}
.container {
    max-width: 700px;
    margin: 0 auto;
    background-color: #ffffff;
    border: 1px solid #dce1e6;
}
.header {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #ffffff;
    padding: 30px 25px;
    text-align: center;
}
.header h1 {
    margin: 0 0 6px 0;
    font-size: 24px;
    letter-spacing: 0.5px;
}
.header .subtitle {
    font-size: 14px;
    opacity: 0.85;
}
.header .date-range {
    font-size: 13px;
    margin-top: 8px;
    opacity: 0.8;
}
.section {
    padding: 20px 25px;
    border-bottom: 1px solid #e8ecf0;
}
.section:last-child {
    border-bottom: none;
}
.section h2 {
    font-size: 18px;
    color: #203a43;
    margin: 0 0 12px 0;
    border-bottom: 2px solid #2c5364;
    padding-bottom: 6px;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
table th {
    background-color: #203a43;
    color: #ffffff;
    padding: 10px 8px;
    text-align: left;
    font-weight: 600;
}
table td {
    padding: 8px 8px;
    border-bottom: 1px solid #e8ecf0;
}
table tr:nth-child(even) {
    background-color: #f8f9fa;
}
.positive {
    color: #27ae60;
    font-weight: bold;
}
.negative {
    color: #e74c3c;
    font-weight: bold;
}
.metrics-box {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}
.metric-card {
    flex: 1 1 180px;
    background: #f4f6f8;
    border-radius: 6px;
    padding: 14px;
    text-align: center;
    border: 1px solid #dce1e6;
}
.metric-value {
    font-size: 22px;
    font-weight: bold;
    color: #203a43;
}
.metric-label {
    font-size: 12px;
    color: #7f8c8d;
    margin-top: 2px;
}
.footer {
    background-color: #f4f6f8;
    padding: 15px 25px;
    font-size: 11px;
    color: #7f8c8d;
    text-align: center;
    border-top: 1px solid #dce1e6;
}
"""


def get_weekly_returns(start_date, end_date):
    conn = sqlite3.connect(str(DB_PATH))

    query = """
        WITH start_nav AS (
            SELECT fn.amfi_code, fn.nav AS nav_start
            FROM fact_nav fn
            JOIN dim_date d ON fn.date_id = d.date_id
            WHERE d.full_date = (
                SELECT MAX(d2.full_date) FROM dim_date d2
                JOIN fact_nav fn2 ON d2.date_id = fn2.date_id
                WHERE fn2.amfi_code = fn.amfi_code AND d2.full_date <= ?
            )
        ),
        end_nav AS (
            SELECT fn.amfi_code, fn.nav AS nav_end
            FROM fact_nav fn
            JOIN dim_date d ON fn.date_id = d.date_id
            WHERE d.full_date = (
                SELECT MAX(d2.full_date) FROM dim_date d2
                JOIN fact_nav fn2 ON d2.date_id = fn2.date_id
                WHERE fn2.amfi_code = fn.amfi_code AND d2.full_date <= ?
            )
        )
        SELECT
            df.amfi_code,
            df.scheme_name,
            df.fund_house,
            df.category,
            df.sub_category,
            s.nav_start,
            e.nav_end,
            ROUND(((e.nav_end - s.nav_start) / s.nav_start) * 100, 4) AS weekly_return_pct
        FROM start_nav s
        JOIN end_nav e ON s.amfi_code = e.amfi_code
        JOIN dim_fund df ON s.amfi_code = df.amfi_code
        WHERE s.nav_start > 0
    """

    df = pd.read_sql_query(query, conn, params=[start_date, end_date])
    conn.close()
    return df


def get_total_aum_latest():
    conn = sqlite3.connect(str(DB_PATH))
    query = """
        SELECT SUM(aum_crore) AS total_aum_crore
        FROM fact_aum
        JOIN dim_date d ON fact_aum.date_id = d.date_id
        WHERE d.full_date = (
            SELECT MAX(d2.full_date) FROM dim_date d2
            JOIN fact_aum fa2 ON d2.date_id = fa2.date_id
        )
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    val = result["total_aum_crore"].iloc[0]
    return val if pd.notna(val) else None


def get_sip_latest_month():
    conn = sqlite3.connect(str(DB_PATH))
    query = """
        SELECT sip_inflow_crore
        FROM fact_sip_inflows
        WHERE month = (SELECT MAX(month) FROM fact_sip_inflows)
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    val = result["sip_inflow_crore"].iloc[0] if len(result) > 0 else None
    return val if pd.notna(val) else None


def get_folio_latest():
    conn = sqlite3.connect(str(DB_PATH))
    query = """
        SELECT total_folios_crore
        FROM fact_folio_count
        WHERE month = (SELECT MAX(month) FROM fact_folio_count)
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    val = result["total_folios_crore"].iloc[0] if len(result) > 0 else None
    return val if pd.notna(val) else None


def get_fund_recommendations():
    conn = sqlite3.connect(str(DB_PATH))
    query = """
        SELECT
            df.scheme_name,
            df.fund_house,
            df.category,
            fp.sharpe_ratio,
            fp.return_5yr_pct,
            fp.alpha,
            fp.expense_ratio_pct,
            fp.morningstar_rating
        FROM fact_performance fp
        JOIN dim_fund df ON fp.amfi_code = df.amfi_code
        WHERE fp.sharpe_ratio IS NOT NULL
          AND fp.morningstar_rating IS NOT NULL
        ORDER BY fp.sharpe_ratio DESC
        LIMIT 5
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def build_html(weekly_df, total_aum, sip_inr, total_folios, recommendations, start_date, end_date):
    top5 = weekly_df.nlargest(5, "weekly_return_pct").copy()
    bottom5 = weekly_df.nsmallest(5, "weekly_return_pct").copy()

    dt_format = "%d %b %Y"
    start_str = pd.Timestamp(start_date).strftime(dt_format)
    end_str = pd.Timestamp(end_date).strftime(dt_format)

    def fmt_ret(val):
        cls = "positive" if val >= 0 else "negative"
        sign = "+" if val >= 0 else ""
        return f'<td class="{cls}">{sign}{val:.2f}%</td>'

    top_rows = ""
    for _, r in top5.iterrows():
        top_rows += f"""
        <tr>
            <td>{r['scheme_name']}</td>
            <td>{r['fund_house']}</td>
            <td>{r['category']}</td>
            {fmt_ret(r['weekly_return_pct'])}
        </tr>"""

    bottom_rows = ""
    for _, r in bottom5.iterrows():
        bottom_rows += f"""
        <tr>
            <td>{r['scheme_name']}</td>
            <td>{r['fund_house']}</td>
            <td>{r['category']}</td>
            {fmt_ret(r['weekly_return_pct'])}
        </tr>"""

    rec_rows = ""
    for _, r in recommendations.iterrows():
        rec_rows += f"""
        <tr>
            <td>{r['scheme_name']}</td>
            <td>{r['fund_house']}</td>
            <td>{r['sharpe_ratio']:.2f}</td>
            <td>{r['return_5yr_pct']:.2f}%</td>
            <td>{r['alpha']:.2f}</td>
            <td>{r['morningstar_rating']}</td>
        </tr>"""

    aum_display = f"\u20b9{total_aum:,.0f} Cr" if total_aum else "N/A"
    sip_display = f"\u20b9{sip_inr:,.0f} Cr" if sip_inr else "N/A"
    folio_display = f"{total_folios:,.2f} Cr" if total_folios else "N/A"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bluestock Weekly Report - {end_str}</title>
<style>{CSS_STYLE}</style>
</head>
<body>
<div class="container">

<div class="header">
    <h1>Bluestock Mutual Fund Weekly Report</h1>
    <div class="subtitle">Performance & Market Analysis</div>
    <div class="date-range">{start_str} \u2014 {end_str}</div>
</div>

<div class="section">
    <h2>Top 5 Performing Funds This Week</h2>
    <table>
        <thead>
            <tr><th>Fund Name</th><th>Fund House</th><th>Category</th><th>Weekly Return</th></tr>
        </thead>
        <tbody>{top_rows}</tbody>
    </table>
</div>

<div class="section">
    <h2>Bottom 5 Performing Funds This Week</h2>
    <table>
        <thead>
            <tr><th>Fund Name</th><th>Fund House</th><th>Category</th><th>Weekly Return</th></tr>
        </thead>
        <tbody>{bottom_rows}</tbody>
    </table>
</div>

<div class="section">
    <h2>Key Market Metrics</h2>
    <div class="metrics-box">
        <div class="metric-card">
            <div class="metric-value">{aum_display}</div>
            <div class="metric-label">Total AUM (Latest Quarter)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{sip_display}</div>
            <div class="metric-label">SIP Inflows (Latest Month)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{folio_display}</div>
            <div class="metric-label">Total Folios</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{weekly_df['weekly_return_pct'].median():.2f}%</div>
            <div class="metric-label">Median Weekly Return</div>
        </div>
    </div>
</div>

<div class="section">
    <h2>Fund Recommendations for the Week</h2>
    <p style="font-size:13px;color:#555;">
        Top-rated funds by Sharpe Ratio, suitable for investors with moderate-to-high risk appetite.
        Always consult your financial advisor before investing.
    </p>
    <table>
        <thead>
            <tr>
                <th>Fund Name</th><th>Fund House</th><th>Sharpe</th>
                <th>5Y Return</th><th>Alpha</th><th>Rating</th>
            </tr>
        </thead>
        <tbody>{rec_rows}</tbody>
    </table>
</div>

<div class="footer">
    <p>
        <strong>Disclaimer:</strong> This report is generated for informational purposes only.
        Past performance is no guarantee of future results. Mutual fund investments are subject to
        market risks. Please read all scheme-related documents carefully before investing.
        Data sourced from AMFI and fund house disclosures. Bluestock Analytics is not a
        SEBI-registered investment advisor.
    </p>
    <p>Generated on {datetime.now().strftime('%d %b %Y at %H:%M')} | Bluestock Analytics</p>
</div>

</div>
</body>
</html>"""

    return html


def send_email(html_content, subject, to_email):
    if not SMTP_USER or not SMTP_PASS or not EMAIL_FROM:
        print("\nSMTP credentials not configured. Set SMTP_USER, SMTP_PASS, EMAIL_FROM env vars.")
        print("Report generated but email NOT sent.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        server.quit()
        print(f"\nEmail sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"\nFailed to send email: {e}")
        return False


def main(start_date=None, end_date=None):
    if end_date is None:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.execute("SELECT MAX(full_date) FROM dim_date")
        end_date = cur.fetchone()[0]
        conn.close()

    if isinstance(end_date, str):
        end_date = end_date.split(" ")[0]

    if start_date is None:
        start_dt = pd.Timestamp(end_date) - timedelta(days=7)
        start_date = start_dt.strftime("%Y-%m-%d")

    print("=" * 70)
    print("BLUESTOCK MUTUAL FUND WEEKLY REPORT GENERATOR")
    print("=" * 70)
    print(f"Report period: {start_date} to {end_date}")
    print()

    print("Computing weekly returns...")
    weekly_df = get_weekly_returns(start_date, end_date)
    print(f"  Computed returns for {len(weekly_df)} funds")

    print("\nFetching market metrics...")
    total_aum = get_total_aum_latest()
    sip_inr = get_sip_latest_month()
    total_folios = get_folio_latest()
    print(f"  Total AUM: {total_aum}")
    print(f"  Latest SIP: {sip_inr}")
    print(f"  Total Folios: {total_folios}")

    print("\nFetching fund recommendations...")
    recommendations = get_fund_recommendations()
    print(f"  Found {len(recommendations)} recommendations")

    print("\nGenerating HTML report...")
    html = build_html(weekly_df, total_aum, sip_inr, total_folios, recommendations, start_date, end_date)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"weekly_report_{end_date.replace('-', '')}.html"
    filepath = REPORTS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nReport saved to {filepath}")

    subject = f"Bluestock Weekly Report - {end_date}"
    to_email = EMAIL_TO or SMTP_USER
    if to_email:
        send_email(html, subject, to_email)

    print("=" * 70)


if __name__ == "__main__":
    main()
