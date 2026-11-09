#!/usr/bin/env python3
"""i9_tracker.py — compute US Form I-9 federal clocks for one employee.

Deterministic, stdlib-only, no network. Computes:

  * Section 1 deadline   — the first day of work for pay (hire date).
  * Section 2 deadline   — 3 business days (Mon-Fri, minus --holidays) after the
                           hire date; the hire date itself if the job lasts
                           fewer than 3 business days (--job-duration-days).
  * Reverification       — the EARLIER of the Section 1 employment-authorization
                           expiry and the List A/C document expiry, plus the
                           90-day advance-warning date. Not required for US
                           citizens, noncitizen nationals, LPRs with a Form
                           I-551, or a document with no expiration date.
  * Rehire               — Supplement B allowed within 3 years of the original
                           Form I-9; otherwise a new Form I-9 is required.
  * Retention            — after employment ends, the LATER of (end + 1 year)
                           and (hire + 3 years).

Statuses: OVERDUE, DUE_TODAY, DUE_IN_<N>_DAYS, COMPLETE, BLOCKED,
NO_REVERIFICATION_REQUIRED. Retention reports RETAIN / RETAIN_WHILE_EMPLOYED /
DESTRUCTION_PERMITTED (informational, never affects the exit code).

Exit codes: 0 = every clock satisfied or not yet due; 2 = at least one clock
OVERDUE or BLOCKED; 1 = usage error.

Example:
  python3 scripts/i9_tracker.py --hire-date 2026-11-02 --today 2026-11-04 \\
      --section1-completed 2026-11-02 --citizenship-status alien_authorized \\
      --auth-expiry 2027-06-30 --doc-list A --doc-expiry 2027-05-31 --json

This tool computes dates; it is not legal advice. Confirm current rules and
form edition at https://www.uscis.gov/i-9.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import NoReturn

SECTION2_BUSINESS_DAYS = 3
SHORT_JOB_THRESHOLD_DAYS = 3
ADVANCE_WARNING_DAYS = 90
REHIRE_WINDOW_YEARS = 3
RETENTION_AFTER_END_YEARS = 1
RETENTION_AFTER_HIRE_YEARS = 3
EXEMPT_STATUSES = {"citizen", "noncitizen_national", "lpr"}
FAILING_STATUSES = {"OVERDUE", "BLOCKED"}


class UsageError(Exception):
    """Invalid input that should exit with code 1."""


class Parser(argparse.ArgumentParser):
    """ArgumentParser that exits 1 (not argparse's default 2) on usage errors."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        sys.exit(1)


def parse_date(value: str, flag: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise UsageError(f"{flag}: expected YYYY-MM-DD, got {value!r}") from exc


def parse_optional_date(value: str | None, flag: str) -> date | None:
    """Parse a date; None or the literal 'none' means 'no expiration date'."""
    if value is None or value.strip().lower() in {"none", "n/a", "na"}:
        return None
    return parse_date(value, flag)


def add_years(d: date, years: int) -> date:
    """Add calendar years. Feb 29 rolls forward to Mar 1 (the later, safer date)."""
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return date(d.year + years, 3, 1)


def load_holidays(inline: str | None, path: str | None) -> set[date]:
    holidays: set[date] = set()
    if inline:
        for item in inline.split(","):
            if item.strip():
                holidays.add(parse_date(item.strip(), "--holidays"))
    if path:
        try:
            lines = Path(path).read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise UsageError(f"--holidays-file: cannot read {path!r}: {exc}") from exc
        for line in lines:
            line = line.split("#", 1)[0].strip()
            if line:
                holidays.add(parse_date(line, "--holidays-file"))
    return holidays


def add_business_days(start: date, n: int, holidays: set[date]) -> date:
    """Return the date n business days after start (start itself is day 0)."""
    current = start
    counted = 0
    while counted < n:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in holidays:
            counted += 1
    return current


def clock_status(deadline: date, today: date, completed: date | None) -> str:
    if completed is not None:
        return "COMPLETE"
    delta = (deadline - today).days
    if delta < 0:
        return "OVERDUE"
    if delta == 0:
        return "DUE_TODAY"
    return f"DUE_IN_{delta}_DAYS"


def make_clock(name: str, deadline: date, today: date, completed: date | None,
               notes: list[str]) -> dict:
    clock = {
        "clock": name,
        "deadline": deadline.isoformat(),
        "completed": completed.isoformat() if completed else None,
        "status": clock_status(deadline, today, completed),
        "late": bool(completed and completed > deadline),
        "notes": notes,
    }
    if clock["late"]:
        clock["notes"].append("Completed after the deadline: do not back-date; "
                              "attach a signed, dated explanation to the form.")
    return clock


def section_clocks(args: argparse.Namespace, today: date, holidays: set[date]) -> list[dict]:
    hire = parse_date(args.hire_date, "--hire-date")
    offer = parse_optional_date(args.offer_accepted, "--offer-accepted")
    s1_done = parse_optional_date(args.section1_completed, "--section1-completed")
    s2_done = parse_optional_date(args.section2_completed, "--section2-completed")

    if args.job_duration_days is not None and args.job_duration_days < 1:
        raise UsageError("--job-duration-days must be >= 1")
    if offer and hire < offer:
        raise UsageError("--hire-date cannot be before --offer-accepted")

    s1 = make_clock("section1", hire, today, s1_done,
                    ["Employee completes and signs by the first day of work for pay."])
    if offer and s1_done and s1_done < offer:
        s1["status"] = "BLOCKED"
        s1["notes"].append("Section 1 dated before offer acceptance: invalid. "
                           "Never complete Section 1 before the offer is accepted.")

    short_job = (args.job_duration_days is not None
                 and args.job_duration_days < SHORT_JOB_THRESHOLD_DAYS)
    if short_job:
        s2_deadline = hire
        s2_notes = [f"Job lasts {args.job_duration_days} day(s) (< 3 business days): "
                    "Section 2 due no later than the first day of work for pay."]
    else:
        s2_deadline = add_business_days(hire, SECTION2_BUSINESS_DAYS, holidays)
        s2_notes = ["Employer examines original documents and completes Section 2 "
                    "within 3 business days of the first day of work for pay."]
    s2 = make_clock("section2", s2_deadline, today, s2_done, s2_notes)
    if s2_done and (s1_done is None or s2_done < s1_done):
        s2["status"] = "BLOCKED"
        s2["notes"].append("Section 2 recorded without (or before) a completed Section 1: "
                           "review Section 1 first.")
    return [s1, s2]


def reverification_clock(args: argparse.Namespace, today: date) -> dict | None:
    status = args.citizenship_status
    if status is None:
        return None
    base = {"clock": "reverification", "deadline": None, "warning_date": None,
            "completed": None, "late": False}
    if status in EXEMPT_STATUSES:
        reason = {
            "citizen": "US citizen",
            "noncitizen_national": "noncitizen national",
            "lpr": "lawful permanent resident who presented Form I-551",
        }[status]
        return {**base, "status": "NO_REVERIFICATION_REQUIRED",
                "notes": [f"Do not reverify a {reason}. Reverifying is document abuse."]}

    auth = parse_optional_date(args.auth_expiry, "--auth-expiry")
    if args.doc_expiry is None:
        raise UsageError("--citizenship-status alien_authorized requires --doc-expiry "
                         "(a date, or 'none' if the List A/C document does not expire)")
    doc = parse_optional_date(args.doc_expiry, "--doc-expiry")
    if doc is None:
        notes = ["The List A/C document has no expiration date: no reverification "
                 "is required (e.g. an unrestricted Social Security card)."]
        if auth is not None:
            notes.append("Section 1 shows an authorization expiry but the document does "
                         "not expire: confirm Section 2 records the correct document.")
        return {**base, "status": "NO_REVERIFICATION_REQUIRED", "notes": notes}

    deadline = min(d for d in (auth, doc) if d is not None)
    source = "document expiry (Section 2)" if deadline == doc else "authorization expiry (Section 1)"
    done = parse_optional_date(args.reverification_completed, "--reverification-completed")
    clock = make_clock("reverification", deadline, today, done,
                       [f"Deadline = earlier date: {source}. Complete Supplement B "
                        "no later than this date; the employee chooses the document."])
    warning = deadline - timedelta(days=ADVANCE_WARNING_DAYS)
    clock["warning_date"] = warning.isoformat()
    if done is None and today >= warning:
        clock["notes"].append(f"Inside the 90-day window: notify the employee now "
                              f"(warning date {warning.isoformat()}).")
    return clock


def rehire_result(args: argparse.Namespace) -> dict | None:
    if args.rehire_date is None:
        return None
    if args.original_i9_date is None:
        raise UsageError("--rehire-date requires --original-i9-date")
    rehire = parse_date(args.rehire_date, "--rehire-date")
    original = parse_date(args.original_i9_date, "--original-i9-date")
    limit = add_years(original, REHIRE_WINDOW_YEARS)
    if rehire <= limit:
        return {"rehire_date": rehire.isoformat(), "window_ends": limit.isoformat(),
                "result": "SUPPLEMENT_B_ALLOWED",
                "notes": ["Within 3 years of the original Form I-9: you may use "
                          "Supplement B, or complete a new Form I-9."]}
    return {"rehire_date": rehire.isoformat(), "window_ends": limit.isoformat(),
            "result": "NEW_FORM_I9_REQUIRED",
            "notes": ["More than 3 years since the original Form I-9: complete a "
                      "new Form I-9 (Sections 1 and 2)."]}


def retention_result(args: argparse.Namespace, today: date) -> dict:
    hire = parse_date(args.hire_date, "--hire-date")
    end = parse_optional_date(args.employment_end, "--employment-end")
    if end is None:
        return {"retain_until": None, "status": "RETAIN_WHILE_EMPLOYED",
                "notes": ["Retain for as long as the employee works for you."]}
    if end < hire:
        raise UsageError("--employment-end cannot be before --hire-date")
    by_end = add_years(end, RETENTION_AFTER_END_YEARS)
    by_hire = add_years(hire, RETENTION_AFTER_HIRE_YEARS)
    until = max(by_end, by_hire)
    rule = "end + 1 year" if until == by_end else "hire + 3 years"
    return {"retain_until": until.isoformat(),
            "status": "DESTRUCTION_PERMITTED" if today > until else "RETAIN",
            "notes": [f"Later of end + 1 year ({by_end}) and hire + 3 years "
                      f"({by_hire}): {rule}. Check for a legal hold before destroying."]}


def build_parser() -> argparse.ArgumentParser:
    p = Parser(
        prog="i9_tracker.py",
        description="Compute US Form I-9 federal deadlines and today's status. "
                    "Exit 0 = all satisfied, 2 = overdue/blocked, 1 = usage error.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Dates are YYYY-MM-DD. Not legal advice; confirm at uscis.gov/i-9.",
    )
    p.add_argument("--hire-date", required=True,
                   help="First day of work for pay (drives Sections 1/2 and retention).")
    p.add_argument("--today", help="Evaluate status as of this date (default: system date).")
    p.add_argument("--offer-accepted", help="Date the offer was accepted; Section 1 "
                   "completed before this date is BLOCKED.")
    p.add_argument("--section1-completed", help="Date Section 1 was signed, if done.")
    p.add_argument("--section2-completed", help="Date Section 2 was signed, if done.")
    p.add_argument("--job-duration-days", type=int, help="Expected job length in "
                   "business days; < 3 makes Section 2 due on the hire date.")
    p.add_argument("--holidays", help="Comma-separated YYYY-MM-DD dates the business "
                   "is closed, skipped when counting business days.")
    p.add_argument("--holidays-file", help="File of YYYY-MM-DD dates, one per line "
                   "('#' comments allowed), skipped when counting business days.")
    p.add_argument("--citizenship-status",
                   choices=["citizen", "noncitizen_national", "lpr", "alien_authorized"],
                   help="Section 1 attestation. citizen/noncitizen_national/lpr (with "
                   "I-551) never require reverification.")
    p.add_argument("--auth-expiry", help="Employment authorization expiry from "
                   "Section 1, or 'none'.")
    p.add_argument("--doc-list", choices=["A", "C"], help="List of the expiring "
                   "document recorded in Section 2. List B is never reverified.")
    p.add_argument("--doc-expiry", help="Expiry of the List A/C document in Section 2, "
                   "or 'none' if it does not expire (required for alien_authorized).")
    p.add_argument("--reverification-completed", help="Date Supplement B "
                   "reverification was completed, if done.")
    p.add_argument("--rehire-date", help="Rehire date; requires --original-i9-date.")
    p.add_argument("--original-i9-date", help="Date the original Form I-9 was completed.")
    p.add_argument("--employment-end", help="Last day of employment, for retention.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return p


def render_text(report: dict) -> str:
    lines = [f"Form I-9 tracker — as of {report['today']} (hire date {report['hire_date']})"]
    for c in report["clocks"]:
        due = c["deadline"] or "-"
        lines.append(f"  {c['clock']:<15} {c['status']:<28} deadline {due}")
        if c.get("warning_date"):
            lines.append(f"  {'':<15} 90-day warning date {c['warning_date']}")
        lines += [f"  {'':<15} - {n}" for n in c["notes"]]
    if report["rehire"]:
        r = report["rehire"]
        lines.append(f"  {'rehire':<15} {r['result']:<28} window ends {r['window_ends']}")
        lines += [f"  {'':<15} - {n}" for n in r["notes"]]
    ret = report["retention"]
    lines.append(f"  {'retention':<15} {ret['status']:<28} until {ret['retain_until'] or '-'}")
    lines += [f"  {'':<15} - {n}" for n in ret["notes"]]
    lines.append(f"RESULT: {'FAIL' if report['exit_code'] == 2 else 'OK'} "
                 f"(exit {report['exit_code']})")
    return "\n".join(lines)


def run(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    try:
        today = parse_date(args.today, "--today") if args.today else date.today()
        holidays = load_holidays(args.holidays, args.holidays_file)
        clocks = section_clocks(args, today, holidays)
        reverify = reverification_clock(args, today)
        if reverify:
            clocks.append(reverify)
        report = {
            "today": today.isoformat(),
            "hire_date": args.hire_date,
            "clocks": clocks,
            "rehire": rehire_result(args),
            "retention": retention_result(args, today),
        }
    except UsageError as exc:
        print(f"i9_tracker.py: error: {exc}", file=sys.stderr)
        return 1
    report["exit_code"] = 2 if any(c["status"] in FAILING_STATUSES for c in clocks) else 0
    print(json.dumps(report, indent=2) if args.json else render_text(report))
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
