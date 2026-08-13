#!/usr/bin/env python3
"""lead-scorer.py — Score and prioritize an inbound lead.

Reads a lead JSON (from a file argument or stdin), computes a 0–100 priority
score across three weighted dimensions (fit, intent, engagement), assigns a
tier (A/B/C), and emits a next action + follow-up cadence.

Deterministic on purpose: the same lead always scores the same, so priority is
comparable across reps and across days.

Usage:
    python3 lead-scorer.py lead.json
    cat lead.json | python3 lead-scorer.py
    python3 lead-scorer.py --example      # print a sample input and exit

Input schema (all fields optional; unknowns are treated as unknown, not zero-
penalised beyond their missing signal):

{
  "name": "Acme Corp - Jane Doe",
  "framework": "GPCT",                # BANT | CHAMP | GPCT (informational)
  "fit": {                            # Ideal Customer Profile match
    "icp_match": 0.9,                 # 0..1 overall ICP fit (required for a fit score)
    "company_size": "mid-market",     # optional, informational
    "seniority": "VP"                 # optional, informational
  },
  "intent": {                         # framework fields; each 0..1 strength, or null if unknown
    "need": 0.8,
    "authority": 0.5,
    "budget": null,
    "timing": 0.7
  },
  "engagement": {
    "signals": ["demo_request", "pricing_page"],  # known buying signals
    "days_since_last_touch": 1                     # recency
  }
}

Exit codes: 0 success, 2 bad input.
"""
import json
import sys

WEIGHTS = {"fit": 0.40, "intent": 0.40, "engagement": 0.20}

# Recognised high-intent buying signals and their weight (0..1 each, capped).
SIGNAL_WEIGHTS = {
    "demo_request": 1.0,
    "trial_signup": 1.0,
    "contact_sales": 1.0,
    "pricing_page": 0.7,
    "webinar": 0.4,
    "content_download": 0.3,
    "newsletter": 0.15,
}

EXAMPLE = {
    "name": "Acme Corp - Jane Doe",
    "framework": "GPCT",
    "fit": {"icp_match": 0.9, "company_size": "mid-market", "seniority": "VP"},
    "intent": {"need": 0.8, "authority": 0.5, "budget": None, "timing": 0.7},
    "engagement": {"signals": ["demo_request", "pricing_page"], "days_since_last_touch": 1},
}


def _clamp01(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, x))


def score_fit(fit):
    """Return (0..1, note). Uses icp_match if present."""
    if not isinstance(fit, dict):
        return 0.0, "no fit data"
    v = _clamp01(fit.get("icp_match"))
    if v is None:
        return 0.0, "icp_match missing"
    return v, f"icp_match={v:.2f}"


def score_intent(intent):
    """Average of known framework field strengths. Unknown (null/missing)
    fields are excluded from the average rather than scored as zero, so a lead
    is not punished for data we simply haven't captured yet."""
    if not isinstance(intent, dict):
        return 0.0, "no intent data"
    known = [_clamp01(v) for v in intent.values() if _clamp01(v) is not None]
    if not known:
        return 0.0, "no known intent fields"
    avg = sum(known) / len(known)
    return avg, f"{len(known)} field(s), avg={avg:.2f}"


def score_engagement(eng):
    """Combine recency and buying signals into 0..1."""
    if not isinstance(eng, dict):
        return 0.0, "no engagement data"
    signals = eng.get("signals") or []
    sig_score = min(1.0, sum(SIGNAL_WEIGHTS.get(s, 0.2) for s in signals)) if signals else 0.0

    days = eng.get("days_since_last_touch")
    if days is None:
        recency = 0.5  # unknown recency: neutral
    else:
        try:
            days = float(days)
        except (TypeError, ValueError):
            days = None
        if days is None:
            recency = 0.5
        elif days <= 1:
            recency = 1.0
        elif days <= 3:
            recency = 0.8
        elif days <= 7:
            recency = 0.6
        elif days <= 30:
            recency = 0.3
        else:
            recency = 0.1
    combined = 0.6 * sig_score + 0.4 * recency
    return combined, f"signals={sig_score:.2f}, recency={recency:.2f}"


def tier_for(score):
    if score >= 75:
        return "A", "Hot — work now"
    if score >= 50:
        return "B", "Nurture — work after A-tier"
    return "C", "Low — automated nurture / disqualify"


def next_action(tier, fit_score):
    cadence = {
        "A": "First touch within 1 hour; multi-touch (call+email+social), 5-7 touches / 2 weeks.",
        "B": "First touch within 1 business day; 3-4 touches / 3-4 weeks + nurture.",
        "C": "Route to automated marketing nurture; re-score on new engagement.",
    }[tier]
    if tier == "C":
        route = "Long-nurture or disqualify with a reason code."
    elif fit_score >= 0.7:
        route = "Route to AE / field-sales pipeline; trigger discovery-call."
    else:
        route = "Route to inside-sales / product-led pipeline."
    return route, cadence


def evaluate(lead):
    if not isinstance(lead, dict):
        raise ValueError("lead JSON must be an object")
    fit, fit_note = score_fit(lead.get("fit"))
    intent, intent_note = score_intent(lead.get("intent"))
    eng, eng_note = score_engagement(lead.get("engagement"))

    score = 100.0 * (WEIGHTS["fit"] * fit + WEIGHTS["intent"] * intent + WEIGHTS["engagement"] * eng)
    score = round(score, 1)
    tier, tier_desc = tier_for(score)
    route, cadence = next_action(tier, fit)

    return {
        "name": lead.get("name", "(unnamed lead)"),
        "framework": lead.get("framework", "unspecified"),
        "score": score,
        "tier": tier,
        "tier_desc": tier_desc,
        "breakdown": {
            "fit": {"value": round(fit, 3), "weight": WEIGHTS["fit"], "note": fit_note},
            "intent": {"value": round(intent, 3), "weight": WEIGHTS["intent"], "note": intent_note},
            "engagement": {"value": round(eng, 3), "weight": WEIGHTS["engagement"], "note": eng_note},
        },
        "route": route,
        "cadence": cadence,
    }


def render(result):
    b = result["breakdown"]
    lines = [
        f"Lead:      {result['name']}",
        f"Framework: {result['framework']}",
        f"Score:     {result['score']}/100   ->   Tier {result['tier']} ({result['tier_desc']})",
        "",
        "Breakdown:",
        f"  fit         {b['fit']['value']:.2f} x {b['fit']['weight']:.2f}   ({b['fit']['note']})",
        f"  intent      {b['intent']['value']:.2f} x {b['intent']['weight']:.2f}   ({b['intent']['note']})",
        f"  engagement  {b['engagement']['value']:.2f} x {b['engagement']['weight']:.2f}   ({b['engagement']['note']})",
        "",
        f"Next action: {result['route']}",
        f"Cadence:     {result['cadence']}",
    ]
    return "\n".join(lines)


def main(argv):
    args = argv[1:]
    if "--example" in args:
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    emit_json = "--json" in args
    args = [a for a in args if a != "--json"]

    raw = None
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
        lead = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    try:
        result = evaluate(lead)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2) if emit_json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
