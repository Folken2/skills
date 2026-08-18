#!/usr/bin/env python3
"""Payroll processor.

Reads an employee timesheet CSV, calculates net pay (gross - tax - deductions)
for each employee, writes individual paystub files, and emits a summary report
as CSV and JSON.

Expected input columns:
    employee_id, name, hours_worked, hourly_rate, tax_rate, deductions

Edge cases handled:
    - Missing/blank numeric values  -> treated as 0.0
    - Negative hours                -> clamped to 0.0, flagged in warnings
    - Negative rate/deductions      -> clamped to 0.0, flagged in warnings
    - Zero rate                     -> allowed (results in $0 gross), flagged
    - tax_rate given as percent     -> values > 1 are interpreted as percent
                                       (e.g. 20 -> 0.20)
    - Missing employee_id/name      -> synthesised placeholder, flagged
"""
import argparse
import csv
import json
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class Paystub:
    employee_id: str
    name: str
    hours_worked: float
    hourly_rate: float
    gross_pay: float
    tax_rate: float
    tax_amount: float
    deductions: float
    net_pay: float
    warnings: list = field(default_factory=list)


def _to_float(value, default=0.0):
    """Parse a possibly-messy CSV cell into a float."""
    if value is None:
        return default
    text = str(value).strip().replace("$", "").replace(",", "")
    if text == "":
        return default
    try:
        return float(text)
    except ValueError:
        return default


def normalize_tax_rate(raw):
    """Accept either a fraction (0.20) or a percent (20) and return a fraction."""
    rate = _to_float(raw, 0.0)
    if rate < 0:
        return 0.0, True
    if rate > 1:
        return rate / 100.0, False
    return rate, False


def process_row(row, index):
    warnings = []

    employee_id = (row.get("employee_id") or "").strip()
    if not employee_id:
        employee_id = f"UNKNOWN-{index}"
        warnings.append("missing employee_id")

    name = (row.get("name") or "").strip()
    if not name:
        name = "Unknown"
        warnings.append("missing name")

    hours = _to_float(row.get("hours_worked"))
    if hours < 0:
        warnings.append(f"negative hours_worked ({hours}) clamped to 0")
        hours = 0.0

    rate = _to_float(row.get("hourly_rate"))
    if rate < 0:
        warnings.append(f"negative hourly_rate ({rate}) clamped to 0")
        rate = 0.0
    elif rate == 0:
        warnings.append("zero hourly_rate -> $0 gross pay")

    tax_rate, tax_neg = normalize_tax_rate(row.get("tax_rate"))
    if tax_neg:
        warnings.append("negative tax_rate clamped to 0")

    deductions = _to_float(row.get("deductions"))
    if deductions < 0:
        warnings.append(f"negative deductions ({deductions}) clamped to 0")
        deductions = 0.0

    gross = round(hours * rate, 2)
    tax_amount = round(gross * tax_rate, 2)
    net = round(gross - tax_amount - deductions, 2)
    if net < 0:
        warnings.append("net_pay is negative after deductions")

    return Paystub(
        employee_id=employee_id,
        name=name,
        hours_worked=hours,
        hourly_rate=rate,
        gross_pay=gross,
        tax_rate=round(tax_rate, 4),
        tax_amount=tax_amount,
        deductions=deductions,
        net_pay=net,
        warnings=warnings,
    )


def read_timesheet(csv_path):
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Timesheet not found: {csv_path}")
    stubs = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return stubs
        for i, row in enumerate(reader, start=1):
            stubs.append(process_row(row, i))
    return stubs


def write_paystub(stub, output_dir):
    out = Path(output_dir) / f"paystub_{stub.employee_id}.txt"
    lines = [
        "=" * 40,
        "           PAYSTUB",
        "=" * 40,
        f"Employee ID : {stub.employee_id}",
        f"Name        : {stub.name}",
        "-" * 40,
        f"Hours Worked: {stub.hours_worked:>12.2f}",
        f"Hourly Rate : {stub.hourly_rate:>12.2f}",
        f"Gross Pay   : {stub.gross_pay:>12.2f}",
        f"Tax Rate    : {stub.tax_rate * 100:>11.2f}%",
        f"Tax Amount  : {stub.tax_amount:>12.2f}",
        f"Deductions  : {stub.deductions:>12.2f}",
        "-" * 40,
        f"NET PAY     : {stub.net_pay:>12.2f}",
        "=" * 40,
    ]
    if stub.warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {w}" for w in stub.warnings)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_summary_csv(stubs, output_dir):
    out = Path(output_dir) / "payroll_summary.csv"
    fields = [
        "employee_id", "name", "hours_worked", "hourly_rate",
        "gross_pay", "tax_rate", "tax_amount", "deductions", "net_pay",
    ]
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for stub in stubs:
            row = {k: getattr(stub, k) for k in fields}
            writer.writerow(row)
    return out


def write_summary_json(stubs, output_dir):
    out = Path(output_dir) / "payroll_report.json"
    totals = {
        "employee_count": len(stubs),
        "total_gross": round(sum(s.gross_pay for s in stubs), 2),
        "total_tax": round(sum(s.tax_amount for s in stubs), 2),
        "total_deductions": round(sum(s.deductions for s in stubs), 2),
        "total_net": round(sum(s.net_pay for s in stubs), 2),
    }
    report = {
        "totals": totals,
        "paystubs": [asdict(s) for s in stubs],
    }
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out, totals


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Process an employee timesheet CSV into paystubs and a payroll report.",
    )
    parser.add_argument("timesheet", help="Path to the timesheet CSV file.")
    parser.add_argument(
        "--output-dir", default="./paystubs",
        help="Directory for paystubs and reports (default: ./paystubs).",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress the per-employee summary printed to stdout.",
    )
    args = parser.parse_args(argv)

    try:
        stubs = read_timesheet(args.timesheet)
    except FileNotFoundError as exc:
        parser.error(str(exc))

    if not stubs:
        print("No employee rows found in timesheet.", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for stub in stubs:
        write_paystub(stub, output_dir)

    csv_path = write_summary_csv(stubs, output_dir)
    json_path, totals = write_summary_json(stubs, output_dir)

    if not args.quiet:
        for stub in stubs:
            flag = "  [!]" if stub.warnings else ""
            print(f"{stub.employee_id:<12} {stub.name:<20} net={stub.net_pay:>10.2f}{flag}")
        print("-" * 50)
        print(f"Employees : {totals['employee_count']}")
        print(f"Gross     : {totals['total_gross']:.2f}")
        print(f"Tax       : {totals['total_tax']:.2f}")
        print(f"Deductions: {totals['total_deductions']:.2f}")
        print(f"Net       : {totals['total_net']:.2f}")
        print(f"\nWrote paystubs + {csv_path.name} + {json_path.name} to {output_dir}/")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
