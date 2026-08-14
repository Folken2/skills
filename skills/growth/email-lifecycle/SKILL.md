---
name: email-lifecycle
description: "Use when designing or fixing lifecycle email — list hygiene and authentication (SPF/DKIM/DMARC), lifecycle-stage mapping (welcome, onboarding, nurture, re-engagement, winback), sequence design, deliverability, and compliance (CAN-SPAM, GDPR, CASL). Also use when emails hit spam, engagement decays, or there's no map of what sends to whom and why."
version: 1.0.0
author: Nuvel Skills
---

# Email Lifecycle

## Overview

Lifecycle email is not "the newsletter" — it's a set of stage-triggered sequences that move a contact from unknown to activated to retained. Done well it's the highest-ROI channel a growth team owns; done carelessly it torches sender reputation and lands the whole domain in spam.

**Core principle:** Deliverability is earned before it's spent. Authentication and list hygiene come first — no clever sequence survives a burned sending domain. Every send must map to a lifecycle stage, a trigger, and a goal; a broadcast to "everyone" is how reputation dies.

## When to use

- Standing up lifecycle email from scratch, or auditing an existing program.
- Emails are landing in spam or bounce/complaint rates are climbing.
- There's no clear map of which sequences exist, what triggers them, or what they're for.

## When NOT to use

- **Single transactional sends** (password reset, receipt) — those follow transactional deliverability rules, not lifecycle design.
- **One-off campaign blasts** — this skill designs triggered lifecycle flows, not standalone broadcasts.
- **Building the email templates themselves** — that's a production task; design the sequence here first.

## The workflow

```
STEP 1        STEP 2        STEP 3       STEP 4          STEP 5        STEP 6
hygiene &  →  map        →  design    →  deliver-    →  compliance →  measure
auth          stages        sequences    ability        checklist     (KPIs)
```

### STEP 1 — List hygiene & authentication

Before designing anything: publish and validate **SPF**, **DKIM**, and **DMARC** for the sending domain. Set up bounce handling (suppress hard bounces immediately) and a list-cleaning policy (remove/suppress chronic non-openers and role addresses).
**Exit:** SPF, DKIM, and DMARC validate; bounce suppression is automated; a list-cleaning cadence is defined.

### STEP 2 — Map lifecycle stages

Define the stages and what qualifies a contact for each: **welcome** (just subscribed), **onboarding** (new user, not yet activated), **nurture** (engaged, not converted), **re-engagement** (going quiet), **winback** (lapsed/churned). Each contact should be in exactly one primary stage at a time.
**Exit:** a lifecycle map exists naming each stage, its entry/exit criteria, and its goal.

### STEP 3 — Design sequences

For each stage, design a sequence with an explicit: **goal** (the one action it drives), **trigger** (the event that starts it), **cadence** (spacing between sends), and **content** (per-email purpose and CTA). Define exit conditions so contacts leave when they convert.
**Exit:** each lifecycle stage has a sequence spec with goal, trigger, cadence, per-email content, and exit conditions.

### STEP 4 — Deliverability baseline

Before launch, measure and record: spam score (Mail-Tester or equivalent), sender reputation (Google Postmaster / SNDS), and expected engagement thresholds. Warm up new domains/IPs gradually.
**Exit:** a deliverability baseline is recorded (spam score, reputation, engagement targets) and a warm-up plan exists if the domain is new.

### STEP 5 — Compliance checklist

Verify against the jurisdictions you send to: **CAN-SPAM** (physical address, honest subject, working unsubscribe honored ≤10 days), **GDPR** (lawful basis, consent records, easy withdrawal), **CASL** (express/implied consent tracked, identification). A one-click unsubscribe must be present and functional on every send.
**Exit:** a compliance checklist passes for every applicable jurisdiction; unsubscribe is verified working.

### STEP 6 — Measure

Instrument per sequence and per stage: open rate, click-through rate, conversion, unsubscribe rate, and revenue attribution. Watch complaint and bounce rates as guardrails — rising complaints override any engagement win.
**Exit:** KPIs and guardrail metrics (complaints, bounces) are instrumented per sequence, with a review cadence set.

## Common Pitfalls

- **Designing sequences before authentication.** A beautiful onboarding flow from an unauthenticated domain goes to spam. SPF/DKIM/DMARC is step one, not a footnote.
- **Emailing disengaged contacts to "reactivate."** Blasting non-openers tanks reputation faster than it wins anyone back. Suppress them or run a *tight, opt-out-honored* winback, then let go.
- **Treating unsubscribe as optional friction.** Hiding or delaying unsubscribe raises complaints (which hurt deliverability far more than an unsub) and breaks CAN-SPAM/CASL. Make it one click.
- **Ignoring complaint rate.** A sequence with a great open rate and a rising complaint rate is failing. Complaints are the metric mailbox providers weight most.
- **One giant "everyone" list.** Without stage segmentation you send irrelevant mail, engagement drops, and providers deprioritize the domain. Map stages first.

## Verification Checklist

- [ ] SPF, DKIM, and DMARC published and validating for the sending domain.
- [ ] Bounce suppression automated; list-cleaning cadence defined.
- [ ] Lifecycle map names every stage with entry/exit criteria and a goal.
- [ ] Each stage has a sequence spec (goal, trigger, cadence, per-email content, exit conditions).
- [ ] Deliverability baseline recorded (spam score, reputation, engagement targets); warm-up plan if new domain.
- [ ] Compliance checklist passes for CAN-SPAM / GDPR / CASL as applicable; unsubscribe verified working.
- [ ] KPIs (open, CTR, conversion, unsubscribe, revenue) plus guardrails (complaints, bounces) instrumented with a review cadence.

## Cross-references

- **content-pipeline** — newsletter/nurture content is produced there and distributed through these sequences.
- **analytics-setup** — supplies the conversion and revenue-attribution tracking STEP 6 reports against.
