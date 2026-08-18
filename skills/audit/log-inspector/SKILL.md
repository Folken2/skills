---
name: log-inspector
description: "Parse structured logs, detect error-frequency spikes, and flag compliance anomalies."
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
    tags: [audit, compliance, logging, enterprise]
---
# Log Inspector

Parse structured application logs, filter by severity, detect error-frequency
spikes within a sliding time window, and surface simple compliance signals.
Prints a summary to stdout and writes a detailed JSON report.

## When to use

- Audit an application log for bursts of errors around an incident.
- Screen logs for sensitive data (passwords, tokens, SSNs) written at low severity.
- Produce a machine-readable inspection report to gate a CI/audit step.

## Input

A JSONL file (one JSON object per line) or a CSV, with these fields/columns:

| Field       | Meaning                                              |
|-------------|------------------------------------------------------|
| `timestamp` | ISO 8601 (`2026-08-18T09:40:00Z`) or Unix epoch secs |
| `level`     | DEBUG / INFO / WARNING / ERROR / CRITICAL            |
| `source`    | Component or service name                            |
| `message`   | Log message text                                     |

Format is auto-detected from the extension (`.jsonl`/`.json` vs `.csv`) and by
sniffing the first line.

## Checks

- **Error spikes** — a sliding window (`--window`) over `ERROR`+ records; any
  window containing at least `--spike-threshold` errors is reported. Overlapping
  windows are collapsed to the peak of each burst.
- **Compliance signals** — messages containing sensitive markers (`password`,
  `ssn`, `credit card`, `secret`, `api_key`, `token`) logged at `INFO`/`DEBUG`.
- **Malformed lines** — unparseable rows are counted and reported.

## Output

- stdout summary: level counts, detected spikes, compliance hits, malformed count.
- `--report` JSON (default `log_inspection_report.json`) with full detail.
- Exit code: `0` clean, `2` if any spike or compliance hit was found, `1` on
  empty/no-record input. Use the exit code to gate an audit pipeline.

## Usage

```bash
python scripts/log_inspector.py app.log --min-severity ERROR --window 5m
```

Options:

- `--min-severity LEVEL` — minimum level to analyze (default `ERROR`).
- `--window 30s|5m|1h` — sliding window for spike detection (default `5m`).
- `--spike-threshold N` — errors per window to count as a spike (default `5`).
- `--report PATH` — JSON report path.

## Edge cases

| Situation                            | Behaviour                                     |
|--------------------------------------|-----------------------------------------------|
| Unparseable JSON line / short CSV row| Counted as malformed, skipped                 |
| Missing/blank `level`                | Treated as `INFO`                             |
| Missing/unparseable `timestamp`      | Excluded from windowing; ERROR+ counted separately |
| Epoch vs ISO timestamps mixed        | Both parsed transparently                     |
| No records match `--min-severity`    | Summary still prints; spikes/compliance empty |
| Empty file / no records at all       | Exits `1` with a stderr message               |
| File not found                       | Exits with an argparse error                  |
| Invalid `--window` value             | Exits with an argparse error                  |
