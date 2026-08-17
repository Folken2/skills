---
name: employee-offboarding
description: Use when an employee is departing and you need to run the exit process — departure confirmation, knowledge transfer, system access revocation, equipment return, exit interview, final payroll/benefits close-out, and compliance audit trail. Triggers on "employee resignation", "termination", "offboarding checklist", "exit process", "access revocation", "knowledge transfer", "last day". Also covers voluntary vs involuntary departure differences, remote-worker specifics, and post-departure alumni management.
version: 1.0.0
author: Nuvel Skills
---

# Employee Offboarding

## Overview

Close out a departing employee cleanly, securely, and with dignity. Offboarding is a **cross-functional workflow** — HR, IT, Payroll, Legal, and the Manager all act — triggered by a single event: the departure. The core principle: **access revocation first, everything else second.**

The highest-leverage action is revoking access the moment departure is confirmed — before equipment return, before the exit interview, before knowledge transfer. An unrevoked account is an open door; a returned laptop is a solved problem. Sequence accordingly.

Distinguish clearly between **voluntary** and **involuntary** departures, because the timeline changes:

- **Voluntary** (resignation, retirement): there is a notice period and a handover window. Access is revoked at **end of the last working day**; knowledge transfer happens during notice.
- **Involuntary** (termination, layoff): access is revoked **immediately**, ideally before or during the notification meeting. Some jurisdictions require **same-day final pay**. There is no handover window — capture knowledge from artifacts, not the departing person.

## When to use

- An employee has resigned, been terminated, retired, or been laid off, and you need to run the exit.
- You need an offboarding checklist for a specific departure (voluntary or involuntary).
- You are revoking system access, coordinating equipment return, or closing out final pay/benefits.
- You are running an exit interview or building the departure's compliance/audit record.
- The departure is a remote worker and you need the remote-specific path (shipping, MDM wipe).

## When NOT to use

- The person is joining or ramping (pre-start, day 1, 30-60-90) → use [[employee-onboarding]].
- The person is staying and you're running 1:1s, reviews, growth, or a **stay** interview → use [[employee-engagement]]. Stay interviews retain; exit interviews explain. If retention is still possible, you're in the wrong skill.
- No departure is confirmed yet — a flight-risk signal is not a resignation. Assess retention in [[employee-engagement]] first.
- A contested/legal termination is unfolding → involve HR and Legal directly before executing; this SOP assumes the decision is made.

## Workflow

### 1. Trigger and classification

Establish the facts that drive every downstream timeline before doing anything else.

- **Departure type:** voluntary or involuntary. This sets the access-revocation timing (step 2).
- **Effective date / last working day.** For involuntary, this is often today.
- **Notice period / handover window:** the time available for knowledge transfer (step 3). Involuntary = none.
- **Remote vs on-site:** determines the equipment-return path (step 4).
- **Manager, IT, Payroll, and Legal contacts** for this departure. Open the offboarding record now (step 7) — every subsequent action logs into it.

### 2. Access revocation (highest priority)

**Involuntary: revoke immediately** — coordinated to complete before or during the notification meeting. **Voluntary: revoke at end of the last working day**, scheduled so nothing lingers past it. Work from the per-hire access inventory maintained in [[employee-onboarding]]; if none exists, enumerate access now.

Revoke across all vectors — don't stop at email:

- **Identity provider / SSO** — disable the account first; this cascades to everything federated behind it.
- **Email and calendar** — suspend, then set forwarding/auto-reply per policy; don't delete yet (retention, step 7).
- **SaaS and internal apps** — including anything *not* behind SSO (individually-licensed tools are the classic miss).
- **VPN and network access.**
- **SSH keys, API tokens, service-account credentials, deploy keys** — revoke, don't just disable the human login.
- **Building/badge access and physical keys.**
- **Shared passwords and shared accounts — rotate them.** Disabling the person's account does nothing if they know a shared credential.

Log each revocation with a timestamp into the access-revocation log (step 7). An incomplete revocation is a breach waiting to happen.

### 3. Knowledge transfer

Capture what leaves with the person. In a **voluntary** departure, use the notice period; in an **involuntary** one, recover from documentation and systems, not the individual.

- **Documentation:** ensure current work, credentials-to-rotate, runbooks, and undocumented process live somewhere the team owns.
- **Handover notes:** a written handover of responsibilities, contacts, and status of open items.
- **Successor / interim owner briefing:** identify who inherits each responsibility; brief them explicitly. Unassigned work is dropped work.
- **In-flight work transfer:** reassign tickets, accounts, approvals, and ownership of shared resources so nothing is orphaned to a disabled account.

### 4. Equipment return

Recover company property and account for each item.

- **Inventory:** laptop, phone, badge, keys, peripherals, corporate cards, and any other issued assets.
- **On-site:** collect on the last day.
- **Remote:** send a **prepaid, tracked shipping** kit with a clear return deadline; track it to received.
- **MDM wipe fallback:** for unreturned or remote devices, remote-wipe / lock via device management. Never let unrecovered hardware hold live company data — the wipe is the backstop when the return stalls.
- Reconcile returned items against the issued list; note any unreturned asset in the record.

### 5. Exit interview

Run a **structured, diagnostic** conversation (voluntary departures especially). Purpose is systemic insight, not a formality.

- Ask why they're leaving, what would have changed it, and about the manager, role, and team experience.
- Keep it consistent across departures so themes are comparable over time.
- **Route findings back into retention** — patterns here should change what [[employee-engagement]] does upstream. An exit interview that isn't actioned is wasted.
- Skip or lighten for involuntary departures where a candid interview isn't appropriate; coordinate with HR/Legal.

### 6. Final payroll and benefits

Close out compensation and benefits to legal requirements.

- **Final paycheck** — issue per jurisdiction. Some states require it on the last day (immediately for involuntary); know your deadline.
- **PTO / accrued leave payout** per policy and law.
- **Benefits termination** — set the coverage end date; avoid gaps or overpayment.
- **Continuation-of-coverage notice** (e.g., COBRA in the US, or local equivalent) — send within the required window.
- **Retirement accounts** — provide 401(k) / pension / superannuation rollover information and next steps.
- Confirm final expense reimbursements and clawbacks (sign-on, tuition) are settled.

### 7. Compliance and audit trail

Make the whole offboarding defensible and auditable.

- **Document every action with a timestamp** — who did what, when: revocations, equipment, pay, interview.
- **Maintain the offboarding record** as the single source of truth for this departure.
- **Keep the access-revocation log** as evidence every vector in step 2 was closed.
- **Data retention / deletion:** apply the retention schedule — keep what law/policy requires (payroll, tax, employment records), delete what must go, on the required timeline. Retention is not "keep everything forever."

### 8. Post-departure

Close the loop after the last day.

- **Alumni management:** add to an alumni network where appropriate; good leavers are rehires, referrals, and customers.
- **Reference letter:** provide per policy for eligible departures.
- **30-day cleanup follow-up:** re-audit that access is fully gone, no orphaned accounts remain, shared credentials were rotated, equipment is reconciled, and final pay/benefits closed cleanly. This catch-all pass finds the one SaaS seat everyone forgot.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Access revoked *after* equipment/exit interview | Longest window for data theft or sabotage | Revoke first — immediate (involuntary) or end of last day (voluntary) |
| Only SSO/email disabled | Individually-licensed SaaS, VPN, tokens stay live | Revoke every vector; rotate shared passwords |
| Shared credentials not rotated | Departed person still holds a working key | Rotate all shared passwords/accounts they knew |
| Involuntary treated on a voluntary timeline | Live access during a termination = high risk | Immediate revocation, coordinated with notification |
| SSH keys / API tokens / service accounts left active | Human login gone but machine access persists | Revoke keys and tokens, not just the login |
| Knowledge walks out the door | Orphaned work, undocumented process, dropped tickets | Handover notes + successor briefing during notice |
| Remote equipment never recovered | Company data on an uncontrolled device | Prepaid tracked return + MDM remote-wipe fallback |
| Final pay/benefits miss legal deadlines | Fines, penalties, legal exposure | Know jurisdiction rules; same-day pay where required |
| No timestamped audit trail | Can't prove revocation; fails audit/dispute | Log every action with timestamp in the offboarding record |
| "Delete everything" or "keep everything" | Breaks retention law either way | Apply the retention schedule per record type |

## Exit criteria

- [ ] Departure classified (voluntary/involuntary), with last working day, notice period, and remote/on-site recorded.
- [ ] All access revoked across every vector (SSO, email, SaaS, VPN, SSH keys, API tokens, badge/keys) on the correct timeline; shared passwords rotated; each revocation logged with a timestamp.
- [ ] Knowledge transferred — documentation current, handover notes written, successor briefed, in-flight work reassigned off the disabled account.
- [ ] All equipment reconciled against the issued list; remote devices returned via prepaid tracking or remote-wiped.
- [ ] Structured exit interview completed (where appropriate) and findings routed back into [[employee-engagement]].
- [ ] Final pay, PTO payout, benefits termination, continuation-of-coverage notice, and retirement rollover completed within legal deadlines.
- [ ] Offboarding record and access-revocation log complete; data retention/deletion applied per schedule.
- [ ] Post-departure done: alumni/reference handled, and a 30-day follow-up confirms no orphaned access or unreconciled equipment remains.

## Sources

Aligned with SHRM offboarding and termination guidance and standard IT security offboarding controls (immediate access deprovisioning, credential rotation, least-privilege lifecycle). Access revocation coordinates with the per-hire access inventory maintained in [[employee-onboarding]]; exit-interview findings feed retention in [[employee-engagement]]. Final-pay timing, accrued-leave payout, continuation-of-coverage (e.g., COBRA in the US), and record-retention obligations vary by jurisdiction — verify against local law and involve HR/Legal for contested terminations.
