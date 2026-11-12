# Results Evidence Ledger

## Evidence hierarchy

1. **Saved aggregate evidence:** five canonical CSVs in `results/tables/`. Numeric claims below are directly traceable to these files.
2. **Executable research contract:** `src/event_alpha/` and contract tests define event formation, labels, summaries, and capacity calculations.
3. **Unavailable evidence:** licensed input panels and security-level event samples. Claims requiring observation-level inspection remain unverified.

No result in this document is reconstructed from the separate state-dependent ML-alpha project.

## Event counts and 20-session results

Source: `a_small_subperiod_summary.csv`.

| Period | Events | Valid 20d | Mean | Median | 1% winsorized mean | Hit rate | Mean − 100 bp |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2000–2004 | 249,220 | 195,457 | 3.8955% | 0.0000% | 2.0914% | 48.5319% | 2.8955% |
| 2005–2009 | 208,194 | 174,470 | 1.7419% | −0.7937% | 0.2889% | 45.4961% | 0.7419% |
| 2010–2014 | 165,976 | 144,063 | 3.2493% | −0.0080% | 1.1483% | 48.7183% | 2.2493% |
| 2015–2019 | 138,272 | 123,453 | 4.4555% | −0.8303% | 0.1035% | 45.2196% | 3.4555% |
| 2020–2025 | 167,632 | 149,916 | 13.9377% | −1.0775% | 3.1439% | 44.4762% | 12.9377% |
| **Total** | **929,294** | **787,359** | — | — | — | — | — |

The fixed-cost column is arithmetic `mean − 0.01`. It is not a portfolio backtest.

## Horizon evidence

The saved table also reports 5- and 10-session next-open labels:

- 5-session raw means range from 0.6915% to 3.7091%;
- 10-session raw means range from 0.9817% to 7.6848%;
- 5-session medians range from 0.0000% to −0.3382%;
- 10-session medians range from 0.0000% to −0.6897%.

The 2015–2019 and 2020–2025 5-session 1% winsorized means are negative (−0.1050% and −0.1253%), despite positive raw means. This reinforces the tail-dependence finding.

## Within-small size concentration

Source: `a_small_structure_splits.csv`.

| Sample | Segment | N | Median ADV20_pre | Mean 20d | Median 20d | 1% winsorized mean 20d |
|---|---|---:|---:|---:|---:|---:|
| Pooled | Microcap-small | 486,725 | $67,861 | 8.4215% | −1.0638% | 1.9965% |
| Pooled | Upper-small | 442,569 | $212,176 | 2.0465% | −0.1359% | 0.4331% |
| 2020–2025 | Microcap-small | 85,156 | $131,998 | 22.5540% | −2.8661% | 9.9872% |
| 2020–2025 | Upper-small | 82,476 | $315,514 | 4.3026% | −0.2009% | 0.1841% |

Market-cap values are not translated into dollars in the public narrative because their source units are not documented in the public input lineage.

## Mechanism and liquidity evidence

Sources: `a_small_mechanism_sorts.csv` and `a_small_mechanism_spreads.csv`.

Mechanism quintiles are assigned within subperiod. Their spreads do not support a stable one-dimensional “lower ADV is always better” account. For example:

- pooled ADV Q5−Q1 20-day mean: −0.9734%;
- pooled ADV Q5−Q1 20-day median: −0.4973%;
- pooled ADV Q5−Q1 20-day winsorized mean: −3.3631%;
- 2020–2025 ADV Q5−Q1 raw mean: +9.8560%, but median: −2.6404% and winsorized mean: −2.3064%.

The sign reversal between raw and robust summaries in the recent period is further evidence that extreme winners dominate simple mean comparisons. These are exploratory sorts, not causal mechanism tests.

## Capacity evidence

Source: `a_small_capacity_summary.csv`.

Median equal-weight entry-cohort capacity at 1% ADV participation:

| Period | All events | ADV70 events |
|---|---:|---:|
| 2000–2004 | $4,155 | $31,236 |
| 2005–2009 | $5,530 | $63,237 |
| 2010–2014 | $5,460 | $73,726 |
| 2015–2019 | $6,824 | $92,364 |
| 2020–2025 | $8,027 | $113,311 |

ADV70 improves this narrow cohort diagnostic by dropping less-liquid observations; it does not establish that filtered returns remain attractive, nor does it represent portfolio AUM.

## Claims deliberately omitted

- no Sharpe ratio, annualized portfolio return, drawdown, or factor alpha;
- no p-value or significance claim;
- no live, holdout, or production performance claim;
- no assertion that the fixed 100 bp haircut is achievable;
- no observation-level distribution plot, because the required event sample is unavailable.
