#!/usr/bin/env python3
"""benefits_admin.py - mechanical helpers for the benefits-administration SOP.

Stdlib only. Three subcommands cover the parts of benefits administration that are
computations rather than judgements: enrollment-window deadlines, eligibility
determination, and three-way reconciliation of elected vs billed records.

Usage:
  benefits_admin.py window --event 2026-10-01 --days 30 [--today 2026-10-19]
  benefits_admin.py eligibility --roster roster.csv [--min-hours 30] [--waiting-days 30]
  benefits_admin.py reconcile --roster roster.csv --carrier carrier.csv [--tolerance 0.01]

Roster CSV columns:  employee_id,name,start_date,hours_per_week,plan,deduction
Carrier CSV columns: employee_id,plan,deduction

Exit codes:
  0  success / no exceptions
  1  reconcile found exceptions (gate a carrier submission on this)
  2  usage or input error
"""

import argparse
import csv
import sys
from datetime import date, timedelta

BORDERLINE_HOURS = 5.0


def parse_date(value):
    try:
        return date.fromisoformat(value.strip())
    except (ValueError, AttributeError):
        raise ValueError("invalid date %r - expected YYYY-MM-DD" % (value,))


def parse_amount(value):
    if value is None:
        return 0.0
    text = str(value).strip().replace("$", "").replace(",", "")
    if text == "":
        return 0.0
    try:
        return float(text)
    except ValueError:
        raise ValueError("invalid amount %r" % (value,))


def read_csv(path, required):
    try:
        handle = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("%s is empty" % path)
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            raise ValueError("%s is missing column(s): %s" % (path, ", ".join(missing)))
        rows = []
        for row in reader:
            if not any((v or "").strip() for v in row.values()):
                continue
            rows.append({k: (v or "").strip() for k, v in row.items()})
        return rows


def cmd_window(args):
    event = parse_date(args.event)
    today = parse_date(args.today) if args.today else date.today()
    if args.days < 0:
        raise ValueError("--days must be non-negative")
    deadline = event + timedelta(days=args.days)
    remaining = (deadline - today).days

    if remaining > 0:
        status = "OPEN"
    elif remaining == 0:
        status = "CLOSES TODAY"
    else:
        status = "EXPIRED"

    print("Enrollment window")
    print("  event date       : %s" % event.isoformat())
    print("  window length    : %d days" % args.days)
    print("  hard deadline    : %s" % deadline.isoformat())
    print("  today            : %s" % today.isoformat())
    print("  days remaining   : %d" % remaining)
    print("  status           : %s" % status)
    print("  reminder dates   : T-7 %s | T-2 %s"
          % ((deadline - timedelta(days=7)).isoformat(),
             (deadline - timedelta(days=2)).isoformat()))
    if remaining < 0:
        print("  ACTION           : window expired - escalate to HR/legal with both dates;"
              " do not backdate the election")
    elif remaining <= 2:
        print("  ACTION           : inside 48h - chase the outstanding election now")
    return 0


def cmd_eligibility(args):
    today = parse_date(args.today) if args.today else date.today()
    rows = read_csv(args.roster, ["employee_id", "start_date", "hours_per_week"])

    results = []
    for row in rows:
        emp = row.get("employee_id", "")
        try:
            hours = parse_amount(row.get("hours_per_week"))
        except ValueError:
            results.append((emp, "INPUT_ERROR", "n/a", row.get("hours_per_week", ""), ""))
            continue
        try:
            start = parse_date(row.get("start_date", ""))
        except ValueError:
            results.append((emp, "INPUT_ERROR", "%.2f" % hours, row.get("start_date", ""), ""))
            continue

        eligible_from = start + timedelta(days=args.waiting_days)
        if hours < args.min_hours:
            status = "INELIGIBLE"
        elif today < eligible_from:
            status = "PENDING"
        else:
            status = "ELIGIBLE"
        borderline = "yes" if abs(hours - args.min_hours) <= BORDERLINE_HOURS else ""
        results.append((emp, status, "%.2f" % hours, eligible_from.isoformat(), borderline))

    width = max([len(r[0]) for r in results] + [len("employee_id")])
    print("%-*s  %-11s  %8s  %-12s  %s" % (width, "employee_id", "status", "hours",
                                            "eligible_from", "borderline"))
    print("-" * (width + 48))
    for emp, status, hours, eff, borderline in results:
        print("%-*s  %-11s  %8s  %-12s  %s" % (width, emp, status, hours, eff, borderline))

    counts = {}
    for r in results:
        counts[r[1]] = counts.get(r[1], 0) + 1
    print("")
    print("records: %d | %s" % (len(results), " | ".join(
        "%s=%d" % (k, counts[k]) for k in sorted(counts))))
    flagged = [r[0] for r in results if r[4] == "yes"]
    if flagged:
        print("borderline (within %.0f hours of the threshold, will drift): %s"
              % (BORDERLINE_HOURS, ", ".join(flagged)))
    return 0


def cmd_reconcile(args):
    roster = read_csv(args.roster, ["employee_id"])
    carrier = read_csv(args.carrier, ["employee_id"])

    elected = {}
    for row in roster:
        elected[row["employee_id"]] = row
    billed = {}
    for row in carrier:
        billed[row["employee_id"]] = row

    exceptions = []
    for emp, row in elected.items():
        plan = row.get("plan", "")
        if not plan:
            exceptions.append((emp, "NO_ELECTION", "roster row has no plan recorded"))
            continue
        if emp not in billed:
            exceptions.append((emp, "MISSING_FROM_CARRIER",
                               "elected %s but not on the carrier file" % plan))
            continue
        cplan = billed[emp].get("plan", "")
        if cplan != plan:
            exceptions.append((emp, "PLAN_MISMATCH",
                               "elected %s, carrier has %s" % (plan, cplan)))
        try:
            elected_amt = parse_amount(row.get("deduction"))
            billed_amt = parse_amount(billed[emp].get("deduction"))
        except ValueError:
            exceptions.append((emp, "INPUT_ERROR", "unparseable deduction amount"))
            continue
        if abs(elected_amt - billed_amt) > args.tolerance:
            exceptions.append((emp, "AMOUNT_MISMATCH",
                               "elected %.2f, carrier %.2f (delta %.2f)"
                               % (elected_amt, billed_amt, elected_amt - billed_amt)))

    for emp in billed:
        if emp not in elected:
            exceptions.append((emp, "EXTRA_ON_CARRIER",
                               "billed but not on the roster - possible departed employee"))

    print("Reconciliation: %d on roster, %d on carrier file, %d exception(s)"
          % (len(elected), len(billed), len(exceptions)))
    if exceptions:
        width = max(len(e[0]) for e in exceptions)
        for emp, kind, detail in exceptions:
            print("  %-*s  %-20s  %s" % (width, emp, kind, detail))
        print("")
        print("Every exception needs a named owner and a documented resolution"
              " before the carrier submission.")
        return 1
    print("Records agree within tolerance %.2f - safe to submit." % args.tolerance)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="benefits_admin.py",
        description="Mechanical helpers for the benefits-administration SOP.")
    sub = parser.add_subparsers(dest="command")

    p_window = sub.add_parser("window", help="compute an enrollment-window deadline")
    p_window.add_argument("--event", required=True, help="event/start date (YYYY-MM-DD)")
    p_window.add_argument("--days", type=int, required=True, help="window length in days")
    p_window.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    p_window.set_defaults(func=cmd_window)

    p_elig = sub.add_parser("eligibility", help="determine eligibility from a roster")
    p_elig.add_argument("--roster", required=True, help="roster CSV path")
    p_elig.add_argument("--min-hours", type=float, default=30.0,
                        help="weekly hours threshold (default 30)")
    p_elig.add_argument("--waiting-days", type=int, default=30,
                        help="waiting period in days from start date (default 30)")
    p_elig.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    p_elig.set_defaults(func=cmd_eligibility)

    p_rec = sub.add_parser("reconcile", help="diff elected vs billed records")
    p_rec.add_argument("--roster", required=True, help="roster CSV path (elected)")
    p_rec.add_argument("--carrier", required=True, help="carrier CSV path (billed)")
    p_rec.add_argument("--tolerance", type=float, default=0.01,
                       help="amount tolerance in currency units (default 0.01)")
    p_rec.set_defaults(func=cmd_reconcile)
    return parser


def main(argv):
    parser = build_parser()
    if not argv:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
