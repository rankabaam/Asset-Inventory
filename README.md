# Asset Inventory Demo

A compact, independently written inventory-and-reconciliation demonstration built with fictional records.

This portfolio application combines a basic asset register and observation records into an offline review-oriented HTML dashboard.

> **Portfolio boundary:** No employer data, proprietary device information, live locations, vendor systems, production IDs, or internal reports are included.

## Run locally

Requires Python 3.10+ with no third-party dependencies.

```bash
python src/inventory.py --assets sample_data/assets.csv --observations sample_data/observations.csv --as-of 2026-10-18 --output output/assets.html
python -m unittest discover -s tests -v
```

[View the sample HTML output](demo/preview.html) (download and open locally).

## Demonstrated capabilities

- Parse and validate two fictional CSV record types
- Reconcile asset observations to an asset register
- Clearly distinguish verified, review, outdated, unknown, and archived status
- Search and inspect an offline HTML dashboard
- Regression-test status precedence and incomplete records

Any freshness threshold or status rule here is **invented for this demo**, not borrowed from an actual operational system. An unknown state never automatically implies an asset is missing.

## Contents

| Path | Description |
|---|---|
| `src/inventory.py` | Import, validation, status model, offline report |
| `sample_data/` | Entirely fictional asset and observation records |
| `demo/preview.html` | Generated sample output |
| `tests/test_inventory.py` | Unit tests |

This repository does not communicate with any live device, location provider, employer system, or production asset database.