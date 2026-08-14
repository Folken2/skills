---
name: vendor-negotiation
description: "Use when preparing for and running a commercial negotiation with a vendor — building market intelligence and a BATNA, setting targets and a walk-away point, choosing pricing levers (volume, tiered, rebates, payment terms) and terms (SLA, warranty, liability, termination, IP, renewal), managing concessions with a trade-off matrix, and documenting the agreement. Triggers on \"negotiate with vendor\", \"BATNA\", \"walk-away point\", \"concession framework\", \"contract terms\"."
version: 1.0.0
author: Nuvel Skills
---

# Vendor Negotiation

## Overview

Run vendor negotiations from a prepared position instead of reacting across the table. The core principle: **never negotiate without a BATNA and a walk-away point.** Your Best Alternative To a Negotiated Agreement is your source of power — it defines the price and terms below which walking away beats agreeing. Everything else (targets, pricing levers, concessions) is planned in advance so that concessions are traded, not given, and every outcome is measured against the targets you set before the first meeting.

## Toolchain

This skill defines the negotiation strategy; the data work runs through supporting skills:

- [[backoffice/xlsx]] — read the market intelligence spreadsheet, write the negotiation plan (BATNA, targets, walk-away), and log outcomes with savings formulas.
- [[backoffice/pdf]] — generate the contract/term-sheet summary from the agreed outcome.

End-to-end data flow: **read the market intelligence spreadsheet with [[backoffice/xlsx]] → prepare the negotiation plan with BATNA/targets → write the negotiation outcome record → generate the contract summary.** A runnable example that builds this three-sheet workbook lives in `scripts/generate_negotiation_workbook.py`.

## When to use

- Preparing for a price/terms negotiation with a shortlisted or incumbent vendor.
- Renewing or renegotiating an existing contract or SLA.
- Structuring a concession strategy before a live negotiation round.

## When NOT to use

- Vetting whether the vendor is even qualified → use [[supplier-qualification]].
- Executing routine orders under an already-agreed contract → use [[purchase-order-management]].
- Forecasting demand or setting order quantities → use [[inventory-planning]].

## Workflow

1. **Prepare.** Read the **Market Intel** sheet with [[backoffice/xlsx]] (supplier, product/category, market price, their price, competitor price, availability, lead time, quality score) to build your benchmarks. Define your **BATNA** and your **walk-away point** (the terms past which you decline), then write the **Negotiation Plan** sheet with [[backoffice/xlsx]] — target price, walk-away price, BATNA, key terms, concessions available, must-haves, nice-to-haves, strategy — and assemble the negotiating team with clear roles. *Exit:* a negotiation plan spreadsheet with BATNA, walk-away, and per-issue targets documented.
2. **Choose strategy.** Select a stance — competitive (leverage alternatives on price), collaborative (grow value jointly), or concession-based — matched to the relationship's importance and your leverage. A strategic supplier warrants collaboration; a commodity buy tolerates competitive pressure. *Exit:* a chosen strategy with rationale.
3. **Plan pricing levers.** Identify the levers you can pull: volume discounts, tiered pricing, rebates, and payment terms (e.g., extended terms or early-pay discounts). Know the value of each to both sides so you trade the cheap-to-you / valuable-to-them ones. *Exit:* a ranked list of pricing levers with their cost/value to each side.
4. **Plan terms.** Set positions on non-price terms: SLA/performance, warranty, liability caps, termination rights, IP/ownership, exclusivity, and renewal/auto-renewal. Non-price terms often carry more long-run value than the unit price. *Exit:* a target and acceptable position for each material term.
5. **Build the concession framework.** Create a **trade-off matrix**: what you will concede, what you require in return, the sequence, walk-away triggers, and the escalation path. Plan concessions as trades, never unilateral give-aways, and never concede past the walk-away point. *Exit:* a concession/trade-off matrix with walk-away triggers and escalation defined.
6. **Negotiate.** Run the rounds against the plan: anchor, trade concessions per the matrix, and re-check every proposal against your BATNA and walk-away. If the deal falls below your reservation and cannot recover, invoke the BATNA. *Exit:* an agreement reached within the target/acceptable band, or a documented decision to walk to the BATNA.
7. **Document the agreement.** Write the outcome to the **Outcome Log** sheet with [[backoffice/xlsx]] (supplier, date, agreed price, terms achieved, concessions given, next review date, notes) with formulas computing savings vs. target and vs. walk-away, then generate the contract/term-sheet summary with [[backoffice/pdf]] — LOI, term sheet, contract, or amendment — with the agreed price, levers, and terms reflected accurately. *Exit:* an executed (or ready-to-execute) agreement matching what was agreed.
8. **Debrief.** Record outcomes vs. targets in the Outcome Log with [[backoffice/xlsx]], capture lessons learned, and note the impact on the supplier relationship for the next round. *Exit:* an outcome record comparing results to the step-1 targets, with lessons and relationship notes.

## Common Pitfalls

| Pitfall | Why it's a problem | Do instead |
|---|---|---|
| Negotiating without a BATNA | No leverage; you accept bad terms under pressure | Define BATNA and walk-away before the first meeting |
| Conceding without a return | Erodes value and trains the vendor to push | Trade every concession per the trade-off matrix |
| Fixating on unit price | Weak SLA/liability/renewal terms cost more long-run | Set targets on non-price terms too |
| No walk-away discipline | Deals drift below your reservation point | Re-check every proposal against the walk-away trigger |
| Skipping the debrief | Lessons and relationship signal are lost | Record outcomes vs. targets and lessons learned |

## Verification Checklist

- [ ] Negotiation plan documents BATNA, walk-away point, and per-issue targets (ideal/acceptable/reservation).
- [ ] A negotiation strategy is chosen with rationale.
- [ ] Pricing levers ranked by cost/value to each side.
- [ ] Target and acceptable positions set for each material non-price term.
- [ ] Concession/trade-off matrix built with walk-away triggers and escalation path.
- [ ] Every concession made in the negotiation was traded, none past the walk-away point.
- [ ] Agreement documented in the correct instrument, matching what was agreed.
- [ ] Debrief records outcomes vs. targets, lessons, and relationship impact.

## Sources

Aligned with principled-negotiation practice (BATNA, reservation/walk-away, interest-based trade-offs) and category-management sourcing strategy. Negotiate only qualified suppliers from [[supplier-qualification]]; the agreed terms then govern orders in [[purchase-order-management]].

## Supporting skills

- [[backoffice/xlsx]] — reads the market intelligence spreadsheet and writes the Negotiation Plan and Outcome Log sheets. Example: `scripts/generate_negotiation_workbook.py` builds a 3-sheet preparation workbook (Market Intel, Negotiation Plan, Outcome Log) with savings-vs-target and savings-vs-walk-away formulas.
- [[backoffice/pdf]] — generates the contract/term-sheet summary from the agreed outcome.
- [[supplier-qualification]], [[purchase-order-management]], [[inventory-planning]] — the qualification, ordering, and planning skills that bracket the negotiation.
