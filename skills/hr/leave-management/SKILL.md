---
name: leave-management
description: Use when managing employee time-off and absence requests — PTO, sick leave, vacation, personal days. Covers the full lifecycle: request submission, accrual tracking, manager approval, blackout periods, minimum staffing, calendar integration, return-to-work after extended leave, and PTO payout coordination at departure.
version: 1.0.0
author: Nuvel Skills
---

# Leave Management

## Overview

Run time-off as a system of record, not a thread of messages. The core principle: **a leave balance is a financial liability, and every approval either draws it down or accrues it.** Accrued-but-unused PTO sits on the books as money owed — payable at departure in many jurisdictions — so an untracked day off is a bookkeeping error, not just a scheduling one.

Three rules keep the system honest:

1. **Balance before approval.** Never approve time off without checking the balance as of the *leave dates*, not today.
2. **Every decision is written and reasoned.** Denials especially — a denial with no recorded reason is indistinguishable from discrimination in a later dispute.
3. **Protected leave is not PTO.** Medical, family, military, jury, and statutory leave run on legal rules that override policy and manager discretion. Route them to HR/legal, don't process them here.

Accrual math and payout obligations connect this skill to [[hr/payroll-processor]] (unpaid-leave deductions) and [[hr/employee-offboarding]] (final PTO payout). Absence patterns that signal disengagement belong in [[hr/employee-engagement]], not in an approval queue.

## When to use

- An employee is submitting or you are processing a PTO, vacation, sick, or personal-day request.
- You are reviewing a request as a manager and need to check balance, coverage, and blackout rules.
- You are reconciling accruals — earned vs. used, carryover, year-end rollover or forfeiture.
- You are setting blackout periods or minimum-staffing thresholds for a team or season.
- Someone is returning from an extended absence and needs a structured return-to-work.
- Payroll needs unpaid-leave days for the current cycle, or offboarding needs a final PTO payout figure.

## When NOT to use

- **Protected or statutory leave** — FMLA/medical, parental, disability, military, jury duty, or local statutory entitlements → escalate to HR/legal. These carry job-protection, notice, certification, and benefits-continuation rules this workflow does not encode.
- A performance or attendance-pattern concern → address via [[hr/employee-engagement]]. Absenteeism is a management conversation, not a denial.
- The person is leaving and you need the payout as part of final pay → run [[hr/employee-offboarding]]; use step 12 here only to produce the balance figure.
- Public holidays, company-wide shutdowns, or sabbatical programs → these are calendar/policy configuration, not per-employee requests.
- The employee has no accrual policy assigned yet → fix that first in [[hr/employee-onboarding]] (policy assignment at hire), then process the request.

## Workflow

### Phase 1 — Policy and accrual baseline

1. **Confirm the applicable leave policy.** Identify the employee's leave types and rules: accrual method (per pay period, monthly, or annual front-load), rate, waiting period for new hires, maximum balance cap, carryover limit, and whether unused time is paid out at departure. Part-time and contract workers often accrue pro-rata — check before assuming. Record the policy on the employee record so every later step reads from one source.
2. **Establish the current balance.** Compute `available = opening_balance + accrued_to_date − used − pending_approved`. Pending-but-approved future leave must be subtracted, or you will approve the same day twice. Where a cap or carryover limit applies, note the date it bites — an employee at cap stops accruing, which is a silent pay cut and should be flagged to them, not discovered later.
3. **Publish the calendar constraints.** Before requests arrive, define and share: blackout periods (peak season, close of quarter, launch windows, audit periods), minimum-staffing thresholds per team or shift, notice requirements (e.g. one day's notice per day requested, longer for multi-week absences), and how conflicts are broken (seniority, first-come, rotation). Rules published in advance are policy; rules applied after the fact are favoritism.

### Phase 2 — Request and approval

4. **Submit the request.** Capture leave type, start and end dates, half-day or partial-day handling, total working days requested (excluding weekends and holidays), coverage plan or delegate, and contactability during the absence. Sick leave is typically retroactive and notified rather than requested — accept it as a logged event, and only require certification where policy and law allow.
5. **Run automated checks before human review.** Validate in this order and surface every failure to the manager at once: sufficient balance on the leave dates; notice period met; no blackout overlap; minimum staffing still satisfied after approval; no conflict with an existing approved absence in the same team. A request that fails a check is not auto-denied — it goes to the manager with the reason attached.
6. **Manager review.** The manager decides on coverage and business need, not on whether the employee "deserves" it. Decide within the policy SLA (2–3 business days is typical; sooner for imminent dates) — silence is the most common failure mode and forces employees to plan around uncertainty.
7. **Record the decision with a reason.** Approve, deny, or propose alternative dates. **Every denial needs a written, business-based reason** — minimum staffing, blackout window, insufficient balance, insufficient notice — and, where possible, an offer of alternative dates. Notify the employee in the same channel the request came in. Never leave a request in limbo: expired requests count as denials without reasons.
8. **Deduct on approval.** On approval, decrement the balance immediately and mark the days as committed. Do not wait for the leave to be taken — an undeducted approval is double-bookable. If the employee has insufficient balance and the absence still proceeds, classify the excess days explicitly as unpaid leave and flag them for step 11.

### Phase 3 — Calendar and coverage

9. **Sync to calendars.** On approval, push to the shared team calendar, set the employee's out-of-office status and auto-reply for the exact dates, and update on-call rotations, recurring meeting ownership, and any approval chains the person sits in. An approved absence that leaves them as the sole approver on a workflow will block the team — reassign it as part of the approval, not on the first day off.
10. **Confirm coverage.** Every in-flight obligation named in step 4 has a named delegate who has acknowledged it. For absences beyond about two weeks, document handover explicitly — the standard from [[hr/employee-offboarding]] applies: a document nobody has read is not a handover.

### Phase 4 — Payroll, return, and departure

11. **Feed payroll.** Before each pay run, export the period's absences: paid leave (no pay impact, balance already deducted), unpaid leave days (pro-rata deduction), and any statutory or partial-pay leave. Hand the unpaid-day counts to [[hr/payroll-processor]] as deductions. Reconcile in both directions — days paid but never approved, and days approved but never paid, are both errors worth catching before the run, not after.
12. **Reconcile accruals on a schedule.** Monthly or per pay period, recompute every balance from first principles and compare against the running ledger. At year-end, apply carryover: roll over up to the limit, and forfeit or pay out the excess per policy — after giving employees advance notice that they are about to lose time. Unnotified forfeiture is the single most common source of leave disputes.
13. **Structure the return to work after extended leave.** For absences beyond roughly two weeks: hold a return-to-work conversation on or before day one covering what changed (team, systems, priorities, process), a phased or reduced schedule where medically indicated or simply sensible, and any accommodations required. Reverse the step 9 calendar and access changes, restore on-call and approval duties on an agreed date rather than instantly, and schedule a check-in at two to four weeks. For medical returns, any fitness-for-duty requirement and any accommodation is an HR/legal matter — do not have the manager evaluate it.
14. **Hand off balances at departure.** When an employee leaves, produce the final accrued-unused balance as of the last working day and pass it to [[hr/employee-offboarding]] (Phase 3, final payroll). Whether unused PTO must be paid out — and by when — depends on jurisdiction and policy; confirm the rule rather than assuming. Freeze new requests after the notice date unless the departure plan explicitly burns down the balance.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Leave approved over chat or email, never recorded | Balances drift; no audit trail; liability is unknown | Every request goes through the system of record, even verbal ones |
| Balance checked as of today, not the leave dates | Approves time the employee hasn't accrued yet | Compute balance as of the requested dates, net of pending approvals |
| Pending-approved future leave not subtracted | The same days get approved twice | Deduct on approval, not on the first day of leave |
| Denial with no recorded reason | Reads as arbitrary or discriminatory in a dispute | Written business reason + alternative dates offered |
| Requests left unanswered until the dates pass | Silent denial; employees can't plan; trust erodes | Decide within the policy SLA; escalate stale requests |
| Blackout periods announced after requests arrive | Retroactive rules; perceived favoritism | Publish blackouts and staffing minimums before the season |
| Protected/statutory leave processed as ordinary PTO | Breaches job-protection, notice, and benefits rules | Route medical, family, military, and jury leave to HR/legal |
| Carryover forfeited without warning | Employees lose earned time; top dispute source | Notify at least a quarter ahead; report at-cap employees |
| Employee silently sitting at the accrual cap | Stops accruing — an unannounced pay cut | Flag on the balance report and prompt them to schedule time |
| Unpaid days never reach payroll | Overpayment, then an awkward clawback | Export absences before every pay run and reconcile both ways |
| Return from long leave with no re-entry plan | Avoidable errors, lost context, re-injury risk | Return-to-work conversation, phased duties, 2–4 week check-in |
| Approvals ignore who else is out | Team drops below safe staffing | Enforce minimum-staffing checks automatically at submission |
| Final PTO payout computed ad hoc at exit | Wrong final pay; statutory penalties in some jurisdictions | Produce the balance from the ledger and hand it to offboarding |

## Exit criteria

- [ ] Every employee has an assigned leave policy on record: accrual method and rate, cap, carryover limit, waiting period, and payout treatment.
- [ ] Blackout periods, minimum-staffing thresholds, notice requirements, and the conflict tie-breaker are published before the period they govern.
- [ ] Each request records leave type, dates, working-day count, coverage plan, and contactability.
- [ ] Automated checks (balance, notice, blackout, staffing, conflicts) run on every request before manager review, with failures surfaced rather than auto-denying.
- [ ] Every request reaches a decision within the policy SLA — no request expires unanswered.
- [ ] Every denial carries a written business reason, and alternative dates were offered where possible.
- [ ] Approved leave is deducted from the balance at approval time, not at the start of the absence.
- [ ] Approved absences are synced to the team calendar and out-of-office, with on-call, approvals, and meeting ownership reassigned.
- [ ] Every in-flight obligation during the absence has a named delegate who has acknowledged it.
- [ ] Unpaid-leave days are exported to [[hr/payroll-processor]] before each pay run and reconciled in both directions.
- [ ] Balances are recomputed and reconciled on a fixed cadence; discrepancies are investigated, not overwritten.
- [ ] Year-end carryover, forfeiture, or payout is applied per policy, with advance notice to affected employees.
- [ ] Extended-leave returns have a documented return-to-work plan, restored access and duties, and a 2–4 week check-in.
- [ ] Protected and statutory leave requests were routed to HR/legal, not processed as ordinary PTO.
- [ ] At departure, the final accrued-unused balance is produced from the ledger and handed to [[hr/employee-offboarding]] for final pay.

## Tools

Any HRIS or leave-tracking system that supports per-employee accrual policies, an auditable request/approval log, and a calendar push will run this workflow. Where none exists, a shared ledger works if it holds one row per request (employee, type, dates, working days, decision, reason, decided-by, decided-on) and one row per accrual event — those two tables are what steps 2, 7, 11, and 14 read from. For pay-impacting output, hand unpaid-day counts to `scripts/payroll_processor.py` in [[hr/payroll-processor]] as the `deductions` input. Structured balance exports and reconciliation reports pair well with [[backoffice/xlsx]].

## Sources

Aligned with SHRM leave management best practices: written and consistently applied leave policy, documented business-based decisions, accrual and carryover tracking as a recorded liability, structured return-to-work after extended absence, and strict separation of ordinary PTO from protected statutory leave. Coordinates with [[hr/payroll-processor]] for unpaid-leave deductions and [[hr/employee-offboarding]] for final PTO payout.

**Jurisdiction warning:** accrual minimums, paid-sick-leave mandates, carryover and use-it-or-lose-it legality, and PTO-payout-at-termination obligations vary by country and by US state — some jurisdictions prohibit forfeiture entirely and require payout on the last day. Protected leave (FMLA and equivalents, parental, disability, military, jury) carries job-protection and certification rules outside this workflow's scope. Confirm the rule for the employee's work location and involve HR/legal for anything protected.
