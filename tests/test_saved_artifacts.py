"""Integrity checks for the public aggregate evidence and source manifest."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"


class SavedArtifactTests(unittest.TestCase):
    def test_subperiod_totals_and_tail_sensitive_metrics(self) -> None:
        data = pd.read_csv(TABLES / "a_small_subperiod_summary.csv")
        self.assertEqual(len(data), 5)
        self.assertEqual(int(data["event_count"].sum()), 929_294)
        self.assertEqual(int(data["valid_20d_count"].sum()), 787_359)
        self.assertTrue((data["mean_20d"] > 0).all())
        self.assertTrue((data["median_20d"] <= 0).all())
        self.assertTrue((data["hit_rate_20d"] < 0.5).all())

        recent = data.loc[data["period"] == "2020-2025"].iloc[0]
        self.assertAlmostEqual(recent["mean_20d"], 0.1393768454438287)
        self.assertAlmostEqual(recent["median_20d"], -0.010775217966221995)
        self.assertAlmostEqual(
            recent["winsor_1pct_mean_20d"], 0.03143898940885322
        )

    def test_structure_split_reconciles_to_event_total(self) -> None:
        data = pd.read_csv(TABLES / "a_small_structure_splits.csv")
        pooled = data.loc[
            (data["split"] == "small_subbucket") & (data["period"] == "pooled")
        ]
        self.assertEqual(int(pooled["n"].sum()), 929_294)
        micro = pooled.loc[pooled["group"] == "microcap_small"].iloc[0]
        upper = pooled.loc[pooled["group"] == "upper_small"].iloc[0]
        self.assertGreater(micro["mean_20d"], upper["mean_20d"])
        self.assertLess(micro["median_20d"], 0)

    def test_capacity_values_are_entry_cohort_diagnostics(self) -> None:
        data = pd.read_csv(TABLES / "a_small_capacity_summary.csv")
        one_percent = data.loc[data["participation_rate"] == 0.01]
        self.assertEqual(len(one_percent), 10)
        recent_all = one_percent.loc[
            (one_percent["period"] == "2020-2025")
            & (one_percent["universe"] == "all_events")
        ].iloc[0]
        recent_adv70 = one_percent.loc[
            (one_percent["period"] == "2020-2025")
            & (one_percent["universe"] == "adv70_events")
        ].iloc[0]
        self.assertAlmostEqual(
            recent_all["median_cohort_capacity_usd"], 8026.755050376225
        )
        self.assertAlmostEqual(
            recent_adv70["median_cohort_capacity_usd"], 113310.90823449931
        )

    def test_preserved_original_files_match_manifest(self) -> None:
        manifest = ROOT / "docs" / "source_manifest_sha256.csv"
        with manifest.open(newline="", encoding="utf-8") as handle:
            rows = csv.DictReader(handle)
            for row in rows:
                public_path = row["public_relative_path"]
                if not public_path:
                    continue
                path = ROOT / public_path
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(
                    digest,
                    row["sha256"],
                    msg=f"hash mismatch for {public_path}",
                )
                self.assertEqual(path.stat().st_size, int(row["bytes"]))

    def test_aggregate_tables_have_no_security_identifiers(self) -> None:
        for path in TABLES.glob("*.csv"):
            columns = {column.lower() for column in pd.read_csv(path, nrows=0).columns}
            self.assertNotIn("permno", columns, msg=path.name)
            self.assertNotIn("ticker", columns, msg=path.name)
            self.assertNotIn("cusip", columns, msg=path.name)


if __name__ == "__main__":
    unittest.main()
