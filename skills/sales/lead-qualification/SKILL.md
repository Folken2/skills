---
name: lead-qualification
description: Use when inbound leads arrive and you need to decide who to work, how fast, and where to route them — capture qualification criteria (BANT/GPCT/CHAMP), score, prioritize, route to the right pipeline, and set a follow-up cadence. Also use when leads are being worked in the wrong order, reps chase unqualified deals, or "why did we ignore that lead" comes up.
version: 1.0.0
author: Nuvel Skills
---

# Lead Qualification

## Overview

Inbound volume is finite attention spread across uneven opportunity. The job is not to qualify every lead perfectly — it is to *rank* them so the best-fit, highest-intent leads get worked first and fast, and poor-fit leads get a graceful path out.

**Core principle:** Capture structured criteria, score against them, act on the score. A lead with no logged qualification data is not "unqualified" — it is *un-triaged*, and un-triaged leads are worked in random order, which is the same as not prioritizing at all.

The discipline here is *speed-to-lead with structure*: high-intent leads decay by the minute, so a fast, consistent scoring pass beats a slow, artisanal one.

## When to use

- A new inbound lead (demo request, form fill, content download, trial signup) needs to be worked.
- A batch of leads accumulated and you need to decide work order.
- Reps are complaining about lead quality, or good leads are going cold.

## When NOT to use

- **Outbound prospecting / list building** — you are creating leads, not triaging inbound ones. Qualify at the discovery stage instead.
- **Deep enterprise qualification of an active opportunity** — once a lead is accepted and in an active deal, use full **discovery-call** and MEDDIC-style qualification, not a lead score.
- **Purely mechanical routing already automated in your CRM** — if scoring is fully automated and trusted, don't re-do it by hand; inspect the rules instead.

## Choose a framework (match to motion)

Pick ONE primary framework per motion and apply it consistently. Mixing frameworks per-lead makes scores incomparable.

| Framework | Captures | Best for |
|---|---|---|
| **BANT** (IBM) | Budget, Authority, Need, Timing | Simple/transactional motions, small teams, short cycles |
| **CHAMP** | Challenges, Authority, Money, Prioritization | Complex B2B; leads with the challenge first, budget later |
| **GPCT** (HubSpot) | Goals, Plans, Challenges, Timeline | Inbound SaaS, consultative motions, longer-term fit |

*Sources: BANT (IBM); CHAMP (InsightSquared); GPCT / GPCTBA&C&I (HubSpot).* For inbound SaaS with shorter cycles, prefer CHAMP or GPCT — BANT's "Budget first" gate rejects good early-stage leads.

## The Workflow

```
STEP 1            STEP 2         STEP 3        STEP 4          STEP 5
capture criteria  →  score    →  prioritize →  route      →  set cadence
(framework + fit)    (0–100)     (tier A/B/C)  (pipeline)     (follow-up)
```

### STEP 1 — Capture criteria (framework + fit)

Record two independent dimensions — do not blend them:

- **Qualification (intent/need):** the chosen framework's fields. E.g. GPCT → Goal, Plan, Challenge, Timeline. Capture what the lead told you or what their behavior implies; mark unknowns as unknown, do not invent.
- **Fit (ICP match):** company size, industry, role/seniority, region, tech stack — how well they match your Ideal Customer Profile.

If a field is unknown, leave it unknown. A confident guess pollutes the score worse than a blank.

### STEP 2 — Score (0–100)

Produce a single comparable number from weighted sub-scores. A workable default weighting:

- **Fit** (ICP match): 40%
- **Intent/need** (framework fields answered + strength): 40%
- **Engagement/urgency** (recency, timeline, buying signals): 20%

Use the bundled `scripts/lead-scorer.py` to compute the score and next action deterministically — hand-scoring drifts between reps and between Mondays and Fridays.

### STEP 3 — Prioritize into tiers

| Tier | Score | Meaning |
|---|---|---|
| **A — Hot** | ≥ 75 | Strong fit + clear intent. Work now. |
| **B — Nurture** | 50–74 | Real but incomplete. Work after A's; fill the gaps. |
| **C — Low / Disqualify** | < 50 | Weak fit or intent. Long-nurture or graceful decline. |

Tier is set by the *score*, not by a rep's gut. If gut and score disagree, fix the captured data (STEP 1), then re-score — don't override the tier silently.

### STEP 4 — Route to the appropriate pipeline

Route on fit **and** motion, not just score:

- **Enterprise / high fit** → AE / field sales pipeline; trigger **discovery-call**.
- **SMB / self-serve fit** → inside sales or product-led pipeline.
- **Wrong ICP but valid** → partner/referral or long-nurture.
- **Not a fit / spam** → disqualify with a reason code (never delete silently — the reason feeds future scoring).

### STEP 5 — Set follow-up cadence

Cadence is set by tier — speed-to-lead matters most for A:

| Tier | First touch | Cadence |
|---|---|---|
| **A** | Within 1 hour (ideally minutes) | Multi-touch (call + email + social), ~5–7 touches over 2 weeks |
| **B** | Within 1 business day | Lighter cadence, 3–4 touches over 3–4 weeks + nurture |
| **C** | Automated nurture | Marketing nurture; re-score on new engagement |

Every lead leaves this step with a **next action + owner + due date** logged. No exceptions.

## Red Flags — STOP

| Thought | Reality |
|---|---|
| "I'll just work leads top-to-bottom as they came in" | FIFO ≠ prioritization. Score first, then work by tier. |
| "This one feels hot, I'll skip scoring" | Gut without captured data is unrepeatable. Score it; if it's hot, it'll tier A. |
| "Budget is unknown so it's a bad lead" | Unknown ≠ disqualified. For inbound, use CHAMP/GPCT, not BANT's budget gate. |
| "I'll fill in the missing fields with a reasonable guess" | Invented data inflates scores. Mark unknowns unknown. |
| "Low score, just delete it" | Disqualify *with a reason code*. Silent deletes destroy scoring feedback. |
| "I'll follow up when I get to it" | A-tier leads decay hourly. Log a next action + due date now. |

## Common Mistakes to Avoid

| Don't | Do |
|---|---|
| Blend fit and intent into one vague vibe | Score them as separate dimensions, then combine |
| Switch frameworks per lead | Pick one framework per motion; keep scores comparable |
| Over-qualify inbound like an enterprise deal | Triage fast; deep-qualify later in discovery |
| Route purely by score | Route by fit + motion (enterprise vs self-serve) |
| Leave leads without a next step | Every lead exits with owner + action + due date |

## Exit Criteria

You are done qualifying a lead when ALL are true:

- [ ] One framework (BANT / CHAMP / GPCT) chosen and its fields captured (unknowns marked, not invented).
- [ ] Fit/ICP dimension captured separately from intent.
- [ ] A numeric score (0–100) produced via `scripts/lead-scorer.py` (or equivalent consistent method).
- [ ] Lead assigned a tier (A / B / C) consistent with its score.
- [ ] Lead routed to a named pipeline (or disqualified **with a reason code**).
- [ ] A follow-up cadence set, with a next action + owner + due date logged.

## Cross-references

- **discovery-call** — once an A/B lead is accepted, run structured discovery to deep-qualify.
- **pipeline-management** — where routed leads live as deals; feeds stage definitions and coverage.
- **superpowers:brainstorming** — if your ICP or scoring weights themselves are unclear, shape them there first.
