#!/usr/bin/env python3
"""Leave accrual, balance, statutory-entitlement and eligibility calculator.

A deterministic, stdlib-only helper for HR teams working without an HRIS.
Three subcommands:

    accrual      Accrue paid leave from hours worked ("1 hour per N hours
                 worked"), apply a carryover cap and an optional annual grant,
                 compute balance = accrued + carried_over - used, and reject
                 a request that would drive the balance negative.
    entitlement  Compute statutory (FMLA-style) usage within a 12-month
                 period: weeks entitled, used, remaining. Accepts continuous
                 leave (start + expected end) and intermittent leave (dated
                 increments in minutes).
    decide       Classify a statutory leave request as ELIGIBLE,
                 NEEDS_CERTIFICATION, INSUFFICIENT_BALANCE or NOT_ELIGIBLE
                 from explicit inputs only. Nothing is inferred or guessed.

Exit codes:
    0  OK / approve (ELIGIBLE, or balance sufficient)
    2  blocked / deny (NOT_ELIGIBLE, INSUFFICIENT_BALANCE,
       NEEDS_CERTIFICATION, or a negative balance)
    1  usage error (bad flags, malformed dates or numbers)

Thresholds default to the US FMLA figures (50 employees in 20+ workweeks;
12 months and 1,250 hours; 12 weeks, 26 for military caregiver). Override
them for other regimes. This is arithmetic, not legal advice.

Examples:
    python3 scripts/leave_accrual.py accrual --hours-worked 1040 \\
        --carried-over 30 --carryover-cap 48 --used 12 --request-hours 8
    python3 scripts/leave_accrual.py entitlement --period-start 2026-01-01 \\
        --continuous 2026-03-02:2026-03-27 --intermittent 2026-05-04:90 --json
    python3 scripts/leave_accrual.py decide --employer-size 120 \\
        --employer-workweeks 52 --months-employed 14 --hours-prior-year 1600 \\
        --requested-weeks 4 --weeks-remaining 12 --certification received
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_BLOCKED = 2

WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
Q2 = Decimal("0.01")
Q4 = Decimal("0.0001")


class UsageError(Exception):
    """Raised for malformed input; mapped to exit code 1."""


# --------------------------------------------------------------------------- parsing


def parse_decimal(text: str) -> Decimal:
    try:
        value = Decimal(str(text).strip())
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from exc
    if not value.is_finite():
        raise argparse.ArgumentTypeError(f"not a finite number: {text!r}")
    return value


def non_negative(text: str) -> Decimal:
    value = parse_decimal(text)
    if value < 0:
        raise argparse.ArgumentTypeError(f"must be >= 0: {text!r}")
    return value


def positive(text: str) -> Decimal:
    value = parse_decimal(text)
    if value <= 0:
        raise argparse.ArgumentTypeError(f"must be > 0: {text!r}")
    return value


def parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text.strip())
    except ValueError as exc:
        raise UsageError(f"bad date {text!r}: expected YYYY-MM-DD") from exc


def iso_date(text: str) -> date:
    try:
        return parse_date(text)
    except UsageError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def parse_range(text: str) -> tuple[date, date]:
    parts = text.split(":")
    if len(parts) != 2:
        raise UsageError(f"bad --continuous {text!r}: expected START:END")
    start, end = parse_date(parts[0]), parse_date(parts[1])
    if end < start:
        raise UsageError(f"bad --continuous {text!r}: END is before START")
    return start, end


def parse_increment(day: str, minutes: str, origin: str) -> tuple[date, int]:
    when = parse_date(day)
    try:
        mins = int(str(minutes).strip())
    except ValueError as exc:
        raise UsageError(f"bad minutes in {origin}: {minutes!r}") from exc
    if mins <= 0:
        raise UsageError(f"minutes must be > 0 in {origin}: {minutes!r}")
    return when, mins


def read_increments_file(path: Path) -> list[tuple[date, int]]:
    if not path.is_file():
        raise UsageError(f"intermittent file not found: {path}")
    rows: list[tuple[date, int]] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for lineno, row in enumerate(csv.DictReader(handle), start=2):
            if "date" not in row or "minutes" not in row:
                raise UsageError(f"{path}: header must contain 'date,minutes'")
            rows.append(parse_increment(row["date"], row["minutes"], f"{path}:{lineno}"))
    return rows


def parse_workdays(text: str) -> set[int]:
    days = {d.strip().lower() for d in text.split(",") if d.strip()}
    unknown = days - WEEKDAYS.keys()
    if not days or unknown:
        raise UsageError(f"bad --workdays {text!r}: use e.g. mon,tue,wed,thu,fri")
    return {WEEKDAYS[d] for d in days}


def add_one_year(start: date) -> date:
    try:
        return start.replace(year=start.year + 1)
    except ValueError:  # 29 Feb -> 1 Mar
        return start.replace(year=start.year + 1, month=3, day=1)


# --------------------------------------------------------------------------- core logic


def compute_accrual(
    hours_worked: Decimal,
    rate_per: Decimal,
    carried_over: Decimal,
    carryover_cap: Decimal | None,
    annual_grant: Decimal,
    used: Decimal,
    request_hours: Decimal,
) -> dict[str, Any]:
    accrued = (hours_worked / rate_per).quantize(Q4, rounding=ROUND_HALF_UP)
    carry_applied = carried_over if carryover_cap is None else min(carried_over, carryover_cap)
    available = accrued + annual_grant + carry_applied
    balance = available - used
    after_request = balance - request_hours

    if balance < 0:
        status, reason = "NEGATIVE_BALANCE", "recorded usage already exceeds available leave"
    elif after_request < 0:
        status = "INSUFFICIENT_BALANCE"
        reason = f"request of {request_hours}h exceeds balance of {balance.quantize(Q2)}h"
    else:
        status, reason = "OK", "request fits within balance"

    return {
        "mode": "accrual",
        "status": status,
        "reason": reason,
        "hours_worked": str(hours_worked),
        "accrual_rule": f"1 hour per {rate_per} hours worked",
        "accrued_hours": str(accrued.quantize(Q2)),
        "annual_grant_hours": str(annual_grant),
        "carried_over_input": str(carried_over),
        "carryover_cap": None if carryover_cap is None else str(carryover_cap),
        "carried_over_applied": str(carry_applied),
        "forfeited_carryover": str(carried_over - carry_applied),
        "used_hours": str(used),
        "balance_hours": str(balance.quantize(Q2)),
        "requested_hours": str(request_hours),
        "balance_after_request": str(after_request.quantize(Q2)),
    }


def compute_entitlement(
    entitled_weeks: Decimal,
    period_start: date,
    continuous: list[tuple[date, date]],
    increments: list[tuple[date, int]],
    workdays: set[int],
    hours_per_week: Decimal,
    increment_minutes: int,
    requested_weeks: Decimal,
) -> dict[str, Any]:
    period_end = add_one_year(period_start) - timedelta(days=1)

    segments: list[dict[str, Any]] = []
    continuous_days = 0
    for start, end in continuous:
        lo, hi = max(start, period_start), min(end, period_end)
        days = 0
        day = lo
        while day <= hi:
            if day.weekday() in workdays:
                days += 1
            day += timedelta(days=1)
        continuous_days += days
        segments.append({"start": start.isoformat(), "end": end.isoformat(),
                         "scheduled_workdays_in_period": days})
    continuous_weeks = Decimal(continuous_days) / Decimal(len(workdays))

    raw_minutes = 0
    charged_minutes = 0
    excluded = 0
    for when, mins in increments:
        if not period_start <= when <= period_end:
            excluded += 1
            continue
        raw_minutes += mins
        # round each absence up to the tracking increment
        charged_minutes += -(-mins // increment_minutes) * increment_minutes
    intermittent_weeks = Decimal(charged_minutes) / (hours_per_week * 60)

    used = continuous_weeks + intermittent_weeks
    remaining = entitled_weeks - used
    after_request = remaining - requested_weeks
    if remaining < 0:
        status, reason = "EXHAUSTED", "usage exceeds entitlement for this period"
    elif after_request < 0:
        status = "INSUFFICIENT_BALANCE"
        reason = f"request of {requested_weeks} weeks exceeds {remaining.quantize(Q2)} remaining"
    else:
        status, reason = "OK", "entitlement remaining covers the request"

    return {
        "mode": "entitlement",
        "status": status,
        "reason": reason,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "weeks_entitled": str(entitled_weeks),
        "continuous_segments": segments,
        "continuous_weeks_used": str(continuous_weeks.quantize(Q4)),
        "intermittent_increments_counted": len(increments) - excluded,
        "intermittent_increments_outside_period": excluded,
        "intermittent_minutes_raw": raw_minutes,
        "intermittent_minutes_charged": charged_minutes,
        "tracking_increment_minutes": increment_minutes,
        "intermittent_weeks_used": str(intermittent_weeks.quantize(Q4)),
        "weeks_used": str(used.quantize(Q4)),
        "weeks_remaining": str(remaining.quantize(Q4)),
        "requested_weeks": str(requested_weeks),
        "weeks_remaining_after_request": str(after_request.quantize(Q4)),
    }


def decide(
    employer_size: int,
    employer_workweeks: int,
    months_employed: Decimal,
    hours_prior_year: Decimal,
    requested_weeks: Decimal,
    weeks_remaining: Decimal,
    certification: str,
    min_employees: int,
    min_workweeks: int,
    min_months: Decimal,
    min_hours: Decimal,
) -> dict[str, Any]:
    failed: list[str] = []
    if employer_size < min_employees:
        failed.append(f"employer has {employer_size} employees (< {min_employees})")
    if employer_workweeks < min_workweeks:
        failed.append(f"employer headcount met in {employer_workweeks} workweeks (< {min_workweeks})")
    if months_employed < min_months:
        failed.append(f"employee has {months_employed} months of service (< {min_months})")
    if hours_prior_year < min_hours:
        failed.append(f"employee worked {hours_prior_year} hours in prior 12 months (< {min_hours})")

    if failed:
        decision = "NOT_ELIGIBLE"
        reason = "; ".join(failed) + ". Check state/local leave, PTO and accommodation before denying."
    elif requested_weeks > weeks_remaining:
        decision = "INSUFFICIENT_BALANCE"
        reason = f"requested {requested_weeks} weeks > {weeks_remaining} remaining in the period"
    elif certification == "pending":
        decision = "NEEDS_CERTIFICATION"
        reason = "eligible; designation waits on certification (allow at least 15 calendar days)"
    else:
        decision = "ELIGIBLE"
        reason = "all eligibility tests met; entitlement covers the request"

    return {
        "mode": "decide",
        "decision": decision,
        "reason": reason,
        "failed_tests": failed,
        "inputs": {
            "employer_size": employer_size,
            "employer_workweeks": employer_workweeks,
            "months_employed": str(months_employed),
            "hours_prior_year": str(hours_prior_year),
            "requested_weeks": str(requested_weeks),
            "weeks_remaining": str(weeks_remaining),
            "certification": certification,
        },
        "thresholds": {
            "min_employees": min_employees,
            "min_workweeks": min_workweeks,
            "min_months": str(min_months),
            "min_hours": str(min_hours),
        },
    }


# --------------------------------------------------------------------------- output


def exit_code_for(result: dict[str, Any]) -> int:
    verdict = result.get("decision", result.get("status"))
    return EXIT_OK if verdict in ("OK", "ELIGIBLE") else EXIT_BLOCKED


def render_table(result: dict[str, Any]) -> str:
    rows: list[tuple[str, str]] = []
    for key, value in result.items():
        if isinstance(value, dict):
            rows.extend((f"{key}.{k}", str(v)) for k, v in value.items())
        elif isinstance(value, list):
            if not value:
                rows.append((key, "-"))
            for i, item in enumerate(value):
                text = ", ".join(f"{k}={v}" for k, v in item.items()) if isinstance(item, dict) else str(item)
                rows.append((f"{key}[{i}]", text))
        else:
            rows.append((key, "-" if value is None else str(value)))
    width = max(len(k) for k, _ in rows)
    lines = [f"{'field'.ljust(width)}  value", f"{'-' * width}  {'-' * 5}"]
    lines += [f"{k.ljust(width)}  {v}" for k, v in rows]
    return "\n".join(lines)


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="leave_accrual.py",
        description="Deterministic leave accrual, balance, statutory-entitlement and "
                    "eligibility calculator. Exit 0 = OK/approve, 2 = blocked/deny, 1 = usage error.",
        epilog="Thresholds default to US FMLA figures; override for other regimes. Not legal advice.",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a human table")
    sub = parser.add_subparsers(dest="command", required=True, metavar="{accrual,entitlement,decide}")

    acc = sub.add_parser("accrual", help="accrue paid leave from hours worked and check a request",
                         description="balance = accrued + annual_grant + min(carried_over, cap) - used")
    acc.add_argument("--hours-worked", type=non_negative, required=True,
                     help="hours actually worked in the accrual period (not calendar time)")
    acc.add_argument("--rate-per", type=positive, default=Decimal(30),
                     help="accrue 1 hour per N hours worked (default: 30)")
    acc.add_argument("--carried-over", type=non_negative, default=Decimal(0),
                     help="unused hours brought forward from the prior period (default: 0)")
    acc.add_argument("--carryover-cap", type=non_negative, default=None,
                     help="maximum hours that may carry over; excess is reported as forfeited (default: no cap)")
    acc.add_argument("--annual-grant", type=non_negative, default=Decimal(0),
                     help="hours front-loaded at the start of the period (default: 0)")
    acc.add_argument("--used", type=non_negative, default=Decimal(0),
                     help="hours already taken this period (default: 0)")
    acc.add_argument("--request-hours", type=non_negative, default=Decimal(0),
                     help="hours requested now; exit 2 if it would drive the balance negative (default: 0)")
    acc.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                     help="emit JSON instead of a human table")

    ent = sub.add_parser("entitlement", help="statutory weeks entitled / used / remaining in a 12-month period")
    ent.add_argument("--period-start", type=iso_date, required=True,
                     help="first day of the 12-month leave period, YYYY-MM-DD (employer's chosen method)")
    ent.add_argument("--entitled-weeks", type=positive, default=Decimal(12),
                     help="weeks entitled per 12-month period (default: 12; use 26 for military caregiver)")
    ent.add_argument("--continuous", action="append", default=[], metavar="START:END",
                     help="continuous leave block, YYYY-MM-DD:YYYY-MM-DD inclusive (expected end if ongoing); repeatable")
    ent.add_argument("--intermittent", action="append", default=[], metavar="DATE:MINUTES",
                     help="one intermittent absence, e.g. 2026-05-04:90; repeatable")
    ent.add_argument("--intermittent-file", type=Path, default=None,
                     help="CSV with header 'date,minutes' listing intermittent absences")
    ent.add_argument("--workdays", default="mon,tue,wed,thu,fri",
                     help="employee's scheduled workdays, comma-separated (default: mon,tue,wed,thu,fri); "
                          "continuous weeks = scheduled workdays on leave / workdays per week")
    ent.add_argument("--hours-per-week", type=positive, default=Decimal(40),
                     help="employee's normal weekly hours, used to convert intermittent minutes to weeks (default: 40)")
    ent.add_argument("--increment-minutes", type=int, default=15,
                     help="tracking increment; each absence is rounded up to it (default: 15; use 1 for to-the-minute)")
    ent.add_argument("--requested-weeks", type=non_negative, default=Decimal(0),
                     help="additional weeks requested now; exit 2 if they exceed what remains (default: 0)")
    ent.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                     help="emit JSON instead of a human table")

    dec = sub.add_parser("decide", help="ELIGIBLE / NEEDS_CERTIFICATION / INSUFFICIENT_BALANCE / NOT_ELIGIBLE",
                         description="Every employee/employer fact is a required flag; nothing is inferred.")
    dec.add_argument("--employer-size", type=int, required=True,
                     help="number of employees on payroll")
    dec.add_argument("--employer-workweeks", type=int, required=True,
                     help="workweeks in the current or prior calendar year the headcount threshold was met")
    dec.add_argument("--months-employed", type=non_negative, required=True,
                     help="total months of service with the employer")
    dec.add_argument("--hours-prior-year", type=non_negative, required=True,
                     help="hours actually worked in the 12 months before the leave starts")
    dec.add_argument("--requested-weeks", type=non_negative, required=True,
                     help="weeks of statutory leave requested")
    dec.add_argument("--weeks-remaining", type=non_negative, required=True,
                     help="weeks remaining in the period (take from the 'entitlement' subcommand)")
    dec.add_argument("--certification", choices=("received", "pending", "not-required"), required=True,
                     help="medical/supporting certification status")
    dec.add_argument("--min-employees", type=int, default=50, help="employer-coverage headcount (default: 50)")
    dec.add_argument("--min-workweeks", type=int, default=20, help="workweeks at that headcount (default: 20)")
    dec.add_argument("--min-months", type=non_negative, default=Decimal(12), help="service months (default: 12)")
    dec.add_argument("--min-hours", type=non_negative, default=Decimal(1250),
                     help="hours worked in prior 12 months (default: 1250)")
    dec.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                     help="emit JSON instead of a human table")
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "accrual":
        return compute_accrual(args.hours_worked, args.rate_per, args.carried_over, args.carryover_cap,
                               args.annual_grant, args.used, args.request_hours)
    if args.command == "entitlement":
        if args.increment_minutes < 1 or args.increment_minutes > 60:
            raise UsageError("--increment-minutes must be between 1 and 60")
        increments = [parse_increment(*item.rsplit(":", 1), "--intermittent")
                      if ":" in item else parse_increment(item, "", "--intermittent")
                      for item in args.intermittent]
        if args.intermittent_file is not None:
            increments += read_increments_file(args.intermittent_file)
        return compute_entitlement(args.entitled_weeks, args.period_start,
                                   [parse_range(r) for r in args.continuous], increments,
                                   parse_workdays(args.workdays), args.hours_per_week,
                                   args.increment_minutes, args.requested_weeks)
    for name in ("employer_size", "employer_workweeks", "min_employees", "min_workweeks"):
        if getattr(args, name) < 0:
            raise UsageError(f"--{name.replace('_', '-')} must be >= 0")
    return decide(args.employer_size, args.employer_workweeks, args.months_employed,
                  args.hours_prior_year, args.requested_weeks, args.weeks_remaining,
                  args.certification, args.min_employees, args.min_workweeks,
                  args.min_months, args.min_hours)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits 2 on bad usage; remap to 1
        return EXIT_OK if exc.code == 0 else EXIT_USAGE
    try:
        result = run(args)
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    print(json.dumps(result, indent=2) if args.json else render_table(result))
    return exit_code_for(result)


if __name__ == "__main__":
    sys.exit(main())
