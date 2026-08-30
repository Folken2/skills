---
name: invoicing
description: "Use when billing a customer end-to-end — from creating an invoice through delivery, payment terms, follow-up, payment capture, and reconciliation. Triggers on \"raise an invoice\", \"bill the customer\", \"send an invoice\", \"chase payment\", \"reconcile a payment\", \"issue a credit note\"."
version: 1.0.0
author: Nuvel Skills
---

# Invoicing

## Overview

The full order-to-cash billing workflow: create a correct invoice, deliver it through the channel the customer can actually pay from, follow up on a fixed cadence, capture payment, and reconcile it against the ledger. The core principle: **an invoice is a legal payment demand, not a receipt** — every field that affects tax, currency, or the payment deadline must be right *before* it leaves, because corrections require a credit note and reset the clock.

Cash reality: the single largest lever on days-sales-outstanding is not chasing harder, it is invoicing accurately and immediately. A disputed or malformed invoice is the most common cause of a 30+ day payment delay, and most disputes trace to a missing PO number, wrong tax treatment, or an ambiguous due date.

## Toolchain

This skill is domain expertise; the actual data work runs through supporting skills:

- **[[backoffice/xlsx]]** — read order/billing data and the AR tracking workbook, and write invoice records back. Reach for it whenever a step reads from or writes to an `.xlsx` file.
- **[[backoffice/pdf]]** — render the finished invoice as the PDF you deliver to the customer.

## When to use

- A deliverable or milestone is complete and a customer must be billed.
- You are setting up delivery, payment terms, or a follow-up cadence for a bill.
- A payment has arrived and must be matched to open invoices.
- A customer disputes a charge and you need to adjust, credit, or write it off.

## When NOT to use

- You are chasing a portfolio of overdue accounts and need aging + dunning strategy → use [[credit-control]].
- You are forecasting when cash will actually land → use [[cashflow-forecasting]].
- The charge is an internal employee expense, not a customer bill → use [[expense-management]].

## Workflow

1. **Assemble invoice data.** Confirm the billable event is real and complete (goods delivered / milestone signed off). When the order or delivery data arrives as a spreadsheet, read it with [[backoffice/xlsx]] and pull: legal customer entity + billing address, customer PO or contract reference, line items with quantity/unit price, and the agreed currency. **Do not invoice against unconfirmed delivery** — that is the top cause of disputes.
2. **Build the invoice.** Populate every required field: unique sequential invoice number (never reuse or skip — auditors flag gaps), issue date, supply date, itemized amounts, applicable tax per line (rate, tax ID, reverse-charge/exemption notes), subtotal, tax total, grand total, and remittance details. State the currency explicitly on every amount.
3. **Set payment terms.** Apply the contracted term — due-on-receipt, net-15/30/60, or milestone/progress billing — and print an explicit **due date as a calendar date**, not "net 30". Add any early-payment discount or late-fee clause. If terms weren't agreed in the contract, resolve them before sending, not after.
4. **Deliver through a payable channel.** Render the invoice as a PDF with [[backoffice/pdf]] and send via the channel the customer's AP process requires — email PDF, customer AP portal upload, or EDI — including machine-readable payment data (bank/IBAN, card link, or digital-wallet reference). Confirm receipt: portal acknowledgement, EDI 997, or a delivery/read signal. An invoice sent to the wrong address is unpaid, not late.
5. **Record and schedule follow-up.** Post the invoice to the AR ledger as open, and write the invoice record (number, customer, amount, issue/due date, status) into the AR tracking spreadsheet with [[backoffice/xlsx]]. Schedule the reminder cadence at creation time: a courtesy reminder ~3–5 days before due, a due-date notice, then overdue touches (e.g. +7 / +14 / +30). Automate the schedule so nothing depends on someone remembering.
6. **Capture payment.** Accept via the offered methods (bank transfer, card, digital wallet), capturing the remittance reference. Note the value date (when funds clear), not just the payment date.
7. **Reconcile.** Match each receipt to its invoice(s) by amount and reference — when the bank pulls receipts as a spreadsheet, read it with [[backoffice/xlsx]] and update the status column in the AR tracking workbook. Handle the three exception types explicitly: **partial payment** (apply to oldest/agreed lines, keep the balance open), **overpayment/unapplied credit** (park as a credit on the account, don't silently absorb it), and **short payment** (identify the deduction reason before closing). Mark fully-settled invoices paid.
8. **Resolve exceptions.** For disputes, log the reason and freeze follow-up on the disputed portion only. Correct errors with a **credit note referencing the original invoice number** (never edit or delete a sent invoice) and reissue if needed. Write off uncollectible balances through the approved authority and reason code, so the ledger reflects reality.

## Common Pitfalls

| Pitfall | Why it's a problem | Do instead |
|---|---|---|
| Reusing, skipping, or non-sequential invoice numbers | Audit/tax red flag; breaks reconciliation | One unbroken sequence; voids stay in-sequence |
| "Net 30" with no calendar due date | Ambiguous deadline delays payment and weakens collections | Print an explicit due date |
| Editing or deleting an already-sent invoice | Destroys the audit trail; tax non-compliance | Issue a credit note referencing the original |
| Sending to a generic inbox, not the AP channel | Invoice never enters the payment queue | Use the portal/EDI/AP address the customer requires |
| Silently absorbing over/short payments | Unapplied cash and phantom balances accumulate | Park credits and log short-pay reasons explicitly |

## Verification Checklist

- [ ] Billable event confirmed complete before the invoice was raised.
- [ ] Invoice carries a unique sequential number, correct tax per line, explicit currency, and a calendar due date.
- [ ] Delivered through a payable channel with receipt confirmed.
- [ ] Invoice posted to the AR ledger and a reminder cadence scheduled at creation.
- [ ] Payments matched to invoices; partials, overpayments, and short-pays handled explicitly.
- [ ] Any correction made via a credit note referencing the original; no sent invoice was edited or deleted.
- [ ] Disputes logged with follow-up frozen only on the disputed portion; write-offs approved with a reason code.

## Supporting skills

- [[backoffice/xlsx]] — read order/billing data and read/write the AR tracking workbook.
- [[backoffice/pdf]] — render the invoice as a deliverable PDF.
- [[credit-control]] — hand off overdue invoices for aging and dunning.
- [[cashflow-forecasting]] — feed open AR into the inflow model.

## Sources

Aligned with standard order-to-cash and AR practice, and general invoicing/tax-document requirements (sequential numbering, credit-note corrections, VAT/GST line treatment). Adapt tax fields, retention periods, and e-invoicing mandates to your jurisdiction.
