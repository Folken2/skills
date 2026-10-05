---
name: hr-compliance-audit
description: "Use when auditing HR records for compliance — a periodic check of every employee file against mandatory documents, verification timing, work-authorization expiry, policy attestation currency, required training, and record-retention windows. Produces a severity-ranked findings report and a 30/60/90 remediation plan. Triggers on: HR audit, compliance check, missing documents, right-to-work verification, record retention, audit readiness."
version: 1.0.0
author: "Nuvel Skills"
---

# HR Compliance Audit

## Overview

Audit the employee record system against a defined rule set, then remediate what fails. The core principle: **compliance is a record-keeping problem before it is a legal problem.** Inspectors do not judge intent; they ask for the document. If the file cannot produce it in minutes, the gap exists regardless of what actually happened.

Two facts drive this skill's design. First, record defects are the norm rather than the exception — field audits repeatedly find that a large share of employee files are missing at least one required document, and the most frequently cited failures cluster in the same places: wage/hour classification, employment-verification forms, and leave notification. Second, retention is a *ceiling as well as a floor*: holding records longer than the stated purpose requires is its own exposure under data-protection rules, so over-retention is scored with the same severity as a missing document.

Run this on a fixed cadence — annually at minimum, quarterly for regulated or high-headcount environments — and re-audit critical findings at 90 days. A finding without an owner and a due date is not a finding, it is an observation, and observations do not get fixed.

## When to use

- A scheduled periodic audit of HR records is due (annual, or quarterly for regulated environments).
- You are preparing for an external inspection or enforcement audit and need to know where the files fail.
- Headcount changed materially (new jurisdiction, new entity, a batch of hires) and record hygiene is unknown.
- A missing-document or retention issue has surfaced and you need the whole picture, not one file.
- You are verifying that a remediation plan from a prior audit actually closed.

## When NOT to use

- You need to *fix* one employee's file end-to-end → do it directly; this skill is portfolio-level review.
- You are checking a departure's access revocation and asset return → use [[employee-offboarding]].
- You are verifying that mandatory **training** is delivered and current → [[training-and-development]] owns delivery; this skill only checks the completion record exists.
- You are auditing whether employees are correctly classified and paid → that needs timekeeping and payroll data; feed [[payroll-processor]] output in as an input here, it is not a substitute.
- You are handling a live employee-relations case → that is an investigation. Do not put case material into the audit file.

## Workflow

1. **Scope the audit.** Write a one-page scope memo: entities, locations and jurisdictions in scope, full review vs. risk-based sample (sample recent hires, recent terminations, and any group with a known past failure), the owner, and what "closed" means. Secure a leadership sponsor — audits without one stall at the first difficult finding.
2. **Assemble the rule set.** For each jurisdiction in scope, put the applicable obligations in one table: required documents per employment type, verification completion deadlines, authorization re-verification triggers, policy-attestation requirements, training requirements, and the retention period per document class. Record the threshold that triggers each duty (headcount, contract type, location) and cite a source plus a last-confirmed date for every row — a rule with no date is a liability.
3. **Export the record data.** Pull a structured export from the HRIS/payroll system, one row per employee: hire date, termination date, employment type, department, manager, verification date, work-authorization expiry, acknowledged handbook version, training completions, and file document inventory. Never audit from a screen-scrape. Validate the export before checking anything: row count must match headcount, and no nulls in the fields that gate a check.
4. **Run the checks.** Execute `scripts/compliance-audit.py` against the export and rule set. It applies seven check families: mandatory document presence per employment type, verification timeliness against hire date, work-authorization expiry inside the look-ahead window, policy-attestation version match, required-training currency, retention window open/closed (purge due), and data completeness that would otherwise make a check unverifiable.
5. **Score and classify every finding.** Severity: **critical** for legal exposure or an unverifiable record, **high** for a systemic process gap, **medium** for a documentation defect, **low** for optimization. Use the script's severity output; override only in writing, with a reason recorded next to the finding.
6. **Build the remediation plan.** Give every critical and high finding an owner, a due date (critical 0–30 days, high 31–60, medium 61–90, low next cycle), and the exact evidence that will prove closure. Separate quick wins (missing acknowledgments, stale versions, export defects) from structural fixes (re-verification workflow, retention automation, jurisdiction coverage).
7. **Do the checks a script cannot do.** The tool can only confirm a document *exists*, never that it is *acceptable*. Hand-review a sample of files for acceptable document categories, correction hygiene (single strike-through, initialled, dated, memo attached where required), and separation of confidential or medical material from the general personnel file. Record sample size and hit rate.
8. **Report, then re-audit.** Publish findings, remediation plan, and scope memo as one artifact. Schedule the 90-day re-audit of critical findings at the moment you publish, not later. Roll medium and low items into the next cycle's scope.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Auditing from the HRIS UI instead of an export | No row-count reconciliation; you review whatever you happened to open | Export to a file, reconcile count against headcount, then audit |
| Findings recorded without a severity | Nothing gets prioritized; the plan becomes a wish list | Score every finding; critical carries a 30-day clock |
| Confidential or medical records inside the general personnel file | Statutory exposure independent of the underlying case | Separate restricted file; record the separation in the audit |
| Verification late "but before the deadline we chose" | Only the legally set deadline counts; invented deadlines are no defence | Encode the actual deadline in the rule set and check against it |
| Retention checked only for "too short" | Over-retention is a data-protection exposure, not diligence | Flag purge-due records at the same severity as missing ones |
| Documents "corrected" by overwrite or deletion | Destroys the audit trail and can look like concealment | Strike through, initial, date, attach a memo; never overwrite |
| Rule row with no source or confirmation date | You cannot defend the standard you audited against | Cite source and last-confirmed date for every rule |
| Critical findings still open at the re-audit date | The exposure you identified persists — now with a paper trail | Re-audit at 90 days; escalate unresolved criticals to the sponsor |

## Exit criteria

- [ ] Scope memo written: entities/jurisdictions, full vs. sample, owner, definition of closed.
- [ ] Rule set documented with source and last-confirmed date per row, including trigger thresholds.
- [ ] Export reconciled against headcount with no nulls in gating fields; export archived alongside the report.
- [ ] `scripts/compliance-audit.py` run; findings report produced with a severity on every finding.
- [ ] Hand review completed (document acceptability, correction hygiene, file separation) with sample size and hit rate recorded.
- [ ] Every critical and high finding has a named owner, a due date, and defined proof of closure.
- [ ] Quick wins separated from structural fixes in the remediation plan.
- [ ] Report, plan, and scope memo published as one artifact; 90-day re-audit scheduled at publication.
- [ ] The audit record itself is retained with restricted access — it contains findings about named individuals.

## Tools

- `scripts/compliance-audit.py` — runs the seven check families over an employee-record export and emits a severity-ranked findings report with a remediation window per finding. Standard library only.
  - `python scripts/compliance-audit.py --sample > audit-input.json` — emit a fillable template.
  - `python scripts/compliance-audit.py audit-input.json` — human-readable report; exit 0 = no critical findings.
  - `python scripts/compliance-audit.py audit-input.json --json` — machine-readable findings for ticket or case import.

## Sources

Aligned with SHRM periodic-audit guidance; the SHRM/U.S. Citizenship and Immigration Services employment-verification (Form I-9 style) conventions on completion timing, re-verification, and retention — three years after hire or one year after termination, whichever is later; and standard HR-audit practice on severity classification and 30/60/90 remediation windows. Common federal retention baselines referenced: payroll records three years, injury and illness logs five years, benefit plan documents six years. Adapt the rule set to your jurisdiction — state and local rules, works-council consultation duties, and data-protection regimes such as GDPR storage limitation frequently add stricter requirements. This skill encodes a process, not legal advice; route systemic exposure to counsel.
