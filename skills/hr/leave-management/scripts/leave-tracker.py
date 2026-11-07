#!/usr/bin/env python3
"""
Leave Tracker — standard leave management operations: initialize accrual
policies, submit and approve requests, show balances, reconcile, and
calculate PTO payout at termination.

Usage:
    python leave-tracker.py init-policies <yaml_file>
    python leave-tracker.py balances        <employee_id>
    python leave-tracker.py submit          <employee_id> <leave_type> <start> <end>
    python leave-tracker.py approve         <request_id>
    python leave-tracker.py reconcile       <payroll_csv>
    python leave-tracker.py payout          <employee_id> <last_date>
    python leave-tracker.py report          [--org org_name]
"""

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


try:
    import yaml
except ImportError:
    yaml = None


DATA_DIR = Path.home() / ".leave_tracker"
DATA_DIR.mkdir(exist_ok=True)
POLICIES_FILE = DATA_DIR / "policies.yaml"
BALANCES_FILE = DATA_DIR / "balances.json"
REQUESTS_FILE = DATA_DIR / "requests.json"


def _load_policies():
    if not POLICIES_FILE.exists():
        return {"leave_types": {}, "employee_groups": {}}
    with open(POLICIES_FILE) as f:
        return yaml.safe_load(f) or {}


def _save_policies(policies):
    with open(POLICIES_FILE, "w") as f:
        yaml.dump(policies, f, default_flow_style=False)


def _load_balances():
    if not BALANCES_FILE.exists():
        return {}
    with open(BALANCES_FILE) as f:
        return json.load(f)


def _save_balances(balances):
    with open(BALANCES_FILE, "w") as f:
        json.dump(balances, f, indent=2)


def _load_requests():
    if not REQUESTS_FILE.exists():
        return []
    with open(REQUESTS_FILE) as f:
        return json.load(f)


def _save_requests(requests):
    with open(REQUESTS_FILE, "w") as f:
        json.dump(requests, f, indent=2)


def cmd_init_policies(args):
    if not yaml:
        print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
        return 1
    if not args.file:
        print("ERROR: provide a YAML policy file path", file=sys.stderr)
        return 1
    with open(args.file) as f:
        policies = yaml.safe_load(f)
    _save_policies(policies)
    types = len(policies.get("leave_types", {}))
    groups = len(policies.get("employee_groups", {}))
    print(f"Policies loaded: {types} leave types, {groups} employee groups")
    return 0


def cmd_balances(args):
    policies = _load_policies()
    balances = _load_balances()
    if args.employee_id:
        bal = balances.get(args.employee_id, {})
        if not bal:
            print(f"No balances found for employee {args.employee_id}")
            return 1
        print(f"Balances for {args.employee_id}:")
        for lt, hours in bal.items():
            print(f"  {lt}: {hours:.2f}h")
    else:
        for eid, bal in sorted(balances.items()):
            total = sum(bal.values())
            print(f"{eid}: {total:.2f}h total ({len(bal)} leave types)")
    return 0


def cmd_submit(args):
    policies = _load_policies()
    balances = _load_balances()
    requests = _load_requests()

    # Basic validation
    if args.leave_type not in policies.get("leave_types", {}):
        print(f"ERROR: Unknown leave type '{args.leave_type}'", file=sys.stderr)
        print(f"Known: {list(policies.get('leave_types', {}).keys())}")
        return 1

    try:
        start = date.fromisoformat(args.start)
        end = date.fromisoformat(args.end)
        duration = (end - start).days + 1
    except ValueError:
        print("ERROR: dates must be YYYY-MM-DD", file=sys.stderr)
        return 1

    # Check balance
    bal = balances.get(args.employee_id, {})
    available = bal.get(args.leave_type, 0)

    if available < duration * 8 and policies.get("leave_types", {}).get(args.leave_type, {}).get("paid", True):
        print(f"ERROR: Insufficient {args.leave_type} balance: {available:.2f}h available, {duration * 8:.2f}h needed", file=sys.stderr)
        return 1

    req = {
        "id": f"REQ-{len(requests) + 1:04d}",
        "employee_id": args.employee_id,
        "leave_type": args.leave_type,
        "start": args.start,
        "end": args.end,
        "duration_days": duration,
        "status": "pending",
        "submitted": datetime.utcnow().isoformat() + "Z",
        "approved_by": None,
    }
    requests.append(req)
    _save_requests(requests)
    print(f"Request {req['id']} submitted: {args.employee_id} {args.leave_type} {args.start}->{args.end} ({duration} days)")
    return 0


def cmd_approve(args):
    requests = _load_requests()
    balances = _load_balances()

    for req in requests:
        if req["id"] == args.request_id:
            if req["status"] != "pending":
                print(f"ERROR: Request {args.request_id} is already {req['status']}", file=sys.stderr)
                return 1
            req["status"] = "approved"
            req["approved_by"] = args.approver or "manager"
            # Deduct balance
            lt = req["leave_type"]
            hours = req["duration_days"] * 8
            emp_bal = balances.setdefault(req["employee_id"], {})
            emp_bal[lt] = emp_bal.get(lt, 0) - hours
            _save_requests(requests)
            _save_balances(balances)
            print(f"Request {args.request_id} approved. Deducted {hours:.2f}h from {req['employee_id']} / {lt}")
            return 0

    print(f"ERROR: Request {args.request_id} not found", file=sys.stderr)
    return 1


def cmd_reconcile(args):
    """Reconcile leave tracker against a payroll CSV (employee_id, leave_type, hours, pay_period)."""
    requests = _load_requests()
    balances = _load_balances()
    approved = [r for r in requests if r["status"] == "approved"]

    # Load payroll CSV
    discrepancies = []
    with open(args.payroll_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            eid = row.get("employee_id", "").strip()
            lt = row.get("leave_type", "").strip()
            payroll_hours = float(row.get("hours", 0))

            # Find matching approved leave
            tracker_hours = sum(r["duration_days"] * 8 for r in approved if r["employee_id"] == eid and r["leave_type"] == lt)
            if abs(tracker_hours - payroll_hours) > 0.5:
                discrepancies.append({
                    "employee_id": eid,
                    "leave_type": lt,
                    "tracker_hours": tracker_hours,
                    "payroll_hours": payroll_hours,
                    "diff": tracker_hours - payroll_hours,
                })

    if discrepancies:
        print("=== Discrepancies Found ===")
        for d in discrepancies:
            print(f"{d['employee_id']}/{d['leave_type']}: tracker={d['tracker_hours']:.2f}h vs payroll={d['payroll_hours']:.2f}h (diff={d['diff']:.2f}h)")
    else:
        print("No discrepancies — all leave records match payroll.")

    return 0


def cmd_payout(args):
    """Calculate PTO payout at termination."""
    policies = _load_policies()
    balances = _load_balances()
    emp_bal = balances.get(args.employee_id, {})
    if not emp_bal:
        print(f"No balances for employee {args.employee_id}")
        return 1

    total_payout_hours = 0
    for lt, hours in emp_bal.items():
        if hours > 0:
            lt_policy = policies.get("leave_types", {}).get(lt, {})
            if lt_policy.get("payout_on_termination", True):
                total_payout_hours += hours

    print(f"Employee: {args.employee_id}")
    for lt, hours in sorted(emp_bal.items()):
        if hours > 0:
            print(f"  {lt}: {hours:.2f}h unused")
    print(f"  Total payout hours: {total_payout_hours:.2f}h")
    print(f"  (Apply the hourly rate to convert to currency)")
    print(f"  (Check local jurisdiction — some mandate payout, some allow forfeit)")
    return 0


def cmd_report(args):
    """Generate a leave summary report."""
    policies = _load_policies()
    balances = _load_balances()
    requests = _load_requests()

    pending = [r for r in requests if r["status"] == "pending"]
    approved = [r for r in requests if r["status"] == "approved"]

    total_balance = sum(sum(b.values()) for b in balances.values())

    report = {
        "total_employees_with_balance": len(balances),
        "total_balance_hours": round(total_balance, 2),
        "pending_requests": len(pending),
        "approved_requests": len(approved),
        "leave_types_enabled": list(policies.get("leave_types", {}).keys()),
        "generated": datetime.utcnow().isoformat() + "Z",
    }

    print(json.dumps(report, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Leave Tracker")
    parser.add_argument("--org", help="Organization name (for reporting)")

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-policies", help="Load leave policies from YAML")
    p_init.add_argument("file", nargs="?", help="Path to YAML policy file")

    p_bal = sub.add_parser("balances", help="Show leave balances")
    p_bal.add_argument("employee_id", nargs="?", default=None, help="Employee ID (omit for all)")

    p_sub = sub.add_parser("submit", help="Submit a leave request")
    p_sub.add_argument("employee_id", help="Employee ID")
    p_sub.add_argument("leave_type", help="Leave type (must match policy)")
    p_sub.add_argument("start", help="Start date YYYY-MM-DD")
    p_sub.add_argument("end", help="End date YYYY-MM-DD")

    p_app = sub.add_parser("approve", help="Approve a pending request")
    p_app.add_argument("request_id", help="Request ID (e.g. REQ-0001)")
    p_app.add_argument("--approver", default=None, help="Approver name/ID")

    p_rec = sub.add_parser("reconcile", help="Reconcile against payroll CSV")
    p_rec.add_argument("payroll_csv", help="Path to payroll CSV (employee_id, leave_type, hours)")

    p_pay = sub.add_parser("payout", help="Calculate PTO payout at termination")
    p_pay.add_argument("employee_id", help="Employee ID")
    p_pay.add_argument("last_date", help="Last working day YYYY-MM-DD")

    p_rep = sub.add_parser("report", help="Generate leave summary report")

    args = parser.parse_args()

    cmds = {
        "init-policies": cmd_init_policies,
        "balances": cmd_balances,
        "submit": cmd_submit,
        "approve": cmd_approve,
        "reconcile": cmd_reconcile,
        "payout": cmd_payout,
        "report": cmd_report,
    }

    fn = cmds.get(args.command)
    if fn:
        return fn(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())