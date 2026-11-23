#!/usr/bin/env python3
"""headcount_planner.py - per-quarter headcount gap plan and requisition plan.

An assumption calculator, not an authority: every number it prints comes from
the inputs or from the attrition probabilities and lead time it echoes back.
No compensation is modelled. Surplus is never expressed as a reduction in
force - only as REDEPLOY_OR_FREEZE (redeploy, freeze backfills, attrit).

USAGE
  headcount_planner.py plan --roster <csv> --demand <csv>
                            --start-period <YYYY-Qn>
                            [--periods <int>]                  (default 4)
                            [--attrition-probability low=0.05,medium=0.25,high=0.5]
                            [--hiring-lead-time-weeks <int>]   (default 8)
                            [--json <path>]
  headcount_planner.py -h | --help

ROSTER CSV (header row required)
  employee_id,name,department,role_level,manager_id,hire_date,
  planned_exit_date,attrition_risk
  attrition_risk: low | medium | high   planned_exit_date may be empty

DEMAND CSV (header row required)
  period,department,role_level,required_headcount     (period like 2027-Q1)

METHOD
  supply(P)  = employees on board at the start of P (hire_date <= P start)
               whose planned_exit_date is empty or after the end of P,
               each weighted by survival (1 - p_annual) ** (k / 4) where k is
               the 1-based period index (attrition probabilities are ANNUAL),
               summed and rounded DOWN to a whole person.
  gap(P)     = demand(P) - supply(P)
  action     : gap > 0 HIRE | gap < 0 REDEPLOY_OR_FREEZE | gap == 0 HOLD
  requisitions: new starts needed by P = gap(P) - starts already planned.
               A requisition opened in period O starts in the first period
               whose start date is on/after O start + lead time. If even the
               plan's first period is too late, it opens in the first period
               and is marked late (priority URGENT).
  SINGLE_POINT: a department/role_level with demand > 0 held by exactly one
               current incumbent who has no peer (same manager_id and same
               role_level) anywhere in the roster - succession risk.

EXIT CODES
  0 success | 1 unreadable file or missing required header |
  2 usage error | 3 internal consistency check failed
"""

import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from datetime import date, timedelta

ROSTER_COLUMNS = ("employee_id", "name", "department", "role_level",
                  "manager_id", "hire_date", "planned_exit_date",
                  "attrition_risk")
DEMAND_COLUMNS = ("period", "department", "role_level", "required_headcount")
DEFAULT_PROBS = {"low": 0.05, "medium": 0.25, "high": 0.5}
PERIOD_RE = re.compile(r"^(\d{4})-Q([1-4])$")


class InputError(Exception):
    pass


def parse_period(label):
    m = PERIOD_RE.match((label or "").strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def period_label(p):
    return f"{p[0]}-Q{p[1]}"


def next_period(p):
    return (p[0] + 1, 1) if p[1] == 4 else (p[0], p[1] + 1)


def prev_period(p):
    return (p[0] - 1, 4) if p[1] == 1 else (p[0], p[1] - 1)


def period_start(p):
    return date(p[0], 3 * (p[1] - 1) + 1, 1)


def period_end(p):
    return period_start(next_period(p)) - timedelta(days=1)


def first_start_period(open_p, lead_days):
    """First period whose start date is on/after open_p start + lead time."""
    ready = period_start(open_p) + timedelta(days=lead_days)
    p = open_p
    while period_start(p) < ready:
        p = next_period(p)
    return p


def parse_date(text):
    text = (text or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def read_csv(path, required, label):
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            header = [h.strip() for h in (reader.fieldnames or [])]
            if not header:
                raise InputError(f"{label} {path}: file is empty - a header "
                                 f"row is required: {','.join(required)}")
            missing = [c for c in required if c not in header]
            if missing:
                raise InputError(f"{label} {path}: missing required header "
                                 f"column(s): {', '.join(missing)}")
            rows = []
            for line_no, raw in enumerate(reader, start=2):
                row = {(k or "").strip(): (v or "").strip()
                       for k, v in raw.items() if k is not None}
                if any(row.values()):
                    row["_line"] = line_no
                    rows.append(row)
            return rows
    except OSError as exc:
        raise InputError(f"cannot read {label} {path}: {exc.strerror}")
    except (UnicodeDecodeError, csv.Error) as exc:
        raise InputError(f"cannot parse {label} {path}: {exc}")


def parse_probs(text):
    probs = dict(DEFAULT_PROBS)
    if not text:
        return probs
    for part in text.split(","):
        key, sep, val = part.partition("=")
        key = key.strip().lower()
        if not sep or key not in probs:
            raise ValueError(f"bad attrition entry '{part}' (expected "
                             "low=..,medium=..,high=..)")
        try:
            num = float(val)
        except ValueError:
            raise ValueError(f"attrition probability for {key} is not a "
                             f"number: '{val}'")
        if not 0.0 <= num <= 1.0:
            raise ValueError(f"attrition probability for {key} must be "
                             f"between 0 and 1, got {num}")
        probs[key] = num
    return probs


def clean_roster(rows, issues):
    seen, roster = set(), []
    for r in rows:
        where = f"roster line {r['_line']} ({r['employee_id'] or 'no id'})"
        if not r["employee_id"]:
            issues.append(f"{where}: missing employee_id - excluded")
            continue
        if r["employee_id"] in seen:
            issues.append(f"{where}: duplicate employee_id - only the first "
                          "row is counted")
            continue
        seen.add(r["employee_id"])
        if not r["department"] or not r["role_level"]:
            issues.append(f"{where}: missing department/role_level - excluded")
            continue
        hire = parse_date(r["hire_date"])
        if hire is None:
            issues.append(f"{where}: unparseable hire_date "
                          f"'{r['hire_date']}' - excluded from supply")
            continue
        exit_d = None
        if r["planned_exit_date"]:
            exit_d = parse_date(r["planned_exit_date"])
            if exit_d is None:
                issues.append(f"{where}: unparseable planned_exit_date "
                              f"'{r['planned_exit_date']}' - excluded from "
                              "supply")
                continue
            if exit_d < hire:
                issues.append(f"{where}: planned_exit_date {exit_d} is before "
                              f"hire_date {hire} - excluded from supply")
                continue
        risk = r["attrition_risk"].lower()
        if risk not in DEFAULT_PROBS:
            issues.append(f"{where}: unknown attrition_risk "
                          f"'{r['attrition_risk']}' - treated as high")
            risk = "high"
        roster.append({"employee_id": r["employee_id"],
                       "department": r["department"],
                       "role_level": r["role_level"],
                       "manager_id": r["manager_id"], "hire": hire,
                       "exit": exit_d, "risk": risk})
    return roster


def clean_demand(rows, window, issues):
    demand = {}
    for r in rows:
        where = f"demand line {r['_line']}"
        p = parse_period(r["period"])
        if p is None:
            issues.append(f"{where}: unparseable period '{r['period']}' - "
                          "skipped")
            continue
        if not r["department"] or not r["role_level"]:
            issues.append(f"{where}: missing department/role_level - skipped")
            continue
        try:
            need = int(r["required_headcount"])
            if need < 0:
                raise ValueError
        except ValueError:
            issues.append(f"{where}: non-numeric or negative "
                          f"required_headcount '{r['required_headcount']}' - "
                          "skipped")
            continue
        if p not in window:
            issues.append(f"{where}: period {period_label(p)} is outside the "
                          "plan window - ignored")
            continue
        key = (r["department"], r["role_level"], p)
        if key in demand:
            issues.append(f"{where}: duplicate demand for {key[0]}/{key[1]} "
                          f"{period_label(p)} - the higher figure is used")
            need = max(need, demand[key])
        demand[key] = need
    return demand


def plan(roster, demand, window, probs, lead_weeks, issues):
    roster_keys = sorted({(e["department"], e["role_level"]) for e in roster})
    demand_keys = sorted({(d, l) for d, l, _ in demand})
    for key in demand_keys:
        if key not in roster_keys:
            issues.append(f"demand for {key[0]}/{key[1]} has no incumbents in "
                          "the roster - supply is 0")
    for key in roster_keys:
        if key not in demand_keys:
            issues.append(f"roster group {key[0]}/{key[1]} has no demand "
                          "forecast - not planned")

    gap_rows, reqs = [], []
    lead_days = lead_weeks * 7
    for key in demand_keys:
        members = [e for e in roster
                   if (e["department"], e["role_level"]) == key]
        planned_starts = 0
        for k, p in enumerate(window, start=1):
            if (key[0], key[1], p) not in demand:
                issues.append(f"no demand row for {key[0]}/{key[1]} "
                              f"{period_label(p)} - period not planned")
                continue
            p_start, p_end = period_start(p), period_end(p)
            supply_f, planned_exits = 0.0, 0
            for e in members:
                if e["hire"] > p_start:
                    continue
                if e["exit"] is not None:
                    if e["exit"] <= p_end:
                        planned_exits += 1
                        continue
                    supply_f += 1.0
                else:
                    supply_f += (1.0 - probs[e["risk"]]) ** (k / 4.0)
            supply = math.floor(round(supply_f, 6))
            need = demand[(key[0], key[1], p)]
            gap = need - supply
            new = max(0, gap - planned_starts)
            for _ in range(new):
                reqs.append(make_req(key, p, window[0], lead_days))
            planned_starts += new
            action = "HIRE" if gap > 0 else ("REDEPLOY_OR_FREEZE" if gap < 0
                                             else "HOLD")
            gap_rows.append({"department": key[0], "role_level": key[1],
                             "period": period_label(p), "supply": supply,
                             "supply_unrounded": round(supply_f, 4),
                             "planned_exits": planned_exits, "demand": need,
                             "gap": gap, "new_requisitions": new,
                             "cumulative_requisitions": planned_starts,
                             "action": action})
    reqs.sort(key=lambda r: (r["department"], r["role_level"],
                             r["needed_by_period"]))
    for i, r in enumerate(reqs, start=1):
        r["requisition_id"] = f"REQ-{i:04d}"
        if parse_period(r["requisition_open_period"]) > parse_period(
                r["start_period"]):
            raise RuntimeError(f"{r['requisition_id']}: open period "
                               f"{r['requisition_open_period']} after start "
                               f"{r['start_period']}")
    gap_rows.sort(key=lambda g: (g["department"], g["role_level"],
                                 parse_period(g["period"])))
    return gap_rows, reqs


def make_req(key, needed_by, first, lead_days):
    open_p = needed_by
    while open_p > first and first_start_period(open_p, lead_days) > needed_by:
        open_p = prev_period(open_p)
    start = first_start_period(open_p, lead_days)
    late = start > needed_by
    if late:
        priority = "URGENT"
    elif open_p == first:
        priority = "HIGH"
    else:
        priority = "NORMAL"
    return {"department": key[0], "role_level": key[1],
            "needed_by_period": period_label(needed_by),
            "requisition_open_period": period_label(open_p),
            "start_period": period_label(start), "late": late,
            "priority": priority}


def single_points(roster, demand, first):
    critical = {(d, l) for (d, l, _), n in demand.items() if n > 0}
    p_start = period_start(first)
    current = [e for e in roster if e["hire"] <= p_start
               and (e["exit"] is None or e["exit"] >= p_start)]
    by_key = defaultdict(list)
    for e in current:
        by_key[(e["department"], e["role_level"])].append(e)
    flags = []
    for key in sorted(by_key):
        if key not in critical or len(by_key[key]) != 1:
            continue
        e = by_key[key][0]
        peers = [o for o in current if o is not e
                 and o["role_level"] == e["role_level"]
                 and o["manager_id"] and o["manager_id"] == e["manager_id"]]
        if not peers:
            flags.append({"department": key[0], "role_level": key[1],
                          "employee_id": e["employee_id"],
                          "flag": "SINGLE_POINT"})
    return flags


def report(args, window, probs, gap_rows, reqs, spofs, issues):
    final = window[-1]
    final_rows = [g for g in gap_rows if g["period"] == period_label(final)]
    totals = {
        "periods_planned": len(window),
        "gap_rows": len(gap_rows),
        "total_positive_gap_final_period": sum(max(0, g["gap"])
                                               for g in final_rows),
        "total_surplus_final_period": sum(max(0, -g["gap"])
                                          for g in final_rows),
        "total_requisitions": len(reqs),
        "late_requisitions": sum(r["late"] for r in reqs),
        "single_point_roles": len(spofs),
        "data_quality_issues": len(issues),
        "compensation_modelled": False,
    }
    print("HEADCOUNT PLAN - assumption calculator, cost-free (no "
          "compensation modelling)")
    print(f"roster / demand        : {args.roster} / {args.demand}")
    print(f"window                 : {period_label(window[0])} .. "
          f"{period_label(final)} ({len(window)} periods)")
    print("attrition (annual)     : " + ", ".join(
        f"{k}={probs[k]}" for k in ("low", "medium", "high"))
          + "  -> survival (1-p)^(k/4), supply rounded down")
    print(f"hiring lead time       : {args.hiring_lead_time_weeks} weeks")
    print("\nGAP TABLE  (expected = survival-weighted supply before rounding "
          "down; reqs = cumulative)")
    print(f"  {'department':<14}{'role_level':<12}{'period':<9}"
          f"{'expected':>9}{'supply':>7}{'demand':>7}{'gap':>5}{'reqs':>6}"
          "  action")
    for g in gap_rows:
        print(f"  {g['department']:<14}{g['role_level']:<12}{g['period']:<9}"
              f"{g['supply_unrounded']:>9.2f}{g['supply']:>7}{g['demand']:>7}"
              f"{g['gap']:>5}{g['cumulative_requisitions']:>6}  {g['action']}")
    print("\nREQUISITION PLAN")
    if not reqs:
        print("  (none)")
    for r in reqs:
        late = "  LATE - interim cover needed" if r["late"] else ""
        print(f"  {r['requisition_id']}  {r['department']}/{r['role_level']}"
              f"  open {r['requisition_open_period']} -> start "
              f"{r['start_period']} (needed by {r['needed_by_period']})"
              f"  {r['priority']}{late}")
    print("\nSUCCESSION RISK")
    if not spofs:
        print("  (none)")
    for s in spofs:
        print(f"  SINGLE_POINT {s['department']}/{s['role_level']} "
              f"incumbent {s['employee_id']}")
    print("\nTOTALS")
    for k, v in totals.items():
        print(f"  {k}: {v}")
    print(f"requisition_order_check: ok ({len(reqs)} requisitions)")
    print("\nDATA QUALITY")
    if not issues:
        print("  (none)")
    for i in issues:
        print(f"  - {i}")
    return totals


def main(argv):
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(add_help=False)
    sub = parser.add_subparsers(dest="mode")
    p = sub.add_parser("plan", add_help=False)
    p.add_argument("--roster", required=True)
    p.add_argument("--demand", required=True)
    p.add_argument("--start-period", required=True)
    p.add_argument("--periods", type=int, default=4)
    p.add_argument("--attrition-probability")
    p.add_argument("--hiring-lead-time-weeks", type=int, default=8)
    p.add_argument("--json")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("usage error - run with --help", file=sys.stderr)
        return 2
    if args.mode != "plan":
        print("usage error - mode must be 'plan'", file=sys.stderr)
        return 2
    start = parse_period(args.start_period)
    if start is None:
        print(f"usage error - --start-period must look like 2027-Q1, got "
              f"'{args.start_period}'", file=sys.stderr)
        return 2
    if not 1 <= args.periods <= 40 or args.hiring_lead_time_weeks < 0:
        print("usage error - --periods must be 1..40 and "
              "--hiring-lead-time-weeks >= 0", file=sys.stderr)
        return 2
    try:
        probs = parse_probs(args.attrition_probability)
    except ValueError as exc:
        print(f"usage error - {exc}", file=sys.stderr)
        return 2
    window = [start]
    while len(window) < args.periods:
        window.append(next_period(window[-1]))
    issues = []
    try:
        roster = clean_roster(read_csv(args.roster, ROSTER_COLUMNS, "roster"),
                              issues)
        demand = clean_demand(read_csv(args.demand, DEMAND_COLUMNS, "demand"),
                              window, issues)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        gap_rows, reqs = plan(roster, demand, window, probs,
                              args.hiring_lead_time_weeks, issues)
    except RuntimeError as exc:
        print(f"internal consistency failure: {exc}", file=sys.stderr)
        return 3
    spofs = single_points(roster, demand, start)
    totals = report(args, window, probs, gap_rows, reqs, spofs, issues)
    if args.json:
        payload = {"assumptions": {
                       "attrition_probability_annual": probs,
                       "hiring_lead_time_weeks": args.hiring_lead_time_weeks,
                       "start_period": period_label(start),
                       "periods": args.periods,
                       "supply_rounding": "floor"},
                   "gap_table": gap_rows, "requisitions": reqs,
                   "single_points": spofs, "totals": totals,
                   "data_quality": issues}
        try:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, sort_keys=True)
                fh.write("\n")
        except OSError as exc:
            print(f"error: cannot write JSON {args.json}: {exc.strerror}",
                  file=sys.stderr)
            return 1
        print(f"\njson written: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
