#!/usr/bin/env python3
"""
Review Cycle Manager — generate a performance review cycle calendar,
per-employee review packets, and track submission status across phases.

Usage:
    python review-cycle-manager.py --start YYYY-MM-DD --org team-name [--quarter Q]

Outputs:
    - cycle_calendar_<org>.csv     — timeline with hard deadlines per phase
    - employee_packet_<name>.json  — per-employee review packet (goals, forms)
    - cycle_status_<org>.json      — submission dashboard at end
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta


PHASE_DURATIONS = {
    "cycle_announcement": {"label": "Announce & manager training", "days": 3},
    "goal_setting":        {"label": "Self-review & goal confirmation", "days": 7},
    "evidence_collection": {"label": "Feedback collection (throughout period)", "days": 0},  # ongoing
    "self_review_due":     {"label": "Self-review due", "days": 5},
    "manager_review_due":  {"label": "Manager review due", "days": 7},
    "calibration":         {"label": "Calibration sessions", "days": 3},
    "review_conversations": {"label": "Review conversations", "days": 10},
    "development_plans":   {"label": "Development plans due", "days": 5},
    "comp_connection":     {"label": "Compensation conversations", "days": 5},
    "cycle_feedback":      {"label": "Cycle feedback & retrospective", "days": 3},
}


def generate_calendar(start_date, org, quarter=None):
    """Produce a cycle calendar with phase deadlines."""
    rows = []
    offset = 0
    for phase, info in PHASE_DURATIONS.items():
        if info["days"] == 0:
            continue  # ongoing phase
        begin = start_date + timedelta(days=offset)
        end = begin + timedelta(days=info["days"] - 1)
        rows.append({
            "phase": phase,
            "label": info["label"],
            "start": begin.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "duration_days": info["days"],
        })
        offset += info["days"]

    filename = f"cycle_calendar_{org}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["phase", "label", "start", "end", "duration_days"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Calendar written: {filename} ({len(rows)} phases)")
    return rows


def generate_packets(employees):
    """Generate per-employee review packets."""
    packets = []
    for emp in employees:
        packet = {
            "name": emp["name"],
            "email": emp.get("email", ""),
            "manager": emp.get("manager", ""),
            "goals": emp.get("goals", []),
            "self_review": {
                "status": "pending",
                "goal_reflections": [{"goal": g["title"], "achievement": "", "challenges": "", "learnings": ""} for g in emp.get("goals", [])],
                "submit_date": None,
            },
            "manager_review": {
                "status": "pending",
                "evaluations": [{"goal": g["title"], "rating": None, "sbi_notes": "", "evidence": ""} for g in emp.get("goals", [])],
                "overall_rating": None,
                "submit_date": None,
            },
            "development_plan": {
                "status": "pending",
                "areas": [],
                "actions": [],
                "review_date": None,
            },
        }
        filename = f"employee_packet_{emp['name'].replace(' ', '_')}.json"
        with open(filename, "w") as f:
            json.dump(packet, f, indent=2)
        packets.append((filename, packet))
        print(f"Packet created: {filename}")

    return packets


def track_status(calendar, packets, org):
    """Generate a cycle status dashboard."""
    total = len(packets)
    self_done = sum(1 for _, p in packets if p["self_review"]["submit_date"])
    mgr_done = sum(1 for _, p in packets if p["manager_review"]["submit_date"])
    dev_done = sum(1 for _, p in packets if p["development_plan"]["status"] == "complete")

    status = {
        "org": org,
        "generated": datetime.utcnow().isoformat() + "Z",
        "total_employees": total,
        "self_review_complete": self_done,
        "manager_review_complete": mgr_done,
        "development_plan_complete": dev_done,
        "calendar_phases": len(calendar),
        "remaining_submissions": total - self_done + total - mgr_done + total - dev_done,
    }

    filename = f"cycle_status_{org}.json"
    with open(filename, "w") as f:
        json.dump(status, f, indent=2)
    print(f"Status dashboard: {filename}")
    return status


def main():
    parser = argparse.ArgumentParser(description="Performance Review Cycle Manager")
    parser.add_argument("--start", required=True, help="Cycle start date YYYY-MM-DD")
    parser.add_argument("--org", required=True, help="Team or org name")
    parser.add_argument("--quarter", help="Quarter label (e.g. Q3-2026)")
    parser.add_argument("--employees", help="Optional path to employees JSON (list of {name, email, manager, goals})")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    calendar = generate_calendar(start, args.org, args.quarter)

    if args.employees:
        with open(args.employees) as f:
            employees = json.load(f)
    else:
        employees = [{"name": "Example_Employee", "email": "", "manager": "", "goals": [{"title": "Example goal — replace with real goals"}]}]

    packets = generate_packets(employees)
    status = track_status(calendar, packets, args.org)

    print(f"\nCycle ready: {len(calendar)} phases, {len(packets)} employees")
    print(f"Status: {status['self_review_complete']}/{status['total_employees']} self-reviews complete")


if __name__ == "__main__":
    main()