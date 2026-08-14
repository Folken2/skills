---
name: purchase-order-management
description: "Use when running a purchase from requisition to close-out — creating and numbering a PO, routing it through an amount/department approval matrix, tracking the order, receiving goods (GRN), performing the 3-way match against PO and invoice, and resolving exceptions like shortages, overages, damage, and price variance. Triggers on \"raise a PO\", \"purchase order approval\", \"goods receipt\", \"3-way match\", \"invoice mismatch\"."
version: 1.0.0
author: Nuvel Skills
---

# Purchase Order Management

## Overview

Run the full purchase-order lifecycle as a controlled, auditable flow from requisition to close-out. The core principle: **no payment without a matched three-way.** The purchase order, the goods receipt, and the supplier invoice must agree on quantity and price before an invoice is approved for payment — this is the single control that stops overbilling, phantom receipts, and unauthorized spend. Every PO is created against budget, approved by the right authority level, and closed with a reviewable record.

## When to use

- Converting an approved need into a purchase order against a qualified supplier.
- Receiving goods/services and reconciling them to a PO and invoice.
- Resolving a receipt or invoice exception (shortage, overage, damage, price variance).

## When NOT to use

- Vetting or onboarding the supplier first → use [[supplier-qualification]].
- Negotiating the price/terms that will populate the PO → use [[vendor-negotiation]].
- Deciding *how much* to order and *when* to reorder → use [[inventory-planning]].

## Workflow

1. **Requisition.** Capture the request: requestor, need, business justification, quantity, required-by date, and a budget check against the owning cost center. Reject or hold requisitions with no budget line. *Exit:* requisition record with an explicit budget-availability result.
2. **PO creation.** Generate a uniquely numbered PO with line items, agreed pricing, payment terms, delivery schedule, ship-to, and applicable tax. Reference the qualified supplier's master record. *Exit:* a PO with a unique number and complete, priced line items.
3. **Approval workflow.** Route the PO through the **approval matrix** — thresholds by amount, department, spend type, and budget holder. Higher value crosses more approval tiers. Do not issue to the supplier before the required approvals are on the record. *Exit:* PO approved per the matrix with approver(s) and date; unapproved POs not transmitted.
4. **Issue and track.** Transmit the approved PO and track its states: order confirmation, production, shipping, and expected receipt. Chase missing confirmations. *Exit:* supplier confirmation received; order status tracked to expected delivery.
5. **Goods receipt.** On delivery, perform receiving inspection: count quantity, check for damage and quality, and record a Goods Receipt Note (GRN) against the PO. Record partial receipts as such. *Exit:* GRN recorded with received quantity and condition, linked to the PO.
6. **3-way match.** Match **PO ↔ receipt (GRN) ↔ invoice** on quantity and price within tolerance. A clean match releases the invoice for payment; anything outside tolerance routes to exceptions. *Exit:* invoice matched within tolerance (approved to pay) or flagged as an exception.
7. **Exceptions.** For shortages, overages, damage, price variance, or quality issues, resolve per policy: short/over-ship reconciliation, debit/credit notes, returns, or supplier dispute. Do not force-approve a mismatch to clear a backlog. *Exit:* each exception resolved with a documented disposition (accept, return, credit, dispute).
8. **Close-out.** On final receipt and matched invoice, close the PO: reconcile the final invoice, record a brief supplier performance note (on-time, quality, accuracy), and archive the PO packet. *Exit:* PO closed, performance noted, packet archived.

## Common Pitfalls

| Pitfall | Why it's a problem | Do instead |
|---|---|---|
| Paying on invoice alone (no match) | Overbilling and phantom receipts go through | Require a clean 3-way match before payment |
| Issuing the PO before approval | Unauthorized/over-budget commitment | Transmit only after the approval matrix clears |
| No budget check at requisition | Spend exceeds the cost-center budget silently | Check budget availability before creating the PO |
| Force-approving mismatches to clear backlog | Defeats the core control; hides supplier errors | Route to exceptions; document each disposition |
| GRN skipped or done from the packing slip | Receipt not verified; damage/shortage invisible | Physically inspect and record a GRN against the PO |

## Verification Checklist

- [ ] Requisition captured with justification and an explicit budget-availability result.
- [ ] PO uniquely numbered with complete, priced line items and terms.
- [ ] PO approved per the amount/department approval matrix before transmission.
- [ ] Order confirmed and tracked to expected delivery.
- [ ] GRN recorded on receipt with quantity and condition, linked to the PO.
- [ ] 3-way match (PO ↔ GRN ↔ invoice) passed within tolerance before payment.
- [ ] Every exception resolved with a documented disposition.
- [ ] PO closed with a supplier performance note and the packet archived.

## Sources

Aligned with standard procure-to-pay (P2P) practice — requisition-to-PO conversion, delegation-of-authority approval matrices, goods receipt notes, and three-way matching as the core payment control. Source suppliers via [[supplier-qualification]]; set order quantities via [[inventory-planning]].
