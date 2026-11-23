#!/usr/bin/env python3
"""retention_schedule.py - HR record retention schedule and inventory audit.

Computes disposition ELIGIBILITY only. It never deletes anything and never
claims to: physical destruction is a separate, human-approved, logged action.

The built-in schedule is US-federal-flavoured reference data, not legal advice.
Re-base it for each jurisdiction the records are subject to; a longer local
rule is expressed per record via `jurisdiction_extra_months`.

USAGE
  retention_schedule.py schedule [--json <path>]
  retention_schedule.py audit --inventory <csv> --as-of <YYYY-MM-DD>
                              [--upcoming-days <int>]       (default 90)
                              [--max-retention-years <int>] (default 30)
                              [--json <path>]
  retention_schedule.py -h | --help

INVENTORY CSV (header row required)
  record_id,record_class,employee_id,event_date,event_type,status,
  legal_hold,jurisdiction_extra_months

  event_type : hire | termination | record_created | plan_termination |
               exposure | claim_filed | claim_resolved
  legal_hold : y | n   (empty or anything else is a DATA_WARNING, never purged)
  jurisdiction_extra_months : integer >= 0, empty = 0
  status     : free text; `active` means the employee is still employed

  Classes whose clock depends on several events (I-9, employment-duration
  classes, claims) are evaluated across all rows that share
  employee_id + record_class - give each event its own row and record_id.

GROUPS (exclusive, in precedence order)
  HOLD          legal_hold=y, or claim_filed with no later claim_resolved
                (flag routine_purge_blocked; disposition is HOLD, never a date)
  DATA_WARNING  unparseable/missing event_date, unknown event_type, bad
                legal_hold, bad or negative jurisdiction_extra_months,
                duplicate record_id, missing event needed by the rule
  UNKNOWN_CLASS record_class not in the schedule (reported, never kept silently)
  DUE_NOW       disposition-eligible on or before --as-of
  UPCOMING      eligible within --upcoming-days after --as-of
  RETAIN        still inside the retention period (or clock not started yet)
  A REVIEW flag is added when the computed retention (earliest event to
  disposition) exceeds --max-retention-years.

EXIT CODES
  0 success | 1 unreadable file or missing required header |
  2 usage error | 3 internal consistency check failed
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import date

EVENT_TYPES = ("hire", "termination", "record_created", "plan_termination",
               "exposure", "claim_filed", "claim_resolved")
CLAIM_EVENTS = ("claim_filed", "claim_resolved")
REQUIRED_COLUMNS = ("record_id", "record_class", "employee_id", "event_date",
                    "event_type", "status", "legal_hold",
                    "jurisdiction_extra_months")
GROUP_ORDER = ("DUE_NOW", "UPCOMING", "HOLD", "RETAIN", "UNKNOWN_CLASS",
               "DATA_WARNING")

# kind: fixed      -> trigger event_date + months
#       calyear    -> end of the trigger's calendar year + months
#       employment -> termination date + months (clock waits while employed)
#       i9         -> later of hire + 36 months or termination + 12 months
#       claim      -> HOLD until claim_resolved, then resolution + months
SCHEDULE = [
    {"record_class": "personnel_file", "kind": "fixed", "months": 12,
     "triggers": ("record_created", "hire", "termination"),
     "trigger": "later of record creation or the personnel action",
     "rule": "EEOC 29 CFR 1602.14",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "hiring_record", "kind": "fixed", "months": 12,
     "triggers": ("record_created", "hire"),
     "trigger": "later of creation or the hire/no-hire decision",
     "rule": "29 CFR 1602.14; 2 years for federal contractors with 150+ "
             "employees or a contract of $150k+ (ADEA / 29 CFR 1627.3)",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "involuntary_termination_record", "kind": "fixed",
     "months": 12, "triggers": ("termination",),
     "trigger": "termination date", "rule": "29 CFR 1602.14",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "payroll_record", "kind": "fixed", "months": 36,
     "triggers": ("record_created",), "trigger": "record date",
     "rule": "FLSA 29 CFR 516.5-.6 (supporting time records 2 years)",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "age_discrimination_payroll_record", "kind": "fixed",
     "months": 36, "triggers": ("record_created",), "trigger": "record date",
     "rule": "ADEA 29 CFR 1627.3",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "i9_employment_eligibility", "kind": "i9", "months": 36,
     "triggers": ("hire", "termination"),
     "trigger": "later of hire + 3 years or termination + 1 year",
     "rule": "IRCA 8 U.S.C. 1324a",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "fmla_record", "kind": "fixed", "months": 36,
     "triggers": ("record_created",), "trigger": "record date",
     "rule": "FMLA 29 CFR 825.500",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "benefits_plan_record", "kind": "fixed", "months": 72,
     "triggers": ("record_created", "plan_termination"),
     "trigger": "end of the plan year / filing date",
     "rule": "ERISA 29 U.S.C. 1027",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "osha_exposure_record", "kind": "employment",
     "months": 360, "triggers": ("exposure", "hire", "termination"),
     "trigger": "end of employment",
     "rule": "OSHA 29 CFR 1910.1020(d)(1)(ii)",
     "disposition": "offer to NIOSH / employee before destruction; then shred"},
    {"record_class": "toxic_substance_exposure", "kind": "employment",
     "months": 360, "triggers": ("exposure", "hire", "termination"),
     "trigger": "end of employment",
     "rule": "OSHA 29 CFR 1910.1020(d)(1)(ii)",
     "disposition": "offer to NIOSH / employee before destruction; then shred"},
    {"record_class": "osha_injury_illness_record", "kind": "calyear",
     "months": 60, "triggers": ("record_created", "exposure"),
     "trigger": "end of the calendar year the record pertains to",
     "rule": "29 CFR 1904.33",
     "disposition": "cross-cut shred / secure digital erase"},
    {"record_class": "medical_record", "kind": "employment", "months": 36,
     "triggers": ("record_created", "hire", "exposure", "termination"),
     "trigger": "end of employment (stored separately from personnel file)",
     "rule": "ADA 42 U.S.C. 12112(d)(3)(B); default statute of limitations "
             "3 years after termination",
     "disposition": "confidential shred / secure digital erase"},
    {"record_class": "background_check_record", "kind": "fixed", "months": 12,
     "triggers": ("record_created", "hire"), "trigger": "report date",
     "rule": "1 year minimum (FCRA claims are actionable up to 5 years); "
             "expert practice 5 years",
     "disposition": "FTC Disposal Rule: shred / burn / pulverize / erase"},
    {"record_class": "claim_or_investigation_record", "kind": "claim",
     "months": 0, "triggers": ("claim_filed", "claim_resolved"),
     "trigger": "final disposition of the charge, suit or appeal",
     "rule": "29 CFR 1602.14; ADEA 29 CFR 1627.3(b)(3)",
     "disposition": "counsel sign-off, then shred / secure digital erase"},
    {"record_class": "no_statutory_period_record", "kind": "fixed",
     "months": 36, "triggers": EVENT_TYPES, "trigger": "record date",
     "rule": "DEFAULT, not a mandate: Uniform Preservation of Private "
             "Business Records Act pattern (3 years)",
     "disposition": "cross-cut shred / secure digital erase"},
]
BY_CLASS = {s["record_class"]: s for s in SCHEDULE}


class InputError(Exception):
    pass


def add_months(d, months):
    y, m = divmod(d.month - 1 + months, 12)
    y, m = d.year + y, m + 1
    for day in (d.day, 30, 29, 28):
        try:
            return date(y, m, day)
        except ValueError:
            continue
    raise ValueError("cannot add months")


def parse_date(text):
    text = (text or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def parse_hold(text):
    t = (text or "").strip().lower()
    if t in ("y", "yes", "true", "1"):
        return True
    if t in ("n", "no", "false", "0"):
        return False
    return None


def read_inventory(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            header = [h.strip() for h in (reader.fieldnames or [])]
            missing = [c for c in REQUIRED_COLUMNS if c not in header]
            if not header:
                raise InputError(f"{path}: file is empty - a header row is "
                                 f"required: {','.join(REQUIRED_COLUMNS)}")
            if missing:
                raise InputError(f"{path}: missing required header column(s): "
                                 f"{', '.join(missing)}")
            rows = []
            for line_no, raw in enumerate(reader, start=2):
                row = {(k or "").strip(): (v or "").strip()
                       for k, v in raw.items() if k is not None}
                if not any(row.values()):
                    continue
                row["_line"] = line_no
                rows.append(row)
            return rows
    except OSError as exc:
        raise InputError(f"cannot read inventory {path}: {exc.strerror}")
    except (UnicodeDecodeError, csv.Error) as exc:
        raise InputError(f"cannot parse inventory {path}: {exc}")


def validate(rows):
    """Attach parsed fields and warnings. Fatal warnings block computation."""
    ids = Counter(r["record_id"] for r in rows)
    for r in rows:
        fatal, info = [], []
        r["_date"] = parse_date(r["event_date"])
        if not r["record_id"]:
            fatal.append("missing record_id")
        elif ids[r["record_id"]] > 1:
            fatal.append("duplicate record_id")
        if r["_date"] is None:
            fatal.append("missing event_date" if not r["event_date"]
                         else f"unparseable event_date '{r['event_date']}'")
        if r["event_type"] not in EVENT_TYPES:
            fatal.append(f"unknown event_type '{r['event_type']}'")
        r["_hold"] = parse_hold(r["legal_hold"])
        if r["_hold"] is None:
            fatal.append(f"legal_hold must be y/n, got '{r['legal_hold']}'")
        extra = r["jurisdiction_extra_months"]
        r["_extra"] = 0
        if extra:
            try:
                r["_extra"] = int(extra)
                if r["_extra"] < 0:
                    fatal.append(f"negative jurisdiction_extra_months {extra}")
            except ValueError:
                fatal.append(f"non-integer jurisdiction_extra_months '{extra}'")
        spec = BY_CLASS.get(r["record_class"])
        if (spec and r["event_type"] in EVENT_TYPES
                and r["event_type"] not in spec["triggers"]
                and r["event_type"] not in CLAIM_EVENTS):
            fatal.append(f"event_type '{r['event_type']}' is not a retention "
                         f"trigger for {r['record_class']}")
        if not r["employee_id"] and spec and spec["kind"] in (
                "i9", "employment", "claim"):
            fatal.append("missing employee_id (needed to join events)")
        r["_fatal"], r["_info"] = fatal, info
    return rows


def compute(rows, as_of, upcoming_days, max_years):
    groups = defaultdict(list)
    for r in rows:
        if not r["_fatal"]:
            groups[(r["employee_id"], r["record_class"])].append(r)

    results = []
    for r in rows:
        res = {"record_id": r["record_id"], "record_class": r["record_class"],
               "employee_id": r["employee_id"], "event_type": r["event_type"],
               "event_date": r["event_date"], "line": r["_line"],
               "legal_hold": bool(r["_hold"]), "group": None,
               "trigger_date": None, "disposition": None,
               "days_remaining": None, "days_overdue": None,
               "governing_rule": None, "flags": [], "warnings": list(r["_fatal"])}
        results.append(res)
        spec = BY_CLASS.get(r["record_class"])
        if r["_hold"]:
            res.update(group="HOLD", disposition="HOLD",
                       governing_rule="legal hold - all destruction suspended")
            res["flags"].append("routine_purge_blocked")
            continue
        if r["_fatal"]:
            res["group"] = "DATA_WARNING"
            continue
        if spec is None:
            res["group"] = "UNKNOWN_CLASS"
            res["warnings"].append("record_class not in schedule - classify "
                                   "before any disposition")
            continue
        if r["_date"] > as_of:
            res["warnings"].append("event_date is after --as-of")
        outcome = evaluate(r, spec, groups[(r["employee_id"],
                                            r["record_class"])])
        res["warnings"].extend(outcome.get("warnings", []))
        if outcome["state"] == "hold":
            res.update(group="HOLD", disposition="HOLD",
                       governing_rule=outcome["rule"])
            res["flags"].append("routine_purge_blocked")
            continue
        if outcome["state"] == "incomplete":
            res["group"] = "DATA_WARNING"
            continue
        if outcome["state"] == "pending":
            res.update(group="RETAIN", disposition="PENDING_TRIGGER",
                       governing_rule=outcome["rule"])
            continue
        disp, trig = outcome["disposition"], outcome["trigger"]
        if disp < trig or disp < r["_date"]:
            raise RuntimeError(f"ordering violation for {r['record_id']}: "
                               f"disposition {disp} < trigger {trig}")
        days = (disp - as_of).days
        res.update(trigger_date=trig.isoformat(), disposition=disp.isoformat(),
                   governing_rule=outcome["rule"])
        if days <= 0:
            res.update(group="DUE_NOW", days_overdue=-days)
        else:
            res["days_remaining"] = days
            res["group"] = "UPCOMING" if days <= upcoming_days else "RETAIN"
        earliest = min(g["_date"] for g in groups[(r["employee_id"],
                                                   r["record_class"])])
        if disp > add_months(earliest, max_years * 12):
            res["flags"].append("REVIEW")
    return results


def with_extra(rule, extra):
    return rule if not extra else f"{rule} + {extra} months jurisdiction rule"


def evaluate(r, spec, group):
    """Return the governing outcome for one row given its event group.

    Group-evaluated clocks (claims, employment, I-9) take the longest
    jurisdiction extension found anywhere in the group, so every row of
    one group gets the same disposition date.
    """
    group_extra = max(g["_extra"] for g in group)
    extra = r["_extra"] if spec["kind"] in ("fixed", "calyear") else group_extra
    filed = [g["_date"] for g in group if g["event_type"] == "claim_filed"]
    resolved = [g["_date"] for g in group if g["event_type"] == "claim_resolved"]
    if filed and (not resolved or max(resolved) < max(filed)):
        return {"state": "hold", "rule": "claim filed, no final disposition - "
                "29 CFR 1602.14; ADEA 29 CFR 1627.3(b)(3)"}
    candidates = []  # (disposition, trigger, rule)
    if resolved:
        claim = BY_CLASS["claim_or_investigation_record"]
        t = max(resolved)
        candidates.append((add_months(t, claim["months"] + group_extra), t,
                           with_extra(claim["rule"], group_extra)))
    kind = spec["kind"]
    rule = with_extra(spec["rule"], extra)
    warnings = []
    if kind == "fixed" and r["event_type"] not in CLAIM_EVENTS:
        t = r["_date"]
        candidates.append((add_months(t, spec["months"] + extra), t, rule))
    elif kind == "calyear" and r["event_type"] not in CLAIM_EVENTS:
        t = date(r["_date"].year, 12, 31)
        candidates.append((add_months(date(t.year + 1, 1, 1),
                                      spec["months"] + extra), t, rule))
    elif kind in ("employment", "i9"):
        hires = [g["_date"] for g in group if g["event_type"] == "hire"]
        terms = [g["_date"] for g in group if g["event_type"] == "termination"]
        if hires and terms and max(terms) < min(hires):
            warnings.append("termination before hire in this record group")
        if not terms:
            note = ("employment ongoing - clock starts at termination"
                    if r["status"].lower() == "active" else
                    "no termination event in group; clock not started")
            if r["status"].lower() not in ("", "active"):
                warnings.append(f"status '{r['status']}' but no termination "
                                "event - add one to start the clock")
            return {"state": "pending", "rule": f"{rule} ({note})",
                    "warnings": warnings}
        elif kind == "employment":
            t = max(terms)
            candidates.append((add_months(t, spec["months"] + extra), t, rule))
        else:
            if not hires:
                warnings.append("I-9 group has termination but no hire event "
                                "- the hire + 3 years leg cannot be checked")
                return {"state": "incomplete", "warnings": warnings}
            t_term, t_hire = max(terms), min(hires)
            candidates.append((add_months(t_hire, 36 + extra), t_hire,
                               with_extra("IRCA 8 U.S.C. 1324a (hire + 3 years)",
                                          extra)))
            candidates.append((add_months(t_term, 12 + extra), t_term,
                               with_extra("IRCA 8 U.S.C. 1324a "
                                          "(termination + 1 year)", extra)))
    if kind == "claim" and not candidates:
        return {"state": "incomplete",
                "warnings": ["claim record without claim_filed/claim_resolved"]}
    if not candidates:
        return {"state": "incomplete",
                "warnings": ["no applicable trigger event for this class"]}
    disp, trig, why = max(candidates, key=lambda c: (c[0], c[1]))
    return {"state": "dated", "disposition": disp, "trigger": trig,
            "rule": why, "warnings": warnings}


def print_schedule():
    print("REFERENCE RETENTION SCHEDULE (US-federal-flavoured; not legal "
          "advice; re-base per jurisdiction)")
    for s in SCHEDULE:
        print(f"\n- {s['record_class']}")
        print(f"    trigger     : {s['trigger']}")
        print(f"    base period : {s['months']} months"
              + (" after employment ends" if s["kind"] == "employment" else ""))
        print(f"    rule        : {s['rule']}")
        print(f"    disposition : {s['disposition']}")


def schedule_json():
    return [{k: (list(v) if isinstance(v, tuple) else v)
             for k, v in s.items()} for s in SCHEDULE]


def print_audit(results, args, as_of):
    by_group = defaultdict(list)
    for res in results:
        by_group[res["group"]].append(res)
    dated = [r for r in results if r["trigger_date"]]
    print("RETENTION AUDIT - eligibility only; nothing has been deleted")
    print(f"inventory           : {args.inventory}")
    print(f"as_of               : {as_of.isoformat()}")
    print(f"upcoming_days       : {args.upcoming_days}")
    print(f"max_retention_years : {args.max_retention_years}")
    print(f"records             : {len(results)}")
    for g in GROUP_ORDER:
        print(f"  {g:<14}: {len(by_group[g])}")
    print(f"  REVIEW flag   : {sum('REVIEW' in r['flags'] for r in results)}")
    print(f"  purge_blocked : "
          f"{sum('routine_purge_blocked' in r['flags'] for r in results)}")
    print(f"ordering_check: ok ({len(dated)} records)")
    for g in GROUP_ORDER:
        rows = sorted(by_group[g], key=lambda r: (r["disposition"] or "",
                                                  r["record_id"], r["line"]))
        if not rows:
            continue
        print(f"\n[{g}]")
        for r in rows:
            when = r["disposition"] or "-"
            if r["days_overdue"] is not None:
                when += f" ({r['days_overdue']} days overdue)"
            elif r["days_remaining"] is not None:
                when += f" ({r['days_remaining']} days remaining)"
            flags = f" flags={','.join(r['flags'])}" if r["flags"] else ""
            print(f"  {r['record_id'] or '(no id)'} line {r['line']} "
                  f"{r['record_class']} emp={r['employee_id'] or '-'} "
                  f"-> {when}{flags}")
            if r["governing_rule"]:
                print(f"      rule: {r['governing_rule']}")
            for w in r["warnings"]:
                print(f"      warning: {w}")


def write_json(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")
    except OSError as exc:
        raise InputError(f"cannot write JSON {path}: {exc.strerror}")
    print(f"\njson written: {path}")


def main(argv):
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(add_help=False)
    sub = parser.add_subparsers(dest="mode")
    p_sched = sub.add_parser("schedule", add_help=False)
    p_sched.add_argument("--json")
    p_audit = sub.add_parser("audit", add_help=False)
    p_audit.add_argument("--inventory", required=True)
    p_audit.add_argument("--as-of", required=True)
    p_audit.add_argument("--json")
    p_audit.add_argument("--upcoming-days", type=int, default=90)
    p_audit.add_argument("--max-retention-years", type=int, default=30)
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("usage error - run with --help", file=sys.stderr)
        return 2
    try:
        if args.mode == "schedule":
            print_schedule()
            if args.json:
                write_json(args.json, {"schedule": schedule_json()})
            return 0
        if args.mode != "audit":
            print("usage error - mode must be 'schedule' or 'audit'",
                  file=sys.stderr)
            return 2
        as_of = parse_date(args.as_of)
        if as_of is None:
            print(f"usage error - --as-of must be YYYY-MM-DD, got "
                  f"'{args.as_of}'", file=sys.stderr)
            return 2
        if args.upcoming_days < 0 or args.max_retention_years < 1:
            print("usage error - --upcoming-days must be >= 0 and "
                  "--max-retention-years >= 1", file=sys.stderr)
            return 2
        rows = validate(read_inventory(args.inventory))
        try:
            results = compute(rows, as_of, args.upcoming_days,
                              args.max_retention_years)
        except RuntimeError as exc:
            print(f"internal consistency failure: {exc}", file=sys.stderr)
            return 3
        print_audit(results, args, as_of)
        if args.json:
            counts = Counter(r["group"] for r in results)
            write_json(args.json, {
                "as_of": as_of.isoformat(), "inventory": args.inventory,
                "upcoming_days": args.upcoming_days,
                "max_retention_years": args.max_retention_years,
                "counts": {g: counts.get(g, 0) for g in GROUP_ORDER},
                "ordering_check": {"status": "ok", "records": sum(
                    1 for r in results if r["trigger_date"])},
                "records": sorted(results, key=lambda r: (r["line"],)),
                "note": "eligibility only - destruction requires human "
                        "approval and a destruction log"})
        return 0
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
