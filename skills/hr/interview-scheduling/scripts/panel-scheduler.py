#!/usr/bin/env python3
"""Resolve a multi-stage interview loop into a conflict-free schedule.

Implements step 5 of the interview-scheduling skill: normalise every
participant's availability to UTC, place each stage only where the entire
required panel is free for the full duration, enforce the candidate's minimum
gap and daily cap, preserve stage order, and report every unfillable stage
with an explicit reason instead of silently dropping it.

Usage:
    python panel-scheduler.py --sample > loop.json
    python panel-scheduler.py loop.json
    python panel-scheduler.py loop.json --json

Exit codes: 0 = every stage scheduled, 1 = at least one stage unscheduled,
            2 = input could not be read or parsed.
"""
import argparse
import itertools
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # Python < 3.9
    ZoneInfo = None

    class ZoneInfoNotFoundError(Exception):
        pass

SAMPLE = {
    "candidate": {
        "name": "Sample Candidate",
        "timezone": "Europe/Madrid",
        "window": {"start": "2026-10-06T09:00", "end": "2026-10-09T18:00"},
        "blocked": [["2026-10-07T13:00", "2026-10-07T15:00"]],
    },
    "slot_granularity_minutes": 30,
    "min_gap_minutes": 15,
    "max_interviews_per_day": 3,
    "interviewers": {
        "recruiter@example.com": {
            "timezone": "Europe/Madrid",
            "availability": [["2026-10-06T09:00", "2026-10-08T18:00"]],
        },
        "engineer@example.com": {
            "timezone": "Europe/Madrid",
            "availability": [["2026-10-06T10:00", "2026-10-06T14:00"],
                             ["2026-10-08T09:00", "2026-10-08T13:00"]],
        },
        "manager@example.com": {
            "timezone": "America/New_York",
            "availability": [["2026-10-06T08:00", "2026-10-06T12:00"]],
        },
    },
    "panels": [
        {"stage": "recruiter screen", "order": 1, "duration_minutes": 30,
         "required": ["recruiter@example.com"]},
        {"stage": "technical", "order": 2, "duration_minutes": 60,
         "required": ["engineer@example.com"]},
        {"stage": "hiring manager", "order": 3, "duration_minutes": 45,
         "required": ["manager@example.com"]},
    ],
}


def _tz(name):
    if ZoneInfo is None:
        raise SystemExit("error: zoneinfo is unavailable; Python 3.9+ required")
    try:
        return ZoneInfo(name or "UTC")
    except ZoneInfoNotFoundError:
        raise SystemExit("error: unknown timezone %r" % name)


def _dt(value, tzname):
    """Parse an ISO local datetime in tzname, return aware UTC datetime."""
    try:
        dt = datetime.fromisoformat(str(value))
    except ValueError:
        raise SystemExit("error: %r is not an ISO datetime" % (value,))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_tz(tzname))
    return dt.astimezone(timezone.utc)


def _merge(intervals):
    """Merge overlapping (start, end) tuples, sorted."""
    out = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if out and start <= out[-1][1]:
            if end > out[-1][1]:
                out[-1] = (out[-1][0], end)
        else:
            out.append((start, end))
    return out


def _free(free_intervals, busy, start, end):
    """True when [start, end] sits inside one free interval and touches no busy block."""
    inside = any(free_start <= start and end <= free_end for free_start, free_end in free_intervals)
    if not inside:
        return False
    return not any(start < b_end and b_start < end for b_start, b_end in busy)


def schedule(data):
    """Return (scheduled, unscheduled). Pure function — no I/O."""
    gran = timedelta(minutes=int(data.get("slot_granularity_minutes", 30)))
    gap = timedelta(minutes=int(data.get("min_gap_minutes", 15)))
    cap = data.get("max_interviews_per_day")

    cand = data.get("candidate") or {}
    ctz_name = cand.get("timezone") or "UTC"
    ctz = _tz(ctz_name)
    win = cand.get("window") or {}
    if not win.get("start") or not win.get("end"):
        raise SystemExit("error: candidate.window requires start and end")
    win_start = _dt(win["start"], ctz_name)
    win_end = _dt(win["end"], ctz_name)
    blocked = _merge([(_dt(s, ctz_name), _dt(e, ctz_name))
                      for s, e in (cand.get("blocked") or [])])

    interviewers = {}
    for email, info in (data.get("interviewers") or {}).items():
        tz_name = info.get("timezone") or "UTC"
        availability = [(_dt(s, tz_name), _dt(e, tz_name))
                        for s, e in (info.get("availability") or [])]
        interviewers[email] = {"timezone": tz_name, "free": _merge(availability)}

    panels = sorted(data.get("panels") or [], key=lambda p: (p.get("order") or 0, p.get("stage") or ""))

    scheduled = []
    unscheduled = []
    cand_busy = []                      # booking + gap shield, candidate side
    booked = defaultdict(list)          # interviewer email -> booked blocks
    per_day = defaultdict(int)          # candidate-local date -> stages booked

    for panel in panels:
        stage = panel.get("stage") or "(unnamed stage)"
        duration = timedelta(minutes=int(panel.get("duration_minutes") or 0))
        required = list(panel.get("required") or [])
        alternates = panel.get("alternates") or {}

        unknown = [e for e in required if e not in interviewers]
        if unknown:
            unscheduled.append({"stage": stage, "order": panel.get("order"),
                                "reason": "interviewer has no availability record: "
                                          + ", ".join(unknown)})
            continue

        # Option lists per required seat: the named interviewer first, then substitutes.
        options = [[e] + list(alternates.get(e) or []) for e in required]
        combos = sorted(itertools.product(*options), key=lambda combo: sum(
            1 for i, e in enumerate(combo) if e != required[i]))
        placed = None
        substitutions = []

        for combo in combos[:200]:
            if any(e not in interviewers for e in combo):
                continue
            slot = win_start
            while slot + duration <= win_end:
                end = slot + duration
                day = slot.astimezone(ctz).date()
                if cap and per_day.get(day, 0) >= int(cap):
                    slot += gran
                    continue
                shielded = (slot - gap, end + gap)
                if any(shielded[0] < b_end and b_start < shielded[1] for b_start, b_end in blocked):
                    slot += gran
                    continue
                if any(slot < b_end and b_start < end for b_start, b_end in cand_busy):
                    slot += gran
                    continue
                if all(_free(interviewers[e]["free"], booked[e], slot, end) for e in combo):
                    placed = (slot, end, combo)
                    break
                slot += gran
            if placed:
                substitutions = [{"seat": required[i], "filled_by": combo[i]}
                                 for i in range(len(combo)) if combo[i] != required[i]]
                break

        if not placed:
            unscheduled.append({"stage": stage, "order": panel.get("order"),
                                "reason": _reason(cand, ctz, win_start, win_end, gran, duration,
                                                  required, interviewers, cap, per_day, panels,
                                                  scheduled)})
            continue

        slot, end, combo = placed
        cand_busy.append((slot - gap, end + gap))
        for e in combo:
            booked[e].append((slot, end))
        per_day[slot.astimezone(ctz).date()] += 1
        scheduled.append({
            "stage": stage,
            "order": panel.get("order"),
            "start_utc": slot.isoformat(),
            "end_utc": end.isoformat(),
            "duration_minutes": int(panel.get("duration_minutes") or 0),
            "candidate_local": "%s–%s (%s)" % (slot.astimezone(ctz).strftime("%Y-%m-%d %H:%M"),
                                               end.astimezone(ctz).strftime("%H:%M"), ctz_name),
            "participants": {
                e: "%s–%s (%s)" % (slot.astimezone(_tz(interviewers[e]["timezone"])).strftime("%Y-%m-%d %H:%M"),
                                   end.astimezone(_tz(interviewers[e]["timezone"])).strftime("%H:%M"),
                                   interviewers[e]["timezone"])
                for e in combo
            },
            "substitutions": substitutions,
        })

    return scheduled, unscheduled


def _reason(cand, ctz, win_start, win_end, gran, duration, required, interviewers,
            cap, per_day, panels, scheduled):
    """Explain why a stage could not be placed."""
    empty = [e for e in required if not interviewers[e]["free"]]
    if empty:
        return "no availability supplied for: " + ", ".join(empty)
    if cap:
        dates = set()
        cursor = win_start
        while cursor + duration <= win_end:
            dates.add(cursor.astimezone(ctz).date())
            cursor += gran
        if dates and all(per_day.get(d, 0) >= int(cap) for d in dates):
            return "candidate daily cap (%s interview(s) per day) reached on every date in the window" % cap
    return "no common conflict-free slot inside the candidate window for the required panel"


def render(scheduled, unscheduled, data):
    cand = (data.get("candidate") or {}).get("name") or "candidate"
    lines = []
    lines.append("INTERVIEW LOOP — proposed schedule")
    lines.append("=" * 62)
    lines.append("Candidate: %s" % cand)
    lines.append("Stages:    %d scheduled / %d total"
                 % (len(scheduled), len(scheduled) + len(unscheduled)))
    lines.append("")
    if scheduled:
        lines.append("SCHEDULED")
        lines.append("-" * 62)
        for s in scheduled:
            lines.append("  %s. %s — %s" % (s["order"], s["stage"], s["candidate_local"]))
            lines.append("     utc: %s" % s["start_utc"])
            for who, when in s["participants"].items():
                lines.append("     %s: %s" % (who, when))
            for sub in s["substitutions"]:
                lines.append("     NOTE substitution: %s -> %s" % (sub["seat"], sub["filled_by"]))
        lines.append("")
    if unscheduled:
        lines.append("UNSCHEDULED — escalate, do not drop")
        lines.append("-" * 62)
        for u in unscheduled:
            lines.append("  %s. %s — %s" % (u["order"], u["stage"], u["reason"]))
        lines.append("")
        lines.append("Next: try a substitute interviewer with the same competency coverage,")
        lines.append("then widen the candidate window, then relax a soft constraint.")
    else:
        lines.append("No interviewer is double-booked; the candidate gap and daily cap hold.")
        lines.append("Send each participant their own local time and require explicit acceptance.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Resolve a conflict-free interview loop.")
    parser.add_argument("input", nargs="?", help="loop request JSON (see --sample)")
    parser.add_argument("--sample", action="store_true", help="emit a fillable template and exit")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit machine-readable schedule")
    args = parser.parse_args(argv)

    if args.sample:
        print(json.dumps(SAMPLE, indent=2))
        return 0
    if not args.input:
        parser.error("provide an input file, or use --sample")

    try:
        with open(args.input, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print("error: cannot read %s: %s" % (args.input, exc), file=sys.stderr)
        return 2

    scheduled, unscheduled = schedule(data)
    if args.as_json:
        print(json.dumps({"scheduled": scheduled, "unscheduled": unscheduled}, indent=2))
    else:
        print(render(scheduled, unscheduled, data))
    return 1 if unscheduled else 0


if __name__ == "__main__":
    sys.exit(main())
