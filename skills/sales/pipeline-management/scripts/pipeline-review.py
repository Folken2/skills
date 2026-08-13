#!/usr/bin/env python3
"""pipeline-review.py — Produce a pipeline health report.

Reads a pipeline JSON (file argument or stdin) and reports:
  * Coverage ratio (open pipeline value vs quota gap) with a health verdict.
  * Pipeline velocity ((# opps x avg deal size x win rate) / cycle length).
  * Stalled deals: those with no next step, or days-in-stage over the stage's
    velocity threshold (default 1.5x the stage's expected days).
  * Summary counts by stage.

Deterministic: same pipeline in, same report out.

Usage:
    python3 pipeline-review.py pipeline.json
    cat pipeline.json | python3 pipeline-review.py
    python3 pipeline-review.py --example      # print a sample input and exit
    python3 pipeline-review.py pipeline.json --json   # machine-readable output

Input schema:

{
  "period": "2026-Q3",
  "quota": 1000000,                  # revenue target for the period
  "committed_won": 250000,           # already-closed-won this period (optional)
  "win_rate": 0.25,                  # 0..1 historical win rate (optional but needed for velocity)
  "stage_expected_days": {           # optional; expected days-in-stage per stage
    "Discovery": 14, "Solution": 21, "Proposal": 14, "Negotiation": 14
  },
  "stall_multiplier": 1.5,           # optional; days-in-stage over this x expected = stalled
  "deals": [
    {
      "id": "D-101",
      "name": "Acme",
      "stage": "Proposal",
      "amount": 60000,
      "days_in_stage": 25,
      "next_step": "Legal review 8/20",   # missing/empty/null => stalled
      "close_date": "2026-09-15"
    }
  ]
}

A deal is counted as OPEN pipeline unless its stage is Closed Won / Closed Lost.
Exit codes: 0 success, 2 bad input.
"""
import json
import sys

CLOSED_WON = {"closed won", "won", "closed-won"}
CLOSED_LOST = {"closed lost", "lost", "closed-lost"}
DEFAULT_STALL_MULT = 1.5


def _num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def is_closed(stage):
    s = (stage or "").strip().lower()
    return s in CLOSED_WON or s in CLOSED_LOST


def coverage_verdict(ratio):
    if ratio is None:
        return "n/a (no quota gap)"
    if ratio >= 5:
        return "high (>=5x) — healthy, possibly sandbagged"
    if ratio >= 3:
        return "healthy (3x-5x)"
    if ratio >= 2:
        return "thin (2x-3x) — creation risk"
    return "critical (<2x) — top-of-funnel problem"


def analyze(pipe):
    if not isinstance(pipe, dict):
        raise ValueError("pipeline JSON must be an object")
    deals = pipe.get("deals") or []
    if not isinstance(deals, list):
        raise ValueError("'deals' must be a list")

    quota = _num(pipe.get("quota"), 0.0)
    committed_won = _num(pipe.get("committed_won"), 0.0)
    win_rate = pipe.get("win_rate")
    win_rate = _num(win_rate, None) if win_rate is not None else None
    stage_expected = pipe.get("stage_expected_days") or {}
    stall_mult = _num(pipe.get("stall_multiplier"), DEFAULT_STALL_MULT) or DEFAULT_STALL_MULT

    open_deals = []
    by_stage = {}
    open_value = 0.0
    cycle_days_samples = []

    for d in deals:
        stage = d.get("stage", "")
        by_stage[stage] = by_stage.get(stage, 0) + 1
        if is_closed(stage):
            continue
        amount = _num(d.get("amount"), 0.0)
        open_value += amount
        open_deals.append(d)

    # Coverage ratio: open pipeline vs the remaining quota gap.
    quota_gap = max(0.0, quota - committed_won)
    coverage = (open_value / quota_gap) if quota_gap > 0 else None

    # Stalled deals.
    stalled = []
    for d in open_deals:
        reasons = []
        ns = d.get("next_step")
        if ns is None or (isinstance(ns, str) and ns.strip() == ""):
            reasons.append("no next step")
        stage = d.get("stage", "")
        dis = d.get("days_in_stage")
        expected = stage_expected.get(stage)
        if dis is not None and expected:
            if _num(dis) > stall_mult * _num(expected):
                reasons.append(
                    f"days_in_stage {int(_num(dis))} > {stall_mult:g}x expected {int(_num(expected))}"
                )
        if reasons:
            stalled.append({
                "id": d.get("id", d.get("name", "?")),
                "stage": stage,
                "amount": _num(d.get("amount"), 0.0),
                "reasons": reasons,
            })

    # Pipeline velocity: (# open opps x avg deal size x win rate) / avg cycle length.
    n_open = len(open_deals)
    avg_deal = (open_value / n_open) if n_open else 0.0
    # Cycle length: use provided avg_cycle_days, else mean days_in_stage as a proxy.
    avg_cycle = pipe.get("avg_cycle_days")
    if avg_cycle is None:
        samples = [_num(d.get("days_in_stage")) for d in open_deals if d.get("days_in_stage") is not None]
        avg_cycle = (sum(samples) / len(samples)) if samples else None
    else:
        avg_cycle = _num(avg_cycle)

    velocity = None
    if win_rate is not None and avg_cycle:
        velocity = (n_open * avg_deal * win_rate) / avg_cycle  # revenue/day

    return {
        "period": pipe.get("period", "(unspecified)"),
        "open_deal_count": n_open,
        "open_pipeline_value": round(open_value, 2),
        "quota": quota,
        "committed_won": committed_won,
        "quota_gap": round(quota_gap, 2),
        "coverage_ratio": round(coverage, 2) if coverage is not None else None,
        "coverage_verdict": coverage_verdict(coverage),
        "avg_deal_size": round(avg_deal, 2),
        "avg_cycle_days": round(avg_cycle, 1) if avg_cycle else None,
        "win_rate": win_rate,
        "pipeline_velocity_per_day": round(velocity, 2) if velocity is not None else None,
        "stalled_count": len(stalled),
        "stalled_value": round(sum(s["amount"] for s in stalled), 2),
        "stalled_deals": stalled,
        "deals_by_stage": by_stage,
    }


def render(r):
    lines = [
        f"Pipeline Health Report — {r['period']}",
        "=" * 44,
        f"Open deals:          {r['open_deal_count']}",
        f"Open pipeline value: {r['open_pipeline_value']:,.0f}",
        f"Quota / gap:         {r['quota']:,.0f} / {r['quota_gap']:,.0f} (won {r['committed_won']:,.0f})",
    ]
    if r["coverage_ratio"] is not None:
        lines.append(f"Coverage ratio:      {r['coverage_ratio']}x  [{r['coverage_verdict']}]")
    else:
        lines.append(f"Coverage ratio:      {r['coverage_verdict']}")
    lines.append(f"Avg deal size:       {r['avg_deal_size']:,.0f}")
    if r["avg_cycle_days"] is not None:
        lines.append(f"Avg cycle (days):    {r['avg_cycle_days']}")
    if r["pipeline_velocity_per_day"] is not None:
        lines.append(f"Pipeline velocity:   {r['pipeline_velocity_per_day']:,.0f} / day")
    else:
        lines.append("Pipeline velocity:   n/a (needs win_rate + cycle length)")

    lines.append("")
    lines.append(f"Stalled deals: {r['stalled_count']}  (value {r['stalled_value']:,.0f})")
    if r["stalled_deals"]:
        for s in r["stalled_deals"]:
            lines.append(f"  - {s['id']} [{s['stage']}] {s['amount']:,.0f}: {'; '.join(s['reasons'])}")
    else:
        lines.append("  (none — every open deal has a next step and healthy velocity)")

    lines.append("")
    lines.append("Deals by stage:")
    for stage, n in r["deals_by_stage"].items():
        lines.append(f"  {stage or '(blank)'}: {n}")
    return "\n".join(lines)


EXAMPLE = {
    "period": "2026-Q3",
    "quota": 1000000,
    "committed_won": 250000,
    "win_rate": 0.25,
    "avg_cycle_days": 60,
    "stage_expected_days": {"Discovery": 14, "Solution": 21, "Proposal": 14, "Negotiation": 14},
    "stall_multiplier": 1.5,
    "deals": [
        {"id": "D-101", "name": "Acme", "stage": "Proposal", "amount": 60000,
         "days_in_stage": 25, "next_step": "Legal review 8/20", "close_date": "2026-09-15"},
        {"id": "D-102", "name": "Globex", "stage": "Discovery", "amount": 40000,
         "days_in_stage": 30, "next_step": "", "close_date": "2026-09-30"},
        {"id": "D-103", "name": "Initech", "stage": "Negotiation", "amount": 120000,
         "days_in_stage": 10, "next_step": "Redlines back 8/15", "close_date": "2026-08-31"},
        {"id": "D-104", "name": "Umbrella", "stage": "Closed Won", "amount": 90000,
         "days_in_stage": 0, "next_step": "onboarding", "close_date": "2026-07-30"},
    ],
}


def main(argv):
    args = argv[1:]
    if "--example" in args:
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    emit_json = "--json" in args
    args = [a for a in args if a != "--json"]

    if args:
        try:
            with open(args[0], "r", encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as e:
            print(f"error: cannot read {args[0]}: {e}", file=sys.stderr)
            return 2
    else:
        if sys.stdin.isatty():
            print("error: no input. Pass a JSON file or pipe JSON on stdin. "
                  "Try --example.", file=sys.stderr)
            return 2
        raw = sys.stdin.read()

    try:
        pipe = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    try:
        report = analyze(pipe)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2) if emit_json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
