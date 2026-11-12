# Synthetic smoke test

`synthetic_smoke_test.py` constructs a small in-memory panel with no CRSP data. It verifies that a deliberately created dormant-to-active event is identified only after lagged volume history is available and that its five-session label enters at the following session's open.

It is a software contract check, not evidence about returns or performance.

```bash
python examples/synthetic_smoke_test.py
```
