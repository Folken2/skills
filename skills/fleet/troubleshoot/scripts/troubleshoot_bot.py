#!/usr/bin/env python3
"""Bot troubleshooting CLI — diagnose and repair a single enterprise bot.

A bot's state lives in its profile directory (`~/.hermes/profiles/<bot>/`):
config, installed skills, and logs. This tool inspects that directory, verifies
the pieces exist, reads recent logs, and can reinstall a skill.

Subcommands:
    diagnose <bot>          Full diagnostic (profile, config, skills, logs)
    check-logs <bot> -n N   Show the last N log lines
    verify-skills <bot>     Verify each configured skill exists on disk
    reinstall <bot> <skill> Remove and re-add a skill

If the `nuvel` CLI is not on PATH, log/skill operations fall back to the
`hermes` runtime. Stdlib-only (subprocess, json, pathlib, argparse, sys).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

OK = "OK"
WARN = "WARN"
FAIL = "FAIL"


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _run(argv: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(argv, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return subprocess.CompletedProcess(argv, 127, "", f"not found: {argv[0]}")


def _profile_dir(bot: str) -> Path:
    return Path.home() / ".hermes" / "profiles" / bot


def _status(label: str, state: str, detail: str = "") -> None:
    line = f"  [{state:<4}] {label}"
    if detail:
        line += f" — {detail}"
    print(line)


def _configured_skills(bot: str) -> list[str]:
    """Skills a bot is *configured* to have.

    Reads the profile config (config.json) if present, else asks the CLI.
    Returns [] if it cannot be determined.
    """
    cfg = _profile_dir(bot) / "config.json"
    if cfg.is_file():
        try:
            data = json.loads(cfg.read_text())
            skills = data.get("skills", [])
            if isinstance(skills, list):
                return [str(s) for s in skills]
        except (json.JSONDecodeError, OSError):
            pass

    if _have("nuvel"):
        proc = _run(["nuvel", "bots", "info", bot, "--json"])
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                data = json.loads(proc.stdout)
                skills = data.get("skills", [])
                if isinstance(skills, list):
                    return [str(s) for s in skills]
            except json.JSONDecodeError:
                pass
    return []


def _installed_skills(bot: str) -> list[str]:
    """Skill directories actually present on disk."""
    skills_dir = _profile_dir(bot) / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(p.name for p in skills_dir.iterdir() if p.is_dir())


def cmd_check_logs(args: argparse.Namespace) -> int:
    """Show the bot's recent logs."""
    bot, n = args.bot, args.lines
    if _have("nuvel"):
        proc = _run(["nuvel", "bots", "logs", bot, "-n", str(n)])
    elif _have("hermes"):
        proc = _run(["hermes", "-p", bot, "logs", "-n", str(n)])
    else:
        # Fall back to reading a log file from the profile directory.
        log = _profile_dir(bot) / "logs" / "bot.log"
        if not log.is_file():
            sys.stderr.write(f"No CLI and no log file at {log}\n")
            return 1
        lines = log.read_text(errors="replace").splitlines()
        print("\n".join(lines[-n:]))
        return 0

    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc.returncode


def cmd_verify_skills(args: argparse.Namespace) -> int:
    """Verify each configured skill exists on disk with a SKILL.md."""
    bot = args.bot
    profile = _profile_dir(bot)
    print(f"=== verify-skills: {bot} ===")

    if not profile.is_dir():
        _status(f"profile {profile}", FAIL, "profile not found")
        return 2

    configured = _configured_skills(bot)
    installed = _installed_skills(bot)
    skills_dir = profile / "skills"

    if not skills_dir.is_dir():
        _status(f"skills dir {skills_dir}", FAIL, "missing")
        return 2
    _status(f"skills dir {skills_dir}", OK, f"{len(installed)} installed")

    problems = 0
    if not configured:
        _status("configured skills", WARN, "could not read config; listing disk only")
        for name in installed:
            has_md = (skills_dir / name / "SKILL.md").is_file()
            _status(name, OK if has_md else WARN,
                    "SKILL.md present" if has_md else "no SKILL.md")
            problems += 0 if has_md else 1
    else:
        for name in configured:
            sk = skills_dir / name
            if not sk.is_dir():
                _status(name, FAIL, "configured but not on disk")
                problems += 1
            elif not (sk / "SKILL.md").is_file():
                _status(name, FAIL, "directory present but no SKILL.md")
                problems += 1
            else:
                _status(name, OK, "installed")

    print(f"\n{problems} problem(s) found")
    return 0 if problems == 0 else 2


def cmd_diagnose(args: argparse.Namespace) -> int:
    """Run a full diagnostic across profile, config, skills, and logs."""
    bot = args.bot
    profile = _profile_dir(bot)
    print(f"=== diagnose: {bot} ===")

    problems = 0

    # 1. Profile directory
    if profile.is_dir():
        _status(f"profile {profile}", OK, "exists")
    else:
        _status(f"profile {profile}", FAIL, "profile not found — escalate")
        print("\n1 critical problem: profile not found")
        return 2

    # 2. Config: model
    model = None
    cfg = profile / "config.json"
    if cfg.is_file():
        try:
            data = json.loads(cfg.read_text())
            model = data.get("model")
            api_key = data.get("api_key", data.get("apiKey"))
        except (json.JSONDecodeError, OSError):
            data, api_key = {}, None
    else:
        data, api_key = {}, None
        if _have("hermes"):
            proc = _run(["hermes", "-p", bot, "config", "get", "model"])
            if proc.returncode == 0:
                model = proc.stdout.strip() or None

    if model:
        _status("model", OK, str(model))
    else:
        _status("model", WARN, "model not set or unreadable")
        problems += 1

    # 3. Config: API key (presence only — never print the value)
    if cfg.is_file():
        if api_key:
            _status("api_key", OK, "present")
        else:
            _status("api_key", FAIL, "empty or missing — escalate")
            problems += 1
    else:
        _status("api_key", WARN, "config.json not found; cannot verify")

    # 4. Skills
    installed = _installed_skills(bot)
    configured = _configured_skills(bot)
    if configured:
        missing = [s for s in configured if s not in installed]
        if missing:
            _status("skills", FAIL, f"missing on disk: {', '.join(missing)}")
            problems += 1
        else:
            _status("skills", OK, f"{len(configured)} configured, all present")
    elif installed:
        _status("skills", OK, f"{len(installed)} installed (config unread)")
    else:
        _status("skills", WARN, "no skills installed")

    # 5. Logs (recent tail)
    print(f"\n--- recent logs ({bot}) ---")
    log_rc = cmd_check_logs(argparse.Namespace(bot=bot, lines=10))
    if log_rc != 0:
        _status("logs", WARN, "could not read logs")

    print(f"\n{problems} problem(s) found")
    return 0 if problems == 0 else 2


def cmd_reinstall(args: argparse.Namespace) -> int:
    """Reinstall a skill: remove it, then re-add it, then verify on disk."""
    bot, skill = args.bot, args.skill
    profile = _profile_dir(bot)
    if not profile.is_dir():
        sys.stderr.write(f"profile not found: {profile} — escalate\n")
        return 2

    configured = _configured_skills(bot)
    if configured:
        remaining = [s for s in configured if s != skill]
        target = remaining + [skill]
    else:
        remaining, target = None, None

    if _have("nuvel"):
        if remaining is not None:
            rm = _run(["nuvel", "bots", "edit", bot, "--skills", "+".join(remaining)])
            if rm.stdout:
                sys.stdout.write(rm.stdout)
            if rm.returncode != 0:
                sys.stderr.write(rm.stderr)
                return rm.returncode
        add_list = "+".join(target) if target else skill
        add = _run(["nuvel", "bots", "edit", bot, "--skills", add_list])
        if add.stdout:
            sys.stdout.write(add.stdout)
        if add.returncode != 0:
            sys.stderr.write(add.stderr)
            return add.returncode
    else:
        sys.stderr.write(
            "nuvel not found: cannot edit skill set automatically.\n"
            f"Manually remove and re-add '{skill}' for bot '{bot}'.\n"
        )
        return 1

    # Verify the skill landed on disk.
    sk = profile / "skills" / skill
    if sk.is_dir() and (sk / "SKILL.md").is_file():
        _status(skill, OK, "reinstalled and present on disk")
        return 0
    _status(skill, FAIL, "reinstall did not produce a valid skill dir — escalate")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="troubleshoot_bot.py",
        description="Diagnose and repair a single enterprise bot.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_diag = sub.add_parser("diagnose", help="Full diagnostic")
    p_diag.add_argument("bot", help="Bot name")
    p_diag.set_defaults(func=cmd_diagnose)

    p_logs = sub.add_parser("check-logs", help="Show recent logs")
    p_logs.add_argument("bot", help="Bot name")
    p_logs.add_argument(
        "-n", "--lines", type=int, default=30, help="Log lines (default 30)"
    )
    p_logs.set_defaults(func=cmd_check_logs)

    p_verify = sub.add_parser("verify-skills", help="Verify skill installation")
    p_verify.add_argument("bot", help="Bot name")
    p_verify.set_defaults(func=cmd_verify_skills)

    p_re = sub.add_parser("reinstall", help="Reinstall a skill")
    p_re.add_argument("bot", help="Bot name")
    p_re.add_argument("skill", help="Skill name to reinstall")
    p_re.set_defaults(func=cmd_reinstall)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
