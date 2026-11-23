---
name: employee-records-retention
description: "Use when building or auditing a retention and disposition schedule for HR records — deciding how long to keep personnel files, hiring records, payroll, I-9s, FMLA, benefits, OSHA exposure and injury logs, medical files, background checks and claim/investigation files, or checking which records are due for disposition, on legal hold, or over-retained. Triggers on: record retention schedule, how long to keep employee records, purge personnel files, records disposition, legal hold, litigation hold, I-9 purge, records audit."
version: 1.0.0
author: "Nuvel Skills"
---

# Employee Records Retention

## Overview

Employee records retention is the practice of assigning every HR record a class, a retention trigger, a minimum period and a disposition method, then auditing the inventory against that schedule. The core principle: **keep each record for the longest period any applicable rule requires, then dispose of it on schedule, and never destroy anything that is under a legal hold or tied to an open claim.**

Periods vary a lot by record type. EEOC rules (29 CFR 1602.14) require personnel and hiring records to be kept for 1 year from creation or the personnel action. Federal-contractor thresholds extend hiring records to 2 years. I-9s are kept 3 years after hire or 1 year after termination, whichever is later. Payroll records are kept 3 years under the FLSA and the ADEA, ERISA benefit-plan records 6 years, OSHA injury logs 5 years, and OSHA exposure records for the duration of employment plus 30 years. Once a discrimination charge is filed, every relevant record must be kept until final disposition, which includes the time to sue and any appeals. Medical, I-9 and claim records must be stored separately from the personnel file.

Over-retention is a risk too. Every record kept past its period is discoverable in litigation and exposed in a breach. Destroying a record early, or destroying one under hold, can lead to spoliation sanctions. A schedule the agent can compute, with a human approving each disposition, addresses both risks.

## When to Use

- Drafting or refreshing an HR retention/disposition schedule.
- Auditing an HR record inventory to find what is due for disposition, upcoming, held or over-retained.
- Planning a periodic purge (for example, the common 7-year convention for terminated-employee files) and checking it against the statutory minimums.
- Checking whether a legal hold or a pending claim blocks a routine purge.
- Setting up segregated storage for medical, I-9 and claim records.

## When NOT to Use

- Deciding whether a specific record is relevant to a pending lawsuit. That is counsel's call; this skill only enforces a hold once counsel declares it.
- Retention of non-HR business records (tax, contracts, corporate minutes) beyond the default class.
- Physically destroying records. The script computes eligibility only. Destruction is a separate, human-approved and logged action.
- Answering a regulator or a data-subject request. Route it to legal/privacy first.

## Workflow

1. **Identify every governing regime.** List each jurisdiction the records are subject to (federal/national, state/province, country, sector rules, collective agreements). The bundled schedule is **US-federal-flavoured reference data and not legal advice**. Re-base it per jurisdiction. Where a local rule is longer, record the difference as `jurisdiction_extra_months` on each affected record.
2. **Print the reference schedule.** Review the record classes, triggers, base periods, governing rules and disposition methods:
   `python3 scripts/retention_schedule.py schedule [--json schedule.json]`
   Confirm each class against the regimes from step 1 before using it.
3. **Build the record inventory.** Export one CSV row per record, or per event for multi-event records, with this header:
   `record_id,record_class,employee_id,event_date,event_type,status,legal_hold,jurisdiction_extra_months`
   - `event_type` is one of `hire`, `termination`, `record_created`, `plan_termination`, `exposure`, `claim_filed`, `claim_resolved`.
   - For "later of" rules (personnel file, hiring record), enter the later date as `event_date`.
   - I-9, OSHA exposure, medical and claim clocks are evaluated across all rows that share `employee_id` + `record_class`. Give each event (hire, termination, claim filed, claim resolved) its own row with a distinct `record_id`.
   - Federal contractors with 150+ employees or a $150k+ contract add `jurisdiction_extra_months=12` to `hiring_record` rows.
   - Mark `status=active` for employees still employed. Employment-duration clocks do not start until a `termination` row exists.
4. **Apply legal holds first.** Get the current hold list from counsel and set `legal_hold=y` on every covered record. A hold suspends all destruction, including automatic deletion in email, chat and HRIS. Record each open charge or suit as a `claim_filed` row.
5. **Run the audit.**
   `python3 scripts/retention_schedule.py audit --inventory inventory.csv --as-of 2026-11-23 --upcoming-days 90 --max-retention-years 30 --json audit.json`
   Always pass an explicit `--as-of`. The script never reads the clock. It exits 0 on success, 1 on an unreadable file or a missing header, 2 on a usage error and 3 if its internal ordering check fails.
6. **Check the internal-consistency line.** The summary must print `ordering_check: ok (N records)`. This confirms that no disposition date is earlier than its governing trigger date. Any other result, or exit 3, means stop and report it. Do not act on the output.
7. **Resolve the exception groups before anything else.**
   - `DATA_WARNING`: fix the source data (missing or unparseable date, unknown event type, bad `legal_hold`, negative or non-integer extra months, duplicate `record_id`, I-9 missing its hire row) and re-run.
   - `UNKNOWN_CLASS`: map the class to a schedule row or add a jurisdiction-approved class. Never keep or dispose of these records silently.
   - `HOLD` (flag `routine_purge_blocked`): exclude from every purge until counsel lifts the hold in writing or a `claim_resolved` row is recorded.
8. **Review over-retention.** Records flagged `REVIEW` exceed the `--max-retention-years` horizon. Confirm that a rule actually requires that horizon, for example OSHA exposure. If none does, correct the class or the extra months.
9. **Prepare the disposition list.** Present `DUE_NOW` (with days overdue) and `UPCOMING` (with days remaining) to the records owner, each with the governing rule shown. Disposition follows the method in the schedule: cross-cut shredding or secure erase for consumer-report data under the FTC Disposal Rule, and offering OSHA exposure records to NIOSH before destruction where that rule applies.
10. **Log the human-approved destruction.** For each destroyed record, log the record id, class, approver, date, method and the audit file it came from. Keep the log permanently. Re-run the audit on a fixed cadence (for example quarterly) and whenever a hold changes.

## Red Flags

| Signal | Why it matters | Action |
|---|---|---|
| A purge is scheduled while a charge or suit is open | Destroying relevant records is spoliation and breaches 29 CFR 1602.14 | Set `legal_hold=y` / add `claim_filed`; confirm the HOLD group before any purge |
| Auto-delete still runs on mailboxes or chat of held custodians | A litigation hold covers automatic deletion too | Suspend the retention policies for those custodians |
| Medical, I-9 or claim documents filed in the personnel file | Exposes confidential data to everyone with file access (ADA 12112(d)(3)(B)) | Move them to segregated, access-restricted storage |
| `UNKNOWN_CLASS` rows ignored | Unclassified records are neither protected nor disposed of | Classify every one before closing the audit |
| One blanket period for all records | Either over-retains (liability) or under-retains (non-compliance) | Use the per-class schedule and take the longest applicable rule |
| `ordering_check` missing or exit code 3 | Computed dates cannot be trusted | Stop; report the failing record; do not act on the output |
| Records of never-hired applicants kept indefinitely | Over-retention with no business need | Dispose at the 1-year (or contractor 2-year) mark unless held |
| Agent output treated as authority to destroy | Destruction needs human approval and a log | Route the DUE_NOW list to the records owner for sign-off |

## Exit Criteria

- [ ] Every jurisdiction the records are subject to is listed, and every one with a longer rule is reflected in `jurisdiction_extra_months`.
- [ ] The audit ran with an explicit `--as-of` and exited 0.
- [ ] The summary shows `ordering_check: ok (N records)`.
- [ ] `DATA_WARNING` count is 0 after source fixes, or every remaining warning is listed with an owner.
- [ ] `UNKNOWN_CLASS` count is 0, or every remaining row is listed with an owner.
- [ ] Every record on counsel's hold list appears in the `HOLD` group with `routine_purge_blocked`.
- [ ] Every `REVIEW`-flagged record has a recorded justification or a correction.
- [ ] The `DUE_NOW` list was sent to a named records owner for approval. No record was destroyed without a destruction-log entry.
- [ ] The JSON audit file is stored with the destruction log.

## Pitfalls

- **Empty file.** A 0-byte inventory exits 1 with `file is empty - a header row is required`. A header-only file exits 0 with 0 records.
- **Missing header column.** The script exits 1 and names the missing columns. Unknown extra columns are ignored.
- **Bad values never fall through to a date.** A missing or unparseable `event_date`, an unknown `event_type`, an event type that does not trigger the class, an empty or invalid `legal_hold`, negative or non-integer `jurisdiction_extra_months` and a duplicate `record_id` (every copy) all land in `DATA_WARNING`. None of these can ever be `DUE_NOW`.
- **Legal hold beats everything.** A row with `legal_hold=y` is reported as `HOLD` even if its other fields are malformed. Its warnings are still printed.
- **Claim holds are group-wide.** A `claim_filed` with no later `claim_resolved` for the same `employee_id` + `record_class` holds every row in that group. Once resolved, the disposition date is the latest of the class rule and the resolution date.
- **Employment-duration clocks wait.** I-9, OSHA exposure and medical rows without a `termination` row are `RETAIN` with `PENDING_TRIGGER`. If `status` says terminated, a warning tells the user to add the termination row. An I-9 group with a termination row but no hire row is a `DATA_WARNING`, because the hire + 3 years leg cannot be checked.
- **Group extension.** In multi-event groups the longest `jurisdiction_extra_months` in the group applies to every row, so all rows of one record share one date.
- **Month arithmetic clamps to month end.** For example, 2024-02-29 + 12 months = 2025-02-28. OSHA injury logs run from 1 January after the year the record pertains to.
- **Event dates after `--as-of`** are computed but warned.
- **`REVIEW` is a flag, not a group.** It measures from the earliest event in the record group to disposition. With the default 30-year horizon it mostly fires on OSHA exposure records, which is expected and only needs a recorded justification.
- **Background checks** use the 1-year minimum. To follow the 5-year expert practice, add `jurisdiction_extra_months=48`.

## Attribution & Sources

This is an original Nuvel Skills SOP. The sources below informed the retention periods, thresholds and legal constraints. They do not endorse this skill. The base retention schedule is US-federal-flavoured and is not legal advice. Jurisdiction-specific law supersedes it, and counsel should confirm it for each jurisdiction the records are subject to.

- SHRM, "Federal Record Retention Requirements": https://www.shrm.org/content/dam/en/shrm/topics-tools/legal-compliance/Federal-Record-Retention-Requirements.pdf
- SHRM, "Complying with Employment Record Requirements": https://www.shrm.org/resourcesandtools/tools-and-samples/toolkits/pages/complyingwithemploymentrecordrequirements.aspx
- SHRM, "Record-Keeping Policy: Record Maintenance, Retention and Destruction": https://shrm.org/resourcesandtools/tools-and-samples/policies/pages/cms_017186.aspx
- EEOC recordkeeping rule, 29 CFR 1602.14: https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XIV/part-1602/section-1602.14
- 29 CFR 1627.3(b)(3) (ADEA payroll records, 3 years; charge-based hold mirrored from 1602.14) and 29 CFR 516.5/.6 (FLSA payroll, 3 years; supporting records, 2 years).
- Reference summary of US federal HR retention rows with citations: https://recordretention.org/how-long-to-keep-employee-records
- OSHA 29 CFR 1910.1020(d)(1)(ii) (exposure records: employment + 30 years) and 29 CFR 1904.33 (injury/illness records: 5 years).
