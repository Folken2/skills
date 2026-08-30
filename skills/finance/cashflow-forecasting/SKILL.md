---
name: cashflow-forecasting
description: "Use when building or maintaining a cash flow forecast — cash position, inflows/outflows, a 13-week rolling model, scenario planning, and variance analysis. Triggers on \"cash forecast\", \"13-week\", \"runway\", \"cash position\", \"will we have enough cash\", \"scenario plan\", \"forecast vs actual\"."
version: 1.0.0
author: Nuvel Skills
---

# Cash Flow Forecasting

## Overview

A disciplined view of when cash actually enters and leaves the business, built bottom-up, reforecast every week, and stress-tested against scenarios. The core principle: **cash timing is not profit** — a profitable business fails when cash arrives after obligations are due, so the forecast tracks *when* money moves (value dates), not when revenue or cost is recognized. The 13-week horizon is the standard because it is far enough to act on a shortfall and near enough to forecast credibly.

Reality: a forecast is only as good as its assumptions and only useful if it's reforecast. A model built once and left alone is worse than none — it breeds false confidence. The value is in the weekly loop: forecast, compare to actuals, understand the variance, and roll forward. Accuracy compounds as assumptions get corrected against reality.

## Toolchain

This skill is domain expertise; the model itself lives in a spreadsheet built through supporting skills:

- **[[backoffice/xlsx]]** — read the opening cash position and the AR/AP source data, and build the 13-week rolling grid as an Excel file with live formulas so each week's closing carries into the next. Reach for it whenever a step reads from or writes to an `.xlsx` file.
- **[[backoffice/pdf]]** — render the forecast and scenario summary as a board- or lender-ready PDF.

## When to use

- You need to know whether cash covers upcoming obligations, or how much runway remains.
- You are building or maintaining a 13-week rolling cash forecast.
- You are stress-testing scenarios (delayed collections, lost customer, cost shock).
- You are reviewing forecast accuracy and reforecasting.

## When NOT to use

- You need to collect a specific overdue invoice → use [[credit-control]]; feed its aging into inflows here.
- You are controlling individual employee spend → use [[expense-management]].
- You are billing a customer → use [[invoicing]].

## Workflow

1. **Establish the opening cash position.** Read the reconciled bank balances across all accounts from the Excel export with [[backoffice/xlsx]]. Adjust for known-but-uncleared items (in-flight transfers, uncashed payments) to get true **available** cash, and separate any restricted or committed funds. A forecast built on an unreconciled opening balance is wrong from week one.
2. **Model inflows bottom-up.** Build expected receipts week by week from real drivers: open AR by expected collection date (from [[credit-control]] aging, not invoice date), recurring/subscription revenue, and probability-weighted new sales. Time each to its **expected value date**, applying realistic collection lag — not the due date, the date cash actually lands.
3. **Model outflows bottom-up.** Schedule payments by due date: AP from open payables, payroll (fixed dates), recurring opex (rent, utilities, subscriptions), committed spend and POs, debt service, and tax/VAT payment dates. Tax and payroll are non-negotiable, lumpy, and easy to forget — anchor them explicitly.
4. **Build the 13-week rolling grid.** Write the model as a new Excel file with [[backoffice/xlsx]]: 13 weekly columns where opening cash + inflows − outflows = closing cash, carried as next week's opening. Use live cell **formulas** for the running balance and subtotals (not hard-coded values) so a changed assumption reflows the whole grid. Weekly granularity (not monthly) is what exposes an *intra-month* trough that a monthly view hides. Document every assumption (collection lag %, payment timing) in the sheet alongside the numbers so they can be challenged and corrected.
5. **Run scenarios.** Build base, best, and worst cases by flexing the high-impact assumptions — collection speed, a lost or delayed key customer, a cost or rate shock, a delayed raise. Run sensitivities on the one or two drivers cash is most exposed to. The output that matters: in the worst case, *when* does cash cross a minimum threshold, and what's the lead time to act.
6. **Identify and act on gaps.** Where any scenario breaches the minimum cash buffer, flag the week and the size, and attach a mitigation (accelerate collections, defer discretionary spend, draw facility, delay non-critical payments). A forecast that surfaces a trough without a triggered action is only half done.
7. **Run variance analysis and reforecast.** Each week, load the actuals export with [[backoffice/xlsx]] and compare last week's forecast to actuals line by line in the model. Classify each variance as **timing** (cash moved weeks, total unchanged) vs. **permanent** (the amount was wrong), because they demand different fixes. Correct the assumptions, then roll the window forward one week (the formula-driven grid recomputes) so it always shows the next 13.
8. **Hold the review cadence.** Weekly flash on position and near-term risk; monthly deep dive on variance drivers, assumption accuracy, and scenario updates; quarterly tie-out to the longer-range plan and budget. Cadence is what keeps the model honest and the assumptions current.

## Common Pitfalls

| Pitfall | Why it's a problem | Do instead |
|---|---|---|
| Timing cash to invoice/accrual dates, not value dates | Forecast lands cash weeks before it arrives | Time every line to its expected value date with realistic lag |
| Monthly-only granularity | Hides the intra-month trough that actually breaks you | Model weekly across the 13-week grid |
| Build-once and never reforecast | Assumptions rot; false confidence | Weekly variance check + roll the window forward |
| Forgetting lumpy outflows (tax, payroll, annual renewals) | A single missed date wipes out the buffer | Anchor tax/payroll/renewal dates explicitly |
| Not separating timing vs. permanent variances | You "fix" a one-off or ignore a real trend | Classify each variance and correct assumptions accordingly |

## Verification Checklist

- [ ] Opening position started from reconciled bank balances; restricted/committed funds separated from available cash.
- [ ] Inflows modelled bottom-up from AR aging, recurring revenue, and weighted pipeline, timed to value dates.
- [ ] Outflows scheduled by due date including payroll, tax, committed spend, and debt service.
- [ ] 13-week rolling grid runs opening → inflows → outflows → closing weekly, with assumptions documented.
- [ ] Base/best/worst scenarios and key sensitivities run; buffer breaches flagged with the week, size, and a mitigation.
- [ ] Weekly variance analysis classifies timing vs. permanent and corrects assumptions.
- [ ] Window rolled forward each week; weekly/monthly/quarterly review cadence in place.

## Supporting skills

- [[backoffice/xlsx]] — read bank/AR/AP source data; build the 13-week grid as an Excel file with live formulas.
- [[backoffice/pdf]] — render the forecast and scenario summary for the board or lenders.
- [[credit-control]] — source AR aging and collection timing for inflows.
- [[expense-management]] — source approved reimbursement timing for outflows.
- [[invoicing]] — source open AR for the inflow model.

## Sources

Aligned with standard treasury and 13-week cash-flow forecasting practice (direct method, value-date timing, rolling reforecast, timing-vs-permanent variance analysis, scenario/sensitivity planning). Adapt the minimum-buffer threshold, tax-payment calendar, and horizon to your business's volatility and financing structure.
