#!/usr/bin/env python3
"""
Track a performance improvement plan (PIP) against its goals, checkpoints, and
evidence, and surface both a per-goal status and the structural gaps that make a
PIP hard to defend.

This is a documentation aid, not a decision-maker. HR and legal own the
close / extend / exit call; this script only makes sure the call is made on the
record instead of on memory.

Usage:
    python pip-tracker.py pip.json
    python pip-tracker.py --sample > pip.json   # emit a filled-in template

Input schema (pip.json):

    {
      "employee": "Alex Kim",
      "opened": "2026-01-05",
      "deadline": "2026-03-05",
      "consequence_stated": true,
      "hr_review": true,
      "support_owner": "J. Rivera",
      "checkins": ["2026-01-12", "2026-01-26", "2026-02-09"],
      "goals": [
        {
          "name": "Enter all client notes in CRM within 24h",
          "standard": ">=95% of interactions logged within 24 hours",
          "evidence": ["Jan: 61%", "Feb: 78%"],
          "status": "at_risk"
        }
      ]
    }

Goal status values: met | on_track | at_risk | not_met | unknown

Output: per-goal status lines, a structural gap list, and an overall signal of
CLOSE / EXTEND / EXIT_REVIEW / INSUFFICIENT_RECORD.
"""
import json
import sys
from datetime import date, datetime

VALID_STATUS = ("met", "on_track", "at_risk", "not_met", "unknown")


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def structural_gaps(pip):
    """Return a list of strings describing defects in the PIP record."""
    gaps = []

    opened = _parse_date(pip.get("opened"))
    deadline = _parse_date(pip.get("deadline"))
    if opened and deadline:
        days = (deadline - opened).days
        if days < 30:
            gaps.append(f"timeline is {days} days — SHRM guidance says a PIP must run at least 30 days")
    elif not deadline:
        gaps.append("no deadline set — an open-ended PIP cannot be enforced or closed")

    if pip.get("consequence_stated") is not True:
        gaps.append("consequences are not stated in the plan — the employee must be told the outcome of not improving")
    if pip.get("hr_review") is not True:
        gaps.append("no HR/legal review recorded before delivery")
    if not pip.get("support_owner"):
        gaps.append("no owner named for the support being provided — an unresourced PIP is a trap")

    checkins = pip.get("checkins") or []
    if not checkins:
        gaps.append("no check-ins logged — skipped check-ins are the fastest way to look like a paper trail")

    goals = pip.get("goals") or []
    if not goals:
        gaps.append("no goals defined — there is nothing to measure improvement against")
    for goal in goals:
        name = goal.get("name") or "(unnamed goal)"
        if not goal.get("standard"):
            gaps.append(f"goal '{name}' has no measurable standard")
        if not goal.get("evidence"):
            gaps.append(f"goal '{name}' has no evidence recorded")
        status = goal.get("status")
        if status not in VALID_STATUS:
            gaps.append(f"goal '{name}' has unrecognised status {status!r} (expected one of {', '.join(VALID_STATUS)})")

    return gaps


def overall_signal(goals, gaps):
    """Map per-goal statuses to a decision signal."""
    statuses = [g.get("status") for g in goals]
    if not goals or not any(s in VALID_STATUS[:-1] for s in statuses):
        return "INSUFFICIENT_RECORD"
    if all(s == "met" for s in statuses):
        return "CLOSE"
    if any(s == "not_met" for s in statuses):
        return "EXIT_REVIEW"
    if all(s in ("met", "on_track") for s in statuses):
        return "CLOSE"
    return "EXTEND"


SIGNAL_NOTE = {
    "CLOSE": "All goals met or on track — document sustained improvement and return to the normal lifecycle.",
    "EXTEND": "Mixed progress with genuine trajectory — one written extension with the reason and a new deadline.",
    "EXIT_REVIEW": "At least one goal is not met — close with a documented outcome and hand the record to HR/legal.",
    "INSUFFICIENT_RECORD": "Not enough evidence to decide — fix the gaps above before closing the plan.",
}

SAMPLE = {
    "employee": "Alex Kim",
    "opened": "2026-01-05",
    "deadline": "2026-03-05",
    "consequence_stated": True,
    "hr_review": True,
    "support_owner": "J. Rivera",
    "checkins": ["2026-01-12", "2026-01-26", "2026-02-09"],
    "goals": [
        {
            "name": "Enter all client notes in CRM within 24h",
            "standard": ">=95% of interactions logged within 24 hours",
            "evidence": ["Jan: 61%", "Feb: 78%"],
            "status": "at_risk",
        },
        {
            "name": "Complete the CRM workflow certification",
            "standard": "Certification passed by 2026-02-20",
            "evidence": ["2026-02-14: passed"],
            "status": "met",
        },
    ],
}


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    if "--sample" in argv:
        print(json.dumps(SAMPLE, indent=2))
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2

    try:
        with open(argv[1], encoding="utf-8") as fh:
            pip = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {argv[1]}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {argv[1]}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(pip, dict):
        print("error: input must be a JSON object describing one PIP", file=sys.stderr)
        return 1

    goals = pip.get("goals") or []
    gaps = structural_gaps(pip)
    signal = overall_signal(goals, gaps)

    label = pip.get("employee", "(unnamed)")
    print(f"PIP tracker — {label}")
    print("=" * 52)

    opened, deadline = _parse_date(pip.get("opened")), _parse_date(pip.get("deadline"))
    if opened and deadline:
        total = (deadline - opened).days
        elapsed = (date.today() - opened).days
        pct = max(0, min(100, round(elapsed / total * 100))) if total > 0 else 100
        print(f"Window: {opened} -> {deadline}  ({total} days, {pct}% elapsed)")
    print(f"Check-ins logged: {len(pip.get('checkins') or [])}")

    print("\nGoals")
    print("-" * 52)
    for goal in goals:
        status = goal.get("status", "unknown")
        print(f"  [{status:>8}] {goal.get('name', '(unnamed goal)')}")
        if goal.get("standard"):
            print(f"             standard: {goal['standard']}")
        for item in goal.get("evidence") or []:
            print(f"             evidence: {item}")

    print("\nStructural gaps (fix before closing)")
    print("-" * 52)
    if gaps:
        for gap in gaps:
            print(f"  ! {gap}")
    else:
        print("  none — the record is structurally complete")

    print(f"\nDecision signal: {signal}")
    print(f"  {SIGNAL_NOTE[signal]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
