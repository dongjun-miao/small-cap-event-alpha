"""Synthetic tests for descriptive and capacity reporting."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from event_alpha.reporting import (  # noqa: E402
    cohort_capacity_summary,
    summarize_subperiod,
    winsorized_mean,
)


class ReportingTests(unittest.TestCase):
    def test_winsorized_mean_matches_explicit_clipping(self) -> None:
        values = pd.Series([0.0, 1.0, 2.0, 100.0])
        lower, upper = values.quantile([0.25, 0.75])
        expected = values.clip(lower, upper).mean()
        self.assertAlmostEqual(winsorized_mean(values, tail=0.25), expected)

    def test_fixed_cost_is_only_an_arithmetic_haircut(self) -> None:
        events = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
                "ret_5d_next_open_to_close": [0.02, 0.04],
                "ret_10d_next_open_to_close": [0.03, 0.05],
                "ret_20d_next_open_to_close": [0.04, 0.06],
            }
        )
        summary = summarize_subperiod(events, "synthetic")
        self.assertAlmostEqual(summary["mean_20d"], 0.05)
        self.assertAlmostEqual(summary["mean_20d_net_100bp"], 0.04)

    def test_equal_weight_cohort_capacity_uses_least_liquid_member(self) -> None:
        events = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    [
                        "2024-01-02",
                        "2024-01-02",
                        "2024-01-03",
                        "2024-01-03",
                        "2024-01-03",
                    ]
                ),
                "adv20_usd_pre": [100.0, 200.0, 300.0, 400.0, 500.0],
            }
        )
        result = cohort_capacity_summary(events, participation_rates=(0.01,))
        # Date capacities: 2 × 100 × 1% = 2; 3 × 300 × 1% = 9.
        self.assertAlmostEqual(result.iloc[0]["median_cohort_capacity_usd"], 5.5)


if __name__ == "__main__":
    unittest.main()
