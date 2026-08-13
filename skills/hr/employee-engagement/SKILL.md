---
name: employee-engagement
description: Use when managing an employee past onboarding through their ongoing lifecycle — recurring 1:1 cadence, quarterly/annual performance review cycles, feedback collection, growth and development plans, recognition, retention/flight-risk checks and stay interviews, and exit interviews at departure. Triggers on "1:1 cadence", "performance review", "growth plan", "stay interview", "retention risk", "exit interview".
version: 1.0.0
author: Nuvel Skills
---

# Employee Engagement

## Overview

Keep employees engaged, growing, and retained across the middle of the lifecycle — from post-onboarding to exit. The core principle: **engagement is a continuous, actioned practice, not a once-a-year survey.** Detect friction early (stay interviews, 1:1s, surveys) and act, so issues surface *before* they become resignation letters. SHRM estimates replacing an employee costs 50–200% of their annual salary — retention is the cheapest talent strategy you have.

## When to use

- Setting or running a recurring 1:1 cadence with an employee or team.
- Running quarterly or annual performance review cycles and calibration.
- Collecting and acting on feedback (surveys, 360s, stay interviews).
- Building growth/development plans, running recognition, or assessing flight risk.
- Conducting an exit interview and feeding findings back into retention.

## When NOT to use

- The person hasn't started or is still in 30-60-90 ramp → use [[employee-onboarding]].
- You are filling an open role or making an offer → use [[hiring]].
- A formal performance-improvement/disciplinary or legal termination process is required → engage HR and legal directly; a growth plan is not a substitute for a documented PIP.

## Workflow

1. **Establish 1:1 cadence.** Set recurring manager↔report 1:1s (weekly or biweekly). Owned by the employee's agenda as much as the manager's; cover progress, blockers, feedback both directions, and growth — not just status. Protect them: cancelled 1:1s are an early disengagement signal.
2. **Continuous feedback.** Give specific, timely feedback close to the event rather than saving it for review season. Supplement with periodic 360/multi-source feedback to surface blind spots and skills gaps.
3. **Performance review cycle.** Run a predictable cycle — lightweight quarterly check-ins plus a deeper annual review. Evaluate against goals set at the start of the period, calibrate across peers for fairness, and separate the development conversation from the compensation decision where possible.
4. **Growth & development plans.** Co-create a development plan tied to the employee's aspirations and the org's needs: target skills, stretch work, learning, and a realistic timeline. Revisit it in 1:1s so it stays live, not a filed-and-forgotten document.
5. **Recognition.** Recognize contributions consistently and specifically, in the employee's preferred mode (public vs. private). Recognition is a low-cost, high-leverage retention driver; make it routine, not annual.
6. **Retention / flight-risk checks.** Watch signals (disengagement, missed 1:1s, compensation drift, no growth path, life changes). Run **stay interviews** with valued employees — proactive, recurring, and *actioned*. Ask what keeps them, what would make them leave, and what would make the job better; then close the loop on what you heard.
7. **Act on findings.** Feed survey, 1:1, and stay-interview themes into concrete changes (workload, comp, growth, management). Unactioned feedback is worse than no feedback — it teaches people not to speak up.
8. **Exit interview (at departure).** When someone leaves, run a structured exit interview to capture honest, systemic feedback (why leaving, what would have changed it, manager and role experience). Coordinate the access-revocation checklist maintained during [[employee-onboarding]]. Route exit themes back into retention programs — what you hear here should change what you do in steps 1–7.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Engagement = one annual survey | Too slow to catch or fix disengagement | Continuous 1:1s, check-ins, stay interviews |
| 1:1s routinely skipped/cancelled | Signals disengagement; blockers fester | Protect the cadence; treat cancellations as a signal |
| Feedback saved for review season | Surprises, recency bias, mistrust | Timely feedback near the event; reviews hold no surprises |
| Development plan filed and forgotten | No growth path → flight risk | Revisit growth plan in 1:1s; keep it live |
| Surveys/stay interviews collected but not actioned | Erodes trust; people stop being candid | Close the loop; convert themes into changes |
| Growth plan used in place of a PIP | Legal/documentation gap on real performance issues | Run a documented PIP with HR/legal when warranted |
| Exit interview skipped or ignored | Loses systemic insight; recurring attrition | Structured exit interview → feed into retention |
| Waiting for exit interview to learn why | Too late to retain the person | Stay interviews surface it while you can still act |

## Exit criteria

- [ ] A recurring 1:1 cadence is set and consistently held (not routinely cancelled).
- [ ] Feedback is given continuously; periodic 360/multi-source input is collected.
- [ ] Performance cycle runs on schedule (quarterly check-ins + annual), with calibration and goals-based evaluation.
- [ ] Each employee has a live growth/development plan revisited in 1:1s.
- [ ] Recognition happens routinely and in the employee's preferred mode.
- [ ] Retention risk is assessed; stay interviews are run with valued employees and their findings actioned.
- [ ] Feedback themes are converted into concrete, tracked changes.
- [ ] At departure, a structured exit interview is completed, access revoked per the onboarding access inventory, and findings routed back into retention.

## Tools

- `scripts/engagement-score.py` — turn the step-6 flight-risk signals (skipped 1:1s, comp drift, no growth plan, low pulse, no recognition, life changes) into a consistent per-employee triage score so no at-risk person is overlooked. Run `python scripts/engagement-score.py --sample > people.json` for a template, then `python scripts/engagement-score.py people.json`. High score = run a stay interview and act, not a verdict that they're leaving.

## Sources

Aligned with SHRM guidance on retention, stay vs. exit interviews, and cost-of-turnover estimates (50–200% of salary), plus standard employee-lifecycle management practice (continuous feedback, 360 reviews, growth planning, recognition). Coordinate departures and access removal with the inventory maintained in [[employee-onboarding]]; involve HR/legal for formal performance or termination processes.
