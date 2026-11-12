"""Summary tables for event performance, implementation, and mechanisms."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from .core import HORIZONS


def winsorized_mean(series: pd.Series, tail: float = 0.01) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    lower, upper = clean.quantile([tail, 1.0 - tail])
    return float(clean.clip(lower=lower, upper=upper).mean())


def summarize_subperiod(
    events: pd.DataFrame,
    period: str,
    *,
    horizons: Iterable[int] = HORIZONS,
    costs_bps: Iterable[int] = (40, 100),
) -> dict[str, object]:
    row: dict[str, object] = {
        "period": period,
        "event_count": int(len(events)),
        "first_event_date": events["date"].min(),
        "last_event_date": events["date"].max(),
    }
    for horizon in sorted({int(value) for value in horizons}):
        column = f"ret_{horizon}d_next_open_to_close"
        values = pd.to_numeric(events[column], errors="coerce").dropna()
        row[f"valid_{horizon}d_count"] = int(len(values))
        row[f"mean_{horizon}d"] = float(values.mean())
        row[f"median_{horizon}d"] = float(values.median())
        row[f"winsor_1pct_mean_{horizon}d"] = winsorized_mean(values, 0.01)
        row[f"hit_rate_{horizon}d"] = float(values.gt(0).mean())
        for cost in costs_bps:
            row[f"mean_{horizon}d_net_{cost}bp"] = float(
                values.mean() - cost / 10_000.0
            )
    return row


def add_adv_filter(events: pd.DataFrame, quantile: float = 0.70) -> pd.DataFrame:
    threshold = events["adv20_usd_pre"].quantile(quantile)
    filtered = events.loc[events["adv20_usd_pre"].ge(threshold)].copy()
    filtered["adv_filter_quantile"] = quantile
    filtered["adv_filter_threshold_usd"] = threshold
    return filtered


def cohort_capacity_summary(
    events: pd.DataFrame,
    *,
    participation_rates: Iterable[float] = (0.005, 0.01, 0.02),
) -> pd.DataFrame:
    """Estimate equal-weight entry-cohort NAV capacity.

    For each signal date and participation rate, every event receives the same
    dollar allocation. The cohort NAV is therefore limited by the least-liquid
    member: ``n_events * min(participation * pre-event ADV20)``.
    """

    valid = events.loc[
        events["adv20_usd_pre"].notna() & events["adv20_usd_pre"].gt(0),
        ["date", "adv20_usd_pre"],
    ]
    rows: list[dict[str, float | int]] = []
    daily = valid.groupby("date", sort=True)["adv20_usd_pre"]
    count = daily.size()
    minimum = daily.min()
    for rate in participation_rates:
        capacity = count * minimum * float(rate)
        rows.append(
            {
                "participation_rate": float(rate),
                "n_signal_dates": int(len(capacity)),
                "median_events_per_date": float(count.median()),
                "median_cohort_capacity_usd": float(capacity.median()),
                "mean_cohort_capacity_usd": float(capacity.mean()),
                "p90_cohort_capacity_usd": float(capacity.quantile(0.90)),
            }
        )
    return pd.DataFrame(rows)


def assign_period_quantiles(
    frame: pd.DataFrame,
    value_column: str,
    *,
    groups: int = 5,
) -> pd.Series:
    result = pd.Series(pd.NA, index=frame.index, dtype="string")
    labels = [f"Q{index}" for index in range(1, groups + 1)]
    for _, indices in frame.groupby("period", sort=False).groups.items():
        values = frame.loc[indices, value_column].replace([np.inf, -np.inf], np.nan)
        valid = values.notna()
        if valid.sum() < groups:
            continue
        ranks = values.loc[valid].rank(method="first")
        result.loc[ranks.index] = pd.qcut(ranks, groups, labels=labels).astype("string")
    return result


def mechanism_sort_table(
    events: pd.DataFrame,
    proxies: Iterable[str],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for proxy in proxies:
        bucket = assign_period_quantiles(events, proxy)
        work = events.assign(bucket=bucket)
        valid_work = work.dropna(subset=["bucket"])
        grouped = valid_work.groupby(
            ["period", "bucket"], observed=True, sort=True
        )
        pooled = valid_work.groupby("bucket", observed=True, sort=True)
        group_iter = [
            (period, name, group)
            for (period, name), group in grouped
        ] + [
            ("pooled", name, group)
            for name, group in pooled
        ]
        for period, name, group in group_iter:
            row: dict[str, object] = {
                "proxy": proxy,
                "period": period,
                "bucket": name,
                "n": int(len(group)),
                "mean_proxy": float(group[proxy].mean()),
                "median_proxy": float(group[proxy].median()),
            }
            for horizon in HORIZONS:
                values = group[f"ret_{horizon}d_next_open_to_close"]
                row[f"mean_{horizon}d"] = float(values.mean())
                row[f"median_{horizon}d"] = float(values.median())
                row[f"winsor_1pct_mean_{horizon}d"] = winsorized_mean(values)
            rows.append(row)
    return pd.DataFrame(rows)


def mechanism_spread_table(sort_table: pd.DataFrame) -> pd.DataFrame:
    """Return Q5-minus-Q1 spreads for every proxy and period."""

    rows: list[dict[str, object]] = []
    for (proxy, period), group in sort_table.groupby(["proxy", "period"], sort=True):
        indexed = group.set_index("bucket")
        if "Q1" not in indexed.index or "Q5" not in indexed.index:
            continue
        low = indexed.loc["Q1"]
        high = indexed.loc["Q5"]
        row: dict[str, object] = {
            "proxy": proxy,
            "period": period,
            "q1_n": int(low["n"]),
            "q5_n": int(high["n"]),
        }
        for horizon in HORIZONS:
            for statistic in ("mean", "median", "winsor_1pct_mean"):
                column = f"{statistic}_{horizon}d"
                row[f"q5_minus_q1_{column}"] = float(high[column] - low[column])
        rows.append(row)
    return pd.DataFrame(rows)


def structure_split_table(events: pd.DataFrame) -> pd.DataFrame:
    """Summarize venue and within-small size splits under the canonical signal."""

    rows: list[dict[str, object]] = []
    for split_column in ("small_subbucket", "exchange"):
        if split_column not in events.columns:
            continue
        valid = events.dropna(subset=[split_column])
        grouped_items = [
            (period, str(group_name), group)
            for (period, group_name), group in valid.groupby(
                ["period", split_column], sort=True
            )
        ] + [
            ("pooled", str(group_name), group)
            for group_name, group in valid.groupby(split_column, sort=True)
        ]
        for period, group_name, group in grouped_items:
            row: dict[str, object] = {
                "split": split_column,
                "period": period,
                "group": group_name,
                "n": int(len(group)),
                "median_mktcap": float(group["mktcap"].median()),
                "median_adv20_usd_pre": float(group["adv20_usd_pre"].median()),
            }
            for horizon in HORIZONS:
                values = group[f"ret_{horizon}d_next_open_to_close"]
                row[f"mean_{horizon}d"] = float(values.mean())
                row[f"median_{horizon}d"] = float(values.median())
                row[f"winsor_1pct_mean_{horizon}d"] = winsorized_mean(values)
            rows.append(row)
    return pd.DataFrame(rows)
