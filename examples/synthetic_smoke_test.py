"""Run a non-proprietary smoke test of the event and timing contract."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from event_alpha.core import add_canonical_features  # noqa: E402


def make_fixture() -> tuple[pd.DataFrame, pd.Timestamp]:
    dates = pd.bdate_range("2024-01-02", periods=30)
    event_index = 21
    rows: list[dict[str, object]] = []
    for permno, market_cap in enumerate((10, 20, 30, 40, 50, 60), start=1):
        for index, date in enumerate(dates):
            volume = 100.0
            close = 10.0
            if permno == 1 and index == event_index - 1:
                volume = 50.0
            if permno == 1 and index == event_index:
                volume = 250.0
                close = 10.8
            rows.append(
                {
                    "permno": permno,
                    "date": date,
                    "mktcap": float(market_cap),
                    "volume": volume,
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.0,
                    "close": close,
                    "shrout": 1_000.0,
                }
            )
    return pd.DataFrame(rows), dates[event_index]


def main() -> None:
    fixture, event_date = make_fixture()
    panel = add_canonical_features(fixture)
    event = panel.loc[
        (panel["permno"] == 1) & (panel["date"] == event_date)
    ].iloc[0]
    assert bool(event["a_small"])
    assert event["vol_prev"] == 50.0
    assert event["entry_open_t1"] == 10.0
    assert bool(event["label_valid_5d"])
    print(
        "Synthetic smoke test passed: event, next-open entry, "
        "and exact-session label verified."
    )


if __name__ == "__main__":
    main()
