#!/usr/bin/env python3
"""Fleet management CLI — wraps `nuvel fleet` / `nuvel bots`.

Keeps a fleet of enterprise bots healthy: show fleet status, inspect a bot
(details + logs), change a bot's model, and run a health check that pings every
bot in the fleet.

If the `nuvel` CLI is not on PATH, commands fall back to the `hermes` runtime
(`hermes -p <bot> ...`) which operates on a single bot profile directly.

Stdlib-only (subprocess, json, shutil, argparse, sys).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def _have(cmd: str) -> bool:
    """True if `cmd` is an executable on PATH."""
    return shutil.which(cmd) is not None


def _run(argv: list[str]) -> subprocess.CompletedProcess:
    """Run a command, capturing output. Never raises on non-zero exit."""
    try:
        return subprocess.run(
            argv, capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(argv, 127, "", f"not found: {argv[0]}")


def _emit(proc: subprocess.CompletedProcess) -> None:
    """Print captured stdout/stderr from a completed process."""
    if proc.stdout:
        sys.stdout.write(proc.stdout)
        if not proc.stdout.endswith("\n"):
            sys.stdout.write("\n")
    if proc.stderr:
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")


def _nuvel(*args: str) -> subprocess.CompletedProcess:
    return _run(["nuvel", *args])


def _hermes(*args: str) -> subprocess.CompletedProcess:
    return _run(["hermes", *args])


def cmd_status(args: argparse.Namespace) -> int:
    """Show fleet status."""
    if _have("nuvel"):
        proc = _nuvel("fleet", "status", args.fleet)
        _emit(proc)
        return proc.returncode
    sys.stderr.write(
        "nuvel not found: cannot query fleet status directly.\n"
        "hermes operates per-bot; pass individual bot names to `inspect`.\n"
    )
    return 1


def cmd_inspect(args: argparse.Namespace) -> int:
    """Show a bot's details plus its recent logs."""
    bot = args.bot
    if _have("nuvel"):
        info = _nuvel("bots", "info", bot)
        logs = _nuvel("bots", "logs", bot, "-n", str(args.lines))
    else:
        info = _hermes("-p", bot, "config", "list")
        logs = _hermes("-p", bot, "logs", "-n", str(args.lines))

    print(f"=== bot: {bot} — details ===")
    _emit(info)
    print(f"\n=== bot: {bot} — last {args.lines} log lines ===")
    _emit(logs)
    return info.returncode or logs.returncode


def cmd_update_model(args: argparse.Namespace) -> int:
    """Change a bot's model, then re-read it to confirm."""
    bot, model = args.bot, args.model
    if _have("nuvel"):
        edit = _nuvel("bots", "edit", bot, "--model", model)
        _emit(edit)
        if edit.returncode != 0:
            return edit.returncode
        confirm = _nuvel("bots", "info", bot)
    else:
        edit = _hermes("-p", bot, "config", "set", "model", model)
        _emit(edit)
        if edit.returncode != 0:
            return edit.returncode
        confirm = _hermes("-p", bot, "config", "get", "model")

    print(f"\n=== bot: {bot} — model after update ===")
    _emit(confirm)
    return confirm.returncode


def _fleet_bots(fleet: str) -> list[str]:
    """Best-effort list of bot names in a fleet via `nuvel fleet status`.

    Tries JSON output first, then falls back to parsing the first token of each
    non-header line. Returns [] if the fleet cannot be enumerated.
    """
    proc = _nuvel("fleet", "status", fleet, "--json")
    if proc.returncode == 0 and proc.stdout.strip():
        try:
            data = json.loads(proc.stdout)
            bots = data.get("bots", data) if isinstance(data, dict) else data
            names = []
            for b in bots:
                if isinstance(b, dict):
                    name = b.get("name") or b.get("bot")
                    if name:
                        names.append(str(name))
                elif isinstance(b, str):
                    names.append(b)
            if names:
                return names
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    proc = _nuvel("fleet", "status", fleet)
    if proc.returncode != 0:
        return []
    names = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.lower().startswith(("name", "bot", "===", "---")):
            continue
        names.append(line.split()[0])
    return names


def _ping(bot: str) -> bool:
    """Return True if the bot responds to a trivial prompt."""
    if _have("nuvel"):
        proc = _nuvel("bots", "logs", bot, "-n", "1")
        return proc.returncode == 0
    proc = _hermes("-p", bot, "-p", "ping")
    return proc.returncode == 0


def cmd_health(args: argparse.Namespace) -> int:
    """Ping every bot in the fleet and report health."""
    if not _have("nuvel"):
        sys.stderr.write(
            "nuvel not found: cannot enumerate the fleet.\n"
            "Health checks require the nuvel CLI.\n"
        )
        return 1

    bots = _fleet_bots(args.fleet)
    if not bots:
        sys.stderr.write(f"No bots found in fleet '{args.fleet}'.\n")
        return 1

    print(f"=== health check: fleet '{args.fleet}' ({len(bots)} bots) ===")
    unhealthy = 0
    for bot in bots:
        ok = _ping(bot)
        status = "HEALTHY" if ok else "UNHEALTHY"
        if not ok:
            unhealthy += 1
        print(f"  {status:<10} {bot}")

    print(f"\n{len(bots) - unhealthy}/{len(bots)} healthy, {unhealthy} unhealthy")
    return 0 if unhealthy == 0 else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manage_fleet.py",
        description="Manage a fleet of enterprise bots (status, inspect, "
        "update-model, health).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show fleet status")
    p_status.add_argument("fleet", help="Fleet name")
    p_status.set_defaults(func=cmd_status)

    p_inspect = sub.add_parser("inspect", help="Show bot details + logs")
    p_inspect.add_argument("bot", help="Bot name")
    p_inspect.add_argument(
        "-n", "--lines", type=int, default=50, help="Log lines (default 50)"
    )
    p_inspect.set_defaults(func=cmd_inspect)

    p_model = sub.add_parser("update-model", help="Change a bot's model")
    p_model.add_argument("bot", help="Bot name")
    p_model.add_argument("model", help="New model identifier")
    p_model.set_defaults(func=cmd_update_model)

    p_health = sub.add_parser("health", help="Ping all bots, report health")
    p_health.add_argument("fleet", help="Fleet name")
    p_health.set_defaults(func=cmd_health)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
