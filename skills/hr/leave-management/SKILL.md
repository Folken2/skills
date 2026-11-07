---
name: leave-management
description: Use when managing employee leave policies and requests — PTO/vacation, sick leave, parental leave, unpaid leave, FMLA, and state-mandated leave. Covers policy definition, standardized intake, approval workflows with tiered routing, accrual tracking and carryover rules, compliance (FMLA, state leave laws), team coverage coordination, and reconciliation at termination. Triggers on "leave request", "PTO approval", "vacation tracking", "sick leave", "FMLA", "accrual policy", "time-off request", "leave balance".
version: 1.0.0
author: Nuvel Skills
---

# Leave Management

## Overview

Turn employee leave from ad-hoc email threads into a predictable, auditable process. The core principle: **a leave system is defined by its policy, not its tool.** A written policy that specific leave types, eligibility, accrual rates, notice requirements, approval authority, and compliance triggers determines whether leave runs smoothly or generates disputes, missed coverage, and compliance exposure.

Clokio and Cflow both find that most leave management problems come from the same root: a process designed for ten employees applied to a hundred without redesign. The spreadsheet and hallway-approval model breaks when headcount, locations, or regulated leave (FMLA, state paid leave) enters the picture. The fix is a standardized, documented workflow with clear routing and audit trails.

## When to use

- You are defining or updating a leave policy (types, eligibility, accrual rules, carryover).
- An employee submits a PTO/vacation, sick, parental, or unpaid leave request.
- You need to approve or deny leave with balance verification and coverage checks.
- You are managing FMLA, state-mandated paid leave, or other compliance-sensitive leave.
- You are calculating accruals, carryover, or PTO payout at termination.
- You are reconciling leave records for payroll or absence reporting.

## When NOT to use

- An employee is departing permanently and you need the full offboarding workflow (final pay, benefits termination, exit interview) → use [[employee-offboarding]].
- You are managing a leave-of-absence that involves a formal accommodation request (ADA, medical restrictions) → engage HR and legal directly; this skill covers standard leave types, not accommodation processes.
- You are tracking attendance (late arrivals, early departures, unexcused absences) — attendance discipline is a separate policy outside leave management.
- You are running an intermittent FMLA case where hours-tracking is managed by a specialized leave administration platform — this skill covers the determination and documentation workflow but not hour-level tracking within the designated period.

## Workflow

### Phase 1 — Policy foundation (define once, reference everywhere)

1. **Write the leave policy document.** A verbal or inferred policy is the most common failure mode — different managers interpret it differently, and HR cannot enforce something unwritten. The policy must cover: leave types recognized (vacation, sick, personal, parental, bereavement, jury duty, unpaid, FMLA, state-specific), eligibility by tenure and employment class, accrual rates and caps, carryover and expiry rules, advance notice requirements per leave type, blackout periods if any, approval authority per type, and compliance triggers (FMLA, state leave). Publish it in the employee handbook and reference it in every communication about leave.

2. **Define approval authority.** Every leave type needs a clear approver. Standard defaults: manager approves standard PTO up to N days; HR must approve FMLA, parental, and extended leaves; C-suite leave routes to the board or designated executive. Document who approves when the manager is on leave. For matrix-managed employees, designate the primary approving manager in advance.

### Phase 2 — Request intake

3. **Employee submits a standardized request.** The request must be submitted through a documented channel (HRIS portal, leave management system, standardized form — never Slack or hallway conversation, which produce no audit trail). The intake captures: employee name and team, leave type, start and end dates with half-day option, expected hours/days to be deducted, optional coverage or handover note, and reason field where required by law (FMLA, sick leave). Balance should display at the point of submission so the employee sees the impact before submitting.

4. **System validates the request.** Before routing for approval, validate: (a) accrual balance is sufficient for paid leave types; (b) no overlapping request exists; (c) notice period meets policy minimums (standard: 2 weeks for vacation, same-day for sick); (d) the leave type is available to the employee (by tenure, location, and class). Reject or flag requests that fail validation with a clear reason sent to the employee.

### Phase 3 — Approval workflow

5. **Route the request based on type and duration.** Standard path: employee → manager → (auto-approved if within policy thresholds). Escalated path (FMLA, parental, extended leave beyond N days, compliance-sensitive): employee → manager → HR approval. For FMLA and state leave, HR must be involved before any decision. Auto-approve non-sensitive leave (jury duty, bereavement) and short sick leave within policy limits.

6. **Manager reviews and decides.** Manager sees: the request, current balance impact, any team conflicts on the dates (approved leave of teammates, known blackout periods, minimum-staffing violations). Decision: approve, deny with reason, or request modification. Approvals must be logged with timestamp and approver identity. For denials, the employee receives the reason and is invited to propose alternative dates.

7. **Notify the employee and update records.** On approval, notify the employee, add the leave to the team calendar or absence feed, and decrement the accrual balance (if applicable). On denial, notify with the reason and any alternative-date path. All notifications produce a timestamped record.

### Phase 4 — Accrual management

8. **Set up accrual rules.** Define per leave type: accrual rate (hours per pay period or per month), maximum accrual cap, carryover limit and expiry date, and eligibility by tenure and employment class. Different employee groups (full-time vs. part-time, by location, by tenure tier) may have different accrual policies — each must be explicit. Accrual balances update automatically on the defined frequency (per pay period, monthly, annually).

9. **Handle carryover and expiry.** At the policy-defined carryover date, apply carryover limits and expire any balance above the cap. Communicate carryover and expiry in advance so employees can plan usage. Some jurisdictions mandate PTO payout or rollover — confirm the local rule rather than applying a uniform forfeit policy.

### Phase 5 — Compliance-sensitive leave

10. **Handle FMLA and state leave.** When a leave type or duration triggers FMLA (12 weeks in a 12-month period for US employers at 50+ employees) or a state paid leave mandate (CA, NY, MA, WA, OR, CO, etc.), involve HR before the decision. The process: determine eligibility (12 months/1250 hours/75-mile radius for FMLA; state-specific for state leaves), calculate entitlement (concurrent FMLA and state leave where applicable), provide required notices (eligibility, rights and responsibilities, designation notice) within statutory timelines, collect medical certification where required, track intermittent leave hours if applicable, and document every step. Missing a statutory deadline (e.g., the 5-business-day FMLA eligibility notice) creates compliance exposure — calendar these deadlines per leave case.

11. **Document the case file.** Every compliance-sensitive leave generates a case file: request, eligibility determination, notices sent, certifications received, approvals, communications, return-to-work documentation. The case file must be auditable on demand — organize it per employee, not per calendar year.

### Phase 6 — Coverage and coordination

12. **Manage team coverage.** Before approving leave that would drop below minimum staffing, surface the conflict to the manager with options: request the employee to adjust dates, arrange coverage (swap, overtime, temp), or override with HR approval. The system must show approved and pending leave on a shared calendar so managers can see conflicts before approving — not after. For planned leave, the employee should note a coverage plan at submission time.

### Phase 7 — Reconciliation and closure

13. **Reconcile leave at payroll.** At each payroll run, confirm that approved leave hours match the deduction from accrual balances and the hours submitted on the employee's timesheet. Discrepancies (leave approved but not deducted, timesheet showing leave that was never approved) go into a reconciliation queue with a clear owner.

14. **Handle leave at termination.** On termination (via [[employee-offboarding]]), calculate PTO payout for accrued but unused time per your jurisdiction's rules — some states mandate payout, others allow use-it-or-lose-it. Process the payout in the final paycheck. Record the final leave balance and payout in the departure record.

15. **Run periodic audits.** Quarterly or annually, audit that: accrual balances match payroll records, no employee has exceeded caps, compliance-sensitive leaves have complete case files, and the policy is being applied consistently. A leave audit prevents the end-of-year "my balance is wrong" disputes that erode trust.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| No written leave policy | Managers interpret it differently; HR can't enforce; inconsistent treatment | Write and publish a single policy covering all leave types and rules |
| Leave requested via Slack or verbal | No audit trail; "I told you last week" disputes | Require submission through a documented channel with a timestamped record |
| No balance check at request time | Employee requests leave they don't have; manager approves a payroll problem | Show balance at point of submission; reject insufficient-balance requests |
| FMLA eligibility notice sent late | Statutory 5-business-day deadline missed; regulator exposure | Calendar the deadline per case; send notice within the required window |
| Same approval path for all leave types | Half-day PTO and 6-week parental leave get the same scrutiny — trivial requests slowed, consequential ones rushed | Tier: auto-approve short sick/jury/bereavement; manager for standard PTO; manager+HR for compliance-sensitive |
| Coverage not checked before approval | Two team members approved for the same dates; understaffed operation | Check team calendar for conflicts before approving; flag minimum-staffing violations |
| Accrual cap and carryover not communicated | Employee expects unused time to roll over; surprise forfeit breeds resentment | Communicate carryover limits and expiry in advance; offer use-it-or-lose-it warning |
| Termination PTO payout calculated wrong | Statutory penalties in states requiring payout | Confirm the jurisdiction's rule; calculate from the employee's work location |
| Leave records scattered across tools | Audit or legal request takes hours to assemble | Centralize leave records per employee; case files for compliance-sensitive leaves |
| No periodic leave audit | Balance errors compound over time; end-of-year disputes are worse to resolve | Run quarterly audits: balances match payroll, caps enforced, case files complete |

## Exit criteria

- [ ] Written leave policy published covering types, eligibility, accrual, notice, approval authority, and compliance triggers.
- [ ] Approval authority matrix documented: who approves which leave types and durations, including manager-out-of-office routing.
- [ ] Standardized request intake channel defined with required fields per leave type.
- [ ] Every leave request is validated against balance, overlaps, notice period, and eligibility before routing.
- [ ] Approval workflow tiered by leave type and duration; auto-approval rules defined for short low-risk leave.
- [ ] Accrual rules configured per leave type with rate, cap, carryover, and expiry; balances update on schedule.
- [ ] FMLA state-leave compliance process documented: eligibility determination, statutory notices, certification, case file, return-to-work.
- [ ] Team calendar or absence feed shows approved and pending leave for coverage checks.
- [ ] Leave records reconciled at each payroll run; discrepancies in a clear queue.
- [ ] Termination PTO payout calculated per jurisdiction rules and included in final pay.
- [ ] Periodic leave audit (quarterly or annual) run and documented.
- [ ] Compliance-sensitive leave case files are complete and auditable on demand.

## Tools

- `scripts/leave-tracker.py` — standard leave management operations: initialize accrual policies from a YAML config, submit and approve requests with balance validation, report balances by employee, reconcile against payroll hours, and calculate PTO payout at termination. Run `python scripts/leave-tracker.py --help` for available commands.

## Sources

Synthesized from published leave management practice: **Clokio** (12 best practices — written policy, standard approval authority, advance notice with exceptions, multi-tiered workflows), **Cflow** (leave-request approval workflow design — standardized intake, approval routing by risk tier, SLAs, audit trails), **MangoApps** (accrual policy design, coverage limits, compliance-sensitive leave routing, termination payout), **Pulpstream** (FMLA and state leave compliance — eligibility calculation, concurrent leaves, statutory notices, case file management), **Mitratech** (multi-jurisdiction leave determination, federal/state/company policy overlay, audit trace), and **ONEHCM** (regulatory compliance, accrual tracking, policy-driven approval rules, periodic auditing). State and federal regulatory references apply to US employment law; adapt paid-leave, PTO-payout, and parental-leave rules to your jurisdiction.

**Jurisdiction warning:** FMLA applies to US private-sector employers with 50+ employees; small employers and non-US entities follow their own statutory leave schemes. State paid-leave mandates (CA, NY, MA, WA, OR, CO, CT, and others) have distinct eligibility, wage-replacement, and job-protection rules. PTO payout at termination is mandated by some states but not others. The US Department of Labor and your state labor agency are the authoritative sources for any compliance step.