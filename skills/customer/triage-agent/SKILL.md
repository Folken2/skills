---
name: triage-agent
description: "Classify customer requests by urgency and department and recommend a routing action."
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
    tags: [customer-service, triage, routing, enterprise]
---
# Customer Triage Agent

Classify an incoming customer request by **urgency** and **department**, then
recommend the next routing action. Classification is fully transparent and
rule-based — no ML model or network calls required.

## When to use

- Triage a support inbox or webhook payload before assignment.
- Batch-classify an exported CSV of tickets into urgency/department buckets.
- Produce a deterministic, auditable routing decision for each request.

## Input

- A single request string (`classify` mode), or
- A CSV with a text column (default `request`) for `batch` mode. Extra columns
  (customer id, timestamp, etc.) are preserved as metadata in the output.

## Classification

**Urgency** (first matching tier wins, highest first):

| Level    | Signals                                                    |
|----------|------------------------------------------------------------|
| critical | urgent, asap, outage, breach, security, data loss, legal   |
| high     | broken, crash, error, failed, blocked, charged twice       |
| medium   | slow, delay, issue, confused, unable, trouble              |
| low      | anything with no higher-tier signal                        |

**Department** (highest keyword score wins; ties broken by fixed priority
`billing > tech > account > support`):

| Department | Signals                                          |
|------------|--------------------------------------------------|
| billing    | invoice, charge, payment, refund, subscription   |
| tech       | error, bug, crash, api, outage, timeout, server  |
| account    | login, password, reset, locked out, 2fa, access  |
| support    | how do i, help, feature, cancel, documentation   |

## Routing

The recommended action combines urgency and department — e.g. critical items are
paged/escalated immediately, high items go to a senior agent within an hour,
medium items are queued same-day, and low items take the standard queue.

## Usage

Single request:

```bash
python scripts/triage_agent.py classify "My invoice is wrong" --verbose
```

Batch of requests:

```bash
python scripts/triage_agent.py batch requests.csv --text-column request --output triaged.csv
```

`classify` supports `--json` for full structured output including keyword scores.

## Edge cases

| Situation                         | Behaviour                                          |
|-----------------------------------|----------------------------------------------------|
| Empty / whitespace-only text      | `urgency=low`, `department=support`, flagged empty |
| No department keyword matches     | Defaults to `support`, warning recorded            |
| No urgency keyword matches        | Defaults to `low`                                  |
| Tie on department score           | Resolved by priority `billing>tech>account>support`|
| Missing text column in batch CSV  | Exits non-zero listing available columns           |
| Input CSV not found               | Exits non-zero with a stderr message               |
| Empty CSV (no data rows)          | Exits non-zero with a message                      |
