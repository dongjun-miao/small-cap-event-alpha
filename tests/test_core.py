"""Contract tests for the canonical event definition."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from event_alpha.core import add_canonical_features  # noqa: E402


class CanonicalSignalTests(unittest.TestCase):
    def make_panel(self) -> pd.DataFrame:
        dates = pd.bdate_range("2020-01-01", periods=30)
        rows = []
        for permno, mktcap in (
            (1, 10.0),
            (2, 20.0),
            (3, 30.0),
            (4, 40.0),
            (5, 50.0),
            (6, 60.0),
        ):
            for index, date in enumerate(dates):
                volume = 100.0
                if permno == 1 and index == 21:
                    volume = 250.0
                rows.append(
                    {
                        "permno": permno,
                        "date": date,
                        "mktcap": mktcap,
                        "volume": volume,
                        "open": 10.0,
                        "high": 11.0,
                        "low": 9.0,
                        "close": 10.8 if permno == 1 and index == 21 else 10.0,
                        "shrout": 1_000.0,
                    }
                )
        panel = pd.DataFrame(rows)
        # Make t-1 dormant relative to the pre-event window.
        panel.loc[(panel["permno"] == 1) & (panel["date"] == dates[20]), "volume"] = 50.0
        return panel

    def test_daily_size_bucket_and_lagged_signal(self) -> None:
        result = add_canonical_features(self.make_panel())
        event_date = pd.Timestamp("2020-01-30")
        row = result.loc[
            (result["permno"] == 1) & (result["date"] == event_date)
        ].iloc[0]
        self.assertEqual(row["size_bucket"], "small")
        self.assertEqual(row["small_subbucket"], "microcap_small")
        self.assertEqual(row["vol_prev"], 50.0)
        self.assertAlmostEqual(row["vol_ma20_pre"], 97.5)
        self.assertTrue(bool(row["a_small"]))

    def test_horizon_requires_exact_market_sessions(self) -> None:
        panel = self.make_panel()
        missing_date = pd.bdate_range("2020-01-01", periods=30)[23]
        panel = panel.loc[
            ~((panel["permno"] == 1) & (panel["date"] == missing_date))
        ]
        result = add_canonical_features(panel)
        event_date = pd.Timestamp("2020-01-30")
        row = result.loc[
            (result["permno"] == 1) & (result["date"] == event_date)
        ].iloc[0]
        self.assertFalse(bool(row["label_valid_5d"]))


if __name__ == "__main__":
    unittest.main()
