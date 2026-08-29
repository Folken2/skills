#!/usr/bin/env python3
"""Audit a directory of skills against the Agent Plugins SKILL.md spec (v1.0.0).

Usage:
    python3 audit_skills.py [--json] [path]

Checks:
1. Frontmatter opens at byte 0 (---)
2. Required fields: name (lowercase, 1-64 chars), description (≤ 1024 chars)
3. Frontmatter closes with --- followed by non-empty body
4. File size ≤ 100,000 chars
5. Name matches directory name
6. Supporting files in allowed subdirs only (scripts/, references/, templates/, assets/)

Reports orphan directories (files but no SKILL.md) and skill subdir structure.
"""

import json
import os
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict | None:
    """Parse YAML frontmatter from SKILL.md content. Returns dict or None."""
    if not content.startswith("---"):
        return None
    # Find closing ---
    rest = content[3:]
    m = re.search(r"\n---\s*\n", rest)
    if not m:
        return None
    fm_text = rest[: m.start()]
    # Simple YAML key-value parser (no nested object support needed)
    result = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # Handle nested keys by prefix
            if key.startswith(" ") or key.startswith("-"):
                continue
            # Only parse top-level keys
            if " " not in key and not key.startswith("-"):
                result[key] = val
    return result


def audit_skill_dir(skill_dir: Path) -> list[str]:
    """Audit a single skill directory. Returns list of issue strings (empty = PASS)."""
    issues = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        issues.append("no SKILL.md in directory")
        return issues

    content = skill_md.read_text(encoding="utf-8", errors="replace")

    # Check 1: Opens at byte 0
    if not content.startswith("---"):
        issues.append("file does not start with --- at byte 0")
        return issues

    # Parse frontmatter
    fm = parse_frontmatter(content)
    if fm is None:
        issues.append("could not parse YAML frontmatter")
        return issues

    # Check 2: Required fields
    if "name" not in fm or not fm["name"].strip():
        issues.append("missing field: name")
    else:
        name = fm["name"]
        if len(name) > 64:
            issues.append(f"name too long ({len(name)} chars > 64)")
        if not re.match(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$", name):
            issues.append(f"invalid name format: '{name}'")

    if "description" not in fm or not fm["description"].strip():
        issues.append("missing field: description")
    else:
        desc = fm["description"]
        if len(desc) > 1024:
            issues.append(f"description too long ({len(desc)} chars > 1024)")

    # Check 3: Frontmatter closes, body exists
    rest = content[3:]
    m = re.search(r"\n---\s*\n", rest)
    if not m:
        issues.append("frontmatter closing --- not found")
        return issues
    body = rest[m.end() :].strip()
    if not body:
        issues.append("empty body after frontmatter")

    # Check 4: File size
    if len(content) > 100_000:
        issues.append(f"file too large ({len(content)} chars > 100000)")

    # Check 5: Name matches directory name
    if "name" in fm:
        dir_name = skill_dir.name
        if fm["name"] != dir_name:
            issues.append(f"name '{fm['name']}' does not match directory name '{dir_name}'")

    # Check 6: Supporting files in allowed subdirs only
    allowed_subdirs = {"scripts", "references", "templates", "assets"}
    for item in skill_dir.iterdir():
        if item.name == "SKILL.md":
            continue
        if item.is_dir():
            if item.name not in allowed_subdirs:
                issues.append(f"unsupported subdirectory: {item.name}")
        elif item.is_file():
            issues.append(f"loose file at skill root: {item.name}")

    return issues


def find_orphan_dirs(root: Path) -> list[str]:
    """Find directories that have files but NO SKILL.md anywhere beneath."""
    orphans = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip . directories
        dirpath_p = Path(dirpath)
        if any(part.startswith(".") for part in dirpath_p.relative_to(root).parts):
            continue
        # Skip the root itself
        if dirpath_p == root:
            continue
        # Skip allowed subdirs if they're under a skill
        if dirpath_p.parent.name in ("scripts", "references", "templates", "assets"):
            # Only flag if the parent skill doesn't exist
            skill_parent = dirpath_p.parent.parent
            if (skill_parent / "SKILL.md").exists():
                continue
        # Check if this dir or any ancestor has SKILL.md
        has_skill = any(
            p.name == "SKILL.md"
            for p in dirpath_p.rglob("*")
            if p.is_file()
        )
        if not has_skill and filenames:
            orphans.append(str(dirpath_p))
    return sorted(set(orphans))


def main():
    root_dir = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else Path.cwd()
    output_json = "--json" in sys.argv

    if not root_dir.exists() or not root_dir.is_dir():
        print(f"Error: {root_dir} is not a valid directory")
        sys.exit(1)

    # Find all SKILL.md files
    skill_files = sorted(root_dir.rglob("SKILL.md"))
    total = len(skill_files)

    results = []
    passes = 0
    failures = 0

    for sk_path in skill_files:
        issues = audit_skill_dir(sk_path.parent)
        rel_path = sk_path.relative_to(root_dir)
        if issues:
            failures += 1
            results.append({
                "path": str(rel_path),
                "dir": sk_path.parent.name,
                "issues": issues,
                "status": "FAIL",
            })
        else:
            passes += 1
            results.append({
                "path": str(rel_path),
                "dir": sk_path.parent.name,
                "issues": [],
                "status": "PASS",
            })

    # Find orphan directories
    orphans = find_orphan_dirs(root_dir)
    # Filter: only report true orphans (no SKILL.md in any subdir)
    true_orphans = []
    for o in orphans:
        o_path = Path(o)
        if not o_path.name.startswith("."):
            has_skill_anywhere = any(
                p.name == "SKILL.md"
                for p in o_path.rglob("*")
                if p.is_file()
            )
            if not has_skill_anywhere:
                files = [f.name for f in o_path.iterdir() if f.is_file()]
                true_orphans.append({"dir": o, "files": files})

    # Supporting subdirs per skill
    supporting = {}
    for sk_path in skill_files:
        rel = sk_path.relative_to(root_dir)
        skill_name = str(rel.parent)
        subdirs = []
        for item in sk_path.parent.iterdir():
            if item.is_dir() and item.name in ("scripts", "references", "templates", "assets"):
                subdirs.append(item.name)
        if subdirs:
            supporting[str(rel)] = subdirs

    if output_json:
        report = {
            "total": total,
            "pass": passes,
            "fail": failures,
            "failures": [r for r in results if r["status"] == "FAIL"],
            "orphan_dirs": true_orphans,
            "supporting_dirs": supporting,
        }
        print(json.dumps(report, indent=2))
        return

    # Text output
    print("=" * 70)
    print(f"SKILL.md AUDIT REPORT — {root_dir}")
    print("=" * 70)
    print(f"Total SKILL.md files found: {total}")
    print(f"PASS: {passes}")
    print(f"FAIL: {failures}")
    print()

    if failures > 0:
        print("-" * 70)
        print("FAILURES:")
        print("-" * 70)
        for r in results:
            if r["status"] == "FAIL":
                print(f"  {r['path']}")
                for issue in r["issues"]:
                    print(f"    ⚠ {issue}")
        print()

    if true_orphans:
        print("-" * 70)
        print("ORPHAN DIRECTORIES (files but no SKILL.md beneath):")
        print("-" * 70)
        for o in true_orphans:
            print(f"  {o['dir']}/  → files: {o['files']}")
        print()

    if supporting:
        print("-" * 70)
        print("SKILLS WITH SUPPORTING SUBDIRS:")
        print("-" * 70)
        for path, dirs in sorted(supporting.items()):
            print(f"  {path}: {dirs}")


if __name__ == "__main__":
    main()