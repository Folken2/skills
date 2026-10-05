#!/usr/bin/env python3
"""Audit an employee-record export against a compliance rule set.

Implements the seven check families of the hr-compliance-audit skill:

  1. data_completeness       fields required to verify anything else
  2. mandatory_documents     required file inventory per employment type
  3. verification_timeliness identity verification completed within N business days of hire
  4. authorization_expiry    work authorization expired, or expiring inside the look-ahead window
  5. policy_attestation      acknowledged handbook/policy version matches the current version
  6. training_currency       required training recorded and inside its validity period
  7. retention_purge_due     retention window elapsed on a terminated record (over-retention)

Every finding carries a severity and a remediation window, because a finding
without an owner-facing deadline does not get fixed.

Usage:
    python compliance-audit.py --sample > audit-input.json
    python compliance-audit.py audit-input.json
    python compliance-audit.py audit-input.json --json

Exit codes: 0 = no critical findings, 1 = at least one critical finding,
            2 = input could not be read or parsed.
"""
import argparse
import json
import sys
from datetime import date, timedelta

SEVERITY_ORDER = ["critical", "high", "medium", "low"]
REMEDIATION_DAYS = {"critical": 30, "high": 60, "medium": 90, "low": None}

SAMPLE = {
    "audit_date": "2026-10-05",
    "current_handbook_version": "2026.1",
    "verification_deadline_business_days": 3,
    "authorization_lookahead_days": 90,
    "training_validity_days": 365,
    "retention": {"after_hire_years": 3, "after_termination_years": 1},
    "required_training": ["security_awareness", "anti_harassment"],
    "required_documents": {
        "default": ["offer_letter", "identity_verification", "tax_form", "handbook_ack"],
        "contractor": ["contract", "identity_verification", "tax_form"],
    },
    "employees": [
        {
            "id": "E-001",
            "name": "Sample Employee",
            "employment_type": "full_time",
            "hire_date": "2025-02-03",
            "termination_date": None,
            "identity_verification_date": "2025-02-05",
            "work_authorization_expiry": "2027-08-01",
            "handbook_ack_version": "2026.1",
            "documents": {
                "offer_letter": "2025-02-01",
                "identity_verification": "2025-02-05",
                "tax_form": "2025-02-03",
                "handbook_ack": "2025-02-03",
            },
            "training_completed": {
                "security_awareness": "2026-03-01",
                "anti_harassment": "2026-03-01",
            },
        },
        {
            "id": "E-002",
            "name": "Sample Leaver (expect findings)",
            "employment_type": "full_time",
            "hire_date": "2019-01-14",
            "termination_date": "2020-06-30",
            "identity_verification_date": "2019-01-16",
            "work_authorization_expiry": None,
            "handbook_ack_version": "2019.1",
            "documents": {
                "offer_letter": "2019-01-10",
                "identity_verification": "2019-01-16",
                "tax_form": "2019-01-14",
            },
            "training_completed": {},
        },
    ],
}


def _parse_date(value):
    """Return a date, or None when absent/unparseable."""
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _add_business_days(start, count):
    day = start
    added = 0
    while added < count:
        day += timedelta(days=1)
        if day.weekday() < 5:
            added += 1
    return day


def _add_years(start, years):
    try:
        return start.replace(year=start.year + years)
    except ValueError:  # 29 Feb -> 28 Feb
        return start.replace(year=start.year + years, day=28)


def _finding(employee, check, severity, detail):
    return {
        "employee_id": employee.get("id") or "(no id)",
        "employee_name": employee.get("name") or "",
        "check": check,
        "severity": severity,
        "detail": detail,
        "remediation_days": REMEDIATION_DAYS[severity],
    }


def run_audit(data):
    """Return (findings, meta). Pure function — no I/O."""
    findings = []
    audit_date = _parse_date(data.get("audit_date")) or date.today()
    current_version = data.get("current_handbook_version")
    verify_days = int(data.get("verification_deadline_business_days", 3))
    lookahead = int(data.get("authorization_lookahead_days", 90))
    training_validity = int(data.get("training_validity_days", 365))
    required_training = data.get("required_training") or []
    doc_rules = data.get("required_documents") or {"default": []}
    retention = data.get("retention") or {}
    employees = data.get("employees") or []

    for emp in employees:
        hire = _parse_date(emp.get("hire_date"))
        hired = emp.get("hire_date")
        terminated = _parse_date(emp.get("termination_date"))

        # 1. data completeness — anything unverifiable is a legal exposure, not a nit
        missing_fields = [f for f in ("id", "hire_date", "employment_type") if not emp.get(f)]
        if missing_fields:
            findings.append(_finding(
                emp, "data_completeness", "critical",
                "record cannot be audited: missing field(s) " + ", ".join(missing_fields),
            ))
        if hired and not hire:
            findings.append(_finding(
                emp, "data_completeness", "critical",
                "hire_date %r is not an ISO date" % hired,
            ))

        # 2. mandatory documents for the employment type
        etype = emp.get("employment_type") or "default"
        required_docs = doc_rules.get(etype, doc_rules.get("default", []))
        documents = emp.get("documents") or {}
        absent = [d for d in required_docs if not documents.get(d)]
        if absent:
            findings.append(_finding(
                emp, "mandatory_documents", "critical",
                "missing required document(s) for %s: %s" % (etype, ", ".join(absent)),
            ))

        # 3. verification timeliness
        verified = _parse_date(emp.get("identity_verification_date"))
        if hire and verified:
            deadline = _add_business_days(hire, verify_days)
            if verified > deadline:
                findings.append(_finding(
                    emp, "verification_timeliness", "critical",
                    "verification recorded %s, %d day(s) after the %d-business-day "
                    "deadline (%s)" % (verified, (verified - deadline).days, verify_days, deadline),
                ))
        elif hire and not verified and "identity_verification" not in required_docs:
            findings.append(_finding(
                emp, "verification_timeliness", "high",
                "no verification date on record for a hire dated %s" % hire,
            ))

        # 4. work-authorization expiry
        expiry = _parse_date(emp.get("work_authorization_expiry"))
        if expiry:
            if expiry < audit_date:
                findings.append(_finding(
                    emp, "authorization_expiry", "critical",
                    "work authorization expired %s (%d day(s) ago) with no re-verification"
                    % (expiry, (audit_date - expiry).days),
                ))
            elif expiry <= audit_date + timedelta(days=lookahead):
                findings.append(_finding(
                    emp, "authorization_expiry", "high",
                    "work authorization expires %s — inside the %d-day look-ahead; "
                    "schedule re-verification" % (expiry, lookahead),
                ))

        # 5. policy attestation version
        if current_version is not None and not terminated:
            acked = emp.get("handbook_ack_version")
            if acked != current_version:
                findings.append(_finding(
                    emp, "policy_attestation", "high",
                    "acknowledged policy version %r does not match current %r"
                    % (acked or "none", current_version),
                ))

        # 6. required training currency
        completed = emp.get("training_completed") or {}
        if not terminated:
            for course in required_training:
                when = _parse_date(completed.get(course))
                if not when:
                    findings.append(_finding(
                        emp, "training_currency", "high",
                        "required training not completed: %s" % course,
                    ))
                elif when + timedelta(days=training_validity) < audit_date:
                    findings.append(_finding(
                        emp, "training_currency", "medium",
                        "training %s expired %s (validity %d days)"
                        % (course, when + timedelta(days=training_validity), training_validity),
                    ))

        # 7. retention — a ceiling as well as a floor
        if terminated:
            windows = []
            if hire:
                windows.append(_add_years(hire, int(retention.get("after_hire_years", 3))))
            windows.append(_add_years(terminated, int(retention.get("after_termination_years", 1))))
            keep_until = max(windows)
            if keep_until < audit_date:
                findings.append(_finding(
                    emp, "retention_purge_due", "medium",
                    "retention window closed %s (hire %s / termination %s) — record is "
                    "past its documented retention period; schedule purge" % (keep_until, hire, terminated),
                ))
            if not hire:
                findings.append(_finding(
                    emp, "retention_purge_due", "high",
                    "terminated record with no hire date — retention period cannot be computed",
                ))

    meta = {
        "audit_date": audit_date.isoformat(),
        "employees_audited": len(employees),
        "findings_total": len(findings),
    }
    return findings, meta


def render(findings, meta):
    lines = []
    lines.append("HR COMPLIANCE AUDIT — findings report")
    lines.append("=" * 62)
    lines.append("Audit date:        %s" % meta["audit_date"])
    lines.append("Employees audited: %d" % meta["employees_audited"])
    lines.append("Findings:          %d" % meta["findings_total"])
    lines.append("")

    counts = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        counts[f["severity"]] += 1
    lines.append("By severity: " + "  ".join(
        "%s=%d" % (s, counts[s]) for s in SEVERITY_ORDER))
    lines.append("")

    if not findings:
        lines.append("No findings. Every record in scope passed all seven check families.")
        lines.append("Reminder: the tool confirms a document exists, never that it is acceptable.")
        return "\n".join(lines)

    for sev in SEVERITY_ORDER:
        group = [f for f in findings if f["severity"] == sev]
        if not group:
            continue
        window = REMEDIATION_DAYS[sev]
        label = "%s (%d)" % (sev.upper(), len(group))
        lines.append(label + ("  — remediate within %d days" % window if window else "  — next cycle"))
        lines.append("-" * 62)
        for f in group:
            lines.append("  [%s] %s — %s" % (f["employee_id"], f["check"], f["detail"]))
        lines.append("")

    lines.append("Remediation: assign an owner and a due date to every critical and high")
    lines.append("finding; record the evidence that will prove closure. Re-audit criticals at 90 days.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit HR employee records against a compliance rule set.")
    parser.add_argument("input", nargs="?", help="audit input JSON (see --sample)")
    parser.add_argument("--sample", action="store_true", help="emit a fillable template and exit")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit machine-readable findings")
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

    findings, meta = run_audit(data)
    if args.as_json:
        print(json.dumps({"meta": meta, "findings": findings}, indent=2))
    else:
        print(render(findings, meta))
    return 1 if any(f["severity"] == "critical" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
