# Academic CV Description

## Recommended version

**Small-Cap Volume Regime-Shift Event Alpha (CRSP, 2000–2025)**

- Built a reproducible event-study pipeline for dormant-to-active volume transitions in U.S. small-cap equities, enforcing lagged signal inputs, next-session-open entry, exact market-session horizons, and pre-event ADV measurement.
- Audited 929,294 saved events across five subperiods: 20-session raw means ranged from 1.74% to 13.94%, while non-positive medians and materially lower 1% winsorized means showed that performance was strongly right-skewed rather than broadly distributed.
- Diagnosed concentration in the microcap-small segment and tested 40–100 bp return haircuts, liquidity filters, and 0.5%–2% ADV participation; concluded that tail dependence and entry-cohort capacity, rather than predictive mean alone, were the principal implementation constraints.

## One-line version

Developed and audited a CRSP small-cap volume regime-shift event study with point-in-time feature timing, next-open execution labels, robust distribution summaries, and ADV-based capacity diagnostics, showing that the apparent post-event drift was highly right-skewed and microcap-concentrated.

## Interview caveat

Describe the output as an **event study**, not a portfolio backtest. Be explicit that the public evidence uses price returns without delisting adjustments, fixed cost haircuts rather than a full execution model, and an entry-cohort capacity diagnostic rather than deployable AUM.
