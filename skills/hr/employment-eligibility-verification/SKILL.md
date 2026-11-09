---
name: employment-eligibility-verification
description: "Use when a US employer must verify a new hire's identity and employment authorization on Form I-9 — from offer acceptance through Section 1, Section 2 document examination, E-Verify, reverification and rehire (Supplement B), retention, internal audit, and responding to a Notice of Inspection. Every step has a hard federal deadline; computes the clocks with scripts/i9_tracker.py. Triggers on: Form I-9, I-9, employment eligibility verification, Section 1, Section 2, List A/B/C documents, E-Verify, reverification, Supplement B, rehire, I-9 retention, I-9 audit, Notice of Inspection, NOI."
version: 1.0.0
author: "Nuvel Skills"
---

# Employment Eligibility Verification

## Overview

Get a correct, on-time Form I-9 on file for every US hire and keep it correct until it can be destroyed. The core principle: **the I-9 is a clock, not a form.** Section 1 is due on the first day of work for pay, Section 2 three business days later, reverification on the day authorization expires, and destruction is only permitted on a computed date. Each missed clock and each substantive error is a separate penalty, and the same rules are enforced in the other direction: asking for too many documents, the wrong documents, or reverifying someone you shouldn't is document abuse.

The sequencing that matters: **offer accepted → Section 1 (employee) → review Section 1 → Section 2 (employer, original documents) → E-Verify if enrolled.** Never compute deadlines by hand — run `scripts/i9_tracker.py` and act on its status and exit code (0 = satisfied, 2 = overdue/blocked, 1 = usage error).

The I-9 runs inside [[hr/employee-onboarding]], starts only after the offer from [[hr/hiring]] is accepted, and its retention clock is set at [[hr/employee-offboarding]]. This skill implements federal requirements; it is not legal advice.

## When to use

- A candidate in the US has accepted an offer and needs a Form I-9 before or on day one.
- Section 2 is due and you need to examine documents, or confirm the 3-business-day deadline.
- An employee's employment authorization or List A/C document is approaching expiry.
- You are rehiring a former employee and must decide between Supplement B and a new Form I-9.
- An employee has left and you need the earliest lawful destruction date for their I-9.
- You are running an internal I-9 audit, or you have received a Notice of Inspection (NOI).

## When NOT to use

- The worker is an independent contractor, not an employee → no I-9; confirm classification first with [[hr/hiring]].
- The work is performed outside the US (other than Puerto Rico's language exception) → follow that country's right-to-work rules; this skill does not apply.
- The offer has not been accepted → do not start Section 1. Finish the offer stage in [[hr/hiring]].
- You need payroll tax forms (W-4, state withholding) → use [[hr/payroll-processor]]; never mix them into the I-9 file.
- You need the general day-one checklist (equipment, access, buddy) → use [[hr/employee-onboarding]]; this skill owns only the I-9 step.

## Workflow

### Phase 1 — Before day one (offer accepted)

1. **Confirm acceptance and the first day of work for pay.** Record both in the employee record in your HRIS. The first day of work for pay is the anchor for every clock; get it from the offer, not an estimate.
2. **Compute the clocks.** Run `python3 scripts/i9_tracker.py --hire-date <first-day> --offer-accepted <date> --holidays-file <closed-days>` and write the Section 1 and Section 2 deadlines into the onboarding task list. For jobs shorter than 3 business days add `--job-duration-days N` — Section 2 is then due on the first day of work for pay.
3. **Pull the current form edition.** Download Form I-9 and the Lists of Acceptable Documents from uscis.gov/i-9 and confirm the edition date is current. Use the English version (Puerto Rico employers may use Spanish).
4. **Send the employee the Lists of Acceptable Documents.** State that they choose what to present: one List A document, or one List B plus one List C document. Do not name, suggest, or require specific documents.
5. **Decide the examination method.** Physical examination of originals by you or an authorized representative is the default. The DHS-authorized alternative (remote) procedure is available only if the employer is enrolled in E-Verify at that hiring site; if used, follow it exactly, including retaining copies of the documents.

### Phase 2 — Section 1 (employee, by end of first day of work for pay)

6. **Employee completes and signs Section 1** any time after accepting the offer and no later than the first day of work for pay. Never before acceptance, never back-dated. If a preparer or translator assists, they complete the Preparer/Translator Certification.
7. **Review Section 1 before touching Section 2.** Check every field is complete and the attestation box is ticked. Errors are corrected by the employee only: line through, correct, initial and date the correction. You may not ask for documents to verify Section 1 information, and you may not complete or fix Section 1 yourself.
8. **Record Section 1 completion.** Re-run the tracker with `--section1-completed <date>`; status must read COMPLETE.

### Phase 3 — Section 2 (employer, within 3 business days) + E-Verify

9. **Examine original, unexpired documents in the employee's presence.** Photocopies are not acceptable; a certified copy of a birth certificate is the only copy allowed. Accept any acceptable choice; if a List A document is presented, do not ask for List B or C.
10. **Apply the correct standard.** Ask whether each document reasonably appears to be genuine and relates to the person presenting it — not forensic verification. If it does not, return it and let the employee present other acceptable documents. Never reject a document because of citizenship status, immigration status, or national origin.
11. **Complete and sign Section 2** by the deadline: document title, issuing authority, number, expiration date, first day of employment, and the certification. Started Monday → complete by Thursday. Re-run the tracker with `--section2-completed <date>`.
12. **Handle copies consistently.** If you copy documents (optional unless using the alternative procedure or E-Verify photo matching requires it), copy them for every employee at that site, store them with the I-9, and never use them for anything else.
13. **Create the E-Verify case, if enrolled.** Only after Section 1 and Section 2 are complete, never to pre-screen applicants, and within the timeframe your E-Verify MOU sets (no later than the third business day after the employee starts work for pay). E-Verify supplements Form I-9 — it never replaces it. Follow the tentative nonconfirmation process exactly and do not take adverse action while the employee contests.

### Phase 4 — Reverification and rehire (Supplement B)

14. **Set the reverification clock at Section 2.** Run the tracker with `--citizenship-status`, `--auth-expiry` (Section 1) and `--doc-list A|C --doc-expiry` (Section 2). The deadline is the EARLIER of the two dates. List B documents are never reverified. US citizens, noncitizen nationals, and LPRs who presented a Form I-551, or anyone who presented an unrestricted Social Security card, return NO_REVERIFICATION_REQUIRED — do not reverify them.
15. **Warn the employee at least 90 days ahead.** The tracker emits the 90-day warning date; put it on the HR calendar. The employee again chooses which acceptable List A or List C document to present.
16. **Complete Supplement B no later than the expiry date.** Examine the new original document, record it in Supplement B, sign and date. If the employee cannot present acceptable documentation by the deadline, they may not continue working — escalate to HR/legal before that date, not after.
17. **Rehire.** Run with `--rehire-date --original-i9-date`. Within 3 years of the original I-9 → SUPPLEMENT_B_ALLOWED (or complete a new Form I-9). More than 3 years → NEW_FORM_I9_REQUIRED, full Sections 1 and 2.

### Phase 5 — Retention, storage and internal audit

18. **Store securely and separately.** Keep I-9s (and any document copies) in a restricted store separate from the personnel file, with access limited to those who need it. Use the information only as the DHS Privacy Notice states. Do not mail completed forms to USCIS or ICE.
19. **Retain while employed; compute destruction on separation.** When [[hr/employee-offboarding]] records the end date, run `--employment-end <date>`. Retain until the LATER of end + 1 year and first day of employment + 3 years. Destroy only when status is DESTRUCTION_PERMITTED and no legal hold applies.
20. **Audit internally at least annually.** Sample or review all I-9s against the HRIS active roster: every employee has a form, every Section 2 is on time, every expiring document has a reverification clock, no terminated-employee form is past its destruction date. Correct errors by lining through, entering the correct information, and initialing and dating — never white-out, never back-date. If a form is missing, complete one now with current dates and attach a signed, dated explanation. Audit everyone or a neutral sample — never select by national origin or citizenship.

### Phase 6 — Responding to a Notice of Inspection

21. **Log the NOI and the production deadline.** An NOI gives the employer at least 3 business days to produce Forms I-9; record the date served and the deadline. Notify HR leadership and legal counsel the same day.
22. **Assemble exactly what was requested.** Pull the I-9s (and any required supporting records, e.g. payroll and the roster) for the period in the NOI. Do not alter, back-date, or create forms now to look compliant; correct only through the documented process in step 20, with explanations attached.
23. **Produce and preserve.** Deliver the originals or legible copies as instructed in the NOI, keep a complete copy of what was produced, and route any Notice of Technical or Procedural Failures to counsel immediately — these carry their own correction deadline.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Asking for a specific document ("bring your passport") | Document abuse; discrimination exposure enforced by DOJ IER | Send the Lists; the employee chooses List A or List B + C |
| Requesting List B/C after an acceptable List A was presented | Over-documentation is document abuse | Accept the List A document and stop |
| Section 1 completed before offer acceptance, or back-dated | Invalid form; back-dating is a falsification finding | Complete after acceptance; date with the actual date |
| Section 2 deadline counted by hand | Weekends and holidays are miscounted; late Section 2 is a penalty | Use `scripts/i9_tracker.py`; act on exit code 2 |
| Accepting photocopies or a remote look without E-Verify enrollment | Originals are required; remote is only for E-Verify employers | Examine originals in person, or use the DHS alternative procedure if enrolled |
| Reverifying citizens, LPRs with an I-551, or a List B document | Unlawful reverification; discrimination exposure | Reverify only expiring List A/C; trust NO_REVERIFICATION_REQUIRED |
| I-9s filed inside the personnel file | Exposes protected data; widens any inspection | Separate, access-restricted storage |
| Treating E-Verify as a replacement for the I-9 | The I-9 is still required for every hire | Complete the I-9 first, then create the E-Verify case |

## Exit criteria

- [ ] Offer acceptance date and first day of work for pay are recorded in the employee record.
- [ ] Current Form I-9 edition (per uscis.gov/i-9) was used, in English (or Spanish in Puerto Rico).
- [ ] Section 1 signed on or after offer acceptance and no later than the first day of work for pay; no back-dated entries.
- [ ] Section 2 signed within 3 business days of the first day of work for pay (or by day one for jobs under 3 business days), based on original documents chosen by the employee.
- [ ] `python3 scripts/i9_tracker.py ... --today <date>` with all completion dates supplied exits 0, and its output is saved to the I-9 file.
- [ ] If enrolled in E-Verify, a case was created after Sections 1 and 2 and its result recorded.
- [ ] Every expiring List A/C document has a reverification deadline and a 90-day warning date on the HR calendar; employees reported as NO_REVERIFICATION_REQUIRED have none.
- [ ] Rehires carry either a completed Supplement B (within 3 years of the original I-9) or a new Form I-9.
- [ ] I-9s are stored separately from personnel files with restricted access; no form is mailed to USCIS or ICE.
- [ ] Every separated employee's I-9 has a computed retain-until date; none is destroyed before it.
- [ ] Internal audit completed within the last 12 months; each correction is initialed and dated, each missing form has an attached explanation.
- [ ] Any NOI was answered within its production deadline, with a copy of everything produced retained.

## Sources

Synthesized from USCIS I-9 Central (uscis.gov/i-9-central): Form I-9 instructions, Completing Section 1 and Section 2, Acceptable Documents, Reverification and Supplement B, Retention and Storage, Remote Document Examination (DHS-authorized alternative procedure), and the Handbook for Employers (M-274). E-Verify case timing and process from e-verify.gov and the E-Verify MOU. Anti-discrimination rules from the DOJ Immigrant and Employee Rights Section (IER). Inspection process from ICE Form I-9 Inspection guidance. Offer stage in [[hr/hiring]]; day-one sequencing in [[hr/employee-onboarding]]; end date in [[hr/employee-offboarding]].

**Jurisdiction warning:** this skill implements US federal Form I-9 requirements only. It is not legal advice. Other countries' right-to-work checks differ entirely; Puerto Rico may use the Spanish-language form; some US states add E-Verify mandates or limits on its use. USCIS revises Form I-9 on a dated schedule and using a superseded edition is itself an error — confirm the current edition and rules at uscis.gov/i-9 before each use. Involve legal counsel on NOIs, missing or fraudulent documents, and any decision to terminate for lack of work authorization.
