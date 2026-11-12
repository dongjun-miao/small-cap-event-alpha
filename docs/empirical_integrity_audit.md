# Empirical Integrity Audit

## Scope and identity

The identified source is the canonical `QR_Project_01_Small_Cap_Event_Alpha` project. Its v2 notebooks, `src/event_alpha` package, pipeline, tests, and five aggregate result tables all describe the small-cap volume regime-shift event study. The separate state-dependent Ridge/tree project and root-level ML cross-sectional-alpha outputs were excluded.

This audit is limited to the code and artifacts available at packaging time. The five private `*_research_v1.csv` inputs and generated PERMNO-level event samples were not present, so this is not a raw-data replication.

## Event observability and timing

**Verified in code**

- `vol_prev` is the one-session lag of volume.
- `vol_ma5_pre` and `vol_ma20_pre` are rolling means of lagged volume; event-day volume cannot enter either baseline.
- `ADV20_pre` is based on lagged `abs(close) × volume` through `t-1`.
- `close_pos` and daily market-cap rank require event-day information, so the signal is not observable until after the close of `t`.
- Entry is the open of `t+1`; exit is the close of `t+h` for 5, 10, and 20 sessions.
- Entry and exit are accepted only when their market-session identifiers equal the required offsets. Missing security rows or trading halts invalidate the label rather than silently changing the horizon.

**Qualification**

The label spans from the next open to a later close and is a price return. It is not a CRSP total return and does not incorporate distributions or delisting returns.

## Universe, survivorship, and data provenance

The code requires unique `(permno, date)` rows and computes daily market-cap percentiles from every valid row supplied for that date. It does not itself reconstruct CRSP share-code, exchange-code, or point-in-time eligibility filters. Those filters are assumed to have been applied in the private preprocessed panel.

Because the private inputs and their preprocessing lineage were unavailable:

- absence of survivorship bias is **not independently verified**;
- security-type and exchange eligibility are **not independently verified**;
- price and share adjustment conventions are **not independently verified**;
- market-cap input units are preserved but cannot be certified from public artifacts.

The public materials must not claim these items were audited end to end.

## File boundaries and missing observations

Each five- or six-year input file is processed independently. The first 20 observations per security in each file are a warm-up region, and final observations without complete horizons are censored. This is explicit and prevents look-ahead across file boundaries, but it also excludes otherwise valid events near boundaries.

The session map is constructed from dates present in each file. Exact-session validation protects against missing security observations, but a market-wide missing date in the entire input file would not be detectable without an external trading calendar.

## Overlapping events and inference

The event sample can contain repeated signals for the same security and overlapping 5/10/20-session holding windows. Saved outputs summarize event-level observations; they do not form a non-overlapping sample, cluster standard errors, or model an overlapping portfolio.

No standard errors, confidence intervals, or p-values are present in the saved tables. The public repository therefore makes descriptive empirical claims only and does not claim statistical significance.

## Return distribution and extreme winners

The saved subperiod evidence consistently separates raw mean, median, 1% winsorized mean, and hit rate. For 20-session labels:

- raw means are 1.74%–13.94% across the five periods;
- medians are 0.00% or negative;
- hit rates are 44.48%–48.72%;
- 1% winsorized means are 0.10%–3.14%.

The post-2020 raw mean is 13.94%, versus a −1.08% median and 3.14% 1% winsorized mean. Within the post-2020 microcap-small segment, the corresponding values are 22.55%, −2.87%, and 9.99%. This is strong artifact-level evidence that a small positive tail materially drives the mean.

The public package does not contain event-level returns, so it cannot show a histogram, estimate higher moments, identify individual winners, or audit whether specific observations are data errors. The robustness figure therefore uses genuine aggregate distribution-sensitive statistics rather than a fabricated distribution.

## Liquidity, costs, and capacity

**Verified**

- Liquidity is measured before the event using lagged ADV20.
- Capacity tables apply 0.5%, 1%, and 2% ADV participation.
- The ADV70 subset retains the most liquid 30% of events within each subperiod.
- A signal-date cohort is constrained by its least-liquid member under equal weights.

**Not a trading model**

- The 40 bp and 100 bp scenarios are fixed return haircuts.
- Bid-ask spreads, nonlinear impact, commissions, borrow, partial fills, and exit liquidity are not modeled.
- Portfolio turnover, overlapping positions, capital reuse, and exposure constraints are not modeled.
- Reported capacity is entry-cohort notional, not deployable fund AUM.

At 1% participation, median cohort capacity is only $4.2k–$8.0k for all events and $31k–$113k for ADV70 events. Implementation capacity is therefore a binding limitation.

## Legacy reconciliation

The excluded v1 notebooks used inconsistent file-wide versus daily size sorts, rolling-window conventions, and exit definitions. The v2 pipeline centralizes the definition in `src/event_alpha/core.py`. Legacy headline results are not used.

## Audit conclusion

**CONDITIONAL GO for public release.** The package is suitable as a transparent empirical research portfolio if it retains the current caveats. It is not suitable for claims of raw-data replication, statistical significance, total-return alpha, production-grade net performance, or institutional scalability. Before claiming full reproducibility, rerun the canonical pipeline in the licensed environment and compare all regenerated aggregate tables against the recorded evidence.
