#!/usr/bin/env python3
"""Plan / apply / doctor transaction runner for agent-config writes and skill installs.

Stdlib only. Every write goes through the same contract:

    plan   -> read-only, prints exact actions, backups and exit status (writes nothing)
    apply  -> refuses without --yes, backs up, atomically replaces, verifies the result
    doctor -> re-reads the world and reports aligned | missing | drifted per action

Manifest (JSON):
{
  "version": 1,
  "actions": [
    {"id": "configure_client:claude_code", "kind": "configure_client",
     "path": "~/.claude.json", "container": "mcpServers", "name": "my-skill",
     "value": {"command": "npx", "args": ["-y", "pkg@1.2.3", "mcp"]},
     "preserve_env_keys": ["MY_OVERRIDE"]},
    {"id": "install_skill:claude_code", "kind": "install_skill",
     "target": "~/.claude/skills/my-skill", "source": "/srv/skills/my-skill"}
  ]
}

Exit codes: 0 ok/planned | 1 needs_confirmation or failed | 2 blocked (unsafe input)
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_BLOCKED = 2


class Blocked(Exception):
    """Unsafe input. Aborts the whole transaction before any write."""


def expand(p):
    return Path(os.path.expanduser(os.path.expandvars(str(p))))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_manifest(path):
    try:
        data = json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise Blocked(f"manifest not found: {path}")
    except json.JSONDecodeError as exc:
        raise Blocked(f"manifest is not valid JSON: {exc}")
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        raise Blocked("manifest has no actions")
    for i, action in enumerate(actions):
        for field in ("id", "kind"):
            if not action.get(field):
                raise Blocked(f"action #{i} is missing '{field}'")
        if action["kind"] == "configure_client" and not action.get("container"):
            raise Blocked(f"action {action['id']}: configure_client needs 'container'")
        if action["kind"] == "install_skill" and not action.get("source"):
            raise Blocked(f"action {action['id']}: install_skill needs 'source'")
    return data


def action_target(action):
    return expand(action.get("path") or action.get("target") or "")


def read_json_regular(path):
    """Return (parsed, None) or (None, block-reason). Refuses symlinks and non-files."""
    if path.is_symlink():
        return None, f"refusing symlink at {path} (managed paths must be real files)"
    if not path.exists():
        return {}, None
    if not path.is_file():
        return None, f"refusing non-file at {path}"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as exc:
        return None, f"malformed JSON in {path}: {exc}"


def container_of(doc, action):
    node = doc
    for key in str(action["container"]).split("."):
        value = node.get(key)
        if value is None:
            value = {}
            node[key] = value
        if not isinstance(value, dict):
            return None, f"{action['container']} exists but is not an object in {action_target(action)}"
        node = value
    return node, None


def desired_value(action, existing):
    value = json.loads(json.dumps(action["value"]))
    keep = action.get("preserve_env_keys") or []
    if keep and isinstance(existing, dict) and isinstance(existing.get("env"), dict):
        merged = dict(value.get("env") or {})
        for key in keep:
            if key in existing["env"]:
                merged[key] = existing["env"][key]
        if merged:
            value["env"] = merged
    return value


def inspect(action):
    """Return a dict describing one action's current state. Never writes."""
    info = {"id": action["id"], "kind": action["kind"], "target": str(action_target(action))}
    if action["kind"] == "configure_client":
        path = action_target(action)
        doc, problem = read_json_regular(path)
        if problem:
            raise Blocked(problem)
        node, problem = container_of(doc, action)
        if problem:
            raise Blocked(problem)
        existing = node.get(action["name"])
        want = desired_value(action, existing)
        info["backup_path"] = str(path) + ".backup"
        if existing is None:
            info["operation"] = "install"
            info["state"] = "missing"
        elif existing == want:
            info["operation"] = "noop"
            info["state"] = "aligned"
        else:
            info["operation"] = "update"
            info["state"] = "drifted"
        info["desired"] = want
        info["current"] = existing
        info["reason"] = (
            f"{action['container']}.{action['name']}: {info['operation']} "
            f"(unrelated keys preserved, backup at {info['backup_path']})"
        )
    else:
        target = action_target(action)
        source = expand(action["source"])
        if not source.is_dir():
            raise Blocked(f"skill source is not a directory: {source}")
        if target.is_symlink():
            raise Blocked(f"refusing symlink at {target} (managed skill dirs must be real directories)")
        if target.exists() and not target.is_dir():
            raise Blocked(f"refusing non-directory at {target}")
        installed = target / "SKILL.md"
        info["operation"] = "install" if not installed.exists() else "refresh"
        info["state"] = "aligned" if installed.exists() else "missing"
        info["reason"] = f"install {source} -> {target}"
    return info


def plan(manifest):
    return [inspect(a) for a in manifest["actions"]]


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".txn-")
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
        os.chmod(tmp, 0o600 if path.name.startswith(".") else 0o644)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def write_action(action, info):
    """Backup then write. Returns the applied record."""
    if info["operation"] == "noop":
        return {"id": action["id"], "operation": "noop", "applied": False}
    path = action_target(action)
    if action["kind"] == "install_skill":
        target_dir = path
        staging = target_dir.with_name(target_dir.name + ".txn-new")
        if staging.exists():
            shutil.rmtree(staging)
        shutil.copytree(expand(action["source"]), staging)
        if target_dir.exists():
            target_dir.rename(target_dir.with_name(target_dir.name + ".txn-old"))
        staging.rename(target_dir)
        shutil.rmtree(target_dir.with_name(target_dir.name + ".txn-old"), ignore_errors=True)
        return {"id": action["id"], "operation": info["operation"], "applied": True}

    backup = Path(info["backup_path"])
    if path.exists():
        first = digest(path)
        if not backup.exists():
            shutil.copy2(path, backup)
        elif digest(backup) != first:
            recovery = Path(str(backup) + f".{first[:16]}.recovery")
            if not recovery.exists():
                shutil.copy2(path, recovery)
    else:
        first = None

    doc = json.loads(path.read_text()) if path.exists() else {}
    node, problem = container_of(doc, action)
    if problem:
        raise Blocked(problem)
    node[action["name"]] = desired_value(action, node.get(action["name"]))
    atomic_write(path, json.dumps(doc, indent=2) + "\n")

    after = json.loads(path.read_text())
    node_after, _ = container_of(after, action)
    if node_after.get(action["name"]) != desired_value(action, node_after.get(action["name"])):
        return {"id": action["id"], "operation": info["operation"], "applied": False,
                "error": "verification failed after write", "restore_hint": str(backup)}
    return {"id": action["id"], "operation": info["operation"], "applied": True,
            "backup": info["backup_path"], "before_sha256": first}


def cmd_plan(args):
    manifest = load_manifest(args.manifest)
    try:
        actions = plan(manifest)
    except Blocked as exc:
        return emit({"status": "blocked", "error": str(exc), "plannedActions": [], "appliedActions": []},
                    args.json, EXIT_BLOCKED)
    changed = [a for a in actions if a["operation"] != "noop"]
    return emit({"status": "planned", "plannedActions": changed, "appliedActions": [],
                 "summary": f"{len(changed)} change(s), {len(actions) - len(changed)} already aligned"},
                args.json, EXIT_OK)


def cmd_apply(args):
    manifest = load_manifest(args.manifest)
    try:
        actions = plan(manifest)
    except Blocked as exc:
        return emit({"status": "blocked", "error": str(exc), "appliedActions": []}, args.json, EXIT_BLOCKED)
    changed = [a for a in actions if a["operation"] != "noop"]
    if changed and not args.yes:
        return emit({"status": "needs_confirmation", "plannedActions": changed, "appliedActions": [],
                     "summary": "re-run with --yes to apply"}, args.json, EXIT_FAIL)
    applied = [write_action(a, i) for a, i in zip(manifest["actions"], actions)]
    failed = [a for a in applied if a.get("error")]
    return emit({"status": "failed" if failed else "applied", "appliedActions": applied},
                args.json, EXIT_FAIL if failed else EXIT_OK)


def cmd_doctor(args):
    manifest = load_manifest(args.manifest)
    try:
        actions = plan(manifest)
    except Blocked as exc:
        return emit({"status": "blocked", "error": str(exc), "checks": []}, args.json, EXIT_BLOCKED)
    checks = [{"id": a["id"], "state": a["state"], "target": a["target"], "operation": a["operation"]}
              for a in actions]
    aligned = all(c["state"] == "aligned" for c in checks)
    return emit({"status": "healthy" if aligned else "unhealthy", "checks": checks},
                args.json, EXIT_OK if aligned else EXIT_FAIL)


def emit(payload, as_json, code):
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"status: {payload['status']}")
        for key in ("summary", "error"):
            if payload.get(key):
                print(f"{key}: {payload[key]}")
        for action in payload.get("plannedActions") or payload.get("checks") or []:
            if isinstance(action, dict):
                print(f"  - {action.get('id')}: {action.get('operation') or action.get('state')} "
                      f"-> {action.get('target')}")
        for action in payload.get("appliedActions") or []:
            if isinstance(action, dict):
                print(f"  * {action.get('id')}: {action.get('operation')} applied={action.get('applied')}")
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["plan", "apply", "doctor"])
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--yes", action="store_true", help="approve the plan (apply only)")
    args = parser.parse_args(argv)
    return {"plan": cmd_plan, "apply": cmd_apply, "doctor": cmd_doctor}[args.command](args)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)
    sys.exit(main())
