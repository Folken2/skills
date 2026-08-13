#!/usr/bin/env python3
"""Automated skill evaluation for a Nuvel Skills theme.

For each skill in a theme, spawn a fresh Claude Code subagent, hand it a
realistic scenario, capture its output, and score it by keyword-matching
against the skill's own workflow steps and expected scenario steps.

Usage:
    python3 evaluate.py <theme>        # e.g. hr

Prints a JSON evaluation report to stdout.
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Repo root is four levels up: scripts/ -> skill-evaluation/ -> skillification/ -> skills/ -> repo
REPO_ROOT = Path(__file__).resolve().parents[4]
SCENARIO_DIR = Path(__file__).resolve().parents[1] / "scenarios"

CLAUDE_BIN = "/opt/data/.local/bin/claude"

# Hardcoded fallback scenarios for common themes (used when no scenarios/<theme>.json exists).
HARDCODED_SCENARIOS = {
    "hr": {
        "hiring": {
            "scenario": "We need to hire a senior backend engineer. Walk through the full hiring process from req to offer acceptance.",
            "expected_steps": ["requisition", "screening", "interview", "offer", "background", "closeout"],
        },
        "employee-onboarding": {
            "scenario": "A senior backend engineer is starting Monday. Walk through the full onboarding process.",
            "expected_steps": ["paperwork", "equipment", "access", "orientation", "buddy", "30-60-90"],
        },
        "employee-engagement": {
            "scenario": "An engineer has been disengaged for 3 months. Walk through the engagement process.",
            "expected_steps": ["1:1", "feedback", "review", "growth", "recognition", "stay interview", "exit"],
        },
    }
}

# Pass/partial thresholds on combined coverage.
PASS_THRESHOLD = 0.80
PARTIAL_THRESHOLD = 0.50


def load_scenarios(theme):
    """Prefer scenarios/<theme>.json, then hardcoded, then empty (generic per-skill)."""
    scenario_file = SCENARIO_DIR / f"{theme}.json"
    if scenario_file.exists():
        return json.loads(scenario_file.read_text())
    return HARDCODED_SCENARIOS.get(theme, {})


def generic_scenario(skill_name):
    """Fallback scenario for a skill with no pre-defined test."""
    pretty = skill_name.replace("-", " ")
    return {
        "scenario": f"A realistic situation requiring the '{pretty}' process has arisen. "
        f"Walk through the full process step-by-step.",
        "expected_steps": [],
    }


def parse_workflow_steps(skill_md):
    """Extract the bold step titles from the '## Workflow' numbered list.

    Returns a list of lowercase keyword phrases (the bold '**Title.**' of each step).
    """
    text = skill_md
    m = re.search(r"^## Workflow\s*$(.*?)^## ", text, re.MULTILINE | re.DOTALL)
    section = m.group(1) if m else text
    steps = []
    for line in section.splitlines():
        line = line.strip()
        sm = re.match(r"^\d+\.\s+\*\*(.+?)\*\*", line)
        if sm:
            # Keep the first clause of the bold title (drop trailing period).
            title = sm.group(1).strip().rstrip(".")
            steps.append(title.lower())
    return steps


def keyword_hit(keyword, haystack):
    """Loose containment match: any token of a multi-word keyword counts as a hit
    if the whole phrase isn't present, so '1:1 cadence' matches text mentioning 1:1."""
    kw = keyword.lower().strip()
    if not kw:
        return False
    if kw in haystack:
        return True
    # Split on non-alphanumerics; require the most distinctive token to appear.
    tokens = [t for t in re.split(r"[^a-z0-9:+-]+", kw) if len(t) > 2]
    return any(t in haystack for t in tokens)


def score_output(output, workflow_steps, expected_steps):
    """Score the subagent output against workflow steps and expected scenario steps.

    Coverage = fraction of workflow step titles mentioned in the output.
    expected_steps provide an independent scenario-level signal folded into notes.
    """
    hay = output.lower()

    wf_hits = [s for s in workflow_steps if keyword_hit(s, hay)]
    wf_coverage = (len(wf_hits) / len(workflow_steps)) if workflow_steps else 0.0

    exp_hits = [s for s in expected_steps if keyword_hit(s, hay)]
    exp_coverage = (len(exp_hits) / len(expected_steps)) if expected_steps else None

    # Combined coverage: average of the two signals when both exist, else whichever exists.
    if expected_steps and workflow_steps:
        coverage = (wf_coverage + exp_coverage) / 2
    elif expected_steps:
        coverage = exp_coverage
    else:
        coverage = wf_coverage

    if coverage >= PASS_THRESHOLD:
        verdict = "pass"
    elif coverage >= PARTIAL_THRESHOLD:
        verdict = "partial"
    else:
        verdict = "fail"

    missed_wf = [s for s in workflow_steps if s not in wf_hits]
    notes_parts = [
        f"{len(wf_hits)}/{len(workflow_steps)} workflow steps covered" if workflow_steps else "no workflow steps parsed",
    ]
    if expected_steps:
        notes_parts.append(f"{len(exp_hits)}/{len(expected_steps)} expected scenario steps covered")
    if missed_wf:
        notes_parts.append("missing: " + ", ".join(missed_wf[:5]))
    if not output.strip():
        notes_parts.append("EMPTY OUTPUT — subagent produced nothing")
        verdict = "fail"

    return verdict, round(coverage * 100, 1), "; ".join(notes_parts)


def run_subagent(skill_name, scenario):
    """Spawn a Claude Code subagent for one skill+scenario. Returns captured stdout."""
    prompt = (
        f"You are an HR agent. You have been trained on a specific SOP about {skill_name}. "
        f"Walk through the process step-by-step for: {scenario}. Be specific and concrete."
    )
    cmd = [
        CLAUDE_BIN,
        "--model", "opus",
        "--effort", "medium",
        "--max-turns", "10",
        "--dangerously-skip-permissions",
        "-p", prompt,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        out = proc.stdout or ""
        if not out.strip() and proc.stderr:
            out = f"[stderr] {proc.stderr.strip()}"
        return out
    except subprocess.TimeoutExpired:
        return "[error] subagent timed out"
    except Exception as e:  # noqa: BLE001
        return f"[error] {e}"


def main():
    if len(sys.argv) < 2:
        print("usage: evaluate.py <theme>", file=sys.stderr)
        sys.exit(2)

    theme = sys.argv[1]
    theme_dir = REPO_ROOT / "skills" / theme
    if not theme_dir.is_dir():
        print(json.dumps({"error": f"theme not found: {theme_dir}"}))
        sys.exit(1)

    scenarios = load_scenarios(theme)

    skill_files = sorted(theme_dir.glob("*/SKILL.md"))
    results = []
    passes = 0

    for skill_md_path in skill_files:
        skill_name = skill_md_path.parent.name
        skill_md = skill_md_path.read_text()
        workflow_steps = parse_workflow_steps(skill_md)

        scenario_def = scenarios.get(skill_name) or generic_scenario(skill_name)
        scenario_text = scenario_def["scenario"]
        expected_steps = scenario_def.get("expected_steps", [])

        print(f"[eval] running subagent for '{skill_name}'...", file=sys.stderr)
        output = run_subagent(skill_name, scenario_text)

        verdict, coverage, notes = score_output(output, workflow_steps, expected_steps)
        if verdict == "pass":
            passes += 1

        results.append(
            {
                "skill": skill_name,
                "score": verdict,
                "notes": notes,
                "coverage": coverage,
            }
        )

    theme_score = round((passes / len(skill_files) * 100), 1) if skill_files else 0.0

    report = {
        "theme": theme,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "theme_score": theme_score,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
