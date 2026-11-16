#!/usr/bin/env python3
"""
workforce_metrics.py - workforce metrics report for a period from a roster CSV.

Usage:
    python3 workforce_metrics.py --roster roster.csv \\
        --period-start 2026-01-01 --period-end 2026-12-31 \\
        [--group-by department] [--replacement-cost-pct 0.5] [--json report.json]
    python3 workforce_metrics.py --help

Roster columns (header row required, extra columns ignored):
    employee_id, name, department, title, manager_id, hire_date,
    termination_date, termination_type, regretted, salary,
    employment_type, location

    hire_date / termination_date  ISO YYYY-MM-DD; empty termination_date = active
    termination_type              voluntary | involuntary | retire | end_of_contract
    regretted                     y | n (only meaningful for leavers)
    salary                        annual salary, numeric (commas allowed)

Definitions:
    headcount_start   hired before period_start and not terminated before it
    headcount_end     hired on/before period_end and not terminated on/before it
    separations       termination_date within [period_start, period_end]
    new_hires         hire_date within [period_start, period_end]
    average headcount (headcount_start + headcount_end) / 2
    turnover rate     separations / average headcount * 100            (SHRM)
    retention rate    employees on the roster for the whole period
                      / headcount_start * 100                          (SHRM)
    regrettable rate  regretted separations / average headcount * 100
    tenure            years from hire_date to period_end, active employees only
    span of control   active direct reports per manager_id (> 8 flagged)
    turnover cost     sum(annual salary of leavers) * replacement-cost-pct

Rows with a missing/unparseable hire_date, an unparseable termination_date,
a termination before hire, or a duplicate employee_id (2nd+ occurrence) are
EXCLUDED from metrics and listed under data-quality issues. Rows with a missing
manager_id or a blank/non-numeric salary are kept but flagged.

Any ratio with a zero denominator is reported as "n/a" with a warning.

Exit codes: 0 success, 1 unreadable file, 2 bad arguments / missing header.
"""
import argparse
import csv
import json
import sys
from collections import Counter
from datetime import date

REQUIRED = [
    "employee_id", "name", "department", "title", "manager_id", "hire_date",
    "termination_date", "termination_type", "regretted", "salary",
    "employment_type", "location",
]
TERM_TYPES = {"voluntary", "involuntary", "retire", "end_of_contract"}
SPAN_LIMIT = 8
NA = "n/a"


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(value)


def parse_salary(value):
    raw = (value or "").strip().replace(",", "")
    if not raw:
        return None, "blank salary"
    try:
        amount = float(raw)
    except ValueError:
        return None, f"non-numeric salary {value.strip()!r}"
    if amount != amount or amount in (float("inf"), float("-inf")) or amount < 0:
        return None, f"invalid salary {value.strip()!r}"
    return amount, None


def ratio(num, den, label, warnings):
    """num / den * 100 rounded, or 'n/a' (with a warning) when den <= 0."""
    if den is None or den <= 0:
        warnings.append(f"{label}: denominator is {den}; reported as n/a")
        return NA
    return round(num / den * 100, 2)


def median(values):
    s = sorted(values)
    n = len(s)
    if n == 0:
        return None
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def load_roster(path, group_by):
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            header = [h.strip() for h in (reader.fieldnames or [])]
            reader.fieldnames = header
            rows = []
            for row in reader:
                clean = {k: (v if isinstance(v, str) else "") for k, v in row.items() if k is not None}
                clean["__short__"] = any(v is None for v in row.values())
                clean["__long__"] = None in row
                rows.append(clean)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        print(f"error: cannot read roster {path}: {exc}", file=sys.stderr)
        sys.exit(1)
    if not header:
        print(f"error: roster {path} is empty (no header row)", file=sys.stderr)
        sys.exit(2)
    missing = [c for c in REQUIRED if c not in header]
    if missing:
        print(f"error: roster {path} missing required header(s): {', '.join(missing)}",
              file=sys.stderr)
        sys.exit(2)
    if group_by not in header:
        print(f"error: --group-by column {group_by!r} not in roster header", file=sys.stderr)
        sys.exit(2)
    return rows


def compute(rows, start, end, group_by, cost_pct):
    issues = []      # data-quality problems, one dict per problem
    warnings = []    # n/a and other computation warnings
    seen = set()
    people = []

    for lineno, row in enumerate(rows, start=2):  # header is line 1
        eid = row.get("employee_id", "").strip()
        tag = {"line": lineno, "employee_id": eid}

        def flag(problem, excluded):
            issues.append({**tag, "problem": problem, "excluded": excluded})

        if row.get("__short__"):
            flag("row has fewer columns than the header (missing values treated as blank)", False)
        if row.get("__long__"):
            flag("row has more columns than the header (extra values ignored)", False)
        if not eid:
            flag("missing employee_id", True)
            continue
        if eid in seen:
            flag("duplicate employee_id (first occurrence kept)", True)
            continue
        seen.add(eid)

        try:
            hire = parse_date(row.get("hire_date"))
        except ValueError as exc:
            flag(f"unparseable hire_date {exc.args[0]!r}", True)
            continue
        if hire is None:
            flag("missing hire_date", True)
            continue
        try:
            term = parse_date(row.get("termination_date"))
        except ValueError as exc:
            flag(f"unparseable termination_date {exc.args[0]!r}", True)
            continue
        if term is not None and term < hire:
            flag(f"termination_date {term} before hire_date {hire}", True)
            continue

        manager = row.get("manager_id", "").strip()
        if not manager:
            flag("missing manager_id (expected only for top of org)", False)
        salary, sal_err = parse_salary(row.get("salary"))
        if sal_err:
            flag(sal_err, False)

        ttype = row.get("termination_type", "").strip().lower()
        regretted = row.get("regretted", "").strip().lower()
        if term is not None:
            if ttype not in TERM_TYPES:
                flag(f"leaver with unknown termination_type {ttype or '(blank)'!r}", False)
                ttype = "unknown"
            if regretted not in ("y", "n"):
                flag(f"leaver with regretted not y/n ({regretted or 'blank'})", False)
                regretted = "unknown"

        people.append({
            "id": eid, "hire": hire, "term": term, "manager": manager,
            "salary": salary, "ttype": ttype, "regretted": regretted,
            "group": row.get(group_by, "").strip() or "(blank)",
        })

    at_start = [p for p in people if p["hire"] < start and (p["term"] is None or p["term"] >= start)]
    at_end = [p for p in people if p["hire"] <= end and (p["term"] is None or p["term"] > end)]
    leavers = [p for p in people if p["term"] is not None and start <= p["term"] <= end]
    hires = [p for p in people if start <= p["hire"] <= end]
    stayed = [p for p in at_start if p["term"] is None or p["term"] > end]

    hc_start, hc_end = len(at_start), len(at_end)
    avg_hc = (hc_start + hc_end) / 2
    type_counts = Counter(p["ttype"] for p in leavers)
    regretted_n = sum(1 for p in leavers if p["regretted"] == "y")

    # Per-group turnover.
    g_start, g_end, g_sep = Counter(), Counter(), Counter()
    for p in at_start:
        g_start[p["group"]] += 1
    for p in at_end:
        g_end[p["group"]] += 1
    for p in leavers:
        g_sep[p["group"]] += 1
    groups = []
    for g in sorted(set(g_start) | set(g_end) | set(g_sep)):
        g_avg = (g_start[g] + g_end[g]) / 2
        groups.append({
            group_by: g, "headcount_start": g_start[g], "headcount_end": g_end[g],
            "average_headcount": g_avg, "separations": g_sep[g],
            "turnover_rate_pct": ratio(g_sep[g], g_avg, f"turnover rate [{group_by}={g}]", warnings),
        })

    # Tenure of active employees at period end.
    tenures = [round((end - p["hire"]).days / 365.25, 2) for p in at_end]
    if not tenures:
        warnings.append("tenure: no active employees at period end; reported as n/a")

    # Span of control among active employees at period end.
    active_ids = {p["id"] for p in at_end}
    reports = Counter(p["manager"] for p in at_end if p["manager"])
    span = []
    for mgr, n in sorted(reports.items(), key=lambda kv: (-kv[1], kv[0])):
        span.append({"manager_id": mgr, "direct_reports": n,
                     "flag": "OVER_LIMIT" if n > SPAN_LIMIT else "",
                     "manager_active": mgr in active_ids})
        if mgr not in active_ids:
            warnings.append(f"span of control: manager_id {mgr} is not an active employee at period end")
    span_values = [s["direct_reports"] for s in span]

    # Turnover cost.
    priced = [p["salary"] for p in leavers if p["salary"] is not None]
    unpriced = len(leavers) - len(priced)
    if unpriced:
        warnings.append(f"turnover cost: {unpriced} leaver(s) without a valid salary excluded; cost is understated")
    leaver_salary = sum(priced)

    metrics = {
        "headcount_start": hc_start,
        "headcount_end": hc_end,
        "average_headcount": avg_hc,
        "new_hires": len(hires),
        "separations": len(leavers),
        "net_headcount_change": hc_end - hc_start,
        "turnover_rate_pct": ratio(len(leavers), avg_hc, "turnover rate", warnings),
        "voluntary_separations": type_counts.get("voluntary", 0),
        "involuntary_separations": type_counts.get("involuntary", 0),
        "retire_separations": type_counts.get("retire", 0),
        "end_of_contract_separations": type_counts.get("end_of_contract", 0),
        "unknown_type_separations": type_counts.get("unknown", 0),
        "voluntary_turnover_rate_pct": ratio(type_counts.get("voluntary", 0), avg_hc, "voluntary turnover rate", warnings),
        "involuntary_turnover_rate_pct": ratio(type_counts.get("involuntary", 0), avg_hc, "involuntary turnover rate", warnings),
        "voluntary_share_of_separations_pct": ratio(type_counts.get("voluntary", 0), len(leavers), "voluntary share of separations", warnings),
        "regretted_separations": regretted_n,
        "regrettable_attrition_rate_pct": ratio(regretted_n, avg_hc, "regrettable attrition rate", warnings),
        "retained_full_period": len(stayed),
        "retention_rate_pct": ratio(len(stayed), hc_start, "retention rate", warnings),
        "median_tenure_years": round(median(tenures), 2) if tenures else NA,
        "mean_tenure_years": round(sum(tenures) / len(tenures), 2) if tenures else NA,
        "managers": len(span),
        "mean_span_of_control": round(sum(span_values) / len(span_values), 2) if span_values else NA,
        "managers_over_span_limit": sum(1 for s in span if s["flag"]),
        "leaver_salary_total": round(leaver_salary, 2),
        "replacement_cost_pct": cost_pct,
        "estimated_turnover_cost": round(leaver_salary * cost_pct, 2),
    }
    if not span_values:
        warnings.append("span of control: no active employee has a manager_id; reported as n/a")
    if hc_end != hc_start + len(hires) - len(leavers):  # should never trigger
        warnings.append("headcount identity end = start + hires - separations does not hold")

    return {
        "period_start": start.isoformat(), "period_end": end.isoformat(),
        "group_by": group_by, "rows_read": len(rows), "rows_used": len(people),
        "metrics": metrics, "by_group": groups, "span_of_control": span,
        "data_quality_issues": issues, "warnings": warnings,
    }


def fmt(v, suffix=""):
    return NA if v == NA else f"{v}{suffix}"


def print_report(r):
    m = r["metrics"]
    print(f"WORKFORCE METRICS  {r['period_start']} -> {r['period_end']}")
    print(f"rows read: {r['rows_read']}  rows used: {r['rows_used']}  "
          f"excluded: {sum(1 for i in r['data_quality_issues'] if i['excluded'])}")
    print()
    print("HEADCOUNT")
    print(f"  start {m['headcount_start']}  end {m['headcount_end']}  average {m['average_headcount']}")
    print(f"  new hires {m['new_hires']}  separations {m['separations']}  net change {m['net_headcount_change']:+d}")
    print()
    print("TURNOVER & RETENTION")
    print(f"  turnover rate            {fmt(m['turnover_rate_pct'], '%')}")
    print(f"  voluntary / involuntary  {m['voluntary_separations']} / {m['involuntary_separations']}"
          f"  (rates {fmt(m['voluntary_turnover_rate_pct'], '%')} / {fmt(m['involuntary_turnover_rate_pct'], '%')})")
    print(f"  retire / end_of_contract / unknown  {m['retire_separations']} / "
          f"{m['end_of_contract_separations']} / {m['unknown_type_separations']}")
    print(f"  regrettable attrition    {m['regretted_separations']}  ({fmt(m['regrettable_attrition_rate_pct'], '%')})")
    print(f"  retention rate           {fmt(m['retention_rate_pct'], '%')}  ({m['retained_full_period']} of {m['headcount_start']})")
    print(f"  tenure (active) median {fmt(m['median_tenure_years'], 'y')}  mean {fmt(m['mean_tenure_years'], 'y')}")
    print(f"  estimated turnover cost  {m['estimated_turnover_cost']:.2f}"
          f"  (leaver salaries {m['leaver_salary_total']:.2f} x {m['replacement_cost_pct']})")
    print()
    print(f"TURNOVER BY {r['group_by'].upper()}")
    if not r["by_group"]:
        print("  (none)")
    for g in r["by_group"]:
        print(f"  {g[r['group_by']]:<24} start {g['headcount_start']:>4}  end {g['headcount_end']:>4}  "
              f"sep {g['separations']:>3}  turnover {fmt(g['turnover_rate_pct'], '%')}")
    print()
    print(f"SPAN OF CONTROL  managers {m['managers']}  mean {fmt(m['mean_span_of_control'])}  "
          f"over {SPAN_LIMIT}: {m['managers_over_span_limit']}")
    for s in r["span_of_control"]:
        if s["flag"]:
            print(f"  {s['manager_id']}: {s['direct_reports']} direct reports  OVER_LIMIT")
    print()
    print(f"DATA QUALITY ISSUES ({len(r['data_quality_issues'])})")
    for i in r["data_quality_issues"]:
        print(f"  line {i['line']} [{i['employee_id'] or '-'}] {i['problem']}"
              f"{'  (EXCLUDED)' if i['excluded'] else ''}")
    print()
    print(f"WARNINGS ({len(r['warnings'])})")
    for w in r["warnings"]:
        print(f"  {w}")


def iso_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an ISO date (YYYY-MM-DD): {value!r}")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--roster", required=True)
    ap.add_argument("--period-start", required=True, type=iso_date)
    ap.add_argument("--period-end", required=True, type=iso_date)
    ap.add_argument("--group-by", default="department")
    ap.add_argument("--replacement-cost-pct", type=float, default=0.5)
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    if args.period_end < args.period_start:
        print("error: --period-end is before --period-start", file=sys.stderr)
        return 2
    pct = args.replacement_cost_pct
    if pct != pct or pct < 0 or pct == float("inf"):
        print("error: --replacement-cost-pct must be a finite number >= 0", file=sys.stderr)
        return 2

    rows = load_roster(args.roster, args.group_by)
    report = compute(rows, args.period_start, args.period_end, args.group_by, pct)
    print_report(report)
    if args.json:
        try:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, sort_keys=True)
                fh.write("\n")
        except OSError as exc:
            print(f"error: cannot write {args.json}: {exc}", file=sys.stderr)
            return 1
        print(f"\nJSON report written to {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
