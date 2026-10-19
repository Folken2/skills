#!/usr/bin/env python3
"""case_tracker.py - milestone SLA tracking and artifact gating for a workplace investigation.

Stdlib only. Keeps the mechanical half of an investigation honest: are the SLA
milestones met, which required artifacts are still missing, and is the case
allowed to close. It does not judge findings - it refuses to let a case close
with an incomplete file.

Usage:
  case_tracker.py new --id CASE-001 --received 2026-10-01 [--severity high] [--out case.json]
  case_tracker.py status --case case.json [--today 2026-10-19]
  case_tracker.py done --case case.json --artifact scope_written [--artifact ...]
  case_tracker.py close --case case.json --finding substantiated

Severity drives the SLA: critical, high, standard.

Exit codes:
  0  success
  1  case cannot close (missing artifacts) or a milestone is overdue
  2  usage or input error
"""

import argparse
import json
import sys
from datetime import date, timedelta

# milestone -> days from the received date, per severity.
# "aftercare" is measured from the report date, not the received date.
SLA = {
    "critical": {"acknowledged": 1, "planned": 2, "evidence_closed": 10,
                 "reported": 15, "aftercare": 30},
    "high": {"acknowledged": 2, "planned": 5, "evidence_closed": 25,
             "reported": 35, "aftercare": 30},
    "standard": {"acknowledged": 3, "planned": 7, "evidence_closed": 30,
                 "reported": 45, "aftercare": 30},
}

MILESTONES = ["acknowledged", "planned", "evidence_closed", "reported", "aftercare"]
FROM_RECEIVED = ["acknowledged", "planned", "evidence_closed", "reported"]

# required artifacts, in workflow order, grouped by phase
ARTIFACTS = [
    "intake_logged", "triage_recorded", "conflict_check", "reporter_acknowledged",
    "scope_written", "plan_written", "evidence_preserved", "respondent_notified",
    "chronology_built", "complainant_interviewed", "witnesses_interviewed",
    "respondent_interviewed", "credibility_assessed", "evidence_index",
    "finding_recorded", "report_written", "action_recommended",
    "outcomes_delivered", "file_archived", "aftercare_scheduled",
]

FINDINGS = ["substantiated", "unsubstantiated", "inconclusive", "not_a_policy_violation"]


def parse_date(value):
    try:
        return date.fromisoformat(str(value).strip())
    except (ValueError, AttributeError):
        raise ValueError("invalid date %r - expected YYYY-MM-DD" % (value,))


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    except json.JSONDecodeError as exc:
        raise ValueError("%s is not valid JSON: %s" % (path, exc))


def save(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def cmd_new(args):
    received = parse_date(args.received)
    if args.severity not in SLA:
        raise ValueError("--severity must be one of: %s" % ", ".join(SLA))
    deadlines = {m: (received + timedelta(days=SLA[args.severity][m])).isoformat()
                 for m in FROM_RECEIVED}
    deadlines["aftercare"] = (received
                              + timedelta(days=SLA[args.severity]["reported"]
                                          + SLA[args.severity]["aftercare"])).isoformat()
    case = {
        "id": args.id,
        "received": received.isoformat(),
        "severity": args.severity,
        "deadlines": deadlines,
        "artifacts": {a: False for a in ARTIFACTS},
        "finding": None,
        "closed": False,
    }
    out = args.out or ("%s.json" % args.id)
    save(out, case)
    print("Case %s created (%s, received %s)" % (args.id, args.severity, received.isoformat()))
    for m in MILESTONES:
        print("  %-16s due %s" % (m, deadlines[m]))
    print("  artifacts required: %d" % len(ARTIFACTS))
    print("  file: %s" % out)
    return 0


def cmd_status(args):
    case = load(args.case)
    today = parse_date(args.today) if args.today else date.today()
    received = parse_date(case["received"])

    print("Case %s  [%s]  received %s  (day %d)"
          % (case["id"], case["severity"], received.isoformat(), (today - received).days))

    overdue = []
    print("\nMilestones")
    for m in MILESTONES:
        due = parse_date(case["deadlines"][m])
        remaining = (due - today).days
        if remaining < 0:
            state = "OVERDUE by %d d" % abs(remaining)
            overdue.append((m, abs(remaining)))
        elif remaining == 0:
            state = "DUE TODAY"
        else:
            state = "in %d d" % remaining
        print("  %-16s due %s  %s" % (m, due.isoformat(), state))

    done = [a for a in ARTIFACTS if case["artifacts"].get(a)]
    missing = [a for a in ARTIFACTS if not case["artifacts"].get(a)]
    pct = int(round(100.0 * len(done) / len(ARTIFACTS)))
    print("\nArtifacts: %d/%d complete (%d%%)" % (len(done), len(ARTIFACTS), pct))
    if missing:
        print("  next required: %s" % missing[0])
        if len(missing) > 1:
            print("  outstanding: %s" % ", ".join(missing))

    if case.get("closed"):
        print("\nCase is CLOSED with finding: %s" % case.get("finding"))
    elif overdue:
        print("\nACTION: %d milestone(s) overdue - %s"
              % (len(overdue), ", ".join(m for m, _ in overdue)))
        print("        Document the reason for the delay in the case file.")
        return 1
    else:
        print("\nNo milestones overdue.")
    return 0


def cmd_done(args):
    case = load(args.case)
    unknown = [a for a in args.artifact if a not in ARTIFACTS]
    if unknown:
        raise ValueError("unknown artifact(s): %s\nvalid: %s"
                         % (", ".join(unknown), ", ".join(ARTIFACTS)))
    for a in args.artifact:
        case["artifacts"][a] = True
    save(args.case, case)
    done = sum(1 for a in ARTIFACTS if case["artifacts"][a])
    print("Marked %d artifact(s) complete - %d/%d (%d%%)"
          % (len(args.artifact), done, len(ARTIFACTS),
             int(round(100.0 * done / len(ARTIFACTS)))))
    return 0


def cmd_close(args):
    case = load(args.case)
    if args.finding not in FINDINGS:
        raise ValueError("--finding must be one of: %s" % ", ".join(FINDINGS))
    missing = [a for a in ARTIFACTS if not case["artifacts"].get(a)]
    if missing:
        print("REFUSED: case %s cannot close - %d artifact(s) missing:" % (case["id"], len(missing)))
        for a in missing:
            print("  - %s" % a)
        print("\nAn incomplete file is not a defensible file. Complete the artifacts"
              " or document why each is not applicable.")
        return 1
    case["finding"] = args.finding
    case["closed"] = True
    save(args.case, case)
    print("Case %s CLOSED - finding: %s" % (case["id"], args.finding))
    print("Next: archive the file per retention policy and diarise the reporter"
          " check-in at 30 and 60-90 days.")
    return 0


def cmd_artifacts(args):
    for a in ARTIFACTS:
        print(a)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="case_tracker.py",
        description="Milestone SLA tracking and artifact gating for a workplace investigation.")
    sub = parser.add_subparsers(dest="command")

    p_new = sub.add_parser("new", help="create a case file with SLA deadlines")
    p_new.add_argument("--id", required=True, help="case identifier, e.g. CASE-001")
    p_new.add_argument("--received", required=True, help="date received (YYYY-MM-DD)")
    p_new.add_argument("--severity", default="standard", choices=sorted(SLA),
                       help="drives the SLA (default standard)")
    p_new.add_argument("--out", help="output path (default <id>.json)")
    p_new.set_defaults(func=cmd_new)

    p_status = sub.add_parser("status", help="show milestone and artifact status")
    p_status.add_argument("--case", required=True, help="case JSON path")
    p_status.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    p_status.set_defaults(func=cmd_status)

    p_done = sub.add_parser("done", help="mark one or more artifacts complete")
    p_done.add_argument("--case", required=True, help="case JSON path")
    p_done.add_argument("--artifact", action="append", required=True,
                        help="artifact name (repeatable)")
    p_done.set_defaults(func=cmd_done)

    p_close = sub.add_parser("close", help="close the case (refuses if artifacts are missing)")
    p_close.add_argument("--case", required=True, help="case JSON path")
    p_close.add_argument("--finding", required=True, choices=FINDINGS)
    p_close.set_defaults(func=cmd_close)

    p_list = sub.add_parser("artifacts", help="list the required artifact names")
    p_list.set_defaults(func=cmd_artifacts)
    return parser


def main(argv):
    parser = build_parser()
    if not argv:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
