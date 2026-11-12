# Figure provenance

- `event_definition_schematic.png` is generated from the canonical event and timing contract in `src/event_alpha/core.py`.
- `event_return_robustness.png` uses only `a_small_subperiod_summary.csv`.
- `liquidity_capacity_sensitivity.png` uses only `a_small_capacity_summary.csv`.

Regenerate all figures with:

```bash
python scripts/build_public_figures.py
```

No observation-level distribution plot is included because the licensed event sample was unavailable. The robustness chart uses genuine mean, median, and 1% winsorized aggregate statistics rather than inventing a return distribution.
