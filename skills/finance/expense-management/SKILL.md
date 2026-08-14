---
name: expense-management
description: "Use when handling corporate spend and employee expenses — expense policy, receipt capture, categorization, approval workflow, reimbursement, corporate-card controls, fraud detection, and spend reporting. Triggers on \"expense policy\", \"approve expenses\", \"reimburse\", \"corporate card\", \"receipt\", \"expense report\", \"duplicate claim\"."
version: 1.0.0
author: Nuvel Skills
---

# Expense Management

## Overview

The employee-spend lifecycle: a clear policy, frictionless capture, correct categorization, tiered approval, timely reimbursement, controlled corporate cards, active fraud detection, and reporting that closes the loop. The core principle: **control lives in the policy and the audit trail, not in the approver's inbox** — a manager rubber-stamping a report they can't verify is not a control. Every expense must be checkable against a written rule and backed by evidence.

Reality: expense fraud and leakage are dominated by small, repeated, plausible amounts — the duplicate submission, the personal meal coded as client entertainment, the round-number "misc" — not the occasional large obvious one. So the design goal is a policy specific enough to make violations visible and automation that flags patterns, freeing approvers to judge the genuine edge cases.

## Toolchain

This skill is domain expertise; the data work runs through supporting skills:

- **[[backoffice/xlsx]]** — read submitted expense reports and corporate-card statements, run policy/duplicate/anomaly checks over the rows, and write the validated report and spend reports back. Reach for it whenever a step reads from or writes to an `.xlsx` file.
- **[[backoffice/pdf]]** — extract fields from receipt PDFs and render the spend report for distribution.

## When to use

- You are writing or revising an expense policy or approval matrix.
- An employee is submitting expenses, or an approver is reviewing/reimbursing them.
- You are setting up or reconciling corporate cards, or running fraud/duplicate checks.
- You need spend reporting by category, department, or vendor.

## When NOT to use

- The spend is a customer bill you are raising, not an employee cost → use [[invoicing]].
- You are chasing overdue customer receivables → use [[credit-control]].
- You are projecting cash needs, not controlling individual claims → use [[cashflow-forecasting]].

## Workflow

1. **Define the policy.** Document allowable vs. non-allowable categories, per-category limits (meals, travel, lodging, entertainment), approval thresholds, required evidence, and submission deadlines. Make each rule *testable* ("lodging ≤ X/night", "receipt required over Y") so compliance is objective, not interpretive. Publish it where employees claim.
2. **Build the approval matrix.** Map who approves what by amount, department, and expense type — including thresholds that require a second/finance approver and rules that block self-approval and manager-approving-own-chain conflicts. Define the exception path for justified policy breaks so they're approved on record, not smuggled through.
3. **Capture expenses with evidence.** Require itemized receipts at point of spend via digital/photo capture; use OCR to extract merchant, date, amount, and tax where available. Enforce the receipt requirement at submission — no receipt over threshold, no submission. Capture the business purpose and, for entertainment, attendees.
4. **Categorize and code.** Map each line to the chart-of-accounts code and correct tax treatment (recoverable VAT/GST vs. not, and any personal-benefit/taxable element like some entertainment or gifts). Consistent coding is what makes step 8 reporting trustworthy — miscoding here corrupts everything downstream.
5. **Route for approval.** Read the submitted expense report from its Excel file with [[backoffice/xlsx]], validate each line against the policy limits, flag anomalies, and send it through the matrix. The approver checks policy compliance, evidence, and business justification — not just the total. Kick back non-compliant items with a reason rather than approving-then-clawing-back. Record who approved what and when, then write the approved report back with the decision column populated.
6. **Reimburse on schedule.** Pay approved out-of-pocket expenses through the defined method (payroll, bank transfer) on a published timeline. A predictable, prompt reimbursement cycle is itself a control — it removes the excuse for employees to float costs on the wrong instrument or inflate later claims.
7. **Control corporate cards.** Set per-card and per-category limits, require the same receipts and coding as reimbursements, and reconcile every statement line to a submitted expense monthly — read the card statement export with [[backoffice/xlsx]] and match it against the expense rows. Chase unreconciled transactions and unsubmitted receipts before close. An unreconciled card is an open control gap.
8. **Detect fraud and report.** Run automated checks over the expense and card spreadsheets: duplicate detection (same amount/date/merchant across users or re-submitted), out-of-policy amounts, split transactions dodging a threshold, weekend/round-number/velocity anomalies, and mismatched receipts. Investigate flags through a consistent, documented process. Then build the spend report by category, department, vendor, and trend as an Excel file with [[backoffice/xlsx]] (render it via [[backoffice/pdf]] for distribution), and feed the findings back into policy and limits.

## Common Pitfalls

| Pitfall | Why it's a problem | Do instead |
|---|---|---|
| Vague policy ("reasonable expenses") | Nothing is objectively a violation; approvers can't enforce | Testable per-category limits and evidence rules |
| Approval based on the total, not the detail | Small policy breaches and miscodes sail through | Check evidence, coding, and business purpose per line |
| Self-approval or approving your own reporting chain | Removes independence; enables abuse | Matrix blocks conflicts; second approver over thresholds |
| Corporate-card statements left unreconciled | Untracked spend and undetected misuse accumulate | Reconcile every line to a coded expense monthly |
| Duplicate/split detection left to human eyes | The dominant fraud pattern is small and repetitive | Automated duplicate/split/velocity flags, then human review |

## Verification Checklist

- [ ] Written policy with testable limits, allowable/non-allowable categories, evidence rules, and deadlines is published.
- [ ] Approval matrix defined by amount/department/type; self- and chain-conflict approvals blocked; exception path documented.
- [ ] Receipts captured with business purpose; receipt requirement enforced at submission.
- [ ] Each line coded to the chart of accounts with correct tax treatment.
- [ ] Reimbursements paid on a published schedule via the defined method.
- [ ] Corporate-card limits set and every statement line reconciled to a coded expense.
- [ ] Automated duplicate/out-of-policy/split/anomaly checks run and flags investigated consistently.
- [ ] Spend reported by category/department/vendor/trend and fed back into policy and limits.

## Supporting skills

- [[backoffice/xlsx]] — read expense reports and card statements; write validated reports and spend reports.
- [[backoffice/pdf]] — extract receipt fields and render the spend report.
- [[cashflow-forecasting]] — feed approved reimbursement timing into the outflow model.

## Sources

Aligned with standard corporate expense-management and internal-control practice (testable policy, segregation of duties, receipt/evidence requirements, card reconciliation, duplicate/anomaly detection). Adapt tax-recoverability, taxable-benefit, and record-retention rules to your jurisdiction.
