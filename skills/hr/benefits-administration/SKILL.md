---
name: benefits-administration
description: "Use when administering employee benefits — annual open enrollment, new-hire enrollment, qualifying life events, eligibility determination, carrier file submission, deduction reconciliation, and coverage termination. Triggers on: open enrollment, benefits enrollment, qualifying life event, QLE, special enrollment period, benefits eligibility, carrier file, deduction reconciliation, COBRA notice, benefits audit."
version: 1.0.0
author: "Nuvel Skills"
---

# Benefits Administration

## Overview

Benefits administration is a **deadline-driven, evidence-driven** process. Almost every serious failure in it is a missed clock: an enrollment window that closed while the form sat in an inbox, a qualifying life event (QLE) that was reported on day 45 of a 30-day window, a carrier file that omitted a new hire so the deduction never started, a continuation notice sent after the statutory deadline. Windows here are usually **not negotiable** — plan documents, carrier contracts, and local law set them, and a late election is generally an irrevocable loss for the employee.

The workflow is built around two independent clocks that must both be tracked:

1. **The enrollment clock** — how long the employee has to elect. Typically 30 days from hire, and 30–60 days from a QLE (the exact window is set by the plan and by jurisdiction, and varies by benefit type).
2. **The administration clock** — when the election must reach payroll and the carrier for the deduction and coverage to take effect correctly, usually aligned to the next payroll cutoff and the carrier's monthly file submission date.

The recurring discipline is **reconciliation**. What payroll deducted, what the carrier billed, and what the employee elected are three different records that drift apart silently. The agent's job is to make them agree on a schedule and to produce an auditable exception list when they don't.

This skill covers the *administration* of benefits. It does not decide plan design, negotiate carrier contracts, or give tax advice. Coverage termination at departure is a step in [[employee-offboarding]]; run it there and use this skill for the ongoing administration around it. Payroll calculation itself belongs to [[payroll-processor]].

**Jurisdiction warning:** eligibility thresholds, waiting periods, permitted QLEs, window lengths, continuation-coverage rules, and notice deadlines differ by country, by US state, and by plan. Treat every number in this skill as a placeholder to be confirmed against the plan document and local law — never as a universal rule.

## When to use

- Annual **open enrollment**: planning the window, communicating it, collecting elections, and closing it.
- **New-hire enrollment**: eligibility determination, waiting period, election window, and carrier setup.
- A **qualifying life event** has been reported and coverage must be changed mid-year.
- You need to **determine eligibility** for a population (hours threshold, FTE, waiting period, plan rules).
- You are preparing or reconciling a **carrier file** or a **payroll deduction file**.
- You are auditing benefits administration: window compliance, missed enrollments, deduction drift, continuation notices.

## When NOT to use

- **Payroll calculation, gross-to-net, tax withholding** → [[payroll-processor]]. This skill produces and consumes the deduction amounts; it does not compute pay.
- **An employee is leaving and coverage must be terminated** → the termination and continuation-notice steps belong to [[employee-offboarding]]; return here only for the reconciliation after it lands.
- **Leave of absence, FMLA-style entitlements, and leave-driven benefit changes** → run the leave process first; a leave often *triggers* a benefits change, so come back with the leave dates.
- **A complaint about how a benefits change was handled** → that is an employee-relations matter, not an administration one.
- **Plan design or vendor selection** → a business decision above this SOP's scope.

## Workflow

### Phase 1 — Annual open enrollment (T-90 to close)

1. **Confirm the plan year parameters before anything else.** Effective dates, the enrollment window open and close dates, the plans and tiers offered, rate tables, and the default election if the employee does nothing. Get these from the carrier/plan documents in writing — do not infer them from last year.
2. **Set the calendar backwards from the deadline.** Work back from the enrollment close date to fix: the carrier file submission deadline, the payroll cutoff that makes the first deduction land in the right period, the reminder schedule, and the final day for corrections. Publish the full calendar at least 90 days ahead so employees can plan.
3. **Build the eligibility population.** Determine who is eligible this plan year from the roster (see step 9's script). Flag new hires, status changes, and anyone whose hours moved across the threshold in either direction — the crossing matters more than the level.
4. **Publish the communications pack.** Plan comparison, rates, what changes this year, how to elect, the hard close date, and what happens if they don't elect. Send reminders at T-30, T-14, T-7, and T-2. State the deadline as an absolute date and time with a timezone.
5. **Collect elections and record them with a timestamp.** Every election gets a submitted-at timestamp and a source. A verbal or chat "I'll take the PPO" is not an election until it is recorded in the system of record.
6. **Run the completeness check before closing.** Compare the elected population against the eligible population. Anyone eligible with no election is either a default-enrollment or a follow-up — decide which, in writing, and action it. Do not close the window with unexplained gaps.
7. **Close the window and freeze.** After close, changes require a documented QLE or a documented administrative correction. Record the freeze date; it is the boundary for every later audit.

### Phase 2 — New-hire enrollment

8. **Determine eligibility on the start date.** Apply the plan's hours/FTE threshold and any waiting period, and record the determination with its basis. Eligibility is a computation with an audit trail, not a judgement call.
9. **Compute the enrollment deadline and diarise it.** Use `benefits_admin.py window --event <start_date> --days <window>` to get the hard deadline and the days remaining. Set reminders at 7 days and 2 days out. The deadline is the single most important date in this workflow.
10. **Enroll and confirm.** Record the election, set up the payroll deduction with the correct effective period, submit the carrier file, and send the employee a written confirmation showing plan, tier, dependents, per-period deduction, and effective date. Confirmation is what surfaces an error while it is still fixable.
11. **Handle the non-elector explicitly.** If the window closes with no election, apply the plan's default (or record the waiver) and notify the employee in writing. Silence must never leave someone in an undefined state.

### Phase 3 — Qualifying life events

12. **Validate the event and start the clock from the event date, not the report date.** The window runs from when the event happened. Record: event type, event date, date reported, supporting documentation, and the computed deadline. Late reporting is the most common cause of a lost election — surface the remaining days immediately.
13. **Check that the event is permitted and that the change is consistent.** Not every life event opens a window, and most plans require the election change to be *consistent* with the event (adding a dependent on birth, dropping coverage on divorce). Confirm both before submitting.
14. **Collect documentation.** Marriage certificate, birth certificate, loss-of-coverage letter, divorce decree — whatever the plan requires. No documentation, no election; the carrier will reject the file and the window will have closed.
15. **Process the change and re-confirm.** Update the election, adjust the payroll deduction from the correct effective period, resubmit to the carrier, and send a written confirmation. Where the window has already expired, escalate to HR/legal with the dates — do not backdate silently.

### Phase 4 — Ongoing administration and reconciliation

16. **Reconcile on a fixed schedule** — at minimum before each carrier file submission and at each payroll close. Use `benefits_admin.py reconcile --roster <roster.csv> --carrier <carrier.csv>` to diff the three records (elected, deducted, billed) on employee ID, plan, and amount.
17. **Work the exception list, don't just produce it.** Every exception needs a named owner and a resolution: missing from carrier file, extra on carrier file, plan mismatch, amount mismatch, coverage active with no deduction, deduction running with no coverage. An exception list nobody actions is worse than no list, because it creates false assurance.
18. **Reconcile the money.** Confirm total deductions collected equal total carrier invoices for the period, and investigate any variance over a documented tolerance. Investigate retroactive corrections and their payroll impact rather than absorbing them.
19. **Keep the records audit-ready.** Plan documents, rate tables, election records with timestamps, QLE documentation, carrier files as submitted, and reconciliation output — retained per policy and per local data-protection rules.

### Phase 5 — Termination and continuation

20. **Coordinate with offboarding.** Coverage end date, the final deduction period, and the continuation-coverage notice all key off the departure record maintained in [[employee-offboarding]]. Confirm the benefits end date there rather than recomputing it.
21. **Issue the continuation notice within the statutory window.** This is a hard legal deadline with real penalties and it applies even when the employee says they don't want coverage. Track the issue date and keep proof of delivery.
22. **Verify post-termination state.** In the reconciliation that follows, confirm coverage actually ended on the recorded date, deductions stopped in the right period, and no premium is being billed for someone who has left.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Window deadlines tracked from the *report* date rather than the *event* date | Silently shortens the employee's window; election is lost | Compute from the event date; record both dates and the remaining days |
| Enrollment window closed with eligible employees unaccounted for | Undefined coverage state; disputes later | Run the completeness check before closing; document defaults and waivers |
| Verbal or chat election treated as an election | No record, no timestamp, no defence | Record in the system of record with a timestamp and source |
| Carrier file submitted without reconciling against the roster | Missed new hires, ghost members, wrong tiers | Reconcile before every submission; action the exceptions |
| Exception list produced but never worked | False assurance; the drift continues | Named owner and resolution per exception |
| Plan parameters assumed from last year | Rates, tiers, and windows change annually | Confirm in writing from the current plan documents |
| QLE change inconsistent with the event | Carrier rejection after the window has closed | Check permitted event *and* consistency before submitting |
| Missing documentation submitted anyway | Rejected file, expired window, unhappy employee | Collect required documents first; escalate rather than backdate |
| Deduction and coverage effective periods mismatched | Employee pays for coverage they don't have, or vice versa | Align to the payroll cutoff and confirm on the first payslip |
| Continuation notice late or skipped because the employee waived | Statutory penalty; applies regardless of waiver | Issue within the window; keep proof of delivery |
| Eligibility determined by judgement with no recorded basis | Unauditable and inconsistently applied | Compute it; record the inputs and the determination |
| Reconciliation done only at year end | Twelve months of drift to unwind | Reconcile at every carrier submission and payroll close |

## Bundled tool

`scripts/benefits_admin.py` — stdlib-only CLI covering the mechanical parts of this SOP. Every subcommand accepts `--help`.

```bash
# Hard deadline for a 30-day enrollment window opened on a start date
python3 scripts/benefits_admin.py window --event 2026-10-01 --days 30 --today 2026-10-19

# Eligibility determination for a roster
python3 scripts/benefits_admin.py eligibility --roster roster.csv --min-hours 30 --waiting-days 30

# Three-way reconciliation: roster (elected) vs carrier (billed)
python3 scripts/benefits_admin.py reconcile --roster roster.csv --carrier carrier.csv
```

Roster CSV columns: `employee_id,name,start_date,hours_per_week,plan,deduction`.
Carrier CSV columns: `employee_id,plan,deduction`.

`reconcile` exits `1` when exceptions exist and `0` when the records agree, so it can gate a submission step. `eligibility` flags employees whose hours sit within 5 of the threshold as `borderline` — the employees most likely to drift in and out of eligibility.

## Exit criteria

- [ ] Plan-year parameters confirmed in writing from current plan/carrier documents: effective dates, window open/close, tiers, rate table, default election.
- [ ] Backward-planned calendar published ≥90 days ahead: carrier file deadline, payroll cutoff, reminder schedule, correction deadline.
- [ ] Eligibility population built and recorded with the basis for each determination; hours-threshold crossers flagged.
- [ ] Communications pack published with an absolute close date and timezone; reminders sent at T-30, T-14, T-7, T-2.
- [ ] Every election recorded in the system of record with a submitted-at timestamp and a source.
- [ ] Completeness check run before close: every eligible employee accounted for as elected, defaulted, or waived in writing.
- [ ] Window freeze date recorded.
- [ ] New-hire eligibility computed and recorded; enrollment deadline diarised with 7-day and 2-day reminders.
- [ ] New-hire deduction set up for the correct effective period and confirmed to the employee in writing (plan, tier, dependents, per-period deduction, effective date).
- [ ] QLE validated: event type, event date, report date, permitted-and-consistent check, documentation received, deadline computed from the event date.
- [ ] QLE processed with correct effective period; carrier resubmitted; written confirmation sent; expired windows escalated rather than backdated.
- [ ] Reconciliation run before every carrier submission and payroll close; exception list produced.
- [ ] Every exception has a named owner and a documented resolution.
- [ ] Total deductions reconciled to total carrier invoices within a documented tolerance; variances investigated.
- [ ] Records retained and audit-ready: plan documents, rate tables, timestamped elections, QLE documentation, submitted carrier files, reconciliation output.
- [ ] Termination coordinated with [[employee-offboarding]]: coverage end date, final deduction period, continuation notice issued within the statutory window with proof of delivery.
- [ ] Post-termination verification confirms coverage ended on the recorded date, deductions stopped, and no premium billed for a departed employee.

## Sources

Synthesized from published benefits-administration practice and regulatory guidance: HealthCare.gov (the four categories of qualifying life events and special-enrollment-period mechanics), Selerix (open-enrollment planning and the year-round special-enrollment process — documenting the event, confirming eligibility, and processing the change), BambooHR (handling qualifying life events without missing the window), Bindbee (QLE types, special enrollment periods, and HR-system impact), and WAEPA (qualifying-life-event documentation checklists). Reconciliation, exception-handling, and confirmation practice reflects standard benefits-administration controls. **Jurisdiction warning:** eligibility thresholds, waiting periods, permitted QLEs, window lengths, continuation-coverage rules (COBRA applies to US employers at 20+ employees; other countries differ entirely), and notice deadlines vary by country, by US state, and by plan — confirm the applicable rule for each employee's work location and each plan document. This skill is administrative guidance, not legal or tax advice.
