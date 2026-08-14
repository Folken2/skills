---
name: supplier-qualification
description: "Use when identifying, vetting, and onboarding a new vendor or supplier — sourcing candidates, running due diligence (financial, legal, certifications, references, insurance), assessing capability and risk, scoring against weighted criteria, and creating the supplier master record. Triggers on \"qualify a supplier\", \"vendor vetting\", \"supplier due diligence\", \"onboard vendor\", \"supplier scorecard\"."
version: 1.0.0
author: Nuvel Skills
---

# Supplier Qualification

## Overview

Turn an unknown vendor into an approved, onboarded supplier through a repeatable gate process. The core principle: **qualification is a decision gate, not a formality.** Every supplier that touches your supply chain carries financial, legal, quality, and continuity risk — the point of qualification is to price that risk *before* you place a purchase order, using a weighted scorecard and an explicit approval gate rather than a gut feel. A supplier who fails a gate should not advance simply because they are cheap or fast.

## When to use

- Adding a net-new vendor to the supplier master, or re-qualifying an existing one.
- Sourcing candidates for a category with no approved supplier (single-source risk).
- A periodic review is due and a tier-1 supplier must be re-scored.

## When NOT to use

- Negotiating price/terms with an already-qualified supplier → use [[vendor-negotiation]].
- Placing an order against an approved supplier → use [[purchase-order-management]].
- Setting stock levels or reorder policy → use [[inventory-planning]].

## Workflow

1. **Identify candidates.** Build a shortlist from industry research, trade shows, referrals, and a formal RFI (Request for Information). Capture each candidate's legal entity name, category, geography, and a one-line fit rationale. *Exit:* ≥3 candidates recorded for the category (or a documented justification if fewer exist).
2. **Run due diligence.** For each shortlisted candidate collect and verify: financial health (statements, credit rating, D&B or equivalent), legal/compliance standing (registration, sanctions/watchlist screening, litigation), required certifications (ISO, industry-specific), 2–3 customer references, and proof of insurance. *Exit:* a due-diligence packet exists per candidate with no open red flags, or red flags explicitly waived by an approver.
3. **Assess capability.** Score production/service capacity, quality systems, technology fit, geographic coverage, and quoted lead times against your actual demand. Confirm the supplier can meet volume at your required cadence — not just a one-off sample. *Exit:* capability rated against documented requirements, gaps noted.
4. **Evaluate risk.** Assess concentration/dependency risk (what % of this category rides on one supplier), geopolitical and regulatory exposure, and single-source fragility. Flag any supplier that would create an unmitigated single point of failure. *Exit:* a risk rating (e.g., low/medium/high) assigned with the top risks named.
5. **Score against weighted criteria.** Combine steps 2–4 into a **qualification scorecard**: each criterion weighted by importance (e.g., quality 30%, price 20%, capacity 20%, risk 15%, compliance 15%), scored, and summed to a single number with a pass threshold. *Exit:* a completed weighted scorecard with a total score and pass/fail against the threshold.
6. **Approval gate.** Route the scorecard through the approval gate for the supplier's tier/spend. An approver signs off, waives specific red flags on the record, or rejects. Do not proceed on a fail without a documented waiver. *Exit:* an approval decision (approve / conditional / reject) is recorded with approver and date.
7. **Onboard.** For approved suppliers, execute onboarding: NDA, master contract, supplier master data (tax IDs, banking, remittance, contacts), system access, and any required training. Verify banking details out-of-band to prevent payment fraud. *Exit:* supplier master record created and complete; NDA and contract executed.
8. **Classify and schedule review.** Segment and tier the supplier (strategic / preferred / transactional), set the periodic re-qualification cadence by tier, and record it on the master. *Exit:* classification and next-review date on the master record.

## Common Pitfalls

| Pitfall | Why it's a problem | Do instead |
|---|---|---|
| Qualifying on price alone | Cheap suppliers fail on quality, continuity, or compliance | Score against weighted criteria across all dimensions |
| Skipping banking verification | Onboarding fraud diverts real payments | Verify banking details out-of-band before first payment |
| Ignoring single-source risk | One supplier's failure halts a whole category | Rate concentration risk; require a backup or a waiver |
| Accepting a sample as proof of capacity | Supplier can't sustain your actual volume/cadence | Assess capacity against real demand, not the sample |
| No re-qualification cadence | Certifications lapse, financials deteriorate silently | Set tier-based periodic review on the master record |

## Verification Checklist

- [ ] ≥3 candidates (or documented justification) identified for the category.
- [ ] Due-diligence packet per candidate: financials, legal/sanctions screen, certifications, references, insurance — no open red flags (or waived).
- [ ] Capability assessed against documented demand requirements.
- [ ] Risk rated, including concentration/single-source exposure.
- [ ] Weighted qualification scorecard completed with total score vs. pass threshold.
- [ ] Approval gate decision recorded (approver + date); no fail advanced without a waiver.
- [ ] Onboarding complete: NDA, contract, master data, access, banking verified out-of-band.
- [ ] Supplier classified/tiered with a next-review date on the master record.

## Sources

Aligned with standard strategic-sourcing and supplier-management practice (RFI/RFP, supplier due diligence, weighted scorecards, supplier segmentation/tiering, single-source risk). Coordinate downstream ordering with [[purchase-order-management]] and commercial terms with [[vendor-negotiation]].
