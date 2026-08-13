#!/usr/bin/env python3
"""
Compute a per-employee engagement / flight-risk score from the signals the
employee-engagement skill's step 6 says to watch.

This is a triage aid, not a verdict: a high-risk score means "run a stay
interview and act," not "this person is leaving." It turns scattered signals
into a consistent, comparable number so no at-risk employee is overlooked.

Usage:
    python engagement-score.py people.json
    python engagement-score.py --sample > people.json   # emit a template to fill in

Input schema (people.json): a list of employees, each with any of these signals.
All are optional; unknown signals are ignored and missing ones score neutral.

    [
      {
        "name": "Alex Kim",
        "onetoones_held_ratio": 0.4,   # held / scheduled over last quarter (0..1)
        "months_since_comp_review": 20,
        "has_growth_plan": false,      # is there a live development plan?
        "survey_score": 2,            # latest engagement pulse, 1..5
        "recognition_last_60d": false,
        "recent_life_change": true    # relo, new manager, reorg, etc.
      }
    ]

Higher score = higher flight risk. Bands: 0-24 low, 25-49 watch, 50-100 act now.
"""
import json
import sys


# Each rule returns points (0 = no concern) plus a short reason when it fires.
def _score(emp):
    points = 0
    reasons = []

    ratio = emp.get("onetoones_held_ratio")
    if isinstance(ratio, (int, float)) and ratio < 0.75:
        p = round((0.75 - ratio) / 0.75 * 25)
        points += p
        reasons.append(f"1:1s frequently skipped ({ratio:.0%} held) +{p}")

    months = emp.get("months_since_comp_review")
    if isinstance(months, (int, float)) and months > 12:
        p = min(20, round((months - 12) * 1.5))
        points += p
        reasons.append(f"comp drift ({months} mo since review) +{p}")

    if emp.get("has_growth_plan") is False:
        points += 20
        reasons.append("no live growth plan +20")

    survey = emp.get("survey_score")
    if isinstance(survey, (int, float)):
        if survey <= 2:
            points += 20
            reasons.append(f"low pulse ({survey}/5) +20")
        elif survey == 3:
            points += 8
            reasons.append(f"lukewarm pulse ({survey}/5) +8")

    if emp.get("recognition_last_60d") is False:
        points += 10
        reasons.append("no recognition in 60d +10")

    if emp.get("recent_life_change") is True:
        points += 10
        reasons.append("recent life/role change +10")

    return min(points, 100), reasons


def band(score):
    if score >= 50:
        return "ACT NOW"
    if score >= 25:
        return "WATCH"
    return "low"


SAMPLE = [
    {
        "name": "Alex Kim",
        "onetoones_held_ratio": 0.4,
        "months_since_comp_review": 20,
        "has_growth_plan": False,
        "survey_score": 2,
        "recognition_last_60d": False,
        "recent_life_change": True,
    },
    {
        "name": "Sam Rivera",
        "onetoones_held_ratio": 0.9,
        "months_since_comp_review": 6,
        "has_growth_plan": True,
        "survey_score": 4,
        "recognition_last_60d": True,
        "recent_life_change": False,
    },
]


def main(argv):
    if "--sample" in argv:
        print(json.dumps(SAMPLE, indent=2))
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            people = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {argv[1]}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {argv[1]}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(people, list):
        print("error: input must be a JSON list of employees", file=sys.stderr)
        return 1

    scored = []
    for emp in people:
        score, reasons = _score(emp)
        scored.append((score, emp.get("name", "(unnamed)"), reasons))
    scored.sort(reverse=True)

    print("Engagement / flight-risk triage (highest risk first)")
    print("=" * 52)
    for score, name, reasons in scored:
        print(f"[{band(score):>7}] {score:>3}  {name}")
        for r in reasons:
            print(f"              - {r}")
    print("\nAct-now / watch employees: schedule a stay interview and close the loop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
