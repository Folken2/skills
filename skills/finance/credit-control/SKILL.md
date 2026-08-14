---
name: credit-control
description: "Use when managing accounts receivable and collections — aging analysis, dunning cadence, payment reminders, payment-plan negotiation, dispute handling, escalation, and cash application. Triggers on \"AR aging\", \"DSO\", \"dunning\", \"chase overdue invoices\", \"collections\", \"payment plan\", \"credit hold\"."
version: 1.0.0
author: Nuvel Skills
---

# Credit Control

## Overview

Systematic accounts-receivable management: measure what's owed and how late it is, chase it on a disciplined escalating cadence, resolve disputes fast, negotiate plans where recovery beats confrontation, and escalate only what genuinely warrants it. The core principle: **collection probability decays with age** — money owed is not money collected, and the odds of recovering an invoice fall sharply the longer it sits past due, so the entire discipline is about acting early and consistently rather than harder and later.

Portfolio reality: a small number of large, aging accounts usually drive most of the overdue balance. Working the aging report by *value and age* — not by whoever shouted last — is what moves DSO. Every account should always have a defined next action and next-action date; a silent overdue account is a leak.

## When to use

- You are managing a book of receivables and need aging, DSO, and a collection plan.
- An invoice is past due and needs the right dunning step and tone.
- A customer can't pay in full and a structured payment plan is on the table.
- An account needs escalation (credit hold, collections agency, legal) or cash needs applying.

## When NOT to use

- You are creating or delivering a single invoice → use [[invoicing]].
- The invoice error is genuine and needs a credit note, not collection → correct it via [[invoicing]].
- You need to know when the cash will land for planning → use [[cashflow-forecasting]].

## Workflow

1. **Build the aging.** Pull all open AR into standard buckets (current, 1–30, 31–60, 61–90, 90+) by customer. Calculate **DSO** (average receivables ÷ credit sales × days in period) and compare to your payment terms and prior periods — rising DSO with flat sales means collection is slipping. Flag the accounts driving the balance.
2. **Segment the book.** Triage accounts by value × age × risk. Prioritize high-value/high-age first, and separate *won't pay* (needs pressure/escalation) from *can't pay yet* (needs a plan) from *disputing* (needs resolution). One-size dunning wastes effort on both ends.
3. **Run the dunning sequence.** Apply a fixed cadence with escalating tone: pre-due courtesy → due-date reminder → gentle overdue nudge (7 days) → firm reminder (14–21 days) → final demand with consequences (30+ days). Match channel to stage — email early, phone as it ages, formal letter for the final demand. Log every contact, response, and promise-to-pay with a follow-up date.
4. **Chase with a promise-to-pay.** Every conversation must end with a specific commitment: amount and date. Record it, and if a promise-to-pay breaks, escalate a step rather than resetting the cadence — broken promises are a stronger risk signal than raw age.
5. **Negotiate a payment plan when warranted.** For a *can't-pay* account worth preserving, agree written terms: an upfront down payment, a fixed installment schedule with dates, and a default clause (miss one → full balance due, account to hold). Get it in writing and monitor each installment. A plan you don't track is just a delay.
6. **Resolve disputes.** For a disputed invoice, verify the claim against the PO/contract/delivery evidence, document it, and set a resolution owner and date. Freeze dunning **only on the disputed amount** and keep collecting the undisputed balance. Route genuine billing errors back to [[invoicing]] for a credit note.
7. **Escalate deliberately.** When cadence and negotiation are exhausted, escalate through defined stages: internal credit hold (stop new orders), then third-party collections agency, then legal/small-claims — each gated on approval and a documented recovery-vs-cost judgment. Don't escalate to legal what a phone call would have fixed, and don't keep dialing an account that needs legal.
8. **Apply cash accurately.** Match every remittance to specific invoices using the remittance advice. Handle unallocated/on-account cash by chasing the customer for allocation detail rather than guessing — misapplied cash creates false overdues and re-chases customers who already paid.

## Common Pitfalls

| Pitfall | Why it's a problem | Do instead |
|---|---|---|
| Chasing by squeaky-wheel, not by value × age | The balance-driving accounts drift older | Work the aging report top-down by value and age |
| Freezing all dunning over a partial dispute | Undisputed money stops flowing | Freeze only the disputed amount; keep collecting the rest |
| Resetting the cadence after a broken promise-to-pay | Rewards non-payment; masks a risk signal | Escalate a step; treat broken PTP as a red flag |
| Payment plan with no down payment or default clause | Becomes an indefinite, unenforceable delay | Down payment + dated installments + default-to-full clause |
| Unallocated cash parked and forgotten | Creates phantom overdues and duplicate chasing | Get remittance detail and apply to specific invoices |

## Verification Checklist

- [ ] AR aging built by customer and bucket; DSO calculated and trended vs terms/prior periods.
- [ ] Book segmented (won't-pay / can't-pay / disputing) and prioritized by value × age.
- [ ] Dunning cadence running with escalating tone and channel; every contact and promise-to-pay logged with a next date.
- [ ] Payment plans in writing with down payment, dated installments, and a default clause; installments monitored.
- [ ] Disputes verified, documented, owned, and dated; dunning frozen only on the disputed amount.
- [ ] Escalations (credit hold → agency → legal) gated on approval and a recovery-vs-cost decision.
- [ ] Remittances applied to specific invoices; no unallocated cash left parked.

## Sources

Aligned with standard credit-control and collections practice (AR aging, DSO, escalating dunning, promise-to-pay discipline, structured payment plans). Adapt escalation steps, late-fee/interest terms, and collection communications to your jurisdiction's consumer- and commercial-debt regulations.
