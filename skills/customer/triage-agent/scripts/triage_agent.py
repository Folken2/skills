#!/usr/bin/env python3
"""Customer request triage agent.

Classifies incoming customer request text by urgency and department using
transparent keyword rules (no ML), then recommends a routing action.

Two modes:
    classify  -> classify a single request string
    batch     -> classify every row of a CSV and write a routed CSV

Classification:
    urgency    -> low | medium | high | critical
    department -> billing | tech | support | account

Edge cases handled:
    - Empty / whitespace-only text   -> urgency=low, department=support,
                                        flagged "empty request"
    - No keyword matches             -> defaults department=support, urgency=low
    - Ties on department score       -> resolved by a fixed priority order
    - Missing CSV text column        -> row flagged, routed to support/low
"""
import argparse
import csv
import json
import sys
from pathlib import Path


# Department keyword rules. Order also acts as tie-break priority.
DEPARTMENT_RULES = [
    ("billing", [
        "invoice", "bill", "charge", "charged", "payment", "refund", "receipt",
        "subscription", "price", "pricing", "overcharge", "credit card", "coupon",
    ]),
    ("tech", [
        "error", "bug", "crash", "crashed", "broken", "not working", "500",
        "exception", "api", "timeout", "outage", "down", "latency", "server",
    ]),
    ("account", [
        "login", "log in", "password", "reset", "locked out", "2fa", "account",
        "sign in", "signin", "username", "email address", "profile", "access",
    ]),
    ("support", [
        "how do i", "help", "question", "feature", "request", "cancel",
        "unsubscribe", "documentation", "guide", "support", "assist",
    ]),
]

# Urgency keyword rules, highest first — first hit wins.
URGENCY_RULES = [
    ("critical", [
        "urgent", "asap", "immediately", "critical", "emergency", "outage",
        "data loss", "breach", "security", "cannot access", "lawsuit", "legal",
        "down for everyone", "production down",
    ]),
    ("high", [
        "broken", "not working", "crash", "error", "failed", "blocked",
        "angry", "frustrated", "escalate", "refund", "charged twice",
    ]),
    ("medium", [
        "slow", "delay", "issue", "problem", "question about", "confused",
        "unable", "trouble",
    ]),
]

ROUTING = {
    ("billing", "critical"): "Page billing on-call; open P1 finance ticket.",
    ("tech", "critical"): "Page engineering on-call; open P1 incident.",
    ("account", "critical"): "Escalate to security/account-recovery team now.",
    ("support", "critical"): "Escalate to senior support lead immediately.",
}


def classify_department(text):
    text_l = text.lower()
    scores = {}
    for dept, keywords in DEPARTMENT_RULES:
        scores[dept] = sum(1 for kw in keywords if kw in text_l)
    best_score = max(scores.values()) if scores else 0
    if best_score == 0:
        return "support", scores
    # tie-break by DEPARTMENT_RULES order
    for dept, _ in DEPARTMENT_RULES:
        if scores[dept] == best_score:
            return dept, scores
    return "support", scores


def classify_urgency(text):
    text_l = text.lower()
    for level, keywords in URGENCY_RULES:
        if any(kw in text_l for kw in keywords):
            return level
    return "low"


def route(department, urgency):
    if (department, urgency) in ROUTING:
        return ROUTING[(department, urgency)]
    action = {
        "critical": "Escalate immediately",
        "high": "Assign to a senior agent within 1 hour",
        "medium": "Queue for same-day response",
        "low": "Queue for standard response",
    }[urgency]
    return f"{action}; route to {department} team."


def triage(text):
    warnings = []
    text = (text or "").strip()
    if not text:
        warnings.append("empty request")
        return {
            "text": "",
            "urgency": "low",
            "department": "support",
            "department_scores": {},
            "action": "Queue for standard response; route to support team.",
            "warnings": warnings,
        }
    department, scores = classify_department(text)
    urgency = classify_urgency(text)
    if all(v == 0 for v in scores.values()):
        warnings.append("no department keywords matched; defaulted to support")
    return {
        "text": text,
        "urgency": urgency,
        "department": department,
        "department_scores": scores,
        "action": route(department, urgency),
        "warnings": warnings,
    }


def cmd_classify(args):
    result = triage(args.text)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(f"Urgency   : {result['urgency']}")
    print(f"Department: {result['department']}")
    print(f"Action    : {result['action']}")
    if args.verbose:
        print(f"Scores    : {result['department_scores']}")
        if result["warnings"]:
            print("Warnings  : " + "; ".join(result["warnings"]))
    return 0


def cmd_batch(args):
    path = Path(args.csv_file)
    if not path.is_file():
        print(f"Input CSV not found: {args.csv_file}", file=sys.stderr)
        return 1

    rows_out = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        if args.text_column not in fieldnames:
            print(
                f"Column '{args.text_column}' not found. Available: {fieldnames}",
                file=sys.stderr,
            )
            return 1
        for row in reader:
            result = triage(row.get(args.text_column, ""))
            out = dict(row)
            out["urgency"] = result["urgency"]
            out["department"] = result["department"]
            out["action"] = result["action"]
            out["warnings"] = "; ".join(result["warnings"])
            rows_out.append(out)

    if not rows_out:
        print("No rows to classify.", file=sys.stderr)
        return 1

    out_fields = list(rows_out[0].keys())
    out_path = Path(args.output)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows_out)

    counts = {}
    for r in rows_out:
        counts[r["urgency"]] = counts.get(r["urgency"], 0) + 1
    print(f"Classified {len(rows_out)} requests -> {out_path}")
    for level in ("critical", "high", "medium", "low"):
        if level in counts:
            print(f"  {level:<8}: {counts[level]}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Triage customer requests by urgency and department.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_classify = sub.add_parser("classify", help="Classify a single request string.")
    p_classify.add_argument("text", help="The customer request text.")
    p_classify.add_argument("--verbose", action="store_true",
                            help="Show keyword scores and warnings.")
    p_classify.add_argument("--json", action="store_true",
                            help="Emit the full result as JSON.")
    p_classify.set_defaults(func=cmd_classify)

    p_batch = sub.add_parser("batch", help="Classify a CSV of requests.")
    p_batch.add_argument("csv_file", help="Input CSV of requests.")
    p_batch.add_argument("--text-column", default="request",
                         help="Column holding the request text (default: request).")
    p_batch.add_argument("--output", default="triaged.csv",
                         help="Output CSV path (default: triaged.csv).")
    p_batch.set_defaults(func=cmd_batch)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
