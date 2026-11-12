# Public Release Checklist

## Completed in this export

- [x] Canonical project identified and separated from the State-Dependent ML Alpha project.
- [x] Original source files and five aggregate result tables preserved byte-for-byte.
- [x] Legacy v1 notebooks excluded from the public package.
- [x] Canonical v2 notebooks inspected: no embedded outputs or execution counts.
- [x] CRSP/WRDS security-level data and event extracts excluded.
- [x] Original `.git` directory and Git history excluded.
- [x] Unrelated ML results, CN data, and an unrelated local token file excluded.
- [x] Event observability, next-open entry, exact-session exit, and lagged ADV documented.
- [x] Survivorship, delisting, overlap, cost, and capacity limitations disclosed.
- [x] Every headline number linked to a saved aggregate table.
- [x] Synthetic contract tests and saved-artifact integrity tests included.
- [x] Figures generated only from verified method definitions or aggregate tables.
- [x] Public package scanned for absolute local paths and credential-like terms.
- [x] ZIP layout checked so `README.md` is at the archive root.
- [x] No GitHub push performed.

## Author decisions before publishing

- [ ] Choose and add a software license.
- [ ] Confirm with the applicable CRSP/WRDS agreement that the aggregate tables may be made public.
- [ ] Review the repository description and CV wording for personal preference.
- [ ] If claiming full reproducibility, rerun in the licensed environment and compare regenerated table hashes with `docs/source_manifest_sha256.csv`.
- [ ] Optionally add a tagged release and DOI after repository review.

## Claims that must remain qualified

- Event-level price returns are not delisting- or dividend-adjusted total returns.
- The private universe-construction lineage was unavailable for this audit.
- Fixed cost haircuts are not an execution simulation.
- Entry-cohort capacity is not portfolio AUM.
- Overlapping-event dependence and statistical significance were not estimated.
- The repository is empirical research, not a live or production trading strategy.

## Release decision

**CONDITIONAL GO.** The export is technically clean and public-safe subject to the author's licensing confirmation. Full raw-data reproducibility remains unverified because licensed inputs and event-level outputs were unavailable.
