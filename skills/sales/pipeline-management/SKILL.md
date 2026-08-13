---
name: pipeline-management
description: Use when managing a sales pipeline end-to-end — defining stages, tracking deal velocity, forecasting, inspecting deals, recovering stalled deals, analyzing losses, and enforcing pipeline hygiene. Also use when the forecast keeps missing, deals sit for weeks with no next step, coverage is thin, "commit" deals slip, or nobody trusts the CRM numbers.
version: 1.0.0
author: Nuvel Skills
---

# Pipeline Management

## Overview

A pipeline is a forecasting instrument, not a to-do list. Its value is *accuracy* — a small, clean, honestly-staged pipeline forecasts better than a large one padded with hope.

**Core principle:** Every open deal has an exit-criteria-defined stage, a next step with a date, and a reason it will close when it says it will. A deal that can't produce those three is not a forecast — it's a wish, and wishes are how the number gets missed.

The discipline here is *hygiene over volume*: reps are rewarded for pipeline that is real, not pipeline that is large.

## When to use

- Running a weekly pipeline review or 1:1 deal inspection.
- Building or sanity-checking a forecast for the period.
- Deals are stalling, slipping, or the forecast keeps missing.
- Onboarding a new segment/team and defining stages from scratch.

## When NOT to use

- **Working a single early lead** — that's **lead-qualification** (triage) then **discovery-call**, not pipeline mechanics.
- **Deep-diagnosing why one specific deal is stuck** — use the stalled-deal recovery section here, then hand back to **discovery-call** to re-discover.

## Key concepts (attributed)

| Concept | Definition | Note |
|---|---|---|
| **Deal velocity** | How fast a deal moves stage-to-stage / creation-to-close | Slowing velocity is the earliest warning of a shortfall |
| **Pipeline (sales) velocity** | `(# opps × avg deal size × win rate) ÷ cycle length` | Revenue-per-day the pipeline generates |
| **Coverage ratio** | `open pipeline value ÷ quota (gap) for the period` | Healthy ≈ **3x–5x**; derive from win rate (win 25% → need ~4x) |
| **Stage probability** | Weighting applied to each stage for weighted forecast | Must reflect *historical* conversion, not optimism |

*Sources: pipeline velocity formula and coverage-ratio guidance are standard RevOps practice (e.g. Clari, Outreach, Forecastio); MEDDIC underpins deal inspection.*

## The Workflow

```
DEFINE         →  TRACK        →  INSPECT       →  RECOVER / FORECAST
stages +          velocity +       deal-by-deal     stalled recovery,
exit criteria      coverage         (MEDDIC)         lost analysis, hygiene
```

### 1 — Stage definitions (exit criteria, not vibes)

Each stage is defined by a **verifiable exit criterion** — an observable thing that must be true to advance, owned by the *buyer's* actions, not the rep's optimism. Example spine:

| Stage | Exit criterion (must be true to advance) |
|---|---|
| **Lead / Qualify** | Fit + intent confirmed; routed (see lead-qualification) |
| **Discovery** | Problem quantified, economic buyer identified, next step set (see discovery-call) |
| **Solution / Eval** | Solution mapped to criteria; champion confirmed; POC scoped |
| **Proposal** | Proposal delivered; pricing + decision process agreed |
| **Negotiation / Paper** | Verbal yes; in procurement/legal; close date has a driver |
| **Closed Won / Lost** | Signed / explicitly disqualified with a reason |

If a deal doesn't meet a stage's exit criterion, it does not belong in that stage. Sandbagging (hiding) and happy-ears (inflating) are both hygiene failures.

### 2 — Track velocity & coverage

- **Velocity:** measure average days-in-stage and creation-to-close. Flag deals exceeding ~1.5× the historical average for their stage — they're stalling.
- **Coverage:** compute open pipeline ÷ the period's quota gap. Below your target multiple (commonly 3x) → you have a *creation* problem, not a closing problem; feed it back to top-of-funnel.
- Use `scripts/pipeline-review.py` to compute velocity, coverage, and stalled-deal flags deterministically.

### 3 — Deal inspection (MEDDIC lens)

For commit/best-case deals, inspect — don't take the stage on faith. For each, confirm: Metrics (quantified value), Economic buyer engaged, Decision criteria known, Decision process mapped, Pain confirmed, Champion active. **Gaps = risk.** A deal with an unknown economic buyer in "Negotiation" is mis-staged, not almost-closed.

### 4 — Stalled deal recovery

A deal is stalled when it has **no logged next step** or has exceeded its stage's velocity threshold. For each:
1. Identify the *specific* stall reason (no champion, lost priority, budget frozen, ghosting, unquantified value).
2. Re-establish value and a compelling event — often means looping back to **discovery-call**.
3. Set a dated next step, or **disqualify it**. A deal you can't re-engage is dead pipeline; killing it improves forecast accuracy.

### 5 — Lost deal analysis

Every Closed Lost gets a **structured reason code** (price, no decision / status quo, lost to competitor X, no budget, timing, wrong fit). Review lost reasons in aggregate: patterns reveal ICP, product, or stage-exit-criteria problems — not just "the rep lost it."

### 6 — Forecast

Produce the number three ways and reconcile: **weighted** (Σ deal value × stage probability), **commit/best-case** (rep judgment on inspected deals), and **historical** (run-rate). Divergence between them is the signal — investigate the gap rather than picking the number you like.

### 7 — Pipeline hygiene (ongoing)

- Every open deal: correct stage (by exit criteria), a next step with a date, a realistic close date with a driver.
- Purge/close deals with past-due close dates and no activity — don't roll them forward silently.
- Reps update daily; managers review weekly. The CRM is the source of truth only if it's kept true.

## Red Flags — STOP

| Thought | Reality |
|---|---|
| "Big pipeline, we're fine" | Volume ≠ health. Check coverage, velocity, and hygiene. |
| "It's in Negotiation, it'll close" | If exit criteria aren't met, it's mis-staged. Inspect it. |
| "I'll just roll the close date forward again" | Repeated slips = a stall you're hiding. Diagnose or disqualify. |
| "This commit deal is solid, trust me" | Run the MEDDIC lens. Unknown economic buyer = risk, not commit. |
| "We lost it, on to the next" | No reason code = no learning. Log it; patterns matter. |
| "The forecast is whatever the weighted number says" | Reconcile weighted vs commit vs historical; the gap is the insight. |
| "Leave the dead ones in, they pad coverage" | Padding destroys forecast trust. Purge stale pipeline. |

## Common Mistakes to Avoid

| Don't | Do |
|---|---|
| Define stages by rep activity | Define stages by verifiable buyer-side exit criteria |
| Judge pipeline by total value | Judge by coverage ratio, velocity, and hygiene |
| Take "commit" deals on faith | Inspect with MEDDIC; gaps = risk |
| Let deals sit with no next step | Every open deal has a dated next step or gets disqualified |
| Close-lost with no reason | Structured reason code on every lost deal |
| Forecast from one method | Reconcile weighted, commit, and historical |

## Exit Criteria

Your pipeline is well-managed for the period when ALL are true:

- [ ] Every stage has a documented, verifiable exit criterion; each open deal sits in a stage whose criterion it meets.
- [ ] Deal velocity tracked; deals exceeding their stage's velocity threshold are flagged as stalled.
- [ ] Coverage ratio computed against the period's quota gap and compared to target (≥ ~3x or your win-rate-derived number).
- [ ] Commit/best-case deals inspected through the MEDDIC lens; gaps recorded as risks.
- [ ] Every stalled deal has a re-engagement next step **or** is disqualified.
- [ ] Every Closed Lost has a structured reason code.
- [ ] A forecast produced and reconciled across weighted / commit / historical.
- [ ] Hygiene pass done: no past-due close dates left rolling silently; every open deal has a dated next step.
- [ ] `scripts/pipeline-review.py` run and its health report reviewed.

## Cross-references

- **lead-qualification** — feeds the top of the pipeline; routing decides which pipeline a deal enters.
- **discovery-call** — defines the Discovery stage's exit criteria and is where stalled deals loop back to re-discover value.
- **superpowers:second-order-impact-analysis** — before changing stage definitions or forecast methodology, trace the downstream reporting/comp impact.
