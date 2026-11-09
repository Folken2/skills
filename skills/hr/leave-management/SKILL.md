---
name: leave-management
description: "Use when an employee asks for time off or a leave of absence — full-cycle leave management from request to return. Covers request intake (including requests that don't say \"leave\"), eligibility assessment, classification (PTO, sick, FMLA-equivalent statutory, parental, bereavement, military, medical), medical certification, statutory notices and their deadlines, approval or written denial with appeal rights, intermittent-leave tracking, coverage planning, payroll/benefits coordination while on leave, and return-to-work. Triggers on: leave request, time off, PTO balance, sick leave, FMLA, parental leave, medical leave, intermittent leave, medical certification, return to work, fitness for duty."
version: 1.0.0
author: "Nuvel Skills"
---

# Leave Management

## Overview

Turn every absence into a classified, documented, and correctly-counted leave record. The core principle: **the statutory clock starts when the employer learns of a potentially protected reason, not when the employee fills in a form.** An employee does not have to say "FMLA" or "leave" — "I can't come in, I'm having surgery" told to a manager is enough. Failing to recognise a protected request is the single most common leave-compliance failure, and every downstream deadline is measured from that moment.

The sequencing that matters: **recognise and date-stamp the request, then assess eligibility, then classify and notify, then decide.** Classification drives which balances are consumed: paid leave usually runs concurrently with unpaid statutory leave, so the statutory entitlement is used up whether or not the time is paid. Decide classification before approval and an employee cannot double-dip; decide it afterwards and you cannot fix the counts without a dispute.

Keep medical detail out of the conversation. Certification comes from the provider, not from questioning the employee, and it is stored apart from the personnel file.

Pay and deductions while someone is on leave are run in [[hr/payroll-processor]]. This skill decides *what* the absence is and how much entitlement it uses.

## When to use

- An employee asks for time off, or tells a manager something that may be a protected reason (own or family health condition, birth/adoption, military service or caregiving, bereavement).
- You need to determine eligibility for statutory leave, or compute a PTO/sick balance from hours worked.
- A medical certification is due, overdue, incomplete, or needs recertification.
- You are tracking intermittent or reduced-schedule leave against an entitlement.
- An employee is returning from leave and needs reinstatement, fitness-for-duty clearance, or balance close-out.
- You are auditing past leave records for classification, notice timing, or counting errors.

## When NOT to use

- The employee is leaving rather than returning, or will not return when leave is exhausted → use [[hr/employee-offboarding]]. Do not offboard while a protected leave is still running.
- You are running gross-to-net, deductions, or a pay run → use [[hr/payroll-processor]]. This skill hands it the pay status and dates.
- The absence pattern is really a performance or engagement issue with no protected reason → use [[hr/employee-engagement]]. Rule out a protected reason first.
- You need a long-term or permanent backfill for the role → use [[hr/hiring]]. Temporary coverage stays here.
- A new hire is asking about leave policy during their first weeks → handle the policy walkthrough in [[hr/employee-onboarding]]; open this workflow only when there's an actual request.

## Workflow

### Phase 1 — Request intake and triage

1. **Recognise the request.** Treat any notice of absence with a possible protected reason as a leave request, whatever words were used. Managers must route these to HR the same day. A missed request does not stop the statutory clock, it only makes you late.
2. **Date-stamp and open a case.** Log in your ticketing system or the employee record: date the employer first learned, who learned it, expected start, expected duration, and whether it is continuous, intermittent, or a reduced schedule. Every notice deadline in Phase 3 counts from this stamp.
3. **Check the employee's notice.** For foreseeable leave the employee should give 30 days' notice; for unforeseeable leave, as soon as practicable. Late notice can delay foreseeable leave, but it never lets you skip the eligibility response.
4. **Triage urgency.** Emergency or same-day absences: protect the employee and the operation first, then do the paperwork. Planned leave: set the Phase 3 deadlines in the case now.

### Phase 2 — Eligibility and classification

5. **Establish employer coverage.** Record headcount and how many workweeks it held. The FMLA baseline is 50+ employees in 20+ workweeks in the current or prior calendar year. Employee eligibility also requires 50+ employees within 75 miles of the employee's worksite — check the worksite, not just the company total, or a remote employee at a small site gets approved for leave they aren't entitled to. Use the real numbers.
6. **Establish employee eligibility.** Pull months of service and hours *actually worked* in the 12 months before leave starts from the employee record. The FMLA baseline is 12 months and 1,250 hours. Scheduled or paid-but-not-worked hours don't count toward the 1,250.
7. **Classify the leave.** Assign one primary type: PTO, sick, statutory family/medical, parental, bereavement, military, or medical. Record every concurrent type too (statutory + paid sick + state leave). Designate each absence, so a single day cannot be counted against two entitlements as if they were separate.
8. **Compute balances from hours worked.** Accrual-based entitlements come from hours worked, not calendar time. California paid sick leave, for example, accrues 1 hour per 30 hours worked. Apply carryover caps and annual grants as written in policy.
9. **Run the helper.** `scripts/leave_accrual.py` (see Helper script below) gives you the accrual balance, statutory weeks remaining, and the eligibility decision. Attach its output to the case.

### Phase 3 — Documentation and statutory notices

10. **Issue the eligibility notice within 5 business days** of the Phase 1 date stamp (DOL WH-381 in the US). Include rights and responsibilities. Date-stamp the send. This is the most often missed deadline in leave compliance.
11. **Request certification from the provider, not the employee's story.** Send the certification form with a return date at least 15 calendar days out, or longer if the employee is making diligent, good-faith efforts. Do not ask about diagnosis, symptoms, or prognosis beyond what the form asks. If the certification is incomplete, tell the employee in writing what is missing.
12. **Store medical documents separately.** Keep certifications in a confidential medical file with restricted access, never in the general personnel file or a manager's inbox.
13. **Issue the designation notice** once you have enough information. State whether the leave is designated as statutory, how much entitlement it will use, and that paid leave runs concurrently where your policy requires it.

### Phase 4 — Decision, coverage and payroll/benefits coordination

14. **Decide in writing.** Approvals state type, dates, entitlement consumed, and pay status. Denials state the specific reason (failed eligibility test, insufficient balance, certification not returned) and the appeal or grievance path with its deadline. A verbal "no" is not a decision.
15. **Re-check before you deny.** Before denying for statutory ineligibility, check state/local leave, accrued PTO or sick time, and disability accommodation. Ineligible for one regime does not mean ineligible for all.
16. **Plan coverage without exposing the reason.** With the manager, agree who covers what, handover dates, and the out-of-office message. Tell the team "on leave", nothing more. Long or uncertain absences may need a temporary hire through [[hr/hiring]].
17. **Hand pay and benefits to payroll.** Send [[hr/payroll-processor]] the leave type, dates, paid/unpaid split, the PTO hours applied concurrently, and any short-term disability offset. Keep group health coverage on the same terms as if the employee were working. Agree in writing how the employee's share of premiums gets paid during unpaid leave.

### Phase 5 — Tracking during leave

18. **Track intermittent leave in small increments.** Record each absence by date and duration in increments no larger than 15 minutes, or to the minute if your payroll can. Convert to weeks using the employee's normal workweek, not a standard 40 hours.
19. **Re-run the entitlement count after each absence.** Update weeks used and remaining with the helper, and warn the employee in writing before the entitlement runs out, not after.
20. **Handle changes formally.** Extensions, early returns, and changes in pattern go through the same classification and, where allowed, recertification. Don't grant an extension informally by email.
21. **Retain records.** Keep dates, hours, notices, and certifications for at least 3 years.

### Phase 6 — Return to work and close-out

22. **Request fitness-for-duty only where you always do.** For leave covering the employee's own serious health condition, ask for a fitness-for-duty certification only if you have a uniformly applied practice of requiring it and said so in the designation notice.
23. **Reinstate to the same or an equivalent role.** Same or equivalent pay, benefits, shift, and location. Seniority and benefits accrued before leave are retained. Accrual *during* unpaid leave is not required unless your policy grants it.
24. **Close the balances.** Recompute and record final statutory weeks used, PTO/sick hours consumed, and remaining balances. Send the employee a written summary.
25. **Close the case.** Notify [[hr/payroll-processor]] of the return-to-pay date and lift any benefit-premium arrangements. If the employee does not return, move them to [[hr/employee-offboarding]] and record the reason.

### Helper script

`scripts/leave_accrual.py` uses only the Python standard library. It always produces the same output for the same input and needs no HRIS. Run `python3 scripts/leave_accrual.py --help` for every flag. Add `--json` for machine-readable output. Exit codes: `0` OK/approve, `2` blocked/deny, `1` usage error.

- `accrual --hours-worked H [--rate-per 30] [--carried-over C --carryover-cap X] [--annual-grant G] --used U --request-hours R` computes balance = accrued + carried over − used, and returns exit 2 if the request would go negative.
- `entitlement --period-start YYYY-MM-DD [--entitled-weeks 12|26] --continuous START:END --intermittent DATE:MINUTES [--intermittent-file f.csv] [--hours-per-week 40] [--workdays mon,...]` reports weeks entitled, used, and remaining.
- `decide --employer-size --employer-workweeks --months-employed --hours-prior-year --requested-weeks --weeks-remaining --certification received|pending|not-required` returns `ELIGIBLE`, `NEEDS_CERTIFICATION`, `INSUFFICIENT_BALANCE`, or `NOT_ELIGIBLE`. Every fact is a required flag. Thresholds default to the FMLA values and can be overridden.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Waiting for the employee to say "FMLA" or fill in a form | The clock started when the manager heard the reason; notices go out late | Train managers to route any possible protected reason to HR the same day |
| Eligibility notice sent after 5 business days | The most common statutory miss; it weakens every later designation | Date-stamp intake; issue the notice from the case deadline, not when convenient |
| Manager asks about the diagnosis | Privacy and discrimination exposure; poisons the relationship | Send the certification form to the provider; ask only what the form asks |
| PTO approved separately from statutory leave | Employee double-dips; entitlement counts become disputable | Designate concurrently; one absence reduces every applicable balance |
| Balances estimated from calendar months | Accrual is earned per hour worked; numbers won't survive audit | Compute from hours worked with `scripts/leave_accrual.py` |
| Intermittent absences logged in half or whole days | Overcharges the employee's entitlement; noncompliant tracking | Track in ≤15-minute increments against the employee's normal workweek |
| Verbal denial with no reason | No record, no appeal path; hard to defend | Written denial with the specific reason and the appeal/grievance route |
| Fitness-for-duty demanded from one employee only | Selective requirement looks like retaliation | Require it only under a uniformly applied, pre-notified practice |

## Exit criteria

- [ ] Case record shows the date the employer first learned of the reason, and who learned it.
- [ ] Eligibility notice issued within 5 business days of that date, date-stamped in the case.
- [ ] Employer-coverage and employee-eligibility inputs (headcount, workweeks, months, hours worked) are recorded with their source, and `scripts/leave_accrual.py decide` was run on them, with output attached.
- [ ] Leave classified with a primary type and every concurrent entitlement listed.
- [ ] Certification requested with a return date at least 15 calendar days after the request, and stored in a separate restricted medical file.
- [ ] Designation notice issued, stating entitlement to be used and concurrent paid leave.
- [ ] Decision issued in writing. Any denial names the specific reason and the appeal path.
- [ ] Balance arithmetic recomputed with `scripts/leave_accrual.py accrual` / `entitlement` and matches the employee record. No balance is negative.
- [ ] Intermittent absences logged by date in increments of 15 minutes or less.
- [ ] Payroll handoff sent to [[hr/payroll-processor]] with dates, paid/unpaid split and benefit-premium arrangement, and acknowledged.
- [ ] On return: employee reinstated to the same or an equivalent role, fitness-for-duty requested only under the documented uniform practice, and a final balance summary sent in writing.
- [ ] Records retained with a disposal date at least 3 years out.

## Sources

Synthesized from published leave-administration practice: the US Department of Labor Wage and Hour Division's FMLA guidance and forms (WH-380 certification, WH-381 eligibility notice, WH-382 designation notice), including coverage and eligibility thresholds, notice timing, the 15-day certification window, intermittent-leave increments, concurrent paid leave, job restoration, fitness-for-duty, and recordkeeping. Also California Labor Commissioner paid-sick-leave guidance on hours-worked accrual, and HR practitioner guidance on manager recognition of leave requests and medical-information confidentiality. Pay mechanics live in [[hr/payroll-processor]]; separation after leave lives in [[hr/employee-offboarding]].

**Jurisdiction warning:** the thresholds, durations, and deadlines above are the US federal FMLA baseline, plus one state accrual example. US states and cities add their own leave laws, often with lower thresholds, paid benefits, or broader covered relationships. Other countries use entirely different statutory leave regimes. Confirm the rule for the employee's work location and apply the most generous one that applies. This skill and its script do the procedure and the arithmetic. They are not legal advice. Involve HR/legal on denials, terminations near or after leave, and accommodation questions.
