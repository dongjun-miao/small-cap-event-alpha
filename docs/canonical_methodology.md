# Methodology and Data Contract

## 1. Input universe

The pipeline expects a point-in-time CRSP research panel with unique
`(permno, date)` rows. At minimum it uses:

`permno, date, mktcap, volume, open, high, low, close`.

`ticker`, `exchange`, and `shrout` are optional reporting fields. The private
source panel is expected to have already applied the intended security-type and
exchange eligibility rules. The repository does not redistribute CRSP data.

Each five-year input file is processed independently. The first 20 observations
of each security in a file are a warm-up region and cannot form a signal; the
last observations without a complete forward horizon receive missing labels.
This prevents silent contamination across file boundaries.

## 2. Daily size classification

For each market date, eligible securities are ranked by market capitalization.
Daily percentiles define:

- small: percentile <= 1/3;
- mid: 1/3 < percentile <= 2/3;
- large: percentile > 2/3.

The small tercile is split again for diagnostics:

- microcap-small: percentile <= 1/6;
- upper-small: 1/6 < percentile <= 1/3.

This replaces the legacy implementation that used a single tercile cut across
an entire five-year file.

## 3. Event definition

For security `i` on formation date `t`, define using only observations through
`t-1`:

```text
vol_prev      = volume[i, t-1]
vol_ma5_pre   = mean(volume[i, t-5:t-1])
vol_ma20_pre  = mean(volume[i, t-20:t-1])
close_pos     = (close[i,t] - low[i,t]) / (high[i,t] - low[i,t] + eps)
```

The volume regime-shift event is:

```text
vol_prev < vol_ma5_pre
vol_prev < 0.8 * vol_ma20_pre
volume[i,t] >= 1.8 * vol_prev
close_pos >= 0.6
```

`A_small` is true when the event occurs in the daily small-cap tercile.

## 4. Forward-return label

For an event formed on market session `t` and horizon `h`:

```text
entry = open at t+1
exit  = close at t+h
return = exit / entry - 1
```

The current horizons are 5, 10, and 20 sessions. Entry and exit are accepted
only if the security observations map to exactly `session_id+1` and
`session_id+h`. A halt or missing row therefore invalidates the label instead
of changing the economic horizon.

The label is a price return. It does not include dividends and is not fully
delisting-aware. This is a known limitation and must be resolved before making
claims about production-grade total returns.

## 5. Cost stress

The aggregate tables apply a simple event-level haircut:

```text
stressed_mean = gross_event_mean - total_cost_bps / 10,000
```

The 40 bp and 100 bp values are sensitivity scenarios, not calibrated execution
models. They do not model nonlinear impact, spread variation, partial fills, or
overlapping portfolio turnover.

## 6. Liquidity and entry-cohort capacity

Pre-event dollar ADV is:

```text
ADV20_pre = mean(abs(close) * volume over t-20:t-1)
```

The ADV70 subset retains events at or above the 70th percentile of pre-event
ADV within each subperiod.

For an equal-weight signal-date cohort at participation rate `p`, the reported
NAV capacity is:

```text
cohort_capacity = number_of_events * min(p * ADV20_pre)
```

This is a conservative entry-cohort diagnostic. It is not a full overlapping
holdings simulation and should not be described as production portfolio AUM.

## 7. Robustness and mechanism tables

Every subperiod table reports raw mean, median, 1% winsorized mean, hit rate,
and cost-stressed means. Mechanism proxies are assigned to quintiles within
each subperiod before pooled summaries are calculated. This reduces the risk
that secular growth in market capitalization or dollar volume drives the sort.

The primary mechanism conclusion is deliberately modest: the event identifies
pre-event dormancy, but the strongest forward-return differences are associated
with the microcap tail and event-day trading intensity. A simple "lower ADV is
always better" mechanism is not supported.
