#!/usr/bin/env python3
"""
Compute close-out hiring metrics from a pipeline JSON file.

Operationalizes the hiring skill's step 9 (close-out & handoff): time-to-fill,
cost-per-hire, source-of-hire mix, and stage-by-stage funnel conversion — the
final metrics every closed requisition should record.

Usage:
    python hiring-metrics.py pipeline.json
    python hiring-metrics.py --sample > pipeline.json   # emit a template to fill in

Input schema (pipeline.json):
    {
      "role": "Senior Backend Engineer",
      "req_opened": "2026-01-06",        # ISO date the approved req opened
      "offer_accepted": "2026-02-20",    # ISO date the finalist accepted
      "costs": {                          # any cost buckets; summed for cost-per-hire
        "job_boards": 900,
        "agency_fee": 4000,
        "referral_bonus": 1500,
        "team_time": 1200
      },
      "sources": {                        # candidates entered, by source-of-hire
        "referral": 8, "job_board": 22, "agency": 5, "direct": 4
      },
      "hired_source": "referral",        # source the actual hire came from
      "funnel": {                         # count reaching each stage, in order
        "applied": 39, "screened": 14, "interviewed": 6, "offer": 1, "hired": 1
      }
    }

Every field is optional; the script reports on whatever it is given.
"""
import json
import sys
from datetime import date


SAMPLE = {
    "role": "Senior Backend Engineer",
    "req_opened": "2026-01-06",
    "offer_accepted": "2026-02-20",
    "costs": {"job_boards": 900, "agency_fee": 4000, "referral_bonus": 1500, "team_time": 1200},
    "sources": {"referral": 8, "job_board": 22, "agency": 5, "direct": 4},
    "hired_source": "referral",
    "funnel": {"applied": 39, "screened": 14, "interviewed": 6, "offer": 1, "hired": 1},
}


def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def report(data):
    lines = []
    role = data.get("role", "(unnamed role)")
    lines.append(f"Hiring metrics — {role}")
    lines.append("=" * (16 + len(role)))

    opened = _parse_date(data.get("req_opened"))
    accepted = _parse_date(data.get("offer_accepted"))
    if opened and accepted:
        ttf = (accepted - opened).days
        lines.append(f"Time-to-fill:      {ttf} days  (req opened {opened} -> accepted {accepted})")
        if ttf > 90:
            lines.append("  ! 90+ days — expected for senior/exec; confirm this matched the plan.")
    else:
        lines.append("Time-to-fill:      n/a (need both req_opened and offer_accepted)")

    costs = data.get("costs") or {}
    if costs:
        total = sum(costs.values())
        lines.append(f"Cost-per-hire:     ${total:,.0f}")
        for bucket, amount in sorted(costs.items(), key=lambda kv: -kv[1]):
            lines.append(f"    {bucket:<16} ${amount:,.0f}")
    else:
        lines.append("Cost-per-hire:     n/a (no costs provided)")

    sources = data.get("sources") or {}
    if sources:
        total_src = sum(sources.values()) or 1
        hired_from = data.get("hired_source")
        lines.append("Source-of-hire mix:")
        for src, n in sorted(sources.items(), key=lambda kv: -kv[1]):
            mark = "  <- hired here" if src == hired_from else ""
            lines.append(f"    {src:<16} {n:>3}  ({n / total_src * 100:4.1f}%){mark}")

    funnel = data.get("funnel") or {}
    if funnel:
        lines.append("Funnel conversion:")
        stages = list(funnel.items())
        for i, (stage, n) in enumerate(stages):
            if i == 0:
                lines.append(f"    {stage:<16} {n:>3}")
            else:
                prev = stages[i - 1][1] or 1
                lines.append(f"    {stage:<16} {n:>3}  ({n / prev * 100:4.1f}% of {stages[i-1][0]})")

    return "\n".join(lines)


def main(argv):
    if "--sample" in argv:
        print(json.dumps(SAMPLE, indent=2))
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {argv[1]}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {argv[1]}: {exc}", file=sys.stderr)
        return 1
    print(report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
