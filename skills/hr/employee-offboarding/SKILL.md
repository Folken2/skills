---
name: employee-offboarding
description: "Use when an employee is leaving the company — full-cycle offboarding from notice to post-departure cleanup. Covers notice acknowledgment, knowledge transfer planning, IT access revocation (time-sensitive — revoke first), equipment return, final payroll and PTO payout, COBRA/benefits termination, exit interview, and alumni network handoff. Triggers on: resignation, termination, last day, offboarding checklist, access revocation, exit interview."
version: 1.0.0
author: "Nuvel Skills"
---

# Employee Offboarding

## Overview

Turn a departure into a clean, auditable close-out. The core principle: **offboarding is a security event first and an HR event second.** Every hour an ex-employee holds live credentials is an hour of unmonitored access to systems, customer data, and code. Orphaned accounts are one of the most common findings in access audits, and they are entirely preventable — revocation is a scheduled action, not a courtesy that waits for a returned laptop.

The sequencing that matters: **revoke access first, then collect equipment, then run the exit interview.** Everything else (payroll, benefits, alumni) follows on a legal clock. Work from the per-hire access inventory maintained during [[employee-onboarding]] — if that inventory is current, revocation is a checklist rather than a scramble.

Departures are also your highest-signal feedback moment. The exit interview belongs to the retention loop in [[employee-engagement]], not to this checklist — run it there and route the findings back.

## When to use

- An employee has resigned, been terminated, or reached the end of a contract.
- You are planning the notice period: knowledge transfer, handover, backfill.
- It is the last day and you need to revoke access, collect equipment, and close out.
- You are handling post-departure obligations: final pay, PTO payout, COBRA/benefits termination.
- You are auditing whether a past departure was fully closed out (orphaned accounts, unreturned assets).

## When NOT to use

- You need the exit interview *content* — questions, structure, feeding themes into retention → use [[employee-engagement]] (step 8). This skill only schedules and gates it.
- The person is at flight risk but hasn't resigned → run a stay interview via [[employee-engagement]]. Don't offboard someone you can still retain.
- You are backfilling the vacated role → use [[hiring]] to source, then [[employee-onboarding]] to ramp.
- The access inventory doesn't exist yet → fix the upstream process in [[employee-onboarding]] (step 3) so future departures are clean.
- An internal transfer, not a departure → adjust access to the new role's least privilege; do not run this workflow.

## Workflow

### Phase 1 — Notice period (week 1–2)

1. **Acknowledge notice in writing.** Confirm receipt of the resignation (or issue the termination notice) with the agreed last working day, notice-period terms, and what happens to unused PTO. Written acknowledgment sets the clock every later step depends on. Involve HR/legal on any involuntary termination *before* notifying the employee.
2. **Set the departure record.** Record: last working day, benefits end date, final pay date, reason for leaving (voluntary/involuntary), and rehire eligibility. This record drives Phases 2 and 3 — create it once, reference it everywhere.
3. **Pull the access inventory.** Retrieve the per-hire access list from [[employee-onboarding]]. Reconcile it against reality: SSO/IdP apps, email, code repos, cloud consoles, SaaS admin seats, shared/service accounts, VPN, building badges, company cards, customer-facing accounts. Anything found that isn't on the list is a gap — log it and fix the onboarding process.
4. **Schedule revocation for the last day.** Pre-stage every revocation with a scheduled time on the final day. Do not revoke early on a voluntary departure without cause — it disrupts handover. Do revoke immediately, before notification, for terminations for cause or any access-sensitive role.
5. **Plan knowledge transfer.** Identify what only this person knows: owned systems, in-flight projects, customer relationships, undocumented runbooks, vendor contacts, recurring obligations. Assign a named receiver for each item — an unassigned item is not transferred.
6. **Execute the handover.** The departing employee documents each item and walks the receiver through it. Reassign ownership formally: tickets, on-call rotations, shared mailboxes, calendar series, recurring approvals, doc and repo ownership, and any single-owner integrations or API keys. Receiver confirms they can operate independently — a document nobody has read is not a handover.
7. **Communicate the departure.** Agree the message and timing with the employee where possible. Notify the team, then affected customers and vendors, with the named replacement contact. Do not let customers learn from a bounced email.
8. **Trigger the backfill.** If the role is being refilled, start [[hiring]] now — notice periods are the cheapest overlap you will get.

### Phase 2 — Last day (revoke first)

9. **Revoke all access.** Work the Phase 1 checklist top to bottom on the scheduled time: disable SSO/IdP identity first (this cascades to most federated apps), then non-federated apps individually. Convert email to a forwarding rule or shared delegate rather than deleting the mailbox — deletion loses records you may need. Rotate any shared or service-account credentials the employee knew. Remove from admin groups, revoke API tokens and personal access tokens, terminate active sessions and refresh tokens, and disable MFA devices. Verify each item as done, not as requested.
10. **Collect equipment and physical assets.** Laptop, phone, peripherals, badge, keys, company card, and any physical records. For remote employees, ship a prepaid return kit with a tracked label and a deadline — track it to delivery. Log serial numbers against the departure record; wipe and re-image returned devices before reissue.
11. **Recover and preserve data.** Before wiping anything, transfer personally-owned drives, local repos, and mailbox contents to the receiver from step 6, and apply any legal hold. Confirm no company data remains on personal devices; collect a written attestation where policy requires it.
12. **Run the exit interview.** Hold it on or near the last day, after access is revoked and while memory is fresh. Use the structured format in [[employee-engagement]] — a neutral interviewer (HR, not the departing person's manager) gets more honest answers. Route themes back into retention.
13. **Close out obligations and agreements.** Review and reconfirm continuing obligations: confidentiality/NDA, IP assignment, non-solicit, and any severance or separation agreement. Provide copies. Collect the final signed acknowledgment.

### Phase 3 — Post-departure

14. **Process final payroll.** Pay final wages plus any accrued-PTO payout per your jurisdiction's deadline — some require payment on the last day or within days, especially for involuntary terminations. Settle outstanding expense reports, commissions, bonuses, and any repayable advances or relocation clawbacks. Late final pay carries statutory penalties in many jurisdictions; confirm your local rule rather than assuming.
15. **Terminate benefits and issue continuation notices.** End health, dental, vision, life, and retirement contributions on the recorded benefits end date. Issue the required continuation-coverage notice (COBRA in the US, or your local equivalent) within the statutory window — this is a hard legal deadline with real penalties, and it applies even when the employee says they don't want coverage. Provide retirement-plan rollover information.
16. **Verify the access revocation.** Two to four weeks out, audit that every account is actually disabled. Pull the IdP report and the app-by-app list and look for anything still active, any lingering group membership, and any sign-in attempts after the last day. Orphaned accounts surface here, not on the last day.
17. **Complete the compliance file.** Archive the departure record, signed agreements, exit interview notes, asset log, and revocation evidence per your retention policy. Update the org chart, headcount, and any regulated registers.
18. **Hand off to the alumni network.** Send a departure note with the final-pay and benefits-continuation summary, add the personal email to the alumni list where the employee consents, and record rehire eligibility. Alumni are your cheapest referral and boomerang-hire pipeline — a clean exit is what makes that possible.

## Red Flags / Common Mistakes

| Red flag | Why it's a problem | Do instead |
|---|---|---|
| Access revoked days after the last day | Unmonitored access to systems and data; the top audit finding | Schedule revocation for the last day; immediate for cause |
| Waiting for the laptop before disabling accounts | Couples a security action to a logistics delay | Revoke access first; collect equipment on its own track |
| Knowledge transfer as a doc dump | Nobody reads it; the knowledge leaves with the person | Named receiver per item; receiver confirms they can operate it |
| No access inventory to work from | Systems get missed; orphaned accounts persist | Work the inventory from [[employee-onboarding]]; log every gap |
| COBRA/continuation notice missed or late | Hard statutory deadline; real financial penalties | Issue on the recorded benefits end date, regardless of stated intent |
| Final pay and PTO payout on the normal cycle | Many jurisdictions require faster; penalties accrue | Confirm the local deadline from the notice date |
| Mailbox and accounts deleted immediately | Destroys records needed for audit or legal hold | Disable and forward; delete only per retention policy |
| Exit interview run by the departing manager | Suppresses the honest answers you need most | Neutral interviewer; route themes via [[employee-engagement]] |

## Exit criteria

- [ ] Notice acknowledged in writing; departure record created with last day, benefits end date, and final pay date.
- [ ] Access inventory reconciled against live systems; every gap logged.
- [ ] All access revoked on the scheduled date and each item individually verified — SSO/IdP, apps, repos, cloud, VPN, badge, cards, tokens, sessions, MFA devices.
- [ ] Shared and service-account credentials the employee knew have been rotated.
- [ ] Knowledge transfer complete: every item has a named receiver who has confirmed independent operation.
- [ ] All equipment and physical assets returned and logged by serial number, or formally written off.
- [ ] Company data recovered from personal devices; legal hold applied where applicable.
- [ ] Exit interview conducted by a neutral interviewer and themes routed into [[employee-engagement]].
- [ ] Final pay and accrued-PTO payout issued within the jurisdiction's deadline; expenses settled.
- [ ] Benefits terminated and continuation-coverage (COBRA or local equivalent) notice issued within the statutory window.
- [ ] Post-departure access audit at 2–4 weeks confirms zero active accounts and no post-departure sign-ins.
- [ ] Compliance file archived; org chart and headcount updated; alumni handoff and rehire eligibility recorded.

## Sources

Synthesized from published offboarding practice: Rippling (offboarding checklist, final pay and benefits termination timing), RoboMQ (automated access deprovisioning and identity lifecycle), Cadenio and Chaser (notice-period handover and knowledge-transfer sequencing), Flip and FirstHR (last-day checklists, equipment return, exit interview placement), KS-Agents (agent-executable offboarding workflows), and OpenOrg (transparent offboarding and alumni-network practice). Least-privilege and access-inventory practice carries over from [[employee-onboarding]]; exit-interview structure lives in [[employee-engagement]].

**Jurisdiction warning:** final-pay deadlines, PTO-payout obligations, notice requirements, and continuation-coverage rules (COBRA applies to US employers at 20+ employees; other countries differ entirely) vary by country and by US state. Confirm the applicable rule for the employee's work location — do not apply these steps as universal law. Involve HR/legal on involuntary terminations, severance agreements, and legal holds.
