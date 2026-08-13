---
name: second-order-impact-analysis
description: Use before declaring a code change complete or merging — when a change touches shared code, data models, APIs, or interfaces — to surface the ripple effects, cascade failures, and downstream impacts that are not obvious from the diff alone.
version: 1.0.0
author: Nuvel Skills (inspired by Brandon Bayer / rag.saas-shipkit)
---

# Second-Order Impact Analysis

## Overview

A change that works in isolation can still break the system. The diff shows the *first-order* effect — the lines you touched. The failures that reach production live in the *second order*: the caller you forgot, the query that now returns a different shape, the cache that's now stale, the client still expecting the old contract.

**Core principle:** Before you call a change done, trace what else it touches — upstream, downstream, data, contract, performance, and reversibility — and surface anything significant to the human *before* it ships.

This is an analysis pass, not a rewrite. Run it against a change you believe is complete, and let it tell you what you missed.

## When to Run

Run this before completion/merge whenever a change touches:

- Shared code — a function, component, hook, or module with more than one caller.
- Data models — schema, migrations, or the shape of persisted/returned data.
- Interfaces — API endpoints, response formats, public function signatures, props.
- Auth, permissions, or anything on a hot path.

Skip it for genuinely local changes (a self-contained bug fix, a comment, a private helper with one caller).

## The Six Dimensions

Work each one. For each, the question is "what breaks that the diff doesn't show?"

### 1. Upstream effects — what depends on this change?

What calls, imports, or consumes the thing you changed?

- Who are all the callers of the changed function/component/endpoint? (Search — don't rely on memory.)
- Do any of them rely on behavior you just altered (return shape, side effects, timing, thrown errors)?
- Are there parent components that pass props into what you changed?

### 2. Downstream effects — what does this change depend on?

What does your change now rely on that could break it or that it could break?

- New dependencies on other services, tables, or modules — are they guaranteed present?
- Does the change assume data that may not exist for older records?
- Routing/state dependencies: does changed page structure or state shape break navigation or existing stores?

### 3. Data integrity — what happens to existing data?

The change works for new data. What about the rows already there?

- Do existing records satisfy the new constraints/shape, or do they need a backfill/migration?
- Can existing data become orphaned, duplicated, or inconsistent?
- Is there a migration required in production? (If so, that's a **red flag** — surface it.)

### 4. API contract — is the interface changing?

Anything another system consumes is a contract.

- Is a response format, field name, status code, or error shape changing?
- Who consumes it — a mobile app, a webhook consumer, a third-party integration, another service?
- If yes: version it, keep backward compatibility, or coordinate the change. A silent contract break is an outage for someone else.

### 5. Performance — scaling, latency, N+1?

- Does this add a query inside a loop (N+1), or a JOIN that scales with data volume?
- Does it invalidate or bypass an existing cache?
- Does it increase bundle size, server load, or a hot-path latency budget?
- Will it be fine at current volume but not at 10× or 100×?

### 6. Rollback — can we undo this?

- If this ships and goes wrong, can it be reverted cleanly?
- Does it involve an irreversible data operation (a destructive migration, a one-way backfill)?
- Is there a feature flag or a staged rollout that de-risks it?

## Severity Triage

Classify each impact you find, and act on the class:

| Flag | Meaning | Action |
|---|---|---|
| 🚨 **Red** | Breaking API change, required prod migration, data-loss risk, security hole, perf regression | **Stop and surface to the human before implementing/merging.** |
| ⚠️ **Yellow** | Added complexity, new dependency, changed UX workflow, ongoing maintenance cost | Discuss; may proceed with mitigation. |
| ✅ **Green** | Contained, reversible, no external consumers | Proceed; note it and move on. |

## Output

Produce a short, honest summary — not a checkbox theater. State what you found per dimension, flag the red/yellow items explicitly, and propose mitigations:

```
SECOND-ORDER IMPACT ANALYSIS

Upstream:    3 callers of getUser(); two rely on the old null-return behavior — must update.
Downstream:  Assumes `org_id` exists; null for pre-2025 accounts — needs backfill.
Data:        🚨 Existing 40k rows violate the new NOT NULL — migration required.
Contract:    /api/users response drops `legacyId` — mobile app still reads it. 🚨 Coordinate.
Performance:  New JOIN adds ~150ms to dashboard load at current volume.
Rollback:    Reversible except the backfill — needs a documented down path.

🚨 USER ATTENTION: prod migration + mobile contract break. Confirm sequencing before merge.
```

If every dimension comes back green, say so plainly — a clean analysis is a valid result.

## Red Flags — STOP and surface before shipping

| Signal | Why it stops you |
|---|---|
| A production data migration is required | Downtime / data-loss risk — the human must sign off. |
| An API response shape/field/status is changing | Silently breaks every existing consumer. |
| Existing rows won't satisfy a new constraint | The migration fails or corrupts data at apply time. |
| A new query sits inside a loop or scales with rows | N+1 / latency regression that current volume hides. |
| The change is irreversible | No rollback path means no safe recovery. |

## Common Mistakes to Avoid

| Don't | Do |
|---|---|
| Trust your memory for "who calls this" | Search for all callers/consumers |
| Assume existing data fits the new shape | Check the rows already in the table |
| Treat a response-format change as internal | Every consumer is a contract you're breaking |
| Ship a red-flag impact silently | Surface it to the human before merging |
| Run the checklist as theater | Report real findings, or state a clean pass honestly |
| Analyze only what you touched | Trace one hop out — upstream and downstream |
