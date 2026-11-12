"""Canonical signal and label definitions.

The functions in this module are the single source of truth used by every
notebook and command-line script in the repository.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


HORIZONS = (5, 10, 20)
EPS = 1e-12

REQUIRED_COLUMNS = {
    "permno",
    "date",
    "mktcap",
    "volume",
    "open",
    "high",
    "low",
    "close",
}


def validate_input_panel(frame: pd.DataFrame) -> None:
    """Validate the minimum point-in-time panel contract."""

    missing = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if frame.duplicated(["permno", "date"]).any():
        raise ValueError("Input contains duplicate (permno, date) rows")
    if frame["date"].isna().any():
        raise ValueError("Input contains missing dates")


def _daily_size_classification(
    frame: pd.DataFrame,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Assign deterministic daily market-cap percentiles and terciles.

    Ranking is performed within each date across the complete eligible input
    universe. ``method='first'`` resolves exact market-cap ties by the stable
    input order, which is sorted by date and PERMNO before this function runs.
    """

    valid = frame["mktcap"].notna() & (frame["mktcap"] > 0)
    percentile = pd.Series(np.nan, index=frame.index, dtype="float64")
    percentile.loc[valid] = (
        frame.loc[valid]
        .groupby("date", sort=False)["mktcap"]
        .rank(method="first", pct=True)
    )
    bucket = pd.Series(pd.NA, index=frame.index, dtype="string")
    bucket.loc[percentile <= 1.0 / 3.0] = "small"
    bucket.loc[(percentile > 1.0 / 3.0) & (percentile <= 2.0 / 3.0)] = "mid"
    bucket.loc[percentile > 2.0 / 3.0] = "large"
    small_subbucket = pd.Series(pd.NA, index=frame.index, dtype="string")
    small_subbucket.loc[percentile <= 1.0 / 6.0] = "microcap_small"
    small_subbucket.loc[
        (percentile > 1.0 / 6.0) & (percentile <= 1.0 / 3.0)
    ] = "upper_small"
    return percentile, bucket, small_subbucket


def _lagged_rolling_mean(
    values: pd.Series,
    groups: pd.Series,
    window: int,
) -> pd.Series:
    lagged = values.groupby(groups, sort=False).shift(1)
    return (
        lagged.groupby(groups, sort=False)
        .rolling(window=window, min_periods=window)
        .mean()
        .reset_index(level=0, drop=True)
        .sort_index()
    )


def _add_forward_labels(
    frame: pd.DataFrame,
    horizons: Iterable[int],
) -> None:
    """Add next-open-entry to horizon-close price returns.

    For an event formed at session ``t``, a horizon ``h`` label enters at the
    open of session ``t+1`` and exits at the close of session ``t+h``. Labels
    are valid only when both observations are exactly the required number of
    market sessions ahead. This prevents trading halts or missing rows from
    silently changing the holding period.

    These are price returns, not dividend- or delisting-adjusted total returns.
    That limitation is disclosed in the methodology and README.
    """

    group = frame.groupby("permno", sort=False)
    entry_open = group["open"].shift(-1)
    entry_session = group["session_id"].shift(-1)
    entry_valid = (
        entry_open.notna()
        & (entry_open > 0)
        & entry_session.eq(frame["session_id"] + 1)
    )
    frame["entry_open_t1"] = entry_open
    frame["entry_valid"] = entry_valid

    for horizon in sorted({int(value) for value in horizons}):
        if horizon <= 0:
            raise ValueError("Forward-return horizons must be positive")
        exit_close = group["close"].shift(-horizon)
        exit_session = group["session_id"].shift(-horizon)
        valid = (
            entry_valid
            & exit_close.notna()
            & (exit_close > 0)
            & exit_session.eq(frame["session_id"] + horizon)
        )
        output = pd.Series(np.nan, index=frame.index, dtype="float64")
        output.loc[valid] = (
            exit_close.loc[valid] / entry_open.loc[valid] - 1.0
        )
        frame[f"ret_{horizon}d_next_open_to_close"] = output
        frame[f"label_valid_{horizon}d"] = valid


def add_canonical_features(
    frame: pd.DataFrame,
    *,
    horizons: Iterable[int] = HORIZONS,
) -> pd.DataFrame:
    """Return a canonical panel with signal, liquidity, and return features."""

    work = frame.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    validate_input_panel(work)
    work = work.sort_values(["date", "permno"], kind="stable").reset_index(drop=True)

    unique_dates = pd.Index(work["date"].drop_duplicates().sort_values())
    session_map = pd.Series(
        np.arange(len(unique_dates), dtype=np.int32),
        index=unique_dates,
    )
    work["session_id"] = work["date"].map(session_map).astype("int32")

    # PERMNO-contiguous layout is faster and is required for group shifts.
    work = work.sort_values(["permno", "date"], kind="stable").reset_index(drop=True)
    groups = work["permno"]
    group = work.groupby("permno", sort=False)

    work["vol_prev"] = group["volume"].shift(1)
    work["vol_ma5_pre"] = _lagged_rolling_mean(work["volume"], groups, 5)
    work["vol_ma20_pre"] = _lagged_rolling_mean(work["volume"], groups, 20)
    work["close_pos"] = (
        (work["close"] - work["low"])
        / (work["high"] - work["low"] + EPS)
    )
    work["intraday_range"] = (
        (work["high"] - work["low"])
        / (work["close"].abs() + EPS)
    )

    dollar_volume = work["close"].abs() * work["volume"]
    work["adv20_usd_pre"] = _lagged_rolling_mean(dollar_volume, groups, 20)
    if "shrout" in work.columns:
        valid_shares = work["shrout"].where(work["shrout"] > 0)
        work["turnover"] = work["volume"] / valid_shares
        work["turnover_ma20_pre"] = _lagged_rolling_mean(
            work["turnover"], groups, 20
        )

    work["vol_prev_to_ma20"] = (
        work["vol_prev"] / (work["vol_ma20_pre"] + EPS)
    )
    work["volume_to_ma20"] = (
        work["volume"] / (work["vol_ma20_pre"] + EPS)
    )
    work["volume_to_prev"] = np.where(
        work["vol_prev"] > 0,
        work["volume"] / work["vol_prev"],
        np.nan,
    )

    # Daily cross-sectional size ranks use the full eligible universe.
    (
        work["mktcap_daily_percentile"],
        work["size_bucket"],
        work["small_subbucket"],
    ) = _daily_size_classification(work)
    work["a_volume_regime"] = (
        work["vol_prev"].lt(work["vol_ma5_pre"])
        & work["vol_prev"].lt(0.8 * work["vol_ma20_pre"])
        & work["volume"].ge(1.8 * work["vol_prev"])
        & work["close_pos"].ge(0.6)
    )
    work["a_small"] = work["a_volume_regime"] & work["size_bucket"].eq("small")

    _add_forward_labels(work, horizons)
    return work


def build_event_sample(
    frame: pd.DataFrame,
    *,
    horizons: Iterable[int] = HORIZONS,
) -> pd.DataFrame:
    """Build the canonical panel and retain only A_small event rows."""

    panel = add_canonical_features(frame, horizons=horizons)
    base_columns = [
        "permno",
        "date",
        "session_id",
        "mktcap",
        "volume",
        "open",
        "high",
        "low",
        "close",
        "size_bucket",
        "small_subbucket",
        "mktcap_daily_percentile",
        "a_volume_regime",
        "a_small",
        "vol_prev",
        "vol_ma5_pre",
        "vol_ma20_pre",
        "adv20_usd_pre",
        "close_pos",
        "intraday_range",
        "vol_prev_to_ma20",
        "volume_to_ma20",
        "volume_to_prev",
        "entry_open_t1",
        "entry_valid",
    ]
    optional = [
        name
        for name in ("ticker", "exchange", "shrout", "turnover", "turnover_ma20_pre")
        if name in panel.columns
    ]
    label_columns: list[str] = []
    for horizon in sorted({int(value) for value in horizons}):
        label_columns.extend(
            [
                f"ret_{horizon}d_next_open_to_close",
                f"label_valid_{horizon}d",
            ]
        )
    return panel.loc[panel["a_small"], base_columns + optional + label_columns].copy()
