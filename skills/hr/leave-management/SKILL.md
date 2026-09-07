---
name: leave-management
description: "Use when an employee needs to request time off, when a manager needs to approve or deny leave, or when HR needs to track leave balances, accruals, and compliance. Handles PTO, vacation, sick leave, parental leave, unpaid leave, and mandated leave types. Triggers on: leave request, PTO request, time off, vacation request, sick leave, FMLA, parental leave, absence management."
version: 1.0.0
author: "Nuvel Skills"
---

# Leave Management

## Overview

Move a time-off request from submission to a recorded, paid-correctly outcome without losing the audit trail. The core principle: **leave is a balance transaction, not a conversation.** Every approval moves hours out of an accrued balance, changes what payroll owes, and may start a statutory clock. Verbal "sure, take Friday" approvals are the root cause of nearly every leave dispute — the balance never moved, payroll never saw it, and nobody can reconstruct who agreed to what.

Three things must stay in sync at all times: **the balance, the calendar, and payroll.** If a request is approved but the balance isn't decremented, you will over-grant. If the balance moves but payroll doesn't see it, you will pay wrong. If neither reaches the calendar, coverage fails silently.

Statutory leave (FMLA, parental, jury duty, medical, and their non-US equivalents) is a separate track that runs *alongside* the ordinary PTO workflow — it has its own eligibility test, notice rules, documentation, and job-protection guarantees. Never collapse it into "vacation."

## When to use

- An employee is requesting time off of any kind — PTO, vacation, sick, personal, parental, bereavement, unpaid.
- A manager needs to review, approve, deny, or modify a pending request.
- You need to check a leave balance, projected accrual, or carryover before committing to dates.
- Coverage needs planning for an absence, or two requests collide on the same dates.
- HR needs to track a statutory leave (FMLA or local equivalent), its notices, and its remaining entitlement.
- You are reconciling leave records against payroll, or auditing balances at period/year end.

## When NOT to use

- A new hire's initial leave-policy briefing and starting-balance setup → part of [[hr/employee-onboarding]].
- A departure with a final accrued-PTO payout, or leave that never returns → [[hr/employee-offboarding]] owns the payout and the close-out.
- Chronic absence being handled as a performance or engagement issue (patterns, disengagement, burnout signals) → [[hr/employee-engagement]]. Denying leave is not a performance tool.
- Actually paying out leave, computing gross-to-net, or issuing paystubs → [[hr/payroll-processor]]. This skill produces the leave input; it does not run payroll.
- Disability accommodation, workers' compensation, or a disciplinary suspension — related to absence but governed by separate legal processes. Escalate to HR/legal.

## Workflow

### Phase 1 — Leave request

1. **Capture the request in writing.** Required fields: employee, leave type, first and last day absent, working days requested, whether partial days apply, and a return-to-work date. Reason detail is required for statutory leave, optional for PTO — do not demand medical specifics you have no right to hold.
2. **Classify the leave type correctly.** PTO/vacation, sick, personal, bereavement, parental, jury/civic, unpaid, or a statutory type. Type determines which balance is charged, whether it is paid, what documentation is needed, and whether a legal clock starts. Misclassification is the single most expensive error in this workflow — fix it now, not at payroll close.
3. **Check the balance before promising anything.** Compare requested days against the *available* balance as of the leave dates, not today's balance — include accrual that will vest before the leave and subtract already-approved future leave. Flag negative-balance requests explicitly: they are a policy decision (advance, unpaid conversion, or denial), never a silent approval.
4. **Validate dates and notice.** Confirm working days versus holidays and weekends, honor the notice period in policy (e.g. 2 weeks for planned leave), and check blackout periods or peak-season restrictions. Sick and emergency leave bypass notice by design — do not enforce advance notice against them.
5. **Route to the right approver.** Direct manager by default; add HR for statutory leave, extended absence, unpaid leave, or anything over the policy threshold. Record the routing so the audit trail shows who *should* have decided, not just who did.

### Phase 2 — Approval workflow

6. **Manager reviews within the policy SLA.** Set and honor a decision deadline (commonly 2–5 business days). Unanswered requests are the top employee complaint in leave systems; an expired request should escalate, not expire silently.
7. **Run the coverage and capacity check.** Look at who else is out on the same dates, minimum staffing for the team, in-flight deadlines, on-call and customer-facing obligations, and any team-wide cap on simultaneous absences. This is the only legitimate business reason to deny discretionary leave.
8. **Decide, and record the decision with a reason.** Approve, deny, or propose alternative dates. A denial must state the business reason and, where possible, offer alternatives — an unexplained denial reads as arbitrary and is what gets escalated. Statutory leave that meets eligibility is **not** discretionary: you may manage the timing where the law allows, but you cannot deny the entitlement.
9. **Commit the transaction.** On approval, do all four in one motion: decrement the balance, write the calendar entry, notify the employee, and queue the payroll input for [[hr/payroll-processor]]. Approval that only exists in an email thread is the failure mode this entire skill exists to prevent.

### Phase 3 — Pre-leave prep

10. **Build a handover plan for absences over 3 days.** Name a specific covering person for each in-flight responsibility — projects, approvals, on-call, recurring meetings, customer contacts. An unassigned item is not covered. Short absences need only a delegate for approvals.
11. **Set the out-of-office and calendar blocks.** Auto-reply with return date and the named covering contact, calendar blocked for the full range (including travel days), meeting series declined or delegated, and the team notified in whatever channel they actually read.
12. **Confirm readiness before the last working day.** Handover walked through with the covering person, access delegated where needed, and any hard deadline inside the absence window either moved or explicitly owned by someone else.

### Phase 4 — During leave

13. **Record one emergency contact path and keep it narrow.** Agree in advance what counts as a genuine emergency and who may initiate contact — the manager, not the whole team.
14. **Protect the boundary.** Do not route routine work, approvals, or "quick questions" to someone on leave. Interrupted leave is not rest, and in some jurisdictions contacting an employee on statutory or protected leave carries real legal exposure. If work genuinely could not be covered, that is a coverage-planning failure to fix in step 10, not a reason to call.

### Phase 5 — Return to work

15. **Run a return check-in on day one.** Short manager conversation: confirm the actual return date matched the plan, hand back the delegated responsibilities, and flag anything that changed. For extended or medical leave, confirm any fitness-for-duty or phased-return requirements before resuming full duties.
16. **Structure the catch-up.** Protect the first day for triage rather than meetings, and have the covering person brief on what happened and what is still open. A returning employee buried in a backlog erases the value of the leave.
17. **Reconcile and close the record.** Compare days actually taken against days approved and correct the balance for early returns, extensions, or days converted to sick leave. Push the final figures to payroll, mark the request closed, and archive it.

### Ongoing — Accrual tracking & recordkeeping

18. **Maintain balances on a defined cycle.** Post accruals on the policy schedule (per pay period, monthly, or annual grant), apply the accrual cap, and reconcile the balance ledger against approved-and-taken leave at least monthly. Every balance change should trace to a dated transaction.
19. **Manage carryover and expiry deliberately.** Apply the carryover cap and expiry date at period end, and warn employees well before use-it-or-lose-it deadlines. Note that in several jurisdictions accrued vacation is earned wages that cannot simply be forfeited — confirm the local rule before expiring anything.
20. **Track statutory leave separately with its own clock.** For FMLA (US: 12 weeks in a 12-month period for eligible employees at covered employers) or the local equivalent, track eligibility, entitlement used and remaining, the measurement period, required notices and their deadlines, certification/recertification, benefit continuation during leave, and job-protection status. Keep medical documentation in a confidential file separate from the personnel file.
21. **Keep the audit trail complete.** Retain request, decision, decision-maker, dates, balance movement, and supporting documentation for the retention period your jurisdiction requires. Review policy annually against changing statutory minimums and publish the current version where employees can actually find it.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Verbal or DM approval, never recorded | Balance never moves; payroll pays wrong; no audit trail | Every approval is a written transaction (step 9) |
| Balance checked as of today, not the leave dates | Ignores pending accrual and already-approved future leave | Project the balance to the leave date range |
| Requests sitting unanswered past the SLA | Employee can't plan; top source of leave complaints | Decision deadline with auto-escalation, not silent expiry |
| Statutory leave treated as discretionary PTO | Denying a legal entitlement; real liability | Separate track, separate clock, eligibility test first (step 20) |
| Sick leave held to the advance-notice rule | Notice is impossible for illness; pushes people to work sick | Exempt sick/emergency leave from notice requirements |
| Approving without a coverage check | Team left short mid-deadline; leave gets recalled | Capacity and conflict check before deciding (step 7) |
| Contacting the employee during leave for routine work | Erases the rest; legal exposure on protected leave | Narrow emergency-only contact path (steps 13–14) |
| Absence over 3 days with no named handover owner | Work silently stalls; returning employee inherits a mess | Named covering person per responsibility (step 10) |
| Denial issued with no stated reason | Reads as arbitrary; escalates and damages trust | State the business reason; offer alternative dates |
| Balance never reconciled against days actually taken | Drift compounds into over-grants and payout disputes | Reconcile at return and monthly (steps 17–18) |
| Medical certifications filed in the personnel file | Confidentiality breach in most jurisdictions | Separate confidential medical file |
| Carryover silently expired at year end | Forfeits earned wages in some jurisdictions | Warn early; confirm the local forfeiture rule first |

## Exit criteria

- [ ] Request captured in writing with employee, leave type, dates, working days, and return date.
- [ ] Leave type correctly classified; paid/unpaid status and documentation requirements confirmed.
- [ ] Available balance projected to the leave dates; any negative balance handled as an explicit policy decision.
- [ ] Notice period, blackout dates, and working-day count validated (sick/emergency leave exempted from notice).
- [ ] Request routed to the correct approver, with HR looped in for statutory, unpaid, or extended leave.
- [ ] Decision made within the policy SLA and recorded with decision-maker, date, and reason.
- [ ] On approval: balance decremented, calendar entry created, employee notified, payroll input queued — all four done.
- [ ] Absences over 3 days have a handover plan with a named covering person per responsibility.
- [ ] Out-of-office, calendar blocks, and team notification are in place before the last working day.
- [ ] Emergency-contact path agreed and narrow; no routine work routed to the employee during leave.
- [ ] Return check-in held; delegated responsibilities formally handed back; fitness-for-duty confirmed where required.
- [ ] Days taken reconciled against days approved; balance corrected for early return or extension.
- [ ] Final leave figures delivered to payroll and the request marked closed.
- [ ] Accruals posted on schedule, caps applied, and the balance ledger reconciled for the period.
- [ ] Statutory leave tracked separately: eligibility, entitlement used/remaining, notices issued on deadline, job protection and benefits continuation confirmed.
- [ ] Full audit trail archived per the retention policy; medical documentation held in a separate confidential file.

## Sources

Synthesized from published absence-management practice: SHRM (leave policy design, PTO accrual and carryover, absence-management guidance), the US Department of Labor Wage and Hour Division (FMLA eligibility, the 12-week entitlement, employer notice and certification obligations), and vendor practice documentation from BambooHR, Rippling, and Factorial on request routing, approval SLAs, coverage checks, and balance reconciliation. Handover and coverage-planning patterns carry over from [[hr/employee-offboarding]]; starting balances and policy briefing are set in [[hr/employee-onboarding]]; payout mechanics belong to [[hr/payroll-processor]].

**Jurisdiction warning:** statutory minimums, accrual and carryover rules, forfeiture of earned vacation, sick-leave mandates, parental-leave entitlements, and job-protection guarantees vary by country and by US state. FMLA specifically applies only to covered employers (50+ employees) and eligible employees (12 months of service, 1,250 hours); other countries have entirely different regimes. Confirm the rule for the employee's work location and involve HR/legal on medical, disability, and protected-leave questions — do not apply these steps as universal law.
