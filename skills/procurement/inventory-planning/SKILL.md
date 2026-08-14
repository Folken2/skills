---
name: inventory-planning
description: "Use when deciding how much to stock and when to reorder — forecasting demand from history/seasonality/pipeline, calculating reorder points and safety stock, sizing orders with EOQ, setting min/max and par levels via ABC classification, managing supplier lead-time variability, and handling stockouts and overstock. Triggers on \"reorder point\", \"safety stock\", \"EOQ\", \"stock levels\", \"stockout\", \"overstock\", \"ABC analysis\"."
version: 1.0.0
author: Nuvel Skills
---

# Inventory Planning

## Overview

Decide how much to stock and when to reorder so you meet demand without tying up cash in excess inventory. The core principle: **safety stock buys service level against variability, not against bad forecasting.** Reorder points are set from lead-time demand plus a safety buffer sized to the *variability* of demand and lead time — not a round number. Effort is focused where it matters via ABC classification, so the few high-value items get tight control and the long tail gets simple rules.

## When to use

- Setting or revising reorder points, safety stock, and order quantities for stocked items.
- Building a demand forecast to drive purchasing.
- Responding to a stockout risk or an overstock/obsolescence problem.

## When NOT to use

- Choosing or onboarding the supplier who fulfills the orders → use [[supplier-qualification]].
- Negotiating the price/terms behind the order → use [[vendor-negotiation]].
- Executing and receiving the actual purchase order → use [[purchase-order-management]].

## Workflow

1. **Forecast demand.** Build a demand forecast per item from historical usage, seasonality, trend, and known pipeline (promotions, contracts, launches). State the forecast period and the assumptions. *Exit:* a per-item demand forecast with its period and assumptions recorded.
2. **Classify items (ABC).** Rank items by annual value/usage into A/B/C classes so control effort matches impact: A items get tight review and low buffers-per-dollar; C items get simple, generous rules. *Exit:* every stocked item assigned an A/B/C class.
3. **Establish lead times.** Record each supplier's lead time *and its variability* (not just the average). Add a buffer proportional to lead-time variability. *Exit:* lead time and variability captured per item/supplier.
4. **Calculate safety stock.** Size safety stock to the demand and lead-time variability and the target service level for the item's class — higher service level and higher variability mean more safety stock. Do not use a flat blanket buffer across dissimilar items. *Exit:* a safety-stock quantity per item tied to a target service level.
5. **Set reorder points.** Reorder point = expected demand over the lead time **+** safety stock. When on-hand drops to this point, an order is triggered. *Exit:* a reorder point per item = lead-time demand + safety stock.
6. **Size the order (EOQ).** Set the order quantity balancing ordering cost against holding cost (EOQ), adjusted for supplier minimums, price breaks, and shelf life. Set min/max and par levels consistent with the reorder point and EOQ. *Exit:* order quantity and min/max/par levels defined per item.
7. **Manage stockouts.** When an item breaches or risks its reorder point, act: expedite, substitute, or communicate to affected customers/internal users. Record the root cause (forecast miss, lead-time slip, demand spike) to correct the parameters. *Exit:* stockout risks actioned with a recorded root cause.
8. **Manage overstock.** Identify excess, slow-moving, and obsolescent stock; act via markdown, redeployment, return-to-vendor, or liquidation before it becomes a write-off. *Exit:* excess/obsolete stock identified and a disposition assigned.
9. **Set review cadence.** Establish a review rhythm: weekly/monthly parameter review, ongoing cycle counting (weighted toward A items), and an annual physical count. Re-tune forecasts and reorder points on this cadence. *Exit:* an inventory review schedule with cycle-count and annual-count plan.

## Common Pitfalls

| Pitfall | Why it's a problem | Do instead |
|---|---|---|
| Flat safety stock across all items | Overstocks stable items, understocks volatile ones | Size safety stock to each item's variability + service target |
| Reorder point set to a round number | Triggers too early or too late vs. real lead time | ROP = lead-time demand + calculated safety stock |
| Using average lead time only | Variability causes stockouts the average hides | Capture and buffer for lead-time *variability* |
| Treating all SKUs equally | Wastes control effort; misses the high-value few | Focus control by ABC class |
| Ignoring slow-moving stock | Excess becomes obsolescence and write-offs | Review overstock on cadence; disposition early |

## Verification Checklist

- [ ] Per-item demand forecast built with period and assumptions recorded.
- [ ] Every stocked item assigned an A/B/C class.
- [ ] Supplier lead time and its variability captured per item.
- [ ] Safety stock sized to variability and a target service level (not a blanket buffer).
- [ ] Reorder point set = lead-time demand + safety stock for each item.
- [ ] Order quantity (EOQ-based) and min/max/par levels defined.
- [ ] Stockout and overstock procedures defined, with root cause / disposition recorded when triggered.
- [ ] Review schedule set: periodic parameter review, cycle counting, annual physical count.

## Sources

Aligned with standard inventory-management practice — ABC analysis, reorder-point and safety-stock formulas, Economic Order Quantity (EOQ), service-level targeting, and cycle counting. Feeds order quantities into [[purchase-order-management]]; depends on lead times from suppliers qualified via [[supplier-qualification]].
