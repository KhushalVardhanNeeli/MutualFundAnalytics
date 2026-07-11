#!/usr/bin/env python3
"""Master ETL pipeline — runs the entire data processing workflow."""

import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = PROJECT_ROOT / "scripts"

STEPS = [
    ("1. Data Ingestion", "data_ingestion.py"),
    ("2. AMFI Validation", "validate_amfi.py"),
    ("3. Fund Master Exploration", "explore_fund_master.py"),
    ("4. Live NAV Fetch", "live_nav_fetch.py"),
    ("5. Data Cleaning", "data_cleaning.py"),
    ("6. Load to SQLite", "load_to_sqlite.py"),
    ("7. Compute Metrics", "compute_metrics.py"),
]

def run_step(label, script):
    print(f"\n{'=' * 70}")
    print(f"  {label}")
    print(f"{'=' * 70}")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        cwd=str(PROJECT_ROOT),
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"\n  FAILED: {script} returned exit code {result.returncode}")
        return False
    print(f"\n  COMPLETED: {script}")
    return True

def main():
    print("=" * 70)
    print("  BLUESTOCK MUTUAL FUND ANALYTICS — ETL PIPELINE")
    print("=" * 70)
    print(f"  Project root: {PROJECT_ROOT}")

    for label, script in STEPS:
        if not run_step(label, script):
            print(f"\nPipeline halted at: {label}")
            return 1

    print(f"\n{'=' * 70}")
    print("  ETL PIPELINE COMPLETED SUCCESSFULLY")
    print(f"{'=' * 70}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
