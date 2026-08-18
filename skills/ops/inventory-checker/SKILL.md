---
name: inventory-checker
description: "Compare inventory levels against reorder thresholds and generate restock recommendations."
version: 1.0.0
author: Nuvel
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: []
  commands: [python3]
  pip_packages: []
metadata:
  hermes:
    tags: [inventory, supply-chain, ops, enterprise]
---
# Inventory Checker

Read an inventory CSV, compare each item's quantity against its reorder
threshold, flag low-stock items, and recommend reorder quantities and costs.

## When to use

- Run a periodic stock check to see what needs reordering.
- Produce a restock report for a purchasing/ops workflow.
- Surface only the critical/out-of-stock items for an urgent alert.

## Input

A CSV with a header row and these columns:

| Column              | Meaning                                  |
|---------------------|------------------------------------------|
| `item_id`           | Unique item identifier                   |
| `name`              | Item display name                        |
| `quantity`          | Current quantity on hand                 |
| `reorder_threshold` | Level at or below which to reorder       |
| `unit_cost`         | Cost per unit (used for reorder cost)    |

## Process

For each item the status is derived from quantity vs. threshold:

| Status   | Condition                                  |
|----------|--------------------------------------------|
| `OUT`    | quantity <= 0                              |
| `CRITICAL` | quantity < threshold / 2                  |
| `LOW`    | quantity < threshold (not CRITICAL/OUT)    |
| `OK`     | quantity >= threshold                      |

Reorder quantity uses a reorder-to-max policy: bring stock up to `2 x threshold`.
`reorder_cost = reorder_qty * unit_cost`. `OK` items get a reorder quantity of 0.

## Output

- `restock_report.csv` (or `--output` path) — every item with status, reorder
  quantity, and reorder cost.
- An alert summary on stdout, sorted by severity, plus totals and estimated
  reorder cost.

## Usage

```bash
python scripts/inventory_checker.py inventory.csv --min-stock 10
```

Options:

- `--min-stock N` — fallback threshold for rows missing `reorder_threshold` (default 10).
- `--output PATH` — restock report CSV path (default `restock_report.csv`).
- `--alert` — print only `CRITICAL` and `OUT` items to stdout.

## Edge cases

| Situation                        | Behaviour                                       |
|----------------------------------|-------------------------------------------------|
| Missing/blank numeric value      | Treated as `0`                                  |
| Negative `quantity`              | Clamped to `0`, warning recorded                |
| Missing `reorder_threshold`      | Falls back to `--min-stock`, warning recorded   |
| Zero threshold                   | Only `OUT` items are flagged                    |
| Negative `unit_cost`             | Clamped to `0`, warning recorded                |
| Missing `item_id`                | Placeholder `UNKNOWN-<row>`, warning recorded   |
| Empty file / no data rows        | Exits non-zero with a stderr message            |
| File not found                   | Exits with an argparse error                    |

The full report CSV always lists every item; the stdout summary shows only
flagged (or, with `--alert`, only critical/out) items.
