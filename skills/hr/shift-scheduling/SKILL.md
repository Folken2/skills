---
name: shift-scheduling
description: "Use when the agent must build or check an hourly shift schedule against staffing demand and labour rules: filling AM/PM/NIGHT (or similar) shifts by role from employee availability, finding uncovered shifts and producing an open-shift broadcast list, totalling weekly hours and projected overtime, and detecting rest-period (clopen) violations, short-notice assignments under predictive-scheduling rules, role or availability mismatches and double bookings. Triggers on \"build next week's rota\", \"are all shifts covered\", \"check this schedule\", \"who can pick up this shift\", \"overtime this week\", \"clopen\", \"fair workweek\" or \"predictive scheduling notice\"."
version: 1.0.0
author: "Nuvel Skills"
---

# Shift Scheduling

## Overview

Shift scheduling matches the staff needed per role, date and shift (demand) to the people who are qualified and available (supply), within the limits set by law and by each employee's contract. The agent does it in two modes with one bundled script: `plan`, which drafts a schedule, and `audit`, which checks a schedule someone else drafted. Both produce the same coverage table, open-shift list and violation report.

The core principle: **schedule from real demand, publish early, and treat rest, notice and overtime as hard constraints checked by a tool, not things to remember.** Under the US FLSA, non-exempt employees must be paid at least 1.5× their regular rate for hours over 40 in a workweek, and a workweek is a fixed, recurring 168-hour period. OSHA treats shifts longer than 8 consecutive hours and irregular schedules as recognised fatigue hazards that reduce alertness, concentration and memory. Fair-workweek / predictive-scheduling laws (Oregon statewide; NYC, Chicago, Philadelphia, Seattle, San Francisco, San Jose, Berkeley, Emeryville, Evanston and Los Angeles locally) generally require schedules to be published about **14 days** in advance, require a predictability premium for late changes, and limit on-call shifts.

It matters because uncovered shifts, clopens and last-minute changes compound each other. A short shift gets filled by whoever is already on site, which creates overtime and short rest, which drives fatigue and absence, which creates the next short shift. A deterministic plan plus an audit catches this before the schedule is published, while it can still be fixed for free.

## When to use

- Drafting a schedule for an upcoming period from a demand forecast and an availability roster.
- Checking a manager-drafted or system-generated schedule before it is published.
- A shift is unfilled and the agent needs a list of qualified people to offer it to.
- Estimating overtime hours for the period before approving the schedule.
- Checking whether changes made after publication triggered notice-period obligations.

## When NOT to use

- Salaried or exempt roles without shift patterns. There is no demand-by-shift to cover.
- Payroll calculation: the script projects overtime *hours*, not pay, premiums or tax.
- Final legal determination of exempt/non-exempt status, local predictability-pay amounts, minor-labour rules or collective-agreement terms. Escalate to HR or legal counsel; this skill only flags candidates for review.
- Real-time sick-call handling inside a shift that has already started. Use the open-shift list from the last run, and never require the sick employee to find their own cover.
- Long-horizon workforce planning (how many people to hire). That is a capacity question, not a schedule.

## Workflow

1. **Fix the scheduling period and the rules.** Record: the schedule dates, the planned publish date, the minimum notice in days (default 14), the weekly overtime threshold (default 40), whether overtime may be scheduled (`--overtime-eligible yes|no`, default `no`), the day the workweek starts (default Monday, and it must match payroll), and the start/end time of each shift label. Default shifts are `AM=06:00-14:00,PM=14:00-22:00,NIGHT=22:00-06:00`.

2. **Build the demand file from real demand.** `date,shift,role,required_headcount`, one row per date × shift × role, derived from the sales/traffic/acuity forecast rather than last period's schedule. Shift labels must match the `--shift-times` labels.

3. **Build the employees file.** `employee_id,name,role,weekly_hours_cap,max_shift_hours,min_rest_hours,availability`. List cross-trained roles separated by `;` (e.g. `cashier;security`). `availability` holds `;`-separated `YYYY-MM-DD:SHIFT` tokens collected from the employees themselves. Set `min_rest_hours` to whichever is stricter: the local rule or company policy (10 h is a common fair-workweek figure).

4. **Draft (plan mode) or collect the draft (audit mode).**
   ```bash
   python3 skills/hr/shift-scheduling/scripts/coverage_planner.py plan \
     --demand /path/to/demand.csv --employees /path/to/employees.csv \
     --schedule-publish-date 2026-11-16 --min-notice-days 14 \
     --max-weekly-hours 40 --overtime-eligible no \
     --shift-times "AM=06:00-14:00,PM=14:00-22:00,NIGHT=22:00-06:00" \
     --workweek-start mon \
     --json /path/to/plan_report.json --out /path/to/assignments.csv
   ```
   The planner fills demand rows in date → shift start time → role order. For each slot it picks the eligible employee with the fewest hours already assigned, breaking ties by `employee_id`, so the same input always gives the same schedule. It never breaks availability, role, overlap, rest, `max_shift_hours`, `weekly_hours_cap`, or (with `--overtime-eligible no`) the weekly threshold. Use `--help` for all options.

5. **Audit the schedule (always, including the planner's own output).**
   ```bash
   python3 skills/hr/shift-scheduling/scripts/coverage_planner.py audit \
     --demand /path/to/demand.csv --employees /path/to/employees.csv \
     --assignments /path/to/assignments.csv \
     --schedule-publish-date 2026-11-16 --min-notice-days 14 \
     --max-weekly-hours 40 --overtime-eligible no \
     --json /path/to/audit_report.json --out /path/to/issues.csv
   ```
   The assignments format is `employee_id,date,shift,start_time,end_time,hours`. Times are 24h `HH:MM`, and an end time at or before the start time means the shift ends the next day. Exit code 0 = report produced (violations are reported, not fatal); 1 = unreadable file; 2 = bad arguments or a missing header.

6. **Resolve violations in this order.** First `DATA_ERROR` (fix inputs and re-run). Then `OVERLAP` and `DUPLICATE_ASSIGNMENT`. Then `REST_VIOLATION` (clopens and back-to-back doubles), `ROLE_MISMATCH` / `AVAILABILITY_MISMATCH`, `WEEKLY_CAP_EXCEEDED`, `OVERTIME` / `OVERTIME_NOT_AUTHORISED`, `MAX_SHIFT_EXCEEDED` / `EXTENDED_SHIFT`, and finally `NOTICE`. Edit the assignments file, then re-run step 5 until the only remaining issues are accepted, documented exceptions.

7. **Work the open-shift broadcast list.** For each `SHORT n` row, offer the shift to the listed qualified employees, in the order listed, through the normal channel. Then go to a voluntary standby list. A row marked `NO QUALIFIED STAFF` is a cross-training or hiring gap: record it and pass it to the people planning headcount. Do not assign someone outside the employee's stated availability without their agreement.

8. **Approve overtime explicitly.** If the summary shows `projected overtime hours > 0`, get named approval with the hour count before publishing. For non-exempt staff those hours must be paid at no less than 1.5× the regular rate.

9. **Publish and freeze.** Publish on or before the publish date used in the audit. For any later change, re-run the audit with the original publish date: every new `NOTICE` row is a change that may owe a predictability premium under local law. Record it and the employee's consent where required.

## Red Flags

| Signal | Why it matters | Action |
|--------|----------------|--------|
| `REST_VIOLATION` (clopen or back-to-back double) | Short rest is a recognised fatigue hazard and often owes a premium under fair-workweek rules | Swap one of the shifts; if unavoidable, get documented consent and apply the premium |
| `OVERLAP` | One person booked in two places at once, so the coverage table overstates staffing | Remove one assignment and re-audit |
| `NOTICE` on many rows | Schedule is published late, or changes are made after publication | Move the publish date earlier; batch changes before publishing |
| `OVERTIME_NOT_AUTHORISED` | Hours above the threshold were scheduled without approval; non-exempt staff must still be paid 1.5× | Rebalance hours or get overtime approved before publishing |
| `EXTENDED_SHIFT` (> 8 h) or `MAX_SHIFT_EXCEEDED` | Longer shifts raise fatigue and error risk | Split the shift, or add breaks and fatigue controls |
| `SHORT n` with `NO QUALIFIED STAFF` | No one holds the role, so a single resignation stops the operation | Cross-train at least two people per critical role |
| The same few employees appear on every broadcast | Burnout and uneven distribution of hours | Grow the standby list; check availability collection |
| `OVER n` coverage | Labour spend above demand | Release surplus hours or move them to short rows |
| Employee with `no usable availability` | They will never be scheduled, which looks like a quiet constructive dismissal | Confirm availability with the employee directly |

## Exit Criteria

- [ ] The final `audit` run exited with code 0 against the exact assignments file that will be published.
- [ ] The final audit shows zero `DATA_ERROR`, `OVERLAP` and `DUPLICATE_ASSIGNMENT` issues.
- [ ] Every remaining `REST_VIOLATION`, `NOTICE`, `OVERTIME*`, `WEEKLY_CAP_EXCEEDED` and `MAX_SHIFT_EXCEEDED` issue is listed in a written exceptions log with an approver's name and the reason.
- [ ] Every `SHORT n` row has a recorded outcome: filled (re-audited), broadcast sent with a timestamp, or logged as a staffing gap.
- [ ] `projected overtime hours` from the final audit matches the figure the approver signed off.
- [ ] The schedule was published on or before the `--schedule-publish-date` used in the final audit.
- [ ] The JSON report of the final audit is stored alongside the published schedule.

## Pitfalls

- **Overtime is per workweek, not per pay period or per day.** The script assigns each shift to the workweek in which it *starts* (`--workweek-start`, a fixed 168-hour period from 00:00). A night shift crossing the week boundary is counted entirely in the week it began; if payroll splits hours at midnight, totals can differ by that shift's post-midnight hours. Some jurisdictions also impose daily overtime, which this script does not compute.
- **`--overtime-eligible no` limits the planner, not the law.** In audit mode, hours over the threshold are still counted in projected overtime and flagged `OVERTIME_NOT_AUTHORISED`, because non-exempt staff are owed overtime pay whether or not it was approved.
- **On-call time.** Under DOL Fact Sheet #22, on-call time can count as hours worked when the employee's freedom is significantly restricted. If it does, put it in the assignments file as a shift so it is counted.
- **Empty inputs.** A zero-byte or header-only demand file produces an empty coverage table, a `DATA_WARNING`, and exit 0. An empty employees file makes every demand row `SHORT` with `NO QUALIFIED STAFF`. An empty assignments file (audit) makes every row `SHORT`. A missing required header exits 2, naming the missing columns.
- **Malformed values.** A malformed date (`2026/11/30`, `2026-13-01`) or a non-integer `required_headcount` makes the row a `DATA_ERROR` and it is skipped. Malformed availability tokens are ignored with a warning. Blank or invalid `weekly_hours_cap` / `max_shift_hours` / `min_rest_hours` fall back to `--max-weekly-hours` / `--extended-shift-hours` / 10 with a warning. Malformed times (`6am`) are a `DATA_ERROR`: the `hours` value is used for weekly totals but rest and overlap checks are skipped for that row.
- **Hours vs times.** When `start_time`/`end_time` are valid they win. A different `hours` value (beyond 3 minutes) is flagged `HOURS_MISMATCH` and the duration computed from the times is used. Blank times fall back to the `--shift-times` default for that label.
- **Shift labels without times** (e.g. `SWING` not in `--shift-times`) are warned about and can never be filled by the planner; add them to `--shift-times`.
- **Duplicate demand rows** for the same date/shift/role are summed with a warning. A duplicate assignment of the same employee to the same date+shift is flagged once and ignored for coverage and hours.
- **Role nobody holds.** The row stays `SHORT` with `NO QUALIFIED STAFF - cross-train or hire`. If qualified staff exist but are all already on the shift, the note says so instead.
- **Unknown employee IDs** in an assignments file are flagged `UNKNOWN_EMPLOYEE` and do not count toward coverage.
- **Greedy is not optimal.** The planner is deterministic and explainable but can leave a slot short that a different combination would have filled. If shortfalls remain, edit the plan by hand and re-audit; do not re-run hoping for a different answer.

## Attribution & Sources

This is an original Nuvel Skills SOP. The sources below informed its quantified thresholds and legal constraints; they do not endorse this skill, and none of this is legal advice.

- US DOL Wage & Hour Division, FLSA overtime: at least 1.5× the regular rate for hours over 40 in a workweek; the workweek is a fixed, recurring 168-hour period. https://www.dol.gov/agencies/whd/overtime
- US DOL, Fact Sheet #22, "Hours Worked Under the FLSA": on-call time rules. https://www.dol.gov/agencies/whd/fact-sheets/22-flsa-hours-worked
- OSHA, Extended/Unusual Work Shifts guide: shifts beyond 8 consecutive hours and irregular schedules as fatigue hazards. https://www.osha.gov/emergency-preparedness/guides/extended-unusual-work-shifts
- Oregon Bureau of Labor and Industries, Predictive Scheduling: advance publication, predictability pay, limits on on-call shifts; the same pattern appears in NYC, Chicago, Philadelphia, Seattle, San Francisco, San Jose, Berkeley, Emeryville, Evanston and Los Angeles. https://www.oregon.gov/boli/workers/pages/predictive-scheduling.aspx
- Shift-coverage operations guidance: schedule from real demand, publish 1–2 weeks ahead, cross-train, keep a voluntary standby list, never require a sick employee to find their own cover. https://firsthr.app/blog/time-tracking/shift-coverage
