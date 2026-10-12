#!/usr/bin/env python3
"""
Apply a merit matrix to a compensation roster and validate the recommendations
before calibration.

A merit matrix maps performance rating x compa-ratio (salary / range midpoint) to
a recommended increase percentage, so that higher performers and employees below
midpoint receive proportionally more, and employees above midpoint receive less.

This produces a starting position for calibration, not a decision. Every override
still needs documented evidence.

Usage:
    python merit-matrix.py roster.json
    python merit-matrix.py --sample > roster.json   # emit a filled-in template

Input schema (roster.json):

    {
      "budget_pct": 3.5,
      "matrix": {                      # optional — overrides the default matrix
        "5": {"below": 7.0, "mid": 5.0, "upper": 3.5, "above": 2.0},
        ...
      },
      "employees": [
        {
          "name": "Alex Kim",
          "rating": 4,                 # 1..5
          "compa_ratio": 0.92,         # salary / range midpoint
          "current_salary": 78000
        }
      ]
    }

compa_ratio may be omitted if current_salary and range_midpoint are supplied.
Output: per-employee recommendation, pool usage, and validation flags.
"""
import json
import sys

# Default merit matrix: rating -> compa-ratio band -> increase %.
# Bands: below < 0.90, mid 0.90-0.99, upper 1.00-1.09, above >= 1.10
DEFAULT_MATRIX = {
    5: {"below": 7.0, "mid": 5.5, "upper": 4.0, "above": 2.5},
    4: {"below": 5.5, "mid": 4.5, "upper": 3.5, "above": 2.0},
    3: {"below": 4.0, "mid": 3.0, "upper": 2.5, "above": 1.5},
    2: {"below": 1.5, "mid": 1.0, "upper": 0.5, "above": 0.0},
    1: {"below": 0.0, "mid": 0.0, "upper": 0.0, "above": 0.0},
}


def band_for(compa_ratio):
    if compa_ratio < 0.90:
        return "below"
    if compa_ratio < 1.00:
        return "mid"
    if compa_ratio < 1.10:
        return "upper"
    return "above"


def _matrix_lookup(matrix, rating, band):
    """matrix keys may be ints or strings after JSON round-trip."""
    row = matrix.get(rating, matrix.get(str(rating)))
    if not row:
        return None
    return row.get(band)


def _resolve_compa(emp):
    ratio = emp.get("compa_ratio")
    if isinstance(ratio, (int, float)):
        return float(ratio)
    salary, midpoint = emp.get("current_salary"), emp.get("range_midpoint")
    if isinstance(salary, (int, float)) and isinstance(midpoint, (int, float)) and midpoint:
        return salary / midpoint
    return None


SAMPLE = {
    "budget_pct": 3.5,
    "employees": [
        {"name": "Alex Kim", "rating": 4, "compa_ratio": 0.92, "current_salary": 78000},
        {"name": "Sam Rivera", "rating": 5, "compa_ratio": 1.14, "current_salary": 121000},
        {"name": "Priya Nair", "rating": 3, "compa_ratio": 1.02, "current_salary": 96000},
        {"name": "Tom Alvarez", "rating": 2, "compa_ratio": 0.88, "current_salary": 71000},
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
            data = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {argv[1]}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {argv[1]}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, dict) or not isinstance(data.get("employees"), list):
        print("error: input must be a JSON object with an 'employees' list", file=sys.stderr)
        return 1

    employees = data["employees"]
    matrix = data.get("matrix") or DEFAULT_MATRIX
    budget_pct = data.get("budget_pct")

    rows, flags, problems = [], [], []
    payroll = 0.0
    total_increase = 0.0

    for emp in employees:
        name = emp.get("name", "(unnamed)")
        salary = emp.get("current_salary")
        if not isinstance(salary, (int, float)):
            problems.append(f"{name}: missing or invalid current_salary")
            continue
        payroll += salary

        rating = emp.get("rating")
        if not isinstance(rating, int) or rating not in DEFAULT_MATRIX:
            problems.append(f"{name}: missing or invalid rating (expected 1-5)")
            rows.append({"name": name, "salary": salary, "rating": rating, "pct": None})
            continue

        ratio = _resolve_compa(emp)
        if ratio is None:
            problems.append(f"{name}: cannot determine compa-ratio (need compa_ratio or salary + range_midpoint)")
            rows.append({"name": name, "salary": salary, "rating": rating, "pct": None})
            continue

        band = band_for(ratio)
        pct = _matrix_lookup(matrix, rating, band)
        if pct is None:
            problems.append(f"{name}: merit matrix has no cell for rating {rating} / band '{band}'")
            rows.append({"name": name, "salary": salary, "rating": rating, "pct": None})
            continue

        increase = salary * pct / 100.0
        total_increase += increase
        rows.append(
            {
                "name": name,
                "salary": salary,
                "rating": rating,
                "ratio": ratio,
                "band": band,
                "pct": pct,
                "increase": increase,
                "new_salary": salary + increase,
            }
        )

    # ---- validation flags (the red flags the skill says to catch pre-calibration)
    by_rating = {}
    for row in rows:
        if row.get("pct") is not None:
            by_rating.setdefault(row["rating"], []).append(row)

    # inverse relationship: a lower-rated employee receiving a larger % than a higher-rated one
    rated = sorted([r for r in rows if r.get("pct") is not None], key=lambda r: r["rating"])
    for i, lower in enumerate(rated):
        for higher in rated[i + 1:]:
            if higher["rating"] > lower["rating"] and higher["pct"] < lower["pct"] - 0.01:
                flags.append(
                    f"inverse relationship: {lower['name']} (rating {lower['rating']}) "
                    f"gets {lower['pct']:.1f}% while {higher['name']} (rating {higher['rating']}) "
                    f"gets {higher['pct']:.1f}% — verify this is evidence-backed"
                )

    # uniform raises within one rating group at the same compa-ratio band (matrix artefact)
    for rating, group in by_rating.items():
        if len(group) >= 3 and len({r["band"] for r in group}) == 1:
            flags.append(
                f"rating {rating}: {len(group)} employees all in the '{group[0]['band']}' band "
                f"receive an identical {group[0]['pct']:.1f}% — check for clustering"
            )

    # range outliers created by this cycle
    for row in rows:
        if row.get("pct") is None or "ratio" not in row:
            continue
        if row["ratio"] < 0.80:
            flags.append(f"{row['name']}: compa-ratio {row['ratio']:.2f} is far below range — consider a market adjustment, not merit")
        if row["ratio"] >= 1.20:
            flags.append(f"{row['name']}: compa-ratio {row['ratio']:.2f} is above range — consider a lump sum instead of base")

    # ---- output
    print("Merit matrix application")
    print("=" * 68)
    print(f"{'Employee':<20}{'Rating':>7}{'Compa':>8}{'Band':>7}{'Inc %':>8}{'Increase':>11}{'New salary':>12}")
    print("-" * 68)
    for row in rows:
        if row.get("pct") is None:
            rating = row.get("rating")
            rating_display = str(rating) if isinstance(rating, int) else "—"
            print(f"{row['name'][:19]:<20}{rating_display:>7}{'—':>8}{'—':>7}{'—':>8}{'—':>11}{'—':>12}")
            continue
        print(
            f"{row['name'][:19]:<20}{row['rating']:>7}{row['ratio']:>8.2f}{row['band']:>7}"
            f"{row['pct']:>7.1f}%{row['increase']:>11,.0f}{row['new_salary']:>12,.0f}"
        )

    print("-" * 68)
    print(f"Payroll in scope:      {payroll:>12,.0f}")
    print(f"Total increase:        {total_increase:>12,.0f}")
    if payroll:
        actual_pct = total_increase / payroll * 100
        print(f"Actual pool usage:     {actual_pct:>11.2f}%")
        if isinstance(budget_pct, (int, float)):
            status = "within budget" if actual_pct <= budget_pct + 1e-9 else "OVER BUDGET"
            print(f"Budget envelope:       {budget_pct:>11.2f}%  -> {status}")
            if actual_pct > budget_pct:
                print(f"Over by:               {(actual_pct - budget_pct) * payroll / 100:>12,.0f}")

    print("\nValidation flags (resolve before calibration)")
    print("-" * 68)
    if flags:
        for flag in flags:
            print(f"  ! {flag}")
    else:
        print("  none — no clustering, inverse relationships, or range outliers detected")

    print("\nData problems")
    print("-" * 68)
    if problems:
        for problem in problems:
            print(f"  x {problem}")
    else:
        print("  none — every employee produced a recommendation")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
