---
name: payroll-processor
description: "Calculate net pay from timesheet CSV data and generate paystub and summary reports."
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
    tags: [payroll, hr, finance, enterprise]
---
# Payroll Processor

Process an employee timesheet CSV into per-employee paystubs and a consolidated
payroll report. For each employee the tool computes gross pay, applies tax, and
subtracts deductions to arrive at net pay.

## When to use

- You have a timesheet export and need to calculate everyone's pay for a period.
- You need auditable paystub files plus a machine-readable payroll summary.
- You want a quick net-pay total across a team or department.

## Input

A CSV file with a header row and the following columns:

| Column        | Meaning                                             |
|---------------|-----------------------------------------------------|
| `employee_id` | Unique identifier for the employee                  |
| `name`        | Employee display name                               |
| `hours_worked`| Hours worked during the pay period                  |
| `hourly_rate` | Pay rate per hour                                   |
| `tax_rate`    | Tax rate as a fraction (`0.20`) or percent (`20`)   |
| `deductions`  | Flat deductions to subtract (benefits, garnishments)|

## Process

1. Parse each row, tolerating messy cells (`$`, commas, blanks).
2. `gross_pay = hours_worked * hourly_rate`
3. `tax_amount = gross_pay * tax_rate` (percent values >1 are divided by 100)
4. `net_pay = gross_pay - tax_amount - deductions`
5. Write one paystub text file per employee, plus a summary CSV and JSON report.

## Output

Written to `--output-dir` (default `./paystubs`):

- `paystub_<employee_id>.txt` — human-readable paystub per employee.
- `payroll_summary.csv` — one row per employee with all computed fields.
- `payroll_report.json` — totals block plus full per-employee detail incl. warnings.

## Usage

```bash
python scripts/payroll_processor.py timesheet.csv --output-dir ./paystubs
```

Options:

- `--output-dir DIR` — where to write outputs (default `./paystubs`).
- `--quiet` — suppress the stdout summary table.

## Edge cases

| Situation                     | Behaviour                                              |
|-------------------------------|--------------------------------------------------------|
| Missing/blank numeric value   | Treated as `0.0`                                       |
| Negative `hours_worked`       | Clamped to `0.0`, warning recorded                     |
| Negative `hourly_rate`        | Clamped to `0.0`, warning recorded                     |
| Zero `hourly_rate`            | Allowed; yields `$0` gross, warning recorded           |
| Negative `deductions`         | Clamped to `0.0`, warning recorded                     |
| Negative `tax_rate`           | Clamped to `0.0`, warning recorded                     |
| `tax_rate` > 1 (e.g. `20`)    | Interpreted as a percent (`0.20`)                      |
| Net pay below zero            | Reported as-is with a warning (over-deducted)          |
| Missing `employee_id`         | Placeholder `UNKNOWN-<row>` assigned, warning recorded |
| Missing `name`                | Set to `Unknown`, warning recorded                     |
| Empty file / no data rows     | Exits non-zero with a message on stderr                |
| File not found                | Exits with an argparse error                           |

All warnings are surfaced in each paystub file and in `payroll_report.json`.
