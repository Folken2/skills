---
name: purchase-order-management
description: "Use when running a purchase from requisition to close-out — creating and numbering a PO, routing it through an amount/department approval matrix, tracking the order, receiving goods (GRN), performing the 3-way match against PO and invoice, and resolving exceptions like shortages, overages, damage, and price variance. Triggers on \"raise a PO\", \"purchase order approval\", \"goods receipt\", \"3-way match\", \"invoice mismatch\"."
version: 1.0.0
author: Nuvel Skills
---

# Purchase Order Management

## Overview

Run the full purchase-order lifecycle as a controlled, auditable flow from requisition to close-out. The core principle: **no payment without a matched three-way.** The purchase order, the goods receipt, and the supplier invoice must agree on quantity and price before an invoice is approved for payment — this is the single control that stops overbilling, phantom receipts, and unauthorized spend. Every PO is created against budget, approved by the right authority level, and closed with a reviewable record.

## Toolchain

This skill defines the control flow; the data operations run through supporting skills:

- [[backoffice/xlsx]] — read the requisition spreadsheet, create and write PO records to the tracking workbook, and record goods receipts and the 3-way match.
- [[backoffice/pdf]] — render the issued PO document and the closed-PO archive packet.

End-to-end data flow: **read the requisition spreadsheet → create the PO record → write to the PO tracking workbook → match incoming goods receipt against the PO → flag exceptions → write the closed PO archive.** A runnable example that builds this three-sheet workbook lives in `scripts/generate_po_tracker.py`.

## When to use

- Converting an approved need into a purchase order against a qualified supplier.
- Receiving goods/services and reconciling them to a PO and invoice.
- Resolving a receipt or invoice exception (shortage, overage, damage, price variance).

## When NOT to use

- Vetting or onboarding the supplier first → use [[supplier-qualification]].
- Negotiating the price/terms that will populate the PO → use [[vendor-negotiation]].
- Deciding *how much* to order and *when* to reorder → use [[inventory-planning]].

## Workflow

1. **Requisition.** Read the requisition spreadsheet with [[backoffice/xlsx]] to capture each request: requestor, need, business justification, quantity, required-by date, and a budget check against the owning cost center. Reject or hold requisitions with no budget line. *Exit:* requisition record with an explicit budget-availability result.
2. **PO creation.** Generate a uniquely numbered PO with line items, agreed pricing, payment terms, delivery schedule, ship-to, and applicable tax, and write the record to the **PO Register** sheet of the tracking workbook with [[backoffice/xlsx]] (PO ID, supplier, requisitioner, date, line-item count, total value, status, approval level, payment terms, delivery date). Reference the qualified supplier's master record. *Exit:* a PO with a unique number and complete, priced line items in the register.
3. **Approval workflow.** Route the PO through the **approval matrix** — thresholds by amount, department, spend type, and budget holder. Higher value crosses more approval tiers. Do not issue to the supplier before the required approvals are on the record. *Exit:* PO approved per the matrix with approver(s) and date; unapproved POs not transmitted.
4. **Issue and track.** Transmit the approved PO and track its states: order confirmation, production, shipping, and expected receipt. Chase missing confirmations. *Exit:* supplier confirmation received; order status tracked to expected delivery.
5. **Goods receipt.** On delivery, perform receiving inspection: count quantity, check for damage and quality, and record a Goods Receipt Note (GRN) against the PO on the **Goods Receipt** sheet with [[backoffice/xlsx]] (receipt ID, PO ID, item, qty ordered, qty received, qty damaged, status Full/Partial/Over/Spoiled, receipt date, inspector). Record partial receipts as such. *Exit:* GRN recorded with received quantity and condition, linked to the PO.
6. **3-way match.** Match **PO ↔ receipt (GRN) ↔ invoice** on quantity and price within tolerance on the **3-Way Match** sheet with [[backoffice/xlsx]], using `IF` formulas over PO value, invoice value, and receipt value to compute variance and set Match/Mismatch status. A clean match releases the invoice for payment; anything outside tolerance routes to exceptions. *Exit:* invoice matched within tolerance (approved to pay) or flagged as an exception.
7. **Exceptions.** For shortages, overages, damage, price variance, or quality issues, resolve per policy: short/over-ship reconciliation, debit/credit notes, returns, or supplier dispute. Do not force-approve a mismatch to clear a backlog. *Exit:* each exception resolved with a documented disposition (accept, return, credit, dispute).
8. **Close-out.** On final receipt and matched invoice, close the PO: reconcile the final invoice, record a brief supplier performance note (on-time, quality, accuracy), and set the register status to Closed with [[backoffice/xlsx]]. Render the archived PO packet with [[backoffice/pdf]]. *Exit:* PO closed in the register, performance noted, packet archived.

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

## Supporting skills

- [[backoffice/xlsx]] — reads the requisition spreadsheet and writes the PO Register, Goods Receipt, and 3-Way Match sheets. Example: `scripts/generate_po_tracker.py` builds a 3-sheet tracking workbook (PO Register, Goods Receipt, 3-Way Match) with `IF`-formula match logic and a mix of matched, partial, and mismatched POs.
- [[backoffice/pdf]] — renders the issued PO document and the closed-PO archive packet.
- [[supplier-qualification]], [[vendor-negotiation]], [[inventory-planning]] — upstream skills that feed suppliers, terms, and order quantities into the PO.
