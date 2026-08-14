---
name: analytics-setup
description: "Use when standing up or fixing web/product analytics — event taxonomy design, property setup (GA4/PostHog/Plausible), conversion and funnel tracking, dashboards across the AARRR pirate metrics, attribution basics, and data-quality checks. Also use when events are inconsistent, numbers don't reconcile, or nobody trusts the dashboard."
version: 1.0.0
author: Nuvel Skills
---

# Analytics Setup

## Overview

Analytics done backwards — tools installed first, taxonomy invented later — produces dashboards nobody trusts and events named `buttonClick2_final`. This skill installs analytics in the correct order: design the taxonomy on paper, then implement, then verify data quality, then build dashboards on top of data you can actually trust.

**Core principle:** The taxonomy is the product; the tool is an implementation detail. A consistent naming convention decided before the first event fires is worth more than any dashboard feature. Untrusted data is worse than no data — it drives confident wrong decisions.

## When to use

- Standing up analytics for a new product or site.
- Existing tracking is inconsistent, events are duplicated/misnamed, or numbers don't reconcile.
- The team wants dashboards but there's no agreed event schema underneath.

## When NOT to use

- **A single ad-hoc question** answerable from existing clean data — just query it.
- **Deep statistical experimentation / A/B analysis** — that needs an experimentation framework, not instrumentation setup.
- **Marketing-attribution modeling at scale** — this covers attribution *basics*; heavy MMM/MTA modeling is its own discipline.

## The workflow

```
STEP 1        STEP 2       STEP 3        STEP 4       STEP 5      STEP 6
event      →  property  →  conversion → dashboards → attribution → data-quality
taxonomy      setup        tracking      (AARRR)      basics        checks
```

### STEP 1 — Design the event taxonomy

On paper, before touching a tool. Define: a **naming convention** (pick one — e.g. `object_action` in snake_case — and enforce it), the **event hierarchy** (which events matter, grouped by user journey), and **properties** (the dimensions each event carries, with types). Keep the event list small and deliberate.
**Exit:** a documented event dictionary exists: every planned event with its name, trigger, and typed properties, all following one convention.

### STEP 2 — Set up the analytics property

Implement the taxonomy in the chosen tool (GA4, PostHog, Plausible, or similar). Configure the property, install the tracking correctly (server-side where it matters), and instrument exactly the events in the dictionary — no more, no less.
**Exit:** the property is live and firing the dictionary's events with their properties; no undocumented events appear in the stream.

### STEP 3 — Conversion tracking

Define the conversions that matter (signup, activation, purchase) as explicit goals/events. Build the core funnels between them. Confirm each conversion event fires exactly once per real conversion.
**Exit:** conversion events and at least one core funnel are defined and firing correctly (verified against a manual test conversion).

### STEP 4 — Build dashboards (AARRR)

Build dashboards across the pirate-metrics frame: **Acquisition** (traffic by source), **Activation** (first-value rate), **Retention** (return/cohort curves), **Revenue** (paid conversion, ARPU), **Referral** (invites/shares). Each chart answers a named question, not "here's some data."
**Exit:** dashboards are live covering acquisition, activation, retention, revenue, and referral, each chart tied to a stated question.

### STEP 5 — Attribution basics

Configure attribution you can explain: first-touch (what starts journeys), last-touch (what closes them), and a simple multi-touch view. Document which model each report uses so numbers are comparable.
**Exit:** at least first- and last-touch attribution is configured, and every report states which model it uses.

### STEP 6 — Data-quality checks

Stand up guardrails: spike/drop detection (alert on anomalous event volume), missing-event checks (a funnel step that suddenly reports zero), and a periodic reconciliation against a source of truth (e.g. billing vs. revenue events).
**Exit:** a data-quality baseline exists with anomaly alerts and a reconciliation check; at least one real analysis has been delivered from the trusted data.

## Common Pitfalls

- **Installing the tool before designing the taxonomy.** You end up with `signup`, `Signup`, `user_signed_up`, and `sign_up` all in the stream. Rename-after-the-fact loses history. Design first.
- **Tracking everything "just in case."** A firehose of undocumented events is unqueryable noise. Instrument the deliberate list; add events when a real question needs them.
- **Trusting dashboards you never verified.** A funnel that looks plausible can be double-counting. Run a manual test conversion and confirm each event fires exactly once before anyone makes decisions on it.
- **Undocumented attribution.** Two reports quoting "conversions" under different models will contradict each other and destroy trust. State the model on every report.
- **No anomaly alerting.** A tag that silently breaks means you discover the gap weeks later, mid-decision. Alert on spikes and drops so breakage surfaces immediately.

## Verification Checklist

- [ ] Event dictionary documented: every event with name, trigger, and typed properties under one naming convention.
- [ ] Analytics property live and firing exactly the dictionary's events — no undocumented events in the stream.
- [ ] Conversion events and at least one core funnel defined and verified against a manual test conversion.
- [ ] Dashboards live across acquisition, activation, retention, revenue, and referral, each chart tied to a question.
- [ ] First- and last-touch attribution configured; every report states its model.
- [ ] Data-quality baseline in place: anomaly alerts + a reconciliation check against a source of truth.
- [ ] At least one real analysis delivered from the trusted data.

## Cross-references

- **seo-audit** / **content-pipeline** / **email-lifecycle** / **paid-acquisition** — all report their KPIs against the instrumentation this skill establishes.
- **dataviz** — for designing the charts themselves once the data is trustworthy.
