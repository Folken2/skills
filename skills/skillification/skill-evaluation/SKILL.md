---
name: skill-evaluation
description: "Automated evaluation of a theme's skills — spawn subagents with only those skills, run scenario tests, score against exit criteria."
version: 1.0.0
author: Nuvel Skills
---

# Skill Evaluation

## When to use this
Use when you want objective evidence that the skills in a theme actually work — before promoting a theme, after editing a skill's workflow, or on a cadence to catch skills that have gone stale. This is the meta-layer sibling of [[skill-promotion]]: promotion decides *whether* a skill enters the repo; evaluation measures *how well* the skills already there hold up under a realistic scenario.

## What it measures
For each skill in a theme, an agent that has been given only that skill is asked to run a realistic, pre-defined scenario. Its output is scored against four criteria:

- **Workflow adherence** — did it follow the numbered steps in the skill's `## Workflow`, in a sensible order?
- **Artifact completeness** — did it produce the outputs the skill promises (the deliverables named in the workflow and `## Exit criteria`)?
- **Missing steps** — did it skip any workflow step or exit criterion?
- **Hallucination** — did it invent steps, tools, or requirements that are *not* in the SOP?

A skill scores **pass / partial / fail** on combined coverage. The **theme-level score** is the percentage of skills in the theme that PASS.

## Methodology

### Phase 1: Scope the theme
1. List every `skills/<theme>/*/SKILL.md`.
2. For each skill, load its `## Workflow` numbered steps and `## Exit criteria` — these are the scoring rubric. Do not invent criteria the skill doesn't claim.

### Phase 2: Pick scenarios
1. Prefer a pre-defined scenario from `scenarios/<theme>.json` (`{"<skill>": {"scenario": "...", "expected_steps": [...]}}`).
2. Fall back to a hardcoded scenario for common themes, then to a generic "walk through the full process" scenario for unknown skills.
3. A good scenario is concrete and end-to-end (a specific role, a specific situation) so the agent has to traverse the whole workflow, not just name it.

### Phase 3: Run the subagents
1. For each skill, spawn a **fresh** Claude Code subagent so there is no cross-contamination between skills.
2. Give it the scenario and ask it to walk the process step-by-step, concretely.
3. Capture the full output. An empty output is an automatic fail.

### Phase 4: Score
1. Match the output against the skill's workflow step titles and the scenario's `expected_steps` (case-insensitive keyword coverage).
2. Coverage ≥ 80% → **pass**, ≥ 50% → **partial**, else **fail**.
3. Note which steps were missed and flag anything that reads as hallucinated (not present in the SOP).

### Phase 5: Report
Emit a structured JSON report:

```json
{
  "theme": "hr",
  "evaluated_at": "<ISO-8601>",
  "results": [
    {"skill": "hiring", "score": "pass", "notes": "...", "coverage": 87.5}
  ],
  "theme_score": 66.7
}
```

## Running it
```bash
python3 skills/skillification/skill-evaluation/scripts/evaluate.py <theme>
```
The script (`scripts/evaluate.py`) drives Phases 1–5 automatically. It spawns each subagent with:
```
claude --model opus --effort medium --max-turns 10 --dangerously-skip-permissions -p "<scenario prompt>"
```
Add or edit scenarios in `scenarios/<theme>.json`; unknown themes get a generic scenario per skill.

## Interpreting results
- **A skill fails** → its workflow is under-specified, the scenario doesn't exercise it, or the agent genuinely skipped steps. Read the `notes` before blaming the skill.
- **Partial across the board** → often a scenario or scoring-keyword mismatch, not a broken skill. Tighten `expected_steps`.
- **A low theme score** → do not promote the theme (see [[skill-promotion]]) until the failing skills are fixed and re-evaluated.

## Exit criteria
- [ ] Every skill in the theme was run against a scenario in a fresh subagent.
- [ ] Each skill has a pass/partial/fail verdict with coverage % and notes.
- [ ] A theme-level score (% of skills passing) is recorded.
- [ ] The JSON report is captured and attached to the promotion/PR decision.
