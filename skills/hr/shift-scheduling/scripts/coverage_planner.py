#!/usr/bin/env python3
"""
coverage_planner.py - plan shift coverage, or audit a proposed schedule.

Usage:
    python3 coverage_planner.py plan  --demand demand.csv --employees staff.csv
        [--schedule-publish-date 2026-11-16] [--min-notice-days 14]
        [--max-weekly-hours 40] [--overtime-eligible no|yes]
        [--shift-times "AM=06:00-14:00,PM=14:00-22:00,NIGHT=22:00-06:00"]
        [--workweek-start mon] [--extended-shift-hours 8]
        [--json report.json] [--out assignments.csv]
    python3 coverage_planner.py audit --demand demand.csv --employees staff.csv
        --assignments assignments.csv [same options as plan]
    python3 coverage_planner.py --help

Inputs (header row required, ISO dates YYYY-MM-DD, 24h times HH:MM):
    demand.csv       date,shift,role,required_headcount
    employees.csv    employee_id,name,role,weekly_hours_cap,max_shift_hours,
                     min_rest_hours,availability
                       role          one role, or several separated by ";" (cross-trained)
                       availability  ";"-separated YYYY-MM-DD:SHIFT tokens
                       blank/non-numeric caps fall back to: weekly_hours_cap =
                       --max-weekly-hours, max_shift_hours = --extended-shift-hours,
                       min_rest_hours = 10 (flagged)
    assignments.csv  employee_id,date,shift,start_time,end_time,hours   (audit only)
                       blank start/end -> taken from --shift-times; end <= start
                       means the shift ends the next day; start/end win over hours

Modes:
    plan   Greedy, deterministic. Demand rows are filled in (date, shift start,
           shift, role) order; each slot goes to the eligible candidate with the
           fewest hours already assigned, ties broken by employee_id. Eligible =
           role match, available for date:SHIFT, not already on that shift, no
           overlap, rest gap >= min_rest_hours on both sides, shift length <=
           max_shift_hours, weekly hours stay <= weekly_hours_cap and, when
           --overtime-eligible no (default), <= --max-weekly-hours.
    audit  Checks a supplied assignment file against the same rules and reports
           every violation instead of preventing it.

Overtime: hours above --max-weekly-hours in one workweek (a fixed, recurring
168-hour period starting 00:00 on --workweek-start; a shift counts in the week it
starts). With --overtime-eligible yes the planner may schedule them and they are
reported as projected OVERTIME; with no, the planner never schedules them and the
audit flags them as OVERTIME_NOT_AUTHORISED.

Notice: when --schedule-publish-date is given, any assignment dated fewer than
--min-notice-days after it is a NOTICE violation (likely predictability pay).

Outputs: coverage table, open-shift broadcast list, weekly hours per employee,
issues (REST/clopen, OVERLAP, NOTICE, ROLE/AVAILABILITY mismatch, DUPLICATE,
HOURS_MISMATCH, MAX_SHIFT, EXTENDED_SHIFT, WEEKLY_CAP, OVERTIME, data errors),
and a summary. --json writes the full report; --out writes the plan as an
assignments CSV (plan mode, re-auditable) or the issue list as CSV (audit mode).

Exit codes: 0 success (violations are reported, not fatal), 1 unreadable file,
2 bad arguments or missing header.
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

DEMAND_COLS = ["date", "shift", "role", "required_headcount"]
EMP_COLS = ["employee_id", "name", "role", "weekly_hours_cap", "max_shift_hours",
            "min_rest_hours", "availability"]
ASSIGN_COLS = ["employee_id", "date", "shift", "start_time", "end_time", "hours"]
DEFAULT_SHIFTS = "AM=06:00-14:00,PM=14:00-22:00,NIGHT=22:00-06:00"
DEFAULT_MIN_REST = 10.0
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
HOURS_TOLERANCE = 0.05  # 3 minutes


class Report:
    def __init__(self):
        self.issues = []

    def add(self, kind, detail, employee_id="", day="", shift=""):
        self.issues.append({"type": kind, "employee_id": employee_id, "date": day,
                            "shift": shift, "detail": detail})


def die(msg, code):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def read_csv(path, required, label):
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            header = [h.strip() for h in (reader.fieldnames or [])]
            reader.fieldnames = header
            rows = []
            for row in reader:
                if not any((v or "").strip() for k, v in row.items() if k is not None and isinstance(v, str)):
                    continue  # skip fully blank lines
                rows.append({k: (v.strip() if isinstance(v, str) else "")
                             for k, v in row.items() if k is not None})
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        die(f"cannot read {label} {path}: {exc}", 1)
    if not header:
        return []  # empty file: treated as zero rows, warned by caller
    missing = [c for c in required if c not in header]
    if missing:
        die(f"{label} {path} missing required header(s): {', '.join(missing)}", 2)
    return rows


def parse_date(text):
    try:
        return date.fromisoformat(text)
    except (ValueError, TypeError):
        return None


def parse_time(text):
    try:
        t = datetime.strptime(text, "%H:%M").time()
    except (ValueError, TypeError):
        return None
    return t


def parse_num(text):
    try:
        v = float(text)
    except (ValueError, TypeError):
        return None
    if v != v or v in (float("inf"), float("-inf")) or v < 0:
        return None
    return v


def norm_shift(s):
    return (s or "").strip().upper()


def norm_role(r):
    return (r or "").strip().casefold()


def span(day, start, end):
    """Return (start_dt, end_dt, hours); end <= start rolls to the next day."""
    s = datetime.combine(day, start)
    e = datetime.combine(day, end)
    if e <= s:
        e += timedelta(days=1)
    return s, e, round((e - s).total_seconds() / 3600, 2)


def week_start(day, first_weekday):
    return day - timedelta(days=(day.weekday() - first_weekday) % 7)


def parse_shift_times(spec):
    out = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            label, times = part.split("=", 1)
            a, b = times.split("-", 1)
        except ValueError:
            raise argparse.ArgumentTypeError(f"bad shift spec {part!r}; want LABEL=HH:MM-HH:MM")
        ta, tb = parse_time(a.strip()), parse_time(b.strip())
        if ta is None or tb is None:
            raise argparse.ArgumentTypeError(f"bad time in shift spec {part!r}")
        out[norm_shift(label)] = (ta, tb)
    return out


# ---------------------------------------------------------------- loaders

def load_demand(rows, shift_times, rep):
    merged = {}
    for n, r in enumerate(rows, start=2):
        day, shift, role = parse_date(r.get("date")), norm_shift(r.get("shift")), r.get("role", "")
        req = r.get("required_headcount", "")
        where = f"demand line {n}"
        if day is None:
            rep.add("DATA_ERROR", f"{where}: malformed date {r.get('date')!r}; row skipped")
            continue
        if not shift or not role:
            rep.add("DATA_ERROR", f"{where}: blank shift or role; row skipped", day=str(day))
            continue
        try:
            need = int(req)
            if need < 0:
                raise ValueError
        except ValueError:
            rep.add("DATA_ERROR", f"{where}: required_headcount {req!r} is not a whole number >= 0; row skipped",
                    day=str(day), shift=shift)
            continue
        key = (day, shift, norm_role(role))
        if key in merged:
            rep.add("DATA_WARNING", f"{where}: duplicate demand row for {day} {shift} {role}; headcounts summed",
                    day=str(day), shift=shift)
            merged[key]["required"] += need
            continue
        merged[key] = {"date": day, "shift": shift, "role": role.strip(), "required": need,
                       "assigned": [], "known_shift": shift in shift_times}
        if shift not in shift_times:
            rep.add("DATA_WARNING", f"{where}: shift {shift!r} has no --shift-times entry; "
                    "plan cannot fill it, audit needs explicit start/end", day=str(day), shift=shift)

    def order(d):
        t = shift_times.get(d["shift"])
        return (d["date"], t[0].isoformat() if t else "99", d["shift"], norm_role(d["role"]))
    return sorted(merged.values(), key=order)


def load_employees(rows, args, rep):
    emps = {}
    for n, r in enumerate(rows, start=2):
        eid = r.get("employee_id", "")
        where = f"employees line {n}"
        if not eid:
            rep.add("DATA_ERROR", f"{where}: blank employee_id; row skipped")
            continue
        if eid in emps:
            rep.add("DATA_ERROR", f"{where}: duplicate employee_id; first occurrence kept", employee_id=eid)
            continue
        roles = {norm_role(x) for x in r.get("role", "").split(";") if x.strip()}
        if not roles:
            rep.add("DATA_WARNING", f"{where}: no role; employee can never be matched", employee_id=eid)

        def num(col, default):
            raw = r.get(col, "")
            v = parse_num(raw)
            if v is None:
                rep.add("DATA_WARNING", f"{where}: {col} {raw!r} blank/invalid; using {default}", employee_id=eid)
                return default
            return v
        avail = set()
        for tok in [t.strip() for t in r.get("availability", "").split(";") if t.strip()]:
            d, _, s = tok.partition(":")
            if parse_date(d) is None or not s.strip():
                rep.add("DATA_WARNING", f"{where}: malformed availability token {tok!r} ignored", employee_id=eid)
                continue
            avail.add((parse_date(d), norm_shift(s)))
        if not avail:
            rep.add("DATA_WARNING", f"{where}: no usable availability; employee will not be planned",
                    employee_id=eid)
        emps[eid] = {
            "id": eid, "name": r.get("name", ""), "roles": roles, "avail": avail,
            "weekly_cap": num("weekly_hours_cap", args.max_weekly_hours),
            "max_shift": num("max_shift_hours", args.extended_shift_hours),
            "min_rest": num("min_rest_hours", DEFAULT_MIN_REST),
            "shifts": [],  # list of dicts: date, shift, start, end, hours
        }
    return emps


# ---------------------------------------------------------------- rules

def weekly_hours(emp, wk, first_weekday):
    return sum(s["hours"] for s in emp["shifts"] if week_start(s["date"], first_weekday) == wk)


def rest_ok(emp, start, end):
    """True if [start, end) neither overlaps nor sits within min_rest of another shift."""
    gap = timedelta(hours=emp["min_rest"])
    for s in emp["shifts"]:
        if start < s["end"] + gap and s["start"] < end + gap:
            return False
    return True


def find_demand(demand_idx, day, shift, emp):
    """Pick the demand row this assignment covers: the matching-role row still short, else first match."""
    rows = demand_idx.get((day, shift), [])
    matches = [d for d in rows if norm_role(d["role"]) in emp["roles"]] if emp else []
    for d in matches:
        if len(d["assigned"]) < d["required"]:
            return d, rows
    return (matches[0] if matches else None), rows


# ---------------------------------------------------------------- modes

def plan(demand, emps, shift_times, args, rep):
    planned = []
    order = sorted(emps)
    for d in demand:
        if not d["known_shift"]:
            continue
        t0, t1 = shift_times[d["shift"]]
        start, end, hours = span(d["date"], t0, t1)
        wk = week_start(d["date"], args.first_weekday)
        role = norm_role(d["role"])
        for _ in range(d["required"]):
            cands = []
            for eid in order:
                e = emps[eid]
                if role not in e["roles"] or (d["date"], d["shift"]) not in e["avail"]:
                    continue
                if eid in d["assigned"] or hours > e["max_shift"] or not rest_ok(e, start, end):
                    continue
                new_week = weekly_hours(e, wk, args.first_weekday) + hours
                if new_week > e["weekly_cap"]:
                    continue
                if args.overtime_eligible == "no" and new_week > args.max_weekly_hours:
                    continue
                cands.append((sum(s["hours"] for s in e["shifts"]), eid))
            if not cands:
                break
            _, pick = min(cands)
            e = emps[pick]
            e["shifts"].append({"date": d["date"], "shift": d["shift"], "start": start, "end": end,
                                "hours": hours})
            d["assigned"].append(pick)
            planned.append({"employee_id": pick, "date": d["date"].isoformat(), "shift": d["shift"],
                            "start_time": t0.strftime("%H:%M"), "end_time": t1.strftime("%H:%M"),
                            "hours": f"{hours:g}"})
    return planned


def audit(rows, demand, emps, shift_times, args, rep):
    demand_idx = defaultdict(list)
    for d in demand:
        demand_idx[(d["date"], d["shift"])].append(d)
    seen = set()
    for n, r in enumerate(rows, start=2):
        where = f"assignments line {n}"
        eid, shift = r.get("employee_id", ""), norm_shift(r.get("shift"))
        day = parse_date(r.get("date"))
        if day is None:
            rep.add("DATA_ERROR", f"{where}: malformed date {r.get('date')!r}; row skipped", eid)
            continue
        ds = str(day)
        emp = emps.get(eid)
        if emp is None:
            rep.add("UNKNOWN_EMPLOYEE", f"{where}: employee_id {eid!r} not in employees file; "
                    "not counted toward coverage", eid, ds, shift)
        if (eid, day, shift) in seen:
            rep.add("DUPLICATE_ASSIGNMENT", f"{where}: {eid} already assigned to {ds} {shift}; "
                    "duplicate ignored for coverage and hours", eid, ds, shift)
            continue
        seen.add((eid, day, shift))

        # Resolve times: explicit start/end, else shift default.
        st_raw, en_raw = r.get("start_time", ""), r.get("end_time", "")
        t0, t1 = parse_time(st_raw), parse_time(en_raw)
        if (st_raw and t0 is None) or (en_raw and t1 is None):
            rep.add("DATA_ERROR", f"{where}: malformed start/end time {st_raw!r}-{en_raw!r}", eid, ds, shift)
            t0 = t1 = None
        elif not st_raw and not en_raw and shift in shift_times:
            t0, t1 = shift_times[shift]
        elif t0 is None or t1 is None:
            t0 = t1 = None
        hours_field = parse_num(r.get("hours", "")) if r.get("hours", "") else None
        if r.get("hours", "") and hours_field is None:
            rep.add("DATA_ERROR", f"{where}: hours {r.get('hours')!r} is not a number >= 0", eid, ds, shift)
        if t0 is not None:
            start, end, hours = span(day, t0, t1)
            if hours_field is not None and abs(hours_field - hours) > HOURS_TOLERANCE:
                rep.add("HOURS_MISMATCH", f"{where}: hours={hours_field:g} but {t0:%H:%M}-{t1:%H:%M} "
                        f"is {hours:g}h; using {hours:g}h", eid, ds, shift)
        elif hours_field is not None:
            start = end = None
            hours = hours_field
            rep.add("DATA_WARNING", f"{where}: no usable start/end; rest and overlap checks skipped, "
                    f"hours={hours:g} used", eid, ds, shift)
        else:
            rep.add("DATA_ERROR", f"{where}: neither usable times nor hours; counted toward coverage only",
                    eid, ds, shift)
            start = end = None
            hours = 0.0

        d, rows_here = find_demand(demand_idx, day, shift, emp)
        if d is not None:
            d["assigned"].append(eid)
        elif emp is not None:
            if rows_here:
                rep.add("ROLE_MISMATCH", f"{where}: {eid} roles {sorted(emp['roles'])} match no demand "
                        f"role on {ds} {shift} ({', '.join(x['role'] for x in rows_here)})", eid, ds, shift)
            else:
                rep.add("NO_DEMAND", f"{where}: no demand row for {ds} {shift}", eid, ds, shift)
        if emp is None:
            continue
        if (day, shift) not in emp["avail"]:
            rep.add("AVAILABILITY_MISMATCH", f"{where}: {eid} is not available for {ds}:{shift}", eid, ds, shift)
        if hours > emp["max_shift"]:
            rep.add("MAX_SHIFT_EXCEEDED", f"{where}: {hours:g}h > max_shift_hours {emp['max_shift']:g}",
                    eid, ds, shift)
        emp["shifts"].append({"date": day, "shift": shift, "start": start, "end": end, "hours": hours})

    # Rest / overlap between consecutive timed shifts per employee.
    for eid in sorted(emps):
        e = emps[eid]
        timed = sorted((s for s in e["shifts"] if s["start"] is not None), key=lambda s: s["start"])
        for a, b in zip(timed, timed[1:]):
            gap = round((b["start"] - a["end"]).total_seconds() / 3600, 2)
            if gap < 0:
                rep.add("OVERLAP", f"{a['date']} {a['shift']} overlaps {b['date']} {b['shift']} by {-gap:g}h",
                        eid, str(b["date"]), b["shift"])
            elif gap < e["min_rest"]:
                what = "back-to-back double shift" if gap == 0 else "clopen"
                rep.add("REST_VIOLATION", f"{what}: {gap:g}h rest between {a['date']} {a['shift']} and "
                        f"{b['date']} {b['shift']} < min_rest_hours {e['min_rest']:g}", eid, str(b["date"]),
                        b["shift"])


# ---------------------------------------------------------------- shared checks & output

def common_checks(emps, args, rep):
    """Notice, extended-shift, weekly cap and overtime checks; returns weekly table."""
    weekly = []
    for eid in sorted(emps):
        e = emps[eid]
        for s in sorted(e["shifts"], key=lambda s: (s["date"], s["shift"])):
            ds = str(s["date"])
            if args.publish is not None:
                lead = (s["date"] - args.publish).days
                if lead < args.min_notice_days:
                    rep.add("NOTICE", f"assigned {lead} day(s) after publish date {args.publish} "
                            f"< min notice {args.min_notice_days}", eid, ds, s["shift"])
            if s["hours"] > args.extended_shift_hours:
                rep.add("EXTENDED_SHIFT", f"{s['hours']:g}h shift > {args.extended_shift_hours:g}h; "
                        "fatigue risk, add breaks/controls", eid, ds, s["shift"])
        by_week = defaultdict(float)
        for s in e["shifts"]:
            by_week[week_start(s["date"], args.first_weekday)] += s["hours"]
        for wk in sorted(by_week):
            h = round(by_week[wk], 2)
            ot = round(max(0.0, h - args.max_weekly_hours), 2)
            flags = []
            if h > e["weekly_cap"]:
                flags.append("WEEKLY_CAP_EXCEEDED")
                rep.add("WEEKLY_CAP_EXCEEDED", f"week of {wk}: {h:g}h > weekly_hours_cap {e['weekly_cap']:g}",
                        eid, str(wk))
            if ot > 0:
                kind = "OVERTIME" if args.overtime_eligible == "yes" else "OVERTIME_NOT_AUTHORISED"
                flags.append(kind)
                rep.add(kind, f"week of {wk}: {h:g}h, {ot:g}h over {args.max_weekly_hours:g}", eid, str(wk))
            weekly.append({"employee_id": eid, "name": e["name"], "week_start": str(wk), "hours": h,
                           "overtime_hours": ot, "flags": flags})
    return weekly


def build(mode, demand, emps, weekly, rep, planned):
    coverage, open_shifts = [], []
    for d in demand:
        short = max(0, d["required"] - len(d["assigned"]))
        coverage.append({"date": str(d["date"]), "shift": d["shift"], "role": d["role"],
                         "required": d["required"], "assigned": len(d["assigned"]),
                         "status": (f"SHORT {short}" if short else
                                    f"OVER {len(d['assigned']) - d['required']}"
                                    if len(d["assigned"]) > d["required"] else "COVERED"),
                         "employees": sorted(d["assigned"])})
        if short:
            role = norm_role(d["role"])
            any_role = any(role in e["roles"] for e in emps.values())
            qualified = sorted(eid for eid, e in emps.items() if role in e["roles"] and eid not in d["assigned"])
            note = ("" if qualified else
                    "ALL QUALIFIED STAFF ALREADY ON THIS SHIFT - use standby list or cross-train" if any_role else
                    "NO QUALIFIED STAFF - cross-train or hire")
            open_shifts.append({"date": str(d["date"]), "shift": d["shift"], "role": d["role"], "open": short,
                                "broadcast_to": qualified, "note": note})
    order = {"DATA_ERROR": 0}
    rep.issues.sort(key=lambda i: (order.get(i["type"], 1), i["type"], i["employee_id"], i["date"],
                                   i["shift"], i["detail"]))
    counts = defaultdict(int)
    for i in rep.issues:
        counts[i["type"]] += 1
    summary = {
        "mode": mode,
        "demand_rows": len(demand),
        "required_headcount": sum(d["required"] for d in demand),
        "assigned_headcount": sum(min(len(d["assigned"]), d["required"]) for d in demand),
        "uncovered_headcount": sum(o["open"] for o in open_shifts),
        "total_assigned_hours": round(sum(w["hours"] for w in weekly), 2),
        "projected_overtime_hours": round(sum(w["overtime_hours"] for w in weekly), 2),
        "issue_counts": dict(sorted(counts.items())),
    }
    return {"summary": summary, "coverage": coverage, "open_shifts": open_shifts,
            "weekly_hours": weekly, "issues": rep.issues, "planned_assignments": planned}


def print_report(r, args):
    s = r["summary"]
    print(f"SHIFT COVERAGE - {s['mode'].upper()}")
    if args.publish is not None:
        print(f"publish date {args.publish}  min notice {args.min_notice_days} days")
    print(f"overtime threshold {args.max_weekly_hours:g}h/week  overtime eligible: {args.overtime_eligible}")
    print()
    print("COVERAGE")
    if not r["coverage"]:
        print("  (no demand rows)")
    for c in r["coverage"]:
        print(f"  {c['date']} {c['shift']:<6} {c['role']:<16} req {c['required']:>2}  "
              f"asg {c['assigned']:>2}  {c['status']:<9} {','.join(c['employees'])}")
    print()
    print(f"OPEN SHIFTS - BROADCAST LIST ({len(r['open_shifts'])})")
    for o in r["open_shifts"]:
        to = ", ".join(o["broadcast_to"]) or o["note"]
        print(f"  {o['date']} {o['shift']:<6} {o['role']:<16} open {o['open']}  -> {to}")
    print()
    print("WEEKLY HOURS")
    if not r["weekly_hours"]:
        print("  (no assigned hours)")
    for w in r["weekly_hours"]:
        print(f"  {w['employee_id']:<8} week {w['week_start']}  {w['hours']:>6g}h  OT {w['overtime_hours']:g}h"
              f"  {' '.join(w['flags'])}")
    print()
    print(f"ISSUES ({len(r['issues'])})")
    for i in r["issues"]:
        who = " ".join(x for x in (i["employee_id"], i["date"], i["shift"]) if x)
        print(f"  {i['type']:<24} {who:<24} {i['detail']}")
    print()
    print("SUMMARY")
    print(f"  demand rows {s['demand_rows']}  required {s['required_headcount']}  "
          f"assigned {s['assigned_headcount']}  uncovered {s['uncovered_headcount']}")
    print(f"  total assigned hours {s['total_assigned_hours']:g}  projected overtime hours "
          f"{s['projected_overtime_hours']:g}")
    for k, v in s["issue_counts"].items():
        print(f"  {k}: {v}")


def iso_date(v):
    d = parse_date(v)
    if d is None:
        raise argparse.ArgumentTypeError(f"not an ISO date (YYYY-MM-DD): {v!r}")
    return d


def nonneg_float(v):
    x = parse_num(v)
    if x is None:
        raise argparse.ArgumentTypeError(f"must be a number >= 0: {v!r}")
    return x


def nonneg_int(v):
    try:
        x = int(v)
    except ValueError:
        x = -1
    if x < 0:
        raise argparse.ArgumentTypeError(f"must be a whole number >= 0: {v!r}")
    return x


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    if not argv or argv[0] not in ("plan", "audit"):
        print(__doc__, file=sys.stderr)
        print("error: first argument must be 'plan' or 'audit'", file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(prog="coverage_planner.py", add_help=False)
    ap.add_argument("mode", choices=["plan", "audit"])
    ap.add_argument("--demand", required=True)
    ap.add_argument("--employees", required=True)
    ap.add_argument("--assignments")
    ap.add_argument("--schedule-publish-date", dest="publish", type=iso_date)
    ap.add_argument("--min-notice-days", type=nonneg_int, default=14)
    ap.add_argument("--max-weekly-hours", type=nonneg_float, default=40.0)
    ap.add_argument("--overtime-eligible", choices=["yes", "no"], default="no")
    ap.add_argument("--shift-times", type=parse_shift_times, default=parse_shift_times(DEFAULT_SHIFTS))
    ap.add_argument("--workweek-start", choices=WEEKDAYS, default="mon")
    ap.add_argument("--extended-shift-hours", type=nonneg_float, default=8.0)
    ap.add_argument("--json")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    args.first_weekday = WEEKDAYS.index(args.workweek_start)
    if args.mode == "audit" and not args.assignments:
        die("audit mode requires --assignments", 2)

    rep = Report()
    d_rows = read_csv(args.demand, DEMAND_COLS, "demand")
    e_rows = read_csv(args.employees, EMP_COLS, "employees")
    if not d_rows:
        rep.add("DATA_WARNING", "demand file has no rows; nothing to cover")
    if not e_rows:
        rep.add("DATA_WARNING", "employees file has no rows; nobody can be assigned")
    demand = load_demand(d_rows, args.shift_times, rep)
    emps = load_employees(e_rows, args, rep)
    planned = []
    if args.mode == "plan":
        planned = plan(demand, emps, args.shift_times, args, rep)
    else:
        a_rows = read_csv(args.assignments, ASSIGN_COLS, "assignments")
        if not a_rows:
            rep.add("DATA_WARNING", "assignments file has no rows")
        audit(a_rows, demand, emps, args.shift_times, args, rep)
    weekly = common_checks(emps, args, rep)
    report = build(args.mode, demand, emps, weekly, rep, planned)
    print_report(report, args)

    try:
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, sort_keys=True)
                fh.write("\n")
            print(f"\nJSON report written to {args.json}")
        if args.out:
            cols = ASSIGN_COLS if args.mode == "plan" else ["type", "employee_id", "date", "shift", "detail"]
            data = planned if args.mode == "plan" else report["issues"]
            with open(args.out, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                w.writerows(data)
            print(f"CSV written to {args.out}")
    except OSError as exc:
        die(f"cannot write output: {exc}", 1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
