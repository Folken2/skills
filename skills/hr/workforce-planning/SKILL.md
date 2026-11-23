---
name: workforce-planning
description: "Use when turning a current roster and a demand forecast into a quarter-by-quarter headcount gap plan and a sequenced hiring plan — supply analysis, demand forecasting, gap analysis, requisition timing against hiring lead time, and succession (single-point-of-failure) risk. Triggers on: workforce plan, headcount plan, capacity plan, hiring plan for next year, gap analysis, how many people do we need, requisition plan, succession risk."
version: 1.0.0
author: "Nuvel Skills"
---

# Workforce Planning

## Overview

Workforce planning compares the people an organisation will have (supply) with the people its strategy needs (demand) for each period. It closes the gap through hiring, development, redeployment or succession, then reviews the plan on a fixed cadence. The core principle: **plan from strategy and keep it running: supply, demand, gap, action, every quarter, with every assumption visible.**

Most organisations plan short term and count seats. A McKinsey HR Monitor 2025 figure, cited in practitioner guidance, puts strategic planning beyond 12 months at only 12% of HR leaders, while 73% do only operational (0–12 month) planning. Gartner (October 2025) reports that 66% of CHROs limit workforce planning to headcount rather than capabilities. The WEF Future of Jobs Report 2025 expects 39% of existing job skills to shift by 2030, with 59% of the workforce needing reskilling. US OPM recommends a 2–3 year horizon, and SHRM frames planning as continuous rather than annual.

This skill covers the quantitative core of that cycle, the headcount gap and the requisition sequence. It treats the result as one input to the capability conversation, not the whole plan. The bundled script is an assumption calculator. It prints every probability and lead time it used, rounds supply down so the plan is never optimistic, and never recommends a reduction in force.

## When to Use

- Building or refreshing a quarterly headcount plan for the next 1–3 years.
- Converting a demand forecast (from the business or finance plan) into requisitions with realistic open and start dates.
- Running a gap analysis by department and role level, including expected attrition and known exits.
- Spotting roles with a single incumbent and no peer (succession risk).
- Running the quarterly review step of an existing workforce plan.

## When NOT to Use

- Compensation, budget or cost modelling. The script is deliberately cost-free. Pair it with a finance model.
- Planning or selecting people for a reduction in force. Surplus is only ever expressed as redeploy, freeze or attrit-only. Workforce reductions need legal and HR process outside this skill.
- Filling a single approved role. Use the organisation's hiring process instead.
- Individual performance or flight-risk decisions. `attrition_risk` is a planning input, not a judgement about a person.

## Workflow

1. **Align to strategy first.** Write down the business objectives for the horizon (OPM recommends 2–3 years) and who owns the demand forecast. Every demand number must trace back to an objective. A headcount plan with no strategy behind it is just a list of positions.
2. **Assemble supply (roster CSV).** Export the current roster with this header:
   `employee_id,name,department,role_level,manager_id,hire_date,planned_exit_date,attrition_risk`
   - `attrition_risk` is `low|medium|high`. `planned_exit_date` covers known exits (retirements, contract ends, resignations) and may be empty.
   - Include accepted offers with their future `hire_date`. They count from the first quarter that starts on or after their hire date.
   - Restrict access to the file. `name` and `attrition_risk` are personal data.
3. **Assemble demand (demand CSV).** Get the forecast from the business owners:
   `period,department,role_level,required_headcount` with quarter labels such as `2027-Q1`.
   Give every department/role_level a row for every quarter in the window. Missing quarters are not planned.
4. **Agree the assumptions.** Set annual attrition probabilities per risk band and the hiring lead time from historical data, for example the trailing 12-month turnover and time-to-start by band. Write down where each number came from.
5. **Run the plan.**
   `python3 scripts/headcount_planner.py plan --roster roster.csv --demand demand.csv --start-period 2027-Q1 --periods 8 --attrition-probability low=0.05,medium=0.25,high=0.5 --hiring-lead-time-weeks 8 --json plan.json`
   Exit codes: 0 success, 1 unreadable input or missing header, 2 usage error, 3 internal consistency failure.
6. **Verify the assumption echo and the ordering check.** Confirm that the printed `attrition (annual)` and `hiring lead time` lines match step 4. Confirm the summary prints `requisition_order_check: ok (N requisitions)`, which means every requisition opens in or before its start period.
7. **Clear the DATA QUALITY block.** Fix unparseable hire dates, exits before hire, duplicate employee ids, unknown attrition risk (treated as high), non-numeric headcount, demand for a group with no incumbents (verify it is a new team, not a typo) and roster groups with no demand. Re-run until every remaining issue is intentional.
8. **Read the gap table.** For each department/role_level and quarter, compare `expected` (survival-weighted, before rounding), `supply` (rounded down), `demand`, `gap` and cumulative requisitions. Actions are fixed by the gap: `HIRE` (gap > 0), `HOLD` (gap = 0), `REDEPLOY_OR_FREEZE` (gap < 0). For a surplus, redeploy people to gap areas, freeze backfills or let natural attrition absorb it.
9. **Sequence the requisitions.** Each line shows the open period, start period, needed-by period and priority. `URGENT` with `LATE` means the lead time cannot meet the need inside the window, so plan interim cover (contractors, internal moves, overtime). `HIGH` means open now.
10. **Address succession risk and capability.** For every `SINGLE_POINT` role, name a successor or a development path (acquisition, development, deployment, succession). Then review the plan against capabilities, not just seats, because skills shift faster than headcount.
11. **Publish and review quarterly.** Share the gap table, the requisition plan, the assumptions and the open data-quality items with the plan owners. Re-run every quarter with refreshed inputs and record the actual against the planned supply as the progress measure.

## Red Flags

| Signal | Why it matters | Action |
|---|---|---|
| Demand numbers with no linked objective | The plan cannot be defended or prioritised | Trace each demand row to a strategic objective (step 1) |
| Attrition probabilities copied from defaults | Every supply number depends on them | Replace them with the organisation's own trailing turnover by band |
| Many `URGENT`/`LATE` requisitions in the first quarter | The plan started too late for the lead time | Arrange interim cover now; start the next cycle earlier |
| `REDEPLOY_OR_FREEZE` read as layoffs | The script never recommends a reduction in force | Redeploy to gap areas, freeze backfills, attrit-only |
| `SINGLE_POINT` on a critical role | One departure stops the work | Name a successor and fund cross-training |
| Plan only counts seats | 66% of CHROs stop at headcount; skills shift by 2030 | Add a capability review per gap row |
| Plan refreshed once a year | Supply and demand drift every quarter | Put the quarterly re-run on the calendar |
| DATA QUALITY block left unread | Excluded rows silently reduce supply | Clear or explicitly accept each issue |

## Exit Criteria

- [ ] Every demand row traces to a named strategic objective and a named forecast owner.
- [ ] The plan ran with exit code 0, and the printed attrition probabilities and lead time match the documented assumptions.
- [ ] The summary shows `requisition_order_check: ok (N requisitions)`.
- [ ] Every DATA QUALITY item is either fixed (absent on re-run) or listed as accepted with an owner.
- [ ] Every `HIRE` row has at least one requisition with an open period and a start period.
- [ ] Every `LATE` requisition has a documented interim-cover action.
- [ ] Every `SINGLE_POINT` role has a named successor or development action.
- [ ] No output or recommendation proposes a reduction in force.
- [ ] A quarterly review date is set, and the JSON plan file is stored with the assumptions.

## Pitfalls

- **Empty file.** A 0-byte roster or demand file exits 1 with `file is empty - a header row is required`. A header-only demand file exits 0, plans nothing and lists every roster group as having no demand forecast.
- **Missing header column.** The script exits 1 and names the missing columns. A bad `--start-period` (for example `2027Q1`), an out-of-range probability or `--periods` outside 1..40 exits 2.
- **Rounding down is deliberately pessimistic.** Supply is floored per group per quarter, so a single incumbent with any non-zero attrition probability shows `supply 0`. Read the `expected` column, and set the band to `0` if the person is confirmed staying.
- **Probabilities are annual.** They are applied as survival `(1-p)^(k/4)` for the k-th quarter of the window. A planned exit inside a quarter removes the person for that whole quarter, and people with a planned exit are not also counted in attrition.
- **New hires are assumed to stay.** Requisitioned starts are not reduced by attrition within the window.
- **Lead time crosses quarters.** A hire is only counted from the first quarter that starts on or after open date + lead time. With the default 8 weeks, a requisition opened in Q1 starts in Q2, so first-quarter gaps are always `LATE` unless the lead time is 0.
- **Malformed rows are excluded, never guessed.** Unparseable hire or exit dates, exits before hire and missing department or role level are excluded from supply. A duplicate `employee_id` counts once. Unknown `attrition_risk` is treated as high. A non-numeric or negative `required_headcount`, a bad period label or a demand row outside the window is skipped. Duplicate demand rows use the higher figure. Every one of these appears in DATA QUALITY.
- **`SINGLE_POINT` only checks demanded roles.** It checks only groups with demand > 0 and looks for a peer with the same `manager_id` and `role_level`. An empty `manager_id` never counts as a peer.
- **Determinism.** The gap table is sorted by (department, role_level, period). Requisition ids are assigned after sorting, so the same input always gives the same output.

## Attribution & Sources

This is an original Nuvel Skills SOP. The sources below informed the planning cycle, the thresholds and the constraints. They do not endorse this skill. The statistics are quoted as published or as cited in the practitioner guide listed below.

- SHRM, "The 4-Step Framework to Build a Future-Ready Workforce": https://www.shrm.org/enterprise-solutions/insights/4-step-framework-to-build-future-ready-workforce
- US OPM, "Workforce Planning Guide" (Human Capital Framework): https://www.opm.gov/policy-data-oversight/human-capital-framework/reference-materials/talent-management/workforce-planning-guide.pdf
- McKinsey, HR Monitor 2025 (12% strategic beyond 12 months; 73% operational): https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/hr-monitor-2025
- Gartner press release, October 2025 (66% of CHROs limit planning to headcount): https://www.gartner.com/en/newsroom/press-releases/2025-10-02-gartner-says-chros-top-priorities-for-2026-center-around-realizing-ai-value-and-driving-performance-amid-uncertainty
- "Workforce Planning: A Step-by-Step Guide for HR Leaders" (seven-step cycle, five R's, four pillars): https://www.pin.com/blog/workforce-planning-guide/
- World Economic Forum, Future of Jobs Report 2025 (39% of skills shift by 2030; 59% need reskilling): https://www.weforum.org/publications/the-future-of-jobs-report-2025/
