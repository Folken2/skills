#!/usr/bin/env python3
"""Log inspector.

Parses structured application logs (JSONL or CSV), filters by severity, detects
error-frequency spikes within a sliding time window, and surfaces simple
compliance/anomaly signals. Prints a summary to stdout and writes a detailed
JSON report.

Expected log fields (JSONL object keys or CSV columns):
    timestamp, level, source, message

Supported timestamp formats:
    - ISO 8601 (e.g. 2026-08-18T09:40:00, with optional 'Z' / offset)
    - Unix epoch seconds (integer or float)

Checks performed:
    - error-frequency spikes: windows where ERROR+ count exceeds --spike-threshold
    - compliance signals: messages containing sensitive markers
      (password, ssn, credit card, secret, api_key, token) at INFO/DEBUG level
    - malformed lines: unparseable rows are counted and reported

Edge cases handled:
    - Unparseable JSON / short CSV rows -> counted as malformed, skipped
    - Missing/blank level               -> treated as INFO
    - Missing/unparseable timestamp     -> excluded from windowing, still counted
    - Empty file                        -> exits non-zero with a message
"""
import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "WARN": 30,
          "ERROR": 40, "CRITICAL": 50, "FATAL": 50}

SENSITIVE_MARKERS = ["password", "ssn", "credit card", "creditcard",
                     "secret", "api_key", "apikey", "token"]

WINDOW_RE = re.compile(r"^(\d+)([smh])$")


def parse_window(text):
    """Parse a window like '5m', '30s', '1h' into seconds."""
    match = WINDOW_RE.match(text.strip().lower())
    if not match:
        raise ValueError(f"Invalid window '{text}'. Use forms like 30s, 5m, 1h.")
    value, unit = int(match.group(1)), match.group(2)
    return value * {"s": 1, "m": 60, "h": 3600}[unit]


def level_value(raw):
    return LEVELS.get((raw or "INFO").strip().upper(), 20)


def parse_timestamp(raw):
    if raw is None:
        return None
    text = str(raw).strip()
    if text == "":
        return None
    # epoch seconds?
    try:
        return datetime.fromtimestamp(float(text), tz=timezone.utc)
    except (ValueError, OSError):
        pass
    # ISO 8601
    iso = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def iter_records(path):
    """Yield (record_dict_or_None, raw_line) for each entry.

    Detects JSONL vs CSV by file extension and content sniffing.
    """
    text_path = Path(path)
    suffix = text_path.suffix.lower()
    with text_path.open(newline="", encoding="utf-8") as fh:
        first = fh.readline()
        fh.seek(0)
        stripped = first.strip()
        is_json = suffix in (".jsonl", ".json") or stripped.startswith("{")
        if is_json:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line), line
                except json.JSONDecodeError:
                    yield None, line
        else:
            reader = csv.DictReader(fh)
            for row in reader:
                if row is None or all(v is None for v in row.values()):
                    yield None, ""
                else:
                    yield dict(row), ""


def inspect(path, min_severity, window_seconds, spike_threshold):
    min_val = level_value(min_severity)
    records = []
    malformed = 0
    level_counts = {}
    source_counts = {}
    compliance_hits = []

    for rec, raw in iter_records(path):
        if rec is None:
            malformed += 1
            continue
        level = (rec.get("level") or "INFO").strip().upper() or "INFO"
        lval = level_value(level)
        ts = parse_timestamp(rec.get("timestamp"))
        source = (rec.get("source") or "unknown").strip() or "unknown"
        message = rec.get("message") or ""

        level_counts[level] = level_counts.get(level, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1

        # compliance check: sensitive markers logged at low severity
        msg_l = str(message).lower()
        if lval < LEVELS["WARNING"]:
            for marker in SENSITIVE_MARKERS:
                if marker in msg_l:
                    compliance_hits.append({
                        "timestamp": rec.get("timestamp"),
                        "level": level,
                        "source": source,
                        "marker": marker,
                        "message": message,
                    })
                    break

        if lval >= min_val:
            records.append({"ts": ts, "level": level, "lval": lval,
                            "source": source, "message": message})

    # spike detection over error+ records with timestamps
    errorish = sorted(
        (r for r in records if r["lval"] >= LEVELS["ERROR"] and r["ts"] is not None),
        key=lambda r: r["ts"],
    )
    spikes = []
    times = [r["ts"] for r in errorish]
    left = 0
    for right in range(len(times)):
        while (times[right] - times[left]).total_seconds() > window_seconds:
            left += 1
        count = right - left + 1
        if count >= spike_threshold:
            spikes.append({
                "window_start": times[left].isoformat(),
                "window_end": times[right].isoformat(),
                "error_count": count,
            })

    # collapse overlapping spike windows into the max per contiguous burst
    collapsed = []
    for spike in spikes:
        if collapsed and spike["window_start"] <= collapsed[-1]["window_end"]:
            if spike["error_count"] > collapsed[-1]["error_count"]:
                collapsed[-1] = spike
        else:
            collapsed.append(spike)

    no_ts_errors = sum(
        1 for r in records if r["lval"] >= LEVELS["ERROR"] and r["ts"] is None
    )

    return {
        "total_matched": len(records),
        "malformed_lines": malformed,
        "level_counts": level_counts,
        "source_counts": source_counts,
        "error_spikes": collapsed,
        "compliance_hits": compliance_hits,
        "errors_without_timestamp": no_ts_errors,
        "window_seconds": window_seconds,
        "spike_threshold": spike_threshold,
        "min_severity": min_severity.upper(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Inspect structured logs for error spikes and compliance issues.",
    )
    parser.add_argument("logfile", help="Path to a JSONL or CSV log file.")
    parser.add_argument(
        "--min-severity", default="ERROR",
        help="Minimum level to include in analysis (default: ERROR).",
    )
    parser.add_argument(
        "--window", default="5m",
        help="Sliding window for spike detection, e.g. 30s, 5m, 1h (default: 5m).",
    )
    parser.add_argument(
        "--spike-threshold", type=int, default=5,
        help="Errors within a window to count as a spike (default: 5).",
    )
    parser.add_argument(
        "--report", default="log_inspection_report.json",
        help="Path for the detailed JSON report (default: log_inspection_report.json).",
    )
    args = parser.parse_args(argv)

    path = Path(args.logfile)
    if not path.is_file():
        parser.error(f"Log file not found: {args.logfile}")

    try:
        window_seconds = parse_window(args.window)
    except ValueError as exc:
        parser.error(str(exc))

    result = inspect(path, args.min_severity, window_seconds, args.spike_threshold)

    if result["total_matched"] == 0 and result["malformed_lines"] == 0:
        print("No log records found.", file=sys.stderr)
        return 1

    Path(args.report).write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("=" * 56)
    print("LOG INSPECTION SUMMARY")
    print("=" * 56)
    print(f"Min severity     : {result['min_severity']}")
    print(f"Matched records  : {result['total_matched']}")
    print(f"Malformed lines  : {result['malformed_lines']}")
    print(f"Window / spike   : {args.window} / >= {result['spike_threshold']} errors")
    print("Level counts:")
    for level, count in sorted(result["level_counts"].items(),
                               key=lambda kv: -LEVELS.get(kv[0], 0)):
        print(f"  {level:<10}: {count}")
    print(f"Error spikes     : {len(result['error_spikes'])}")
    for spike in result["error_spikes"]:
        print(f"  [SPIKE] {spike['error_count']} errors "
              f"{spike['window_start']} .. {spike['window_end']}")
    if result["errors_without_timestamp"]:
        print(f"Errors w/o timestamp (not windowed): {result['errors_without_timestamp']}")
    print(f"Compliance hits  : {len(result['compliance_hits'])}")
    for hit in result["compliance_hits"][:10]:
        print(f"  [COMPLIANCE] '{hit['marker']}' at {hit['level']} "
              f"from {hit['source']}")
    print("-" * 56)
    print(f"Report written to: {args.report}")

    # non-zero exit if anomalies found, so this can gate CI/audits
    return 2 if (result["error_spikes"] or result["compliance_hits"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
