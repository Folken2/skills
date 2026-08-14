---
name: order-management
description: "Use when a customer contacts support about an order — locating it, verifying identity, checking status, resolving shipping/fulfillment issues, or processing returns, refunds, replacements, and payment problems. Triggers on 'where is my order', 'I want a refund', 'my package is damaged', 'wrong item', 'cancel my order', 'payment failed', 'change my address'."
version: 1.0.0
author: Nuvel Skills
---

# Order Management

## Overview

Order support is where a company's promises get tested. The customer already paid; now something is late, wrong, or missing, and the interaction determines whether they order again. The core principle: **verify identity, establish the true order state, then apply a consistent decision rule — never improvise a refund or replacement on the fly.** Consistency protects both the customer (fair treatment) and the business (margin, fraud exposure).

This skill maps the full order lifecycle and gives a decision matrix for the highest-friction moments — refunds, replacements, and payment disputes — so any agent reaches the same outcome for the same facts. It is industry-agnostic: the same flow serves physical goods, digital products, and subscriptions.

## Toolchain

Order support runs on the order records, not memory. Use these supporting skills for the data work:

- [[backoffice/xlsx]] — search the orders master spreadsheet to locate an order, read its true status, write the refund/return decision to a separate tracking workbook, and generate the daily returns report.
- [[backoffice/pdf]] — render a refund confirmation letter or a returns report as a PDF for the customer or finance.

A runnable example lives in `scripts/generate_order_template.py`, which builds a three-sheet order workbook (Orders Master, Returns/Refunds, Order Lookup) with lookup formulas.

## When to use

- A customer asks about the status, contents, delivery, or cancellation of an order.
- A shipment is delayed, damaged, lost, or arrived wrong.
- A return, refund, or replacement needs eligibility assessment and processing.
- A payment failed, was double-charged, disputed, or needs to be refunded.

## When NOT to use

- The ticket has not been classified or prioritized yet → run [[ticket-triage]] first.
- The problem is a product defect or technical fault, not a fulfillment issue → use [[technical-troubleshooting]].
- You only need help wording a sensitive reply → use [[customer-communication]].

## Workflow

1. **Locate the order.** Search the **Orders Master** spreadsheet with [[backoffice/xlsx]] — by Order ID first, then by account email, then by name + delivery ZIP as a fallback (the Order Lookup sheet's XLOOKUP/VLOOKUP formula does this for a single ID). Confirm you have the *specific* order in question — customers with multiple recent orders routinely reference the wrong one.
2. **Verify identity before acting.** Match the requester to the order owner using your standard proof (logged-in session, email on file, order number + billing detail). Never change an address, cancel, or refund to a party you have not verified — this is the primary fraud and account-takeover vector in order support.
3. **Establish the true status.** Read the order's Status, Tracking, Est Delivery, and Actual Delivery columns from the Orders Master sheet with [[backoffice/xlsx]] — processing, shipped (with tracking), out for delivery, delivered, returned, refunded — and reconcile it with what the customer observes. When tracking says "delivered" but the customer disagrees, treat it as an investigation, not a contradiction.
4. **Diagnose shipping/fulfillment issues.** For **delays**, confirm the carrier status and set a realistic new expectation. For **damaged/wrong item**, gather evidence (photos, item received vs ordered). For **lost**, confirm the delivery window has genuinely passed and open a carrier trace before reshipping.
5. **Apply the refund/replacement decision matrix.** Decide against fixed rules, not mood: check **eligibility** (within return window? item condition? reason category — defect vs buyer's remorse?), then choose the remedy (repair/replace/refund/store credit), and state the **timeline** the customer should expect. Company-fault cases (damaged, wrong, lost) get the fastest, no-cost path; customer-choice returns follow the standard policy. Write the decision as a new row in the **Returns/Refunds** tracking workbook with [[backoffice/xlsx]] — Return ID, Order ID, Reason, Amount, Refund Status, Date Initiated — so every refund is auditable and never lives only in the ticket.
6. **Resolve payment issues.** For a **failed** payment, identify the decline reason and offer a retry or alternate method. For a **double charge or dispute**, confirm the transaction records before promising anything, and route chargebacks to the finance/payments owner. For an approved **refund**, state the method and the settlement window (card refunds commonly take several business days).
7. **Handle exceptions explicitly.** Address changes (only pre-shipment, post-verification), split shipments (set expectations for each parcel), and backorders (give an honest restock date or offer an alternative). Do not let an exception silently stall — name it and give the customer a decision.
8. **Confirm resolution and communicate.** Send the matching communication template for the scenario: what happened, what you did, what the customer will see next, and by when. Log the outcome and reason code in the Returns/Refunds sheet with [[backoffice/xlsx]] (set Refund Status and Date Completed), then generate the **daily returns report** — counts and totals by reason and status — and optionally render a refund confirmation letter to PDF with [[backoffice/pdf]]. Logging keeps refund/replacement rates and root causes trackable.

## Common Pitfalls

- **Acting before verifying identity.** Refunding or changing an address for an unverified requester invites fraud and account takeover. Verify first, every time.
- **Improvising remedies.** Ad-hoc refunds erode margin and create unfair, inconsistent treatment. Run every refund/replacement through the decision matrix.
- **Trusting "delivered" or the customer blindly.** A "delivered" scan and a "never arrived" claim can both be true. Open a trace and investigate rather than instantly reship or dismiss.
- **Promising a refund timeline you don't control.** Card settlement takes days on the bank's clock. State the real window so the customer doesn't return angry on day two.
- **Letting backorders and split shipments go silent.** Unspoken exceptions become "where is my order" tickets. Surface them proactively with a date or a choice.

## Verification Checklist

- [ ] The specific order was located and confirmed with the customer.
- [ ] Requester identity was verified before any change, cancellation, or refund.
- [ ] True order status was established and reconciled with what the customer sees.
- [ ] Any shipping issue (delay/damaged/wrong/lost) has evidence gathered and a carrier trace where needed.
- [ ] Refund/replacement decision was made against the eligibility matrix, with remedy and timeline stated.
- [ ] Payment issues were reconciled against transaction records before any promise; disputes routed correctly.
- [ ] Exceptions (address change, split shipment, backorder) were surfaced with a clear next step or choice.
- [ ] The matching communication was sent and the outcome logged with a reason code.
- [ ] The refund/return decision was written to the Returns/Refunds tracking workbook and a daily returns report was generated.

## Supporting skills

- [[backoffice/xlsx]] — search the Orders Master sheet, write refund/return decisions to the Returns/Refunds tracker, and build the daily returns report.
- [[backoffice/pdf]] — render a refund confirmation letter or returns report as a PDF for the customer or finance.
- [[ticket-triage]], [[technical-troubleshooting]], [[customer-communication]] — upstream routing, defect diagnosis, and the wording of sensitive replies.
