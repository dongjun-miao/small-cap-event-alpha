# Data Access and Licensing

## What is not distributed

This repository does not include:

- CRSP or WRDS daily security-level data;
- derived PERMNO/date event samples;
- ticker-level extracts or reconstructed panels;
- WRDS usernames, API keys, tokens, passwords, or connection files;
- institution-specific query code or cached downloads.

The public CSVs contain only aggregate research summaries.

## Obtaining data

Full reproduction requires lawful access to CRSP through WRDS or another licensed provider and a private preprocessing step that creates the schema in `configs/data_contract.yaml`. Users are responsible for complying with their institution's subscription agreement, data-retention policy, and rules governing derived outputs.

This repository does not grant rights to CRSP/WRDS content. The fact that an aggregate table is included should not be treated as legal advice about a particular license. The author should confirm that the planned public aggregate disclosures are permitted under the applicable agreement before publishing.

## Safe workflow

1. Keep licensed input files outside the Git working tree.
2. Pass their directory to `scripts/run_research.py --data-dir`.
3. Write intermediate event samples only to ignored `output/` storage.
4. Review aggregate tables for disclosure compliance before copying them into `results/tables/`.
5. Run the public-release scan and inspect `git status` before any commit.

Never commit credentials, local connection files, query caches, security-level rows, or original vendor documentation.

## Software license

No open-source software license has been selected in this export. Under the default legal position, public visibility does not itself grant reuse rights. The author should select and add a code license separately from any data license after deciding the intended permissions.
