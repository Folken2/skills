---
name: compliance-checks
description: "Use when HR needs to verify employment eligibility (I-9, E-Verify), track mandatory compliance training completion, audit policy acknowledgments, review recordkeeping and retention, or prepare for an audit or inspection. Covers US federal employment compliance (I-9, E-Verify, W-4, OSHA, harassment prevention, data privacy). Triggers on: I-9 audit, E-Verify, compliance check, training compliance, policy acknowledgment, recordkeeping, audit prep, inspection readiness."
version: 1.0.0
author: "Nuvel Skills"
---

# Compliance Checks

## Overview

Run employment compliance as a **scheduled, auditable practice — not a fire drill.** The organizations that fail inspections are rarely the ones with bad intent; they are the ones that only look at their files after a Notice of Inspection arrives, when the correction window has already closed and every fix now looks like a cover-up.

The **Form I-9 is the most commonly audited employment record and the most commonly errored.** Substantive errors carry per-form civil penalties, and a typical unaudited employer has errors on a large share of forms — missing dates, unsigned attestations, over-documentation, expired reverifications. Most are cheap to fix *before* an inspection and expensive after.

Two rules govern everything below. **Correct in ink, never in secret:** a good-faith correction — single line through the error, correct entry, initial, date — is a defense; an erased, backdated, or silently re-created form is evidence of bad faith and converts a paperwork violation into an alleged knowing one. And **evidence beats assertion:** "everyone did the training" is not a record. If you cannot produce a dated, attributable artifact, it did not happen.

## When to use

- Running a periodic (annual or semi-annual) internal I-9 audit, or reviewing E-Verify case status and open cases.
- Tracking completion of mandatory training — harassment prevention, OSHA/safety, data privacy, code of conduct, anti-discrimination, cybersecurity — and chasing overdue re-train cycles.
- Verifying that every active employee has acknowledged the handbook and required policies, including re-signature after a policy update.
- Auditing personnel files, retention schedules, medical-record separation, and the destruction calendar.
- Preparing for a known audit, inspection, or client/customer compliance review, or building a compliance scorecard for leadership.
- Remediating a gap surfaced by any of the above and documenting what was fixed and when.

## When NOT to use

- Completing a new hire's **initial** I-9, W-4, and first policy acknowledgments → [[hr/employee-onboarding]] owns first-time collection. This skill audits what onboarding produced.
- Applying the **retention cutoff** at a departure — when the I-9 and personnel file for a terminated employee may be destroyed → [[hr/employee-offboarding]] owns the offboarding record close-out; this skill audits whether that cutoff was applied correctly across the population.
- FMLA eligibility, notices, certifications, and medical documentation handling → [[hr/leave-management]].
- Culture, ethics-climate, or speak-up survey work → [[hr/employee-engagement]]. Compliance measures records; engagement measures behavior.
- **Responding to an active government inspection, subpoena, charge, or complaint.** Stop and involve counsel. Do not start a self-audit after receiving a Notice of Inspection — a correction made in that window is not made in good faith.
- Immigration sponsorship, visa petitions, or work-authorization strategy for a specific individual — that is immigration counsel's work, not an HR checklist.

## Workflow

### Phase 1 — I-9 & E-Verify compliance

1. **Build the reconciliation list first.** Pull the active-employee roster (all employees hired after Nov 6, 1986) and the I-9 file, and reconcile in both directions. Two findings matter most: an active employee with **no I-9 at all** (highest severity — remediate immediately, dated today, never backdated) and an I-9 on file for someone who is not an employee.
2. **Confirm the file is properly segregated.** I-9s belong in a separate binder or system — never inside personnel files. Segregation limits what an inspector may see and is itself a control.
3. **Review Section 1 (employee).** Every field complete; citizenship/immigration status attested with exactly one box checked; A-Number/USCIS number present where the status requires it; employee signature present and **dated no later than the first day of employment**; preparer/translator certification completed if used.
4. **Review Section 2 (employer).** Document title, issuing authority, number, and expiration recorded; **List A alone, or one from List B and one from List C — never both a List A and List B/C** (over-documentation is a violation); employer signature, title, business name and address present; certification dated **within 3 business days of the start date**; the first day of employment recorded and matching the HRIS start date.
5. **Flag the classic error set.** Missing dates or signatures, wrong date format, mismatched start dates, blank Section 2 lines, transposed document numbers, and expired List B documents accepted at hire. Classify each as **technical** (correctable, usually no penalty if fixed) or **substantive** (missing signature, missing Section 2, no form at all — penalty exposure).
6. **Correct in good faith and on the record.** Single line through the error, enter the correct information, initial and date the correction with the *actual* current date. Employees correct Section 1; the employer corrects Section 2. If a form is unsalvageable, complete a new one, attach it to the original, and write a dated memo explaining why — never destroy or backdate the original.
7. **Check reverification.** Build a tickler of employment authorizations expiring in the next 90–120 days and reverify in Supplement B **before** expiry. Do **not** reverify US citizens, non-citizen nationals, lawful permanent residents, or List B identity documents — unnecessary reverification is itself discriminatory. Rehires within the allowed window may use Supplement B instead of a new form.
8. **Review E-Verify status** (if enrolled). Every required case created within 3 business days of the start date; **no open, unclosed, or expired cases**; Tentative Nonconfirmations handled with proper employee notice and a documented contest path; Final Nonconfirmations and case-closure reasons recorded. Verify you did not run E-Verify selectively on some hires and not others.
9. **Verify remote-inspection eligibility if used.** The alternative (remote) document-examination procedure is available only to employers enrolled and in good standing in E-Verify who use it consistently for a site or for all remote hires. Confirm the eligibility box on the form is checked, that legible copies of every examined document are retained, and that in-person and remote treatment is not split in a way that disadvantages any group.
10. **Log every finding** with employee, form section, error, severity, action taken, and date. This log is the deliverable — Phase 5 consumes it.

### Phase 2 — Mandatory training compliance

11. **Define the required-training matrix before measuring anything.** For each training, record: the trigger (all employees / managers only / role-based), the source of the requirement (federal, state, contractual, insurer, internal), the new-hire deadline, and the recurrence cycle. Typical set — **harassment prevention** (state-mandated in several states, commonly annual or biennial with a separate manager version), **safety/OSHA** (role- and hazard-specific, some standards require annual refresher), **data privacy** (GDPR/CCPA/HIPAA as applicable), **code of conduct** (annual), **anti-discrimination/EEO**, and **cybersecurity/security awareness** (commonly annual, often required by cyber insurance or SOC 2).
12. **Measure completion against the correct denominator.** Compute completion rate per training as completed ÷ *currently assigned and past due*, split by new-hire cadence versus annual cadence. Excluding people on leave or hired last week inflates the number; counting them as failures does too. State the denominator explicitly in the scorecard.
13. **Chase the overdue list, not the aggregate.** Produce a per-employee overdue list with days past due, escalate to managers at a defined threshold, and re-check. A 92% completion rate is meaningless if the missing 8% is every manager in the highest-risk function.
14. **Verify the evidence, not the dashboard.** Each completion must have a dated, attributable record — LMS certificate, signed attestation, or attendance roster with the curriculum version. Confirm the content version actually satisfies the jurisdiction's requirement (duration, interactivity, manager-specific content) where the mandate specifies it.
15. **Reconcile assignments against the current roster.** New hires assigned within the required window, role changes triggering newly required training, and departures removed from the denominator. Stale assignment lists are the most common cause of a false compliance reading.

### Phase 3 — Policy acknowledgment audit

16. **Inventory the policies requiring acknowledgment** with each one's current version and effective date: employee handbook, code of conduct, data privacy, IT acceptable use, plus role-specific policies (expense/travel, trading or conflict-of-interest, safety procedures, client confidentiality, AI-tool usage).
17. **Reconcile acknowledgments against the active roster, per policy and per version.** The finding is not "has an acknowledgment" — it is "has acknowledged the **current version**." Produce the gap list by employee × policy.
18. **Confirm each acknowledgment is a valid record:** employee identity, policy name **and version**, date, and a signature or auditable e-signature event. An undated acknowledgment, or one that does not name the version, proves nothing about what was agreed to.
19. **Enforce re-acknowledgment on material policy updates.** When a policy changes materially, re-issue with a stated deadline and track to completion — do not assume the original signature carries forward. Retain superseded versions with their date ranges so you can prove what was in force at any past moment.
20. **Close the loop on non-signers.** Escalate through the manager, and record refusals explicitly with date and reason. A documented refusal is a defensible record; silence is not.

### Phase 4 — Recordkeeping & retention audit

21. **Audit personnel file structure and separation.** Confirm four distinct files: the general personnel file; a **confidential medical file** (ADA/FMLA/health records — legally required to be separate); an I-9 file; and, where applicable, a separate investigations file. Confirm access is restricted to those with a business need and that access is logged where the system supports it.
22. **Apply the I-9 retention rule precisely.** Retain for **3 years after the date of hire, or 1 year after the date employment ends — whichever is later.** Compute the date for every terminated employee, purge those past it, and keep an eligible-to-purge report. Over-retaining I-9s expands audit exposure for no benefit.
23. **Check the other retention clocks** against the applicable rule and the longest-applicable jurisdiction: payroll and time records, tax records, benefits and ERISA records, applicant/recruiting records, OSHA logs, and training records. Where a contract, insurer, or state rule is longer than the federal minimum, the longer clock wins.
24. **Verify medical and sensitive-data confidentiality controls.** Medical records never in the personnel file; benefits, disability, and leave documentation restricted; SSNs and identity documents encrypted or locked; third-party processors (HRIS, payroll, LMS) covered by a current agreement. Include the data-privacy obligations that apply to *employee* data, not only customer data.
25. **Run the destruction schedule as a real process.** Maintain a written retention schedule, run destruction on a defined cadence, log what was destroyed and when, use a secure method, and — critically — **suspend destruction under a legal hold** for any record touched by pending or anticipated litigation, a charge, or an investigation. Destroying under hold is worse than any retention gap.

### Phase 5 — Inspection readiness & remediation

26. **Produce a compliance scorecard** — one row per area (I-9, E-Verify, each training, each policy, retention) with: population, compliant count, gap count, completion rate, and a severity rating. Show the denominator and the as-of date on every row.
27. **Prioritize gaps by risk, not by count.** Severity is (likelihood of being examined) × (penalty or harm if found). Missing I-9s, unclosed E-Verify cases, destruction under legal hold, and medical records in personnel files outrank a batch of missing initials. Fix the highest-severity items first, even if the count is small.
28. **Remediate with an owner and a date per gap.** Corrections in good faith and on the record; missing forms completed today with today's date; overdue training assigned with a deadline; acknowledgments re-issued. Never backdate anything, and never treat a remediation as complete until the artifact exists.
29. **Document the audit itself.** Record scope, method, date, who performed it, findings by severity, actions taken, and what remains open with a target date. A documented self-audit with an honest open-items list is strong evidence of good faith; an undocumented one earns you nothing.
30. **Assemble the inspection-ready package and set the next review date.** Know where each record class lives and who can produce it, keep a designated responder and a "call counsel first, produce nothing before the statutory response window" instruction in writing, and schedule the next cycle (I-9 and policy acknowledgments annually; training continuously with quarterly review). Put it on the calendar now — the schedule is what makes this a practice instead of a fire drill.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Self-audit started *after* a Notice of Inspection arrives | Corrections in that window aren't good faith; can look like concealment | Audit on a schedule; once notice arrives, stop and call counsel |
| Errors erased, whited out, or a "clean" form re-created | Destroys the audit trail; a paperwork issue becomes an alleged knowing violation | Line through, correct, initial, date with the actual date (step 6) |
| Missing form completed with a backdated signature | Falsification — far worse than the original gap | Complete today, date today, attach a dated memo explaining why |
| Both a List A **and** List B/C documents collected | Over-documentation is itself an I-9 violation | List A **or** List B + List C, never both (step 4) |
| Reverifying permanent residents or List B identity documents | Unnecessary reverification is discriminatory | Reverify only expiring employment authorization (step 7) |
| I-9s filed inside personnel files | Exposes unrelated records to inspectors; weakens confidentiality | Separate I-9 file; separate confidential medical file (steps 2, 21) |
| E-Verify run for some hires but not others | Selective verification is a discrimination finding | Consistent application for all required hires (step 8) |
| Open or expired E-Verify cases left unclosed | A standing, visible compliance failure in the system of record | Close every case; document TNC notice and contest path |
| Completion rate reported without stating the denominator | Excluding the overdue population manufactures a false green | Completed ÷ assigned-and-past-due, denominator stated (step 12) |
| Acknowledgment on file, but for a superseded policy version | Proves agreement to text no longer in force | Track acknowledgment by policy **version**; re-sign on update (steps 17–19) |
| Records kept "just in case," forever | Over-retention expands discovery and audit exposure and may breach privacy rules | Written retention schedule with actual, logged destruction (step 25) |
| Records destroyed on schedule while a claim is pending | Spoliation — sanctions far exceed any retention benefit | Legal hold suspends destruction, no exceptions (step 25) |
| Medical or leave documentation in the general personnel file | Confidentiality breach under ADA and similar rules | Separate confidential medical file with restricted access (step 24) |
| Audit run but never written up | No provable good faith; findings resurface next cycle | Document scope, findings, actions, open items, next date (step 29) |
| One-off cleanup with no next review scheduled | Drift restarts immediately; next audit is again a fire drill | Set the next cycle date before closing (step 30) |

## Exit criteria

- [ ] Active roster reconciled against the I-9 file in both directions; every employee hired after Nov 6, 1986 has a form, and missing forms are completed with today's date.
- [ ] Sections 1 and 2 reviewed on every in-scope form; each error classified technical vs substantive and logged with employee, section, and severity.
- [ ] Corrections made in good faith and on the record (line-through, initial, current date); no erasures, no backdating, and any replacement form attached to the original with a dated memo.
- [ ] Document-collection reviewed for over-documentation (List A **or** B+C) and for List B documents that were expired at hire.
- [ ] Reverification tickler built for authorizations expiring in the next 90–120 days; no unnecessary reverification of citizens, LPRs, or List B documents.
- [ ] E-Verify reviewed: all required cases created within 3 business days, zero open or expired cases, TNC notice and contest steps documented, application confirmed consistent across hires.
- [ ] Remote/alternative document examination confirmed eligible and consistently applied, with legible copies of examined documents retained.
- [ ] Required-training matrix defined (trigger, source, new-hire deadline, recurrence) and completion measured per training with the denominator stated.
- [ ] Per-employee overdue training list produced, escalated to managers, and re-checked; completions backed by dated, attributable evidence of the correct content version.
- [ ] Policy inventory current with version and effective date; every active employee reconciled against the **current version** of each required policy.
- [ ] Acknowledgment records verified to include employee, policy name, version, date, and signature/e-signature event; re-acknowledgment issued and tracked after material updates; refusals documented.
- [ ] Personnel, confidential medical, I-9, and investigation files confirmed separate, with access restricted to business need.
- [ ] I-9 retention computed per employee (later of 3 years from hire or 1 year from termination); eligible-to-purge list produced and executed.
- [ ] Retention clocks verified for payroll, tax, benefits, applicant, OSHA, and training records against the longest applicable rule.
- [ ] Destruction schedule executed and logged with a secure method; legal holds identified and destruction suspended for every affected record.
- [ ] Compliance scorecard produced per area with population, gaps, rate, severity, and as-of date; gaps ranked by risk, not count.
- [ ] Every gap has a named owner and a due date; completed remediations have a verifiable artifact.
- [ ] Audit documented (scope, method, date, auditor, findings by severity, actions, open items) and the next review date scheduled.

## Sources

Synthesized from published US employment-compliance practice: USCIS *Handbook for Employers M-274* and the Form I-9 instructions (Section 1 and 2 completion, the 3-business-day rule, List A/B/C document rules, good-faith correction procedure, Supplement B reverification and rehire, the 3-years-from-hire-or-1-year-from-termination retention rule, and the E-Verify alternative remote-examination procedure); DHS/USCIS E-Verify program rules (case creation timing, TNC handling, non-discriminatory application); Department of Justice Immigrant and Employee Rights guidance on over-documentation and unnecessary reverification; OSHA training and recordkeeping standards; EEOC and ADA guidance on confidential medical-record separation; and SHRM guidance on internal I-9 audits, records retention schedules, handbook acknowledgment, and training-compliance tracking. Initial collection of these records is covered by [[hr/employee-onboarding]]; departure-time retention cutoffs by [[hr/employee-offboarding]]; FMLA documentation by [[hr/leave-management]]; culture and speak-up measurement by [[hr/employee-engagement]].

**Jurisdiction warning:** this skill describes US federal employment compliance. State and local law adds requirements — mandated harassment-prevention training with specific duration and content (e.g. CA, NY, IL, CT, DE, ME, WA), state-level E-Verify mandates, longer retention periods, and separate privacy regimes (CCPA/CPRA for employee data, GDPR outside the US). Non-US employers have entirely different work-authorization systems; the I-9 and E-Verify steps do not transfer. Penalty amounts are adjusted annually and are not stated here. Confirm the rules for each work location, and involve employment or immigration counsel before responding to any government notice, inspection, or charge.
