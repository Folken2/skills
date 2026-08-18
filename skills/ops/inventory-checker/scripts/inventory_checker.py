#!/usr/bin/env python3
"""Inventory checker.

Reads an inventory CSV, compares each item's quantity against its reorder
threshold, flags low-stock items, and recommends reorder quantities. Emits a
restock report CSV and an alert summary to stdout.

Expected input columns:
    item_id, name, quantity, reorder_threshold, unit_cost

Status logic (per item):
    OUT      quantity <= 0
    CRITICAL quantity < threshold / 2
    LOW      quantity < threshold  (and not CRITICAL/OUT)
    OK       quantity >= threshold

Reorder quantity: bring stock up to 2x the threshold (a simple reorder-to-max
policy). Items already OK get a reorder quantity of 0.

Edge cases handled:
    - Missing/blank numeric values -> treated as 0
    - Negative quantity            -> clamped to 0, flagged
    - Missing threshold            -> falls back to --min-stock
    - Zero threshold               -> only OUT items flagged
"""
import argparse
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Item:
    item_id: str
    name: str
    quantity: int
    reorder_threshold: int
    unit_cost: float
    status: str = "OK"
    reorder_qty: int = 0
    reorder_cost: float = 0.0
    warnings: list = field(default_factory=list)


def _to_number(value, cast, default):
    if value is None:
        return default
    text = str(value).strip().replace("$", "").replace(",", "")
    if text == "":
        return default
    try:
        return cast(float(text))
    except ValueError:
        return default


def evaluate(row, index, default_threshold):
    warnings = []

    item_id = (row.get("item_id") or "").strip() or f"UNKNOWN-{index}"
    if item_id.startswith("UNKNOWN-"):
        warnings.append("missing item_id")
    name = (row.get("name") or "").strip() or "Unnamed"

    quantity = _to_number(row.get("quantity"), int, 0)
    if quantity < 0:
        warnings.append(f"negative quantity ({quantity}) clamped to 0")
        quantity = 0

    threshold = _to_number(row.get("reorder_threshold"), int, None)
    if threshold is None:
        threshold = default_threshold
        warnings.append(f"missing reorder_threshold; using default {default_threshold}")
    if threshold < 0:
        threshold = 0

    unit_cost = _to_number(row.get("unit_cost"), float, 0.0)
    if unit_cost < 0:
        warnings.append("negative unit_cost clamped to 0")
        unit_cost = 0.0

    if quantity <= 0:
        status = "OUT"
    elif threshold > 0 and quantity < threshold / 2:
        status = "CRITICAL"
    elif quantity < threshold:
        status = "LOW"
    else:
        status = "OK"

    target = max(threshold * 2, threshold)
    reorder_qty = max(target - quantity, 0) if status != "OK" else 0
    reorder_cost = round(reorder_qty * unit_cost, 2)

    return Item(
        item_id=item_id,
        name=name,
        quantity=quantity,
        reorder_threshold=threshold,
        unit_cost=unit_cost,
        status=status,
        reorder_qty=reorder_qty,
        reorder_cost=reorder_cost,
        warnings=warnings,
    )


def read_inventory(csv_path, default_threshold):
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Inventory file not found: {csv_path}")
    items = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return items
        for i, row in enumerate(reader, start=1):
            items.append(evaluate(row, i, default_threshold))
    return items


def write_report(items, output_path):
    fields = [
        "item_id", "name", "quantity", "reorder_threshold", "unit_cost",
        "status", "reorder_qty", "reorder_cost",
    ]
    with Path(output_path).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for item in items:
            writer.writerow({k: getattr(item, k) for k in fields})


SEVERITY = {"OUT": 3, "CRITICAL": 2, "LOW": 1, "OK": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check inventory levels against reorder thresholds and flag restocks.",
    )
    parser.add_argument("inventory", help="Path to the inventory CSV file.")
    parser.add_argument(
        "--min-stock", type=int, default=10,
        help="Fallback reorder threshold when a row omits one (default: 10).",
    )
    parser.add_argument(
        "--output", default="restock_report.csv",
        help="Path for the restock report CSV (default: restock_report.csv).",
    )
    parser.add_argument(
        "--alert", action="store_true",
        help="Print only CRITICAL and OUT items.",
    )
    args = parser.parse_args(argv)

    try:
        items = read_inventory(args.inventory, args.min_stock)
    except FileNotFoundError as exc:
        parser.error(str(exc))

    if not items:
        print("No inventory rows found.", file=sys.stderr)
        return 1

    write_report(items, args.output)

    flagged = [i for i in items if i.status != "OK"]
    if args.alert:
        shown = [i for i in items if i.status in ("CRITICAL", "OUT")]
    else:
        shown = flagged

    shown.sort(key=lambda i: (-SEVERITY[i.status], i.item_id))

    for item in shown:
        print(
            f"[{item.status:<8}] {item.item_id:<10} {item.name:<24} "
            f"qty={item.quantity:<5} thr={item.reorder_threshold:<5} "
            f"reorder={item.reorder_qty:<5} cost={item.reorder_cost:.2f}"
        )

    total_reorder_cost = round(sum(i.reorder_cost for i in flagged), 2)
    print("-" * 60)
    print(f"Total items       : {len(items)}")
    print(f"Needing restock   : {len(flagged)}")
    print(f"  OUT             : {sum(1 for i in items if i.status == 'OUT')}")
    print(f"  CRITICAL        : {sum(1 for i in items if i.status == 'CRITICAL')}")
    print(f"  LOW             : {sum(1 for i in items if i.status == 'LOW')}")
    print(f"Est. reorder cost : {total_reorder_cost:.2f}")
    print(f"Report written to : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
