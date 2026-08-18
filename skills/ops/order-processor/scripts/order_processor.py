#!/usr/bin/env python3
"""Order processor.

Moves orders through a fulfillment state machine:

    received -> validated -> fulfilled -> shipped

Each `--stage` advances eligible orders one step and enforces a validation gate:

    validate : received  -> validated   (requires customer, item, quantity>0)
    fulfill  : validated -> fulfilled    (requires an already-validated order)
    ship     : fulfilled -> shipped      (requires an already-fulfilled order)

Orders that don't satisfy the gate are left unchanged and reported as errors.
Unknown/blank statuses are treated as `received`.

Expected input columns:
    order_id, customer, item, quantity, status

Output:
    - updated orders CSV (default: <input>_updated.csv)
    - a processing log CSV recording every transition and error
"""
import argparse
import csv
import sys
from pathlib import Path


STAGES = {
    "validate": ("received", "validated"),
    "fulfill": ("validated", "fulfilled"),
    "ship": ("fulfilled", "shipped"),
}

VALID_STATUSES = {"received", "validated", "fulfilled", "shipped"}


def _int(value, default=None):
    text = str(value or "").strip()
    if text == "":
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def normalize_status(raw):
    status = (raw or "").strip().lower()
    if status not in VALID_STATUSES:
        return "received"
    return status


def validate_gate(order):
    """Return a list of validation errors for the validate stage."""
    errors = []
    if not (order.get("customer") or "").strip():
        errors.append("missing customer")
    if not (order.get("item") or "").strip():
        errors.append("missing item")
    qty = _int(order.get("quantity"))
    if qty is None:
        errors.append("missing/invalid quantity")
    elif qty <= 0:
        errors.append(f"quantity must be > 0 (got {qty})")
    return errors


def process(orders, stage):
    from_status, to_status = STAGES[stage]
    log = []
    for order in orders:
        order_id = (order.get("order_id") or "").strip() or "UNKNOWN"
        current = normalize_status(order.get("status"))
        order["status"] = current  # persist normalization

        if current == to_status:
            log.append((order_id, current, current, "skipped", "already at target stage"))
            continue
        if current != from_status:
            log.append((order_id, current, current, "skipped",
                        f"not eligible for '{stage}' (needs '{from_status}')"))
            continue

        if stage == "validate":
            errors = validate_gate(order)
            if errors:
                log.append((order_id, current, current, "error", "; ".join(errors)))
                continue

        order["status"] = to_status
        log.append((order_id, from_status, to_status, "advanced", ""))
    return log


def read_orders(csv_path):
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Orders file not found: {csv_path}")
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        orders = [dict(row) for row in reader]
    return orders, fieldnames


def write_orders(orders, fieldnames, output_path):
    if "status" not in fieldnames:
        fieldnames = fieldnames + ["status"]
    with Path(output_path).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for order in orders:
            writer.writerow({k: order.get(k, "") for k in fieldnames})


def write_log(log, log_path):
    with Path(log_path).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["order_id", "from_status", "to_status", "result", "detail"])
        writer.writerows(log)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Advance orders through received->validated->fulfilled->shipped.",
    )
    parser.add_argument("orders", help="Path to the orders CSV file.")
    parser.add_argument(
        "--stage", required=True, choices=sorted(STAGES),
        help="Stage to apply: validate | fulfill | ship.",
    )
    parser.add_argument(
        "--output", default=None,
        help="Updated orders CSV path (default: <input>_updated.csv).",
    )
    parser.add_argument(
        "--log", default="processing_log.csv",
        help="Processing log CSV path (default: processing_log.csv).",
    )
    args = parser.parse_args(argv)

    try:
        orders, fieldnames = read_orders(args.orders)
    except FileNotFoundError as exc:
        parser.error(str(exc))

    if not orders:
        print("No orders found in input.", file=sys.stderr)
        return 1

    if "status" not in fieldnames:
        fieldnames = fieldnames + ["status"]

    log = process(orders, args.stage)

    output_path = args.output
    if output_path is None:
        p = Path(args.orders)
        output_path = str(p.with_name(f"{p.stem}_updated{p.suffix or '.csv'}"))

    write_orders(orders, fieldnames, output_path)
    write_log(log, args.log)

    advanced = sum(1 for e in log if e[3] == "advanced")
    errors = sum(1 for e in log if e[3] == "error")
    skipped = sum(1 for e in log if e[3] == "skipped")

    for order_id, frm, to, result, detail in log:
        if result == "advanced":
            print(f"[OK]    {order_id:<12} {frm} -> {to}")
        elif result == "error":
            print(f"[ERROR] {order_id:<12} {detail}")
    print("-" * 50)
    print(f"Stage    : {args.stage}")
    print(f"Advanced : {advanced}")
    print(f"Errors   : {errors}")
    print(f"Skipped  : {skipped}")
    print(f"Orders   : {output_path}")
    print(f"Log      : {args.log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
