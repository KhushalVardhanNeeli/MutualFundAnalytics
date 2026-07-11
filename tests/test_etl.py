"""Tests for the Bluestock Mutual Fund Analytics ETL pipeline."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROJECT_ROOT / "bluestock_mf.db"


class TestDataRaw(unittest.TestCase):
    def test_all_raw_files_exist(self):
        expected = [
            "01_fund_master.csv", "02_nav_history.csv",
            "03_aum_by_fund_house.csv", "04_monthly_sip_inflows.csv",
            "05_category_inflows.csv", "06_industry_folio_count.csv",
            "07_scheme_performance.csv", "08_investor_transactions.csv",
            "09_portfolio_holdings.csv", "10_benchmark_indices.csv",
        ]
        for f in expected:
            self.assertTrue((DATA_RAW / f).exists(), f"Missing: {f}")

    def test_fund_master_has_40_schemes(self):
        fm = pd.read_csv(DATA_RAW / "01_fund_master.csv")
        self.assertEqual(len(fm), 40)

    def test_nav_history_positive(self):
        nav = pd.read_csv(DATA_RAW / "02_nav_history.csv")
        self.assertTrue((nav["nav"] > 0).all())

    def test_transaction_amounts_positive(self):
        tx = pd.read_csv(DATA_RAW / "08_investor_transactions.csv")
        self.assertTrue((tx["amount_inr"] > 0).all())


class TestDataCleaned(unittest.TestCase):
    def test_all_cleaned_files_exist(self):
        files = list(DATA_PROCESSED.glob("*.csv"))
        self.assertGreaterEqual(len(files), 10)

    def test_fund_master_unique_codes(self):
        fm = pd.read_csv(DATA_PROCESSED / "01_fund_master.csv")
        self.assertEqual(len(fm["amfi_code"].unique()), len(fm))

    def test_performance_expense_ratio_range(self):
        perf = pd.read_csv(DATA_PROCESSED / "07_scheme_performance.csv")
        self.assertTrue((perf["expense_ratio_pct"] >= 0.1).all())
        self.assertTrue((perf["expense_ratio_pct"] <= 2.5).all())


class TestConfig(unittest.TestCase):
    def test_config_paths(self):
        from scripts.config import PROJECT_ROOT, DATA_RAW as cfg_raw
        self.assertTrue(PROJECT_ROOT.exists())
        self.assertTrue(cfg_raw.exists())

    def test_config_constants(self):
        from scripts.config import RISK_FREE_RATE, TRADING_DAYS, SCHEME_CODES
        self.assertEqual(RISK_FREE_RATE, 0.065)
        self.assertEqual(TRADING_DAYS, 252)
        self.assertIn(125497, SCHEME_CODES.values())


class TestComputeMetrics(unittest.TestCase):
    def test_var_cvar(self):
        from scripts.compute_metrics import compute_var_cvar
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.015, 1000)
        var, cvar = compute_var_cvar(returns, 0.95)
        self.assertLess(var, 0)
        self.assertLessEqual(cvar, var)

    def test_hhi(self):
        from scripts.compute_metrics import compute_hhi
        hhi = compute_hhi([30, 25, 15, 10, 10, 5, 5])
        self.assertAlmostEqual(hhi, 2000.0)

    def test_hhi_empty(self):
        from scripts.compute_metrics import compute_hhi
        self.assertTrue(np.isnan(compute_hhi([])))


if __name__ == "__main__":
    unittest.main(verbosity=2)
