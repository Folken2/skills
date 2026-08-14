---
name: ticket-triage
description: "Use when a new support ticket arrives and needs to be classified, prioritized, and routed — issue type, severity, SLA assignment, tier routing, first response, and escalation. Triggers on 'triage this ticket', 'what priority', 'who handles this', 'route to the right team', 'is this an escalation'."
version: 1.0.0
author: Nuvel Skills
---

# Ticket Triage

## Overview

Triage is the first 5 minutes of a support ticket's life, and it sets everything that follows: how fast it gets answered, who works it, and whether a critical issue surfaces before it becomes an incident. The core principle: **classify before you solve.** A ticket that is mis-tagged as a low-priority question when it is a security report, or routed to tier 1 when it needs engineering, loses hours that no later diligence recovers.

This skill produces a repeatable triage matrix (type × severity → SLA + tier) so every ticket is handled consistently regardless of who is at the desk. It is deliberately harness-agnostic and industry-agnostic — the same flow works for a SaaS help desk, an e-commerce inbox, or a B2B account team.

## Toolchain

Triage is data work, not just judgment. Use these supporting skills to move real ticket data:

- [[backoffice/xlsx]] — read the inbound ticket import spreadsheet, write triaged tickets back with severity/SLA/tier columns, and generate the daily open/closed/escalated report workbook.
- [[backoffice/pdf]] — render the daily triage report or an escalation summary as a shareable PDF for stakeholders.

A runnable example lives in `scripts/generate_ticket_template.py`, which builds a three-sheet ticket-tracking workbook (Tickets, SLA Matrix, Daily Report) you can use as the triage template.

## When to use

- A new ticket, email, chat, or call has arrived and has not been classified.
- A queue has backed up and needs to be sorted by priority.
- You need to decide who owns a ticket, or whether it should escalate now.
- You are defining or auditing the team's SLA and routing rules.

## When NOT to use

- The ticket is already triaged and you are actively resolving a technical fault → use [[technical-troubleshooting]].
- The ticket is an order/fulfillment matter already routed to you → use [[order-management]].
- You only need help phrasing a reply → use [[customer-communication]].

## Workflow

1. **Capture the essentials.** Read the inbound ticket import spreadsheet with [[backoffice/xlsx]] — one row per raw ticket — and for each row record: source (email/chat/phone/social/in-app), customer identity and account tier, a one-line problem statement in the customer's words, and any urgency signals (production down, revenue impact, angry tone, legal/security language, deadline). Do not proceed on a vague "it's broken" — get one concrete symptom.
2. **Classify the type.** Tag exactly one primary type: **bug** (product not working as designed), **question** (how-to / clarification), **request** (feature or change), **complaint** (dissatisfaction, no defect), or **order** (billing, shipping, account/fulfillment). Also tag the product/feature area for routing and trend analysis.
3. **Assign severity.** Rate **critical** (widespread outage, data loss, security, or blocked revenue — no workaround), **high** (major feature broken for one customer, workaround painful), **medium** (partial impairment with a workaround), or **low** (cosmetic, question, minor request). Severity is about impact, not the customer's volume.
4. **Set the SLA.** Map type × severity to a response-time and resolution-time target using the **SLA Matrix** sheet as a lookup table (read it with [[backoffice/xlsx]]), and note whether the clock runs on business hours or 24/7 for this severity. Define the escalation threshold — the elapsed time at which an unresolved ticket auto-escalates. Write the resolved SLA Due timestamp into the ticket row so the matrix is applied uniformly.
5. **Route to a tier.** **Tier 1** handles first response and common/known issues; **tier 2** handles technical diagnosis and account-specific problems; **tier 3** is engineering/management for defects, data, or policy exceptions. Route to the lowest tier that can fully resolve it — do not skip tiers to look fast, and do not park a tier-3 issue in tier 1. Write the classified rows — with Priority Score, Assigned Tier, and SLA Due columns filled — back to a new triaged workbook with [[backoffice/xlsx]] (billing→Tier1, technical→Tier2, bug→Tier3; Critical=100 / High=75 / Medium=50 / Low=25 priority score).
6. **Send the first response.** Acknowledge receipt, restate the problem so the customer knows they were understood, set an expectation (who is on it and by when), and state the next step. A fast, honest acknowledgment beats a slow "solved" — first-response time is the metric customers feel most.
7. **Apply escalation criteria.** Escalate immediately — regardless of SLA timer — on: any security/privacy report, data loss, a repeat of an already-"resolved" issue, a critical account at churn risk, legal/regulatory language, or severity crossing the threshold. Escalation is a routing decision, not an admission of failure.
8. **Hand off with a structured summary.** When moving a ticket between tiers or agents, pass a summary: problem, type/severity, what was tried, customer expectation already set, and the specific ask of the receiving tier. A handoff without context forces the customer to repeat themselves — the top driver of support dissatisfaction. At end of shift, generate the **Daily Report** sheet with [[backoffice/xlsx]] that uses COUNTIFS formulas over the Tickets sheet to count open/closed/escalated tickets by severity and tier, and optionally render it to PDF with [[backoffice/pdf]] for the stand-up.

## Common Pitfalls

- **Solving before classifying.** Jumping straight to a fix means severity and SLA are never set, so criticals hide in the queue. Tag first, always.
- **Severity by customer volume, not impact.** The loudest customer is not automatically critical, and a quiet security report is not low. Rate the impact on the system and the business.
- **Skipping tiers to appear responsive.** Pushing a defect through tier 1 "just to reply fast" burns a cycle and delays the real fix. Route to the tier that can actually resolve it.
- **Silent handoffs.** Reassigning without a summary forces the customer to re-explain. Every tier change carries context.
- **No first response until there's an answer.** Waiting for a full solution blows first-response SLA. Acknowledge and set expectations immediately, then work the fix.

## Verification Checklist

- [ ] Ticket has a source, customer/account tier, and a concrete one-line problem statement.
- [ ] Exactly one primary type and a product/feature area are tagged.
- [ ] Severity (critical/high/medium/low) is assigned by impact, with a documented reason.
- [ ] SLA (response + resolution time, business-hours vs 24/7, escalation threshold) is set from the triage matrix.
- [ ] Ticket is routed to the lowest tier that can fully resolve it.
- [ ] A first response acknowledging the issue and setting an expectation has been sent.
- [ ] Escalation criteria were checked; any security/data/at-risk trigger was actioned immediately.
- [ ] Any tier or agent handoff carries a structured summary (problem, severity, tried, expectation, ask).
- [ ] Triaged tickets were written back to a workbook with Priority Score, Assigned Tier, and SLA Due columns, and a daily open/closed/escalated report was generated.

## Supporting skills

- [[backoffice/xlsx]] — read the ticket import spreadsheet, write the triaged workbook (Tickets + SLA Matrix), and build the daily open/closed/escalated report.
- [[backoffice/pdf]] — render the daily triage report or escalation summary as a shareable PDF.
- [[order-management]], [[technical-troubleshooting]], [[customer-communication]] — the downstream skills a triaged ticket routes into.
