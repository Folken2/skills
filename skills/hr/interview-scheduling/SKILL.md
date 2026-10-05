---
name: interview-scheduling
description: "Use when coordinating interviews across a candidate and a multi-person panel — collecting availability, resolving timezones, finding conflict-free slots, sequencing stages, protecting candidate experience, and handling reschedules and no-shows. Triggers on: schedule interview, panel coordination, interviewer availability, reschedule, interview loop, recruiting coordinator."
version: 1.0.0
author: "Nuvel Skills"
---

# Interview Scheduling

## Overview

Turn a panel of interviewers and one candidate into a confirmed, conflict-free interview loop. The core principle: **the candidate's experience is the product.** Scheduling is the only part of hiring every candidate experiences first-hand, and it is the part most often run informally — which is exactly why loops drift, interviewers get double-booked, and candidates conclude the company is disorganised before they have met an engineer.

This skill is the coordinator half of [[hiring]] step 5. It owns one loop end-to-end: gathering availability, computing a conflict-free sequence, confirming with every participant, and running the reschedule path. The governing constraint is that **the candidate's time is scarcer than the interviewers'** — build the loop around the candidate's windows, then fit the panel to it, never the reverse.

Keep the loop tight: stages stacked on one day, or on adjacent days, cut drop-off. A candidate who has to explain their own availability three times is a candidate who accepts elsewhere.

## When to use

- A candidate has advanced past screening and needs a multi-stage interview loop booked.
- A loop needs redesigning (stage added or removed, duration changed, interviewer swapped).
- A participant reschedules, or the candidate asks for a different time.
- You are confirming, reminding, or chasing a confirmation before interview day.
- You are auditing an existing loop for conflicts, missing panellists, or candidate-hostile sequencing.

## When NOT to use

- Interviews are not authorised yet — requisition, success profile, and panellist focus areas come first → [[hiring]] steps 1–4.
- You need to decide *who* the interviewers are → that is a hiring-manager decision taken at intake.
- You are collecting scorecards, running the debrief, or making the selection decision → [[hiring]] steps 5–6.
- The candidate has accepted and you are setting up their first day → [[employee-onboarding]].
- You are scheduling an internal 1:1, review, or coaching conversation → [[employee-engagement]].

## Workflow

1. **Confirm the loop is authorised.** Verify with the hiring manager: number of stages, duration per stage, the competencies each stage covers, and the named interviewers per stage. A loop built on an unapproved panel produces cancellations you will personally absorb.
2. **Collect constraints before availability.** Establish the candidate's timezone and hard constraints (employment hours, caregiving windows, notice-period limits), each interviewer's timezone, and company-side constraints (working-hours policy, quiet hours, regional rules). Separate *hard* constraints (unmovable) from *soft* preferences (negotiable) — conflating them is how loops become unbookable.
3. **Set the scheduling window.** Offer the candidate a bounded, concrete window (specific dates across two weeks) rather than an open "when works for you". Bounded options convert faster, stop loops stretching past the point where the candidate signs elsewhere, and cut the round trips needed to land a slot.
4. **Gather availability as discrete intervals.** Collect each interviewer's availability as start/end intervals in their own timezone, with the timezone named explicitly. Never accept "mornings are fine" as availability — unquantified availability is the single largest source of double-bookings.
5. **Compute the conflict-free sequence.** Run `scripts/panel-scheduler.py` against the loop request. It normalises every interval to UTC, finds slots where all required interviewers are simultaneously free for the full duration, enforces the candidate gap and daily-cap rules, and keeps stage order so prerequisites precede dependents. Any stage it cannot fill comes back with a reason rather than a silent omission.
6. **Fill gaps by substitution, then by waiver.** For an unscheduled stage: first try a substitute interviewer with the same competency coverage, then widen the candidate's window, then relax a *soft* constraint — in that order, and with the hiring manager's agreement. Never quietly drop a stage to make the calendar close.
7. **Confirm with everyone, independently.** Send each participant an invite carrying: local time in their own timezone, stage, duration, whom they are meeting, the competencies they cover, the scorecard link, and what the candidate has been told. Require explicit acceptance from every interviewer before the loop counts as booked — a tentative invite is not a confirmed loop.
8. **Prepare the candidate.** Send one consolidated confirmation with the full loop: each stage's format, the timezone reference, joining details, who they meet at each stage, and what to expect. Nominate a named contact for changes; a candidate with no contact chases a generic inbox and drops out.
9. **Run the reminder and reschedule path.** Send reminders at the agreed lead time (typically 24 hours) to every participant. On a reschedule, freeze the loop, identify which stages can move without breaking stage order, and re-run step 5 against the new constraints — reusing stored availability rather than re-collecting it. On a no-show, apply the documented policy (wait period, contact attempts) and record the outcome.
10. **Close the loop.** After the final stage, confirm every scorecard is submitted (route to [[hiring]] step 6), release interviewers' holds, and log the loop's operational metrics: days from advancement to booked, reschedule count, no-show count, and stages that required substitution.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Times given in "the company's timezone" without naming it | The classic off-by-hours cancellation; candidate misses the interview | Send each participant their local time with the timezone named |
| Vague availability accepted ("mornings work") | Guarantees later conflicts and rework | Collect start/end intervals per interviewer, in writing |
| Panel booked first, candidate asked afterwards | The candidate is the scarce resource; you book over them | Build around the candidate's window, then fit the panel |
| Stage order broken to make the calendar close | Candidate must prove skills before context is set | Keep prerequisites first; substitute or widen instead |
| A tentative invite treated as confirmed | The loop collapses on interview day | Explicit acceptance from every interviewer before "booked" |
| One interviewer double-booked across adjacent stages | Rushed, low-signal interviews and avoidable cancellations | Enforce the minimum-gap rule; check each stage's panel |
| Stage silently dropped because it cannot be filled | Compromises the hiring decision and looks inconsistent | Report the stage as unscheduled with a reason; escalate it |
| Stream of last-minute changes sent to the candidate | Reads as chaos; damages employer brand | One consolidated confirmation; changes via the named contact |
| Availability re-collected on every reschedule | Interviewers disengage and start declining | Re-run the solver on the stored availability intervals |

## Exit criteria

- [ ] Loop authorised: stages, durations, competencies, and named interviewers confirmed by the hiring manager.
- [ ] Hard and soft constraints separated for the candidate and every interviewer; timezones named.
- [ ] Availability captured as discrete start/end intervals per interviewer and stored for reuse.
- [ ] `scripts/panel-scheduler.py` run; every stage either scheduled conflict-free or reported unscheduled with an explicit reason.
- [ ] No interviewer double-booked; candidate day-cap and minimum-gap rules respected.
- [ ] Explicit acceptance received from every interviewer, not merely an invite sent.
- [ ] Candidate received a single consolidated confirmation with local times, formats, panellist names, and a named contact.
- [ ] Reminder scheduled at the agreed lead time for all participants.
- [ ] Reschedule path executed against stored availability (no re-collection) with stage order preserved.
- [ ] Loop closed: scorecards routed to [[hiring]], holds released, operational metrics recorded.

## Tools

- `scripts/panel-scheduler.py` — resolves a multi-stage interview loop into a conflict-free schedule. Normalises availability to UTC, enforces the candidate gap and daily cap, preserves stage order, and reports unschedulable stages with a reason. Standard library only.
  - `python scripts/panel-scheduler.py --sample > loop.json` — emit a fillable template.
  - `python scripts/panel-scheduler.py loop.json` — proposed schedule with per-stage status.
  - `python scripts/panel-scheduler.py loop.json --json` — machine-readable schedule for calendar or ticket import.

## Sources

Aligned with standard recruiting-coordination practice and structured-interview guidance — consistent questions and scorecards per stage, per the SHRM structured-hiring research that also underpins [[hiring]] — plus established candidate-experience practice: bounded scheduling windows, a single consolidated confirmation, named points of contact, and short loops. Timezone handling follows the IANA timezone-database convention used by calendar systems (normalise to UTC, render per participant in local time), consumed here through Python's standard-library `zoneinfo`. Adapt interview-day logistics, working-hours expectations, and accessibility accommodations to your jurisdiction and your organisation's policy.
