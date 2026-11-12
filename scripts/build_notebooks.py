"""Build the three lightweight GitHub-facing notebooks using stdlib JSON."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"


def markdown(text: str) -> dict[str, object]:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().splitlines()],
    }


def code(text: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.strip().splitlines()],
    }


def write_notebook(name: str, cells: list[dict[str, object]]) -> None:
    payload = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.x"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    (NOTEBOOK_DIR / name).write_text(
        json.dumps(payload, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


COMMON_SETUP = """
from pathlib import Path
import pandas as pd

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
RESULTS = ROOT / "results" / "tables"
"""


write_notebook(
    "05_us_signal_on_crsp_v2.ipynb",
    [
        markdown(
            """
# 05 - Canonical A_small signal and subperiod evidence

This notebook presents aggregate results from the canonical signal contract.
The full security-level build is intentionally run through
`scripts/run_research.py` so all three notebooks use the same implementation.

Canonical choices: daily cross-sectional size terciles, lagged 5/20-day volume
baselines, next-session-open entry, horizon-close exit, and exact session
alignment.
"""
        ),
        code(COMMON_SETUP),
        code(
            """
summary = pd.read_csv(RESULTS / "a_small_subperiod_summary.csv")
summary["event_count"].sum(), summary["valid_20d_count"].sum()
"""
        ),
        code(
            """
columns = [
    "period", "event_count", "valid_20d_count", "mean_20d",
    "median_20d", "winsor_1pct_mean_20d", "mean_20d_net_100bp",
]
summary[columns]
"""
        ),
        markdown(
            """
## Reading the table

The mean 20-day return is positive in every subperiod, including after the
simple 100 bp haircut. Medians and winsorized means are much weaker, especially
after 2015, so the evidence is explicitly described as right-tail concentrated.
"""
        ),
    ],
)

write_notebook(
    "06_us_a_small_implementability_v2.ipynb",
    [
        markdown(
            """
# 06 - Implementability and entry-cohort capacity

Liquidity is measured using lagged pre-event ADV20, preventing the event-day
volume shock from inflating its own capacity estimate. Capacity is a
signal-date equal-weight cohort diagnostic, not a production AUM claim.
"""
        ),
        code(COMMON_SETUP),
        code(
            """
capacity = pd.read_csv(RESULTS / "a_small_capacity_summary.csv")
capacity.loc[capacity["participation_rate"].eq(0.01), [
    "period", "universe", "median_events_per_date",
    "median_cohort_capacity_usd", "p90_cohort_capacity_usd",
]]
"""
        ),
        markdown(
            """
## Interpretation

Filtering to the upper 30% of pre-event ADV materially raises cohort capacity,
but the absolute values remain small. The evidence supports a niche,
capacity-constrained event effect rather than institutional-scale deployment.
"""
        ),
    ],
)

write_notebook(
    "07_us_a_small_mechanism_v2.ipynb",
    [
        markdown(
            """
# 07 - Dormancy, trading intensity, and microcap concentration

Mechanism proxies are bucketed within each five-year subperiod before pooled
Q5-minus-Q1 spreads are calculated. Mean, median, and winsorized results are
shown together to diagnose winner concentration.
"""
        ),
        code(COMMON_SETUP),
        code(
            """
spreads = pd.read_csv(RESULTS / "a_small_mechanism_spreads.csv")
spreads.loc[spreads["period"].eq("pooled"), [
    "proxy", "q5_minus_q1_mean_20d", "q5_minus_q1_median_20d",
    "q5_minus_q1_winsor_1pct_mean_20d",
]]
"""
        ),
        code(
            """
structure = pd.read_csv(RESULTS / "a_small_structure_splits.csv")
structure.loc[
    structure["period"].eq("pooled"),
    ["split", "group", "n", "median_mktcap", "mean_20d",
     "median_20d", "winsor_1pct_mean_20d"],
]
"""
        ),
        markdown(
            """
## Mechanism conclusion

The results support pre-event dormancy as a sample characteristic, but not a
simple monotonic "lower ADV is better" story. Raw mean spreads are strongest
for intraday range, turnover, and the daily microcap subgroup, while median
effects remain weak. The appropriate conclusion is a right-tail,
trading-intensity mechanism with binding liquidity and capacity constraints.
"""
        ),
    ],
)

print(f"Built notebooks in {NOTEBOOK_DIR}")
