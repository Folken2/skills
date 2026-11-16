---
name: workforce-analytics
description: "Use when the agent must produce a workforce metrics report for a defined period from an HR roster export: headcount and net change, turnover rate (overall and per department or other group), voluntary vs involuntary split, regrettable attrition, retention rate, tenure, span of control and estimated turnover cost. Triggers on requests such as \"what is our turnover rate\", \"attrition report\", \"quarterly people metrics\", \"retention by department\", \"how much is turnover costing us\", \"span of control check\", or any board, budget or headcount-planning pack that needs people numbers computed from a roster CSV."
version: 1.0.0
author: "Nuvel Skills"
---

# Workforce Analytics

## Overview

Workforce analytics turns a roster (who was hired, who left, when, why, at what salary, reporting to whom) into a small, defensible set of period metrics that leadership can act on. The agent computes them with a bundled script so every number is reproducible from the same file.

The core principle: **every rate has a stated formula, a stated period and a stated denominator, and is broken down by group, never reported only company-wide.** SHRM defines turnover as separations divided by average headcount, times 100, and retention as employees employed for the full measurement period divided by employees at period start, times 100. It also recommends computing the rate per department, because a healthy company-wide average can hide one team that is losing a third of its people.

Turnover is expensive and it hides in the averages. A 10% company-wide rate can mean every team losing 10%, or one team losing 40% while the rest lose nothing, and those call for very different responses. The script prices turnover as leaver salary × a replacement-cost fraction (default 0.5) and flags data-quality problems before anyone sees a rate, because a wrong hire date or a duplicate ID is enough to skew a small department's numbers.

## When to use

- A period people report is due (monthly, quarterly, annual) and a roster export is available.
- Someone asks for turnover, attrition, retention, tenure or headcount change, overall or by department, location, title or employment type.
- A budget or business case needs an estimate of what turnover is costing.
- Leadership wants to know which managers have too many direct reports.
- Before an engagement or retention initiative, to establish a baseline that can be measured again later.

## When NOT to use

- The question is about one individual's performance, pay or exit. This skill produces aggregates, not case decisions.
- Groups are so small that one person moves the rate by 20+ points and results could identify individuals (e.g. a 3-person team). Report counts, not rates, or merge groups.
- Payroll calculation, compensation benchmarking or pay-equity analysis. Those need different data and legal review.
- The only available data is a headcount snapshot with no hire or termination dates. Turnover cannot be computed from a snapshot; get a roster with event dates first.
- Predicting who will leave next (flight-risk scoring). This skill describes what happened in a period; it does not model individuals.

## Workflow

1. **Confirm the question and the period.** Write down the exact period (`--period-start`, `--period-end`, inclusive ISO dates), the grouping the audience cares about (department by default) and the replacement-cost fraction to use. If the requester has no figure for replacement cost, use the default 0.5 and say so in the report.

2. **Get the roster export.** It must be a CSV with a header row containing: `employee_id, name, department, title, manager_id, hire_date, termination_date, termination_type, regretted, salary, employment_type, location`. It must include **everyone employed at any point in the period**, including leavers. An "active employees" export silently produces 0% turnover. Dates are `YYYY-MM-DD`; `termination_type` is one of `voluntary`, `involuntary`, `retire`, `end_of_contract`; `regretted` is `y`/`n`.

3. **Run the metrics script.**
   ```bash
   python3 skills/hr/workforce-analytics/scripts/workforce_metrics.py \
     --roster /path/to/roster.csv \
     --period-start 2026-01-01 --period-end 2026-12-31 \
     --group-by department --replacement-cost-pct 0.5 \
     --json /path/to/workforce_report.json
   ```
   Use `--help` for the full definitions. Exit code 0 = report produced; 1 = file unreadable; 2 = bad arguments or a missing required header (the stderr message names the missing columns).

4. **Triage data quality before reading any rate.** Read the `DATA QUALITY ISSUES` block first. Rows marked `(EXCLUDED)` (missing or unparseable hire date, unparseable termination date, termination before hire, duplicate `employee_id`) are not in any metric. If excluded rows are more than about 2% of the roster or include any leaver, fix the source data and re-run. Missing `manager_id` is expected only for the top of the organisation; anywhere else it breaks span of control.

5. **Read the headline metrics.** Check that `end = start + new hires − separations` (the script warns if not). Report the turnover rate, the voluntary/involuntary split, regrettable attrition, retention rate and median tenure, each with its formula and period. Note that turnover and retention measure different populations: turnover includes people hired and lost within the period, retention only counts the starting cohort.

6. **Break down by group.** Read `TURNOVER BY <GROUP>`. Highlight groups whose rate is well above the company rate, but check headcount first: a group with average headcount under about 10 needs its counts shown next to its rate. Re-run with `--group-by location`, `title` or `employment_type` if the department view doesn't explain the pattern.

7. **Check span of control.** List every manager flagged `OVER_LIMIT` (more than 8 active direct reports) and every warning about a `manager_id` that is not an active employee (orphaned reporting lines after a manager left).

8. **Price the turnover.** Report `estimated turnover cost` together with its inputs (sum of leaver salaries × fraction) and any warning that leavers without a valid salary were left out, which makes the cost understated.

9. **Write the report.** One page: period and definitions, headline table, group table, flagged managers, cost estimate, data-quality caveats with counts, and two or three observed patterns stated as questions to investigate (e.g. "Sales lost 2 of 2 starting AEs, both within 18 months of hire. What changed?"). Attach the JSON output for traceability. Do not name individual leavers in a report that goes beyond HR.

## Red Flags

| Signal | Why it matters | Action |
|--------|----------------|--------|
| Turnover is 0% and separations = 0 | The export probably contains only active employees | Re-export including everyone terminated in the period |
| Any leaver row is `(EXCLUDED)` | Separations are undercounted, so turnover and cost are understated | Fix the date/ID in the source and re-run before reporting |
| One group's turnover is above 100% | Legitimate with a small, churning group, but readers will distrust it | Show counts next to the rate; explain the average-headcount denominator |
| Rates reported as `n/a` | Zero denominator, e.g. a group with no headcount or no separations | Report the count instead and say why the rate is undefined |
| Manager over 8 direct reports | Coaching and 1:1 time per report thins out; it often comes up in exit feedback | Raise with the org owner; consider a lead role or a split |
| `manager_id` not an active employee | Reports are orphaned after a manager left | Get the reporting line corrected in the HR system |
| High `unknown` termination types or blank `regretted` | Voluntary/regretted splits cannot be trusted | Ask HR to complete exit coding for the listed rows |
| Regrettable attrition close to total voluntary attrition | High performers are leaving at the same rate as everyone else | Prioritise stay interviews and a compensation review for the affected groups |

## Exit Criteria

- [ ] The script ran with exit code 0 on a roster that includes leavers, and the JSON report file exists.
- [ ] The report states the period start and end dates, the group-by column and the replacement-cost fraction used.
- [ ] Every `(EXCLUDED)` data-quality row has been either fixed and re-run, or listed in the report with its count.
- [ ] Headline table includes: headcount start/end, new hires, separations, turnover %, voluntary and involuntary counts, regrettable attrition %, retention %, median tenure, estimated turnover cost.
- [ ] A per-group turnover table is included, with counts shown for every group with average headcount under 10.
- [ ] Every manager flagged `OVER_LIMIT` is listed by `manager_id`.
- [ ] Every `n/a` value in the report has an accompanying reason.
- [ ] No individual leaver is named in any version of the report shared outside HR.

## Pitfalls

- **Boundary conventions.** Someone hired *on* `period-start` is counted as a new hire, not in starting headcount. Someone whose `termination_date` falls *on* `period-end` is a separation and is not in ending headcount. This keeps `end = start + hires − separations` exact. Termination date means the last day employed.
- **Average headcount is `(start + end) / 2`.** This is the simple SHRM method. For periods with big swings (e.g. seasonal hiring), run the script month by month and average the monthly headcounts yourself.
- **Small groups.** Because the denominator is average headcount, a group of one that loses its only member scores 200%. That is arithmetically correct but needs explaining; see Red Flags.
- **Empty file.** A zero-byte roster has no header and exits with code 2 (`roster is empty (no header row)`). A header-only roster exits 0 with every rate `n/a` and one warning per undefined ratio. It never crashes or prints `inf`/`nan`.
- **Malformed rows.** A short row (fewer columns than the header) is flagged and its missing values are treated as blank, which usually triggers `missing hire_date` and exclusion. Extra columns are ignored. Salaries may contain thousands separators (`"110,000"`). Negative or non-numeric salaries are flagged and left out of the cost.
- **Duplicates.** Only the first occurrence of an `employee_id` is used. If someone was rehired, the roster needs one row per employment spell with distinct IDs (e.g. `E123-2`), or the second spell is dropped.
- **Unknown termination types** (e.g. `quit`) are counted as separations, so they are in the turnover rate, but they are reported as `unknown` rather than voluntary or involuntary.
- **Tenure** is measured to `period-end` for employees still active at period end. It is not tenure at exit.
- **Replacement cost is an estimate.** The 0.5 default is a planning assumption, not a measured cost. State it, and let finance replace it with a figure based on actual recruiting and ramp-up costs if they have one.

## Attribution & Sources

This is an original Nuvel Skills SOP. The sources below informed the metric definitions and thresholds; they do not endorse this skill.

- SHRM, "Calculate Employee Turnover Rate": turnover = separations / average headcount × 100; retention = employees employed for the full period / employees at period start × 100; compute per department. https://www.shrm.org/topics-tools/tools/how-to-guides/how-to-determine-turnover-rate
- SHRM, "Data Will Show You Why Your Employees Leave or Stay": the same formulas and a department-level breakdown. https://www.shrm.org/topics-tools/news/talent-acquisition/data-will-show-employees-leave-stay
- SHRM, Talent Analytics topic hub: metric selection and attrition-pattern analysis. https://www.shrm.org/topics-tools/topics/talent-analytics
