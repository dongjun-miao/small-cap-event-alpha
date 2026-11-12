"""File-by-file canonical research pipeline."""

from __future__ import annotations

import gc
from pathlib import Path
import re

import pandas as pd

from .core import HORIZONS, build_event_sample
from .reporting import (
    add_adv_filter,
    cohort_capacity_summary,
    mechanism_sort_table,
    mechanism_spread_table,
    structure_split_table,
    summarize_subperiod,
)


USE_COLUMNS = [
    "permno",
    "ticker",
    "exchange",
    "date",
    "mktcap",
    "volume",
    "open",
    "high",
    "low",
    "close",
    "shrout",
]


def period_from_path(path: Path) -> str:
    return path.name.split("_research", maxsplit=1)[0]


def run_pipeline(
    data_dir: Path,
    output_dir: Path,
    *,
    reuse_event_samples: bool = False,
) -> dict[str, Path]:
    """Run the full canonical analysis across all research_v1 files."""

    period_pattern = re.compile(r"^\d{4}-\d{4}_research_v1\.csv$")
    files = sorted(
        path
        for path in data_dir.glob("*_research_v1.csv")
        if period_pattern.fullmatch(path.name)
    )
    if not files:
        raise FileNotFoundError(f"No *_research_v1.csv files found in {data_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    event_dir = output_dir / "event_samples"
    event_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, object]] = []
    capacity_tables: list[pd.DataFrame] = []
    event_frames: list[pd.DataFrame] = []

    for path in files:
        period = period_from_path(path)
        event_path = event_dir / f"a_small_events_{period}.csv.gz"
        if reuse_event_samples and event_path.exists():
            print(f"[{period}] reusing {event_path.name}", flush=True)
            events = pd.read_csv(event_path, parse_dates=["date"], low_memory=False)
            frame = None
        else:
            print(f"[{period}] loading {path.name}", flush=True)
            frame = pd.read_csv(
                path,
                usecols=lambda name: name in USE_COLUMNS,
                parse_dates=["date"],
                low_memory=False,
            )
            events = build_event_sample(frame, horizons=HORIZONS)
            events["period"] = period
        summaries.append(summarize_subperiod(events, period))

        all_capacity = cohort_capacity_summary(events)
        all_capacity.insert(0, "universe", "all_events")
        all_capacity.insert(0, "period", period)
        capacity_tables.append(all_capacity)

        filtered = add_adv_filter(events, 0.70)
        filtered_capacity = cohort_capacity_summary(filtered)
        filtered_capacity.insert(0, "universe", "adv70_events")
        filtered_capacity.insert(0, "period", period)
        capacity_tables.append(filtered_capacity)

        if not (reuse_event_samples and event_path.exists()):
            events.to_csv(event_path, index=False, compression="gzip")
        event_frames.append(events)
        print(
            f"[{period}] signals={len(events):,}; saved {event_path.name}",
            flush=True,
        )
        if frame is not None:
            del frame
        gc.collect()

    all_events = pd.concat(event_frames, ignore_index=True)
    subperiod = pd.DataFrame(summaries)
    capacity = pd.concat(capacity_tables, ignore_index=True)
    mechanism = mechanism_sort_table(
        all_events,
        proxies=(
            "adv20_usd_pre",
            "vol_prev_to_ma20",
            "volume_to_ma20",
            "volume_to_prev",
            "intraday_range",
            "turnover_ma20_pre",
        ),
    )
    mechanism_spreads = mechanism_spread_table(mechanism)
    structure_splits = structure_split_table(all_events)

    paths = {
        "subperiod_summary": output_dir / "a_small_subperiod_summary.csv",
        "capacity_summary": output_dir / "a_small_capacity_summary.csv",
        "mechanism_sorts": output_dir / "a_small_mechanism_sorts.csv",
        "mechanism_spreads": output_dir / "a_small_mechanism_spreads.csv",
        "structure_splits": output_dir / "a_small_structure_splits.csv",
    }
    subperiod.to_csv(paths["subperiod_summary"], index=False)
    capacity.to_csv(paths["capacity_summary"], index=False)
    mechanism.to_csv(paths["mechanism_sorts"], index=False)
    mechanism_spreads.to_csv(paths["mechanism_spreads"], index=False)
    structure_splits.to_csv(paths["structure_splits"], index=False)
    print(f"Completed canonical pipeline. Outputs: {output_dir}", flush=True)
    return paths
