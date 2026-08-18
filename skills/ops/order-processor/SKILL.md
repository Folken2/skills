---
name: order-processor
description: "Advance orders through a validated fulfillment state machine and log every transition."
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
    tags: [orders, fulfillment, operations, enterprise]
---
# Order Processor

Process orders through a defined fulfillment state machine, one stage per run,
with a validation gate at each transition. Every order's outcome is recorded in
a processing log.

## State machine

```
received --validate--> validated --fulfill--> fulfilled --ship--> shipped
```

Each `--stage` advances only the orders currently in the correct source state:

| Stage      | Transition               | Gate                                   |
|------------|--------------------------|----------------------------------------|
| `validate` | received -> validated    | requires customer, item, quantity > 0  |
| `fulfill`  | validated -> fulfilled   | requires an already-validated order    |
| `ship`     | fulfilled -> shipped     | requires an already-fulfilled order    |

Orders not in the source state are skipped (reported, unchanged). Orders that
fail the validate gate stay in `received` and are reported as errors.

## Input

A CSV with a header row and these columns:

| Column      | Meaning                                        |
|-------------|------------------------------------------------|
| `order_id`  | Unique order identifier                        |
| `customer`  | Customer name/id                               |
| `item`      | Item ordered                                   |
| `quantity`  | Quantity ordered (must be > 0 to validate)     |
| `status`    | Current stage (received/validated/fulfilled/shipped) |

## Output

- Updated orders CSV (default `<input>_updated.csv`) with new `status` values.
- `processing_log.csv` — one row per order: `order_id, from_status, to_status,
  result (advanced|skipped|error), detail`.
- A summary on stdout with counts of advanced / errors / skipped.

## Usage

```bash
python scripts/order_processor.py orders.csv --stage validate
```

Run stages in sequence to move orders end-to-end:

```bash
python scripts/order_processor.py orders.csv          --stage validate --output o1.csv
python scripts/order_processor.py o1.csv              --stage fulfill  --output o2.csv
python scripts/order_processor.py o2.csv              --stage ship     --output o3.csv
```

Options: `--output PATH` (updated CSV), `--log PATH` (processing log).

## Edge cases

| Situation                          | Behaviour                                        |
|------------------------------------|--------------------------------------------------|
| Blank/unknown `status`             | Treated as `received`                            |
| Order already at target stage      | Skipped with an "already at target stage" note   |
| Order not in the source stage      | Skipped with a "not eligible" note               |
| `validate` with missing customer/item | Left in `received`, reported as an error       |
| Non-positive or non-numeric quantity  | Fails the validate gate, reported as an error  |
| Missing `order_id`                 | Logged as `UNKNOWN`                              |
| Input CSV lacks a `status` column  | A `status` column is added to the output         |
| Empty file / no data rows          | Exits non-zero with a stderr message             |
| File not found                     | Exits with an argparse error                     |
