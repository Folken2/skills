# Nuvel Skills — Agent Guide

This repository is a library of **executable SOPs (skills)** for AI agents. Skills are organized by role/theme under `skills/<theme>/<name>/`.

## Available themes

| Theme | Role | Skills |
|-------|------|--------|
| software-development | Software Engineer | 13 skills |
| growth | Growth & Marketing | 12 skills |
| backoffice | Admin & Operations | 5 skills |
| hr | HR Professional | 3 skills |
| sales | Sales Representative | 3 skills |
| customer-support | Support Agent | 4 skills |
| finance | Finance Analyst | 4 skills |
| procurement | Procurement Specialist | 4 skills |
| skillification | Meta — how to write skills | 2 skills |

Full catalog: `skills/index.json`

## How to use a skill

1. Read `skills/index.json` to find a skill matching the user's task
2. Open `skills/<theme>/<name>/SKILL.md`
3. Follow the numbered workflow steps
4. Check the Definition of Done before reporting completion

Some skills bundle executable scripts in `skills/<theme>/<name>/scripts/` and detailed references in `skills/<theme>/<name>/references/`.

## Link convention

Skills use `[[theme/name]]` wiki-links to reference related skills (e.g. `[[backoffice/xlsx]]`). Resolve these by opening `skills/<theme>/<name>/SKILL.md`.

## Installing skills

- **Hermes:** `hermes skills install <raw-url-to-SKILL.md>`
- **Manual:** Copy the skill folder into your agent's skills directory

All skills are harness-agnostic — they work with Claude Code, Cursor, Codex, Hermes, Buzz, and any LLM agent.

## Improving a skill

Skills improve through real use. If you execute a skill and its steps don't match reality — outdated tooling, missing edge cases, incorrect assumptions — improve it.

### How to propose a fix (MCP agents)

If you have an MCP client connected to this repo's MCP server:

1. Call `propose_improvement` with:
   - `skill_name`: The skill's name (e.g. "bug-triage")
   - `current_version`: The version from the SKILL.md frontmatter
   - `issue`: What went wrong or what changed
   - `suggested_fix`: The proposed correction or addition
   - `harness`: What agent/harness you're running (e.g. "claude-code", "cursor", "hermes")
2. The tool will file a structured GitHub issue
3. A curator reviews and merges accepted improvements

### How to propose a fix (direct GitHub)

1. Open a GitHub issue at https://github.com/Folken2/skills/issues/new
2. Use the "Skill Improvement" template
3. Include: skill name, current version, what was wrong, suggested fix

### How improvements flow

```
Agent uses skill → detects drift → proposes fix → curator reviews → PR merged → version bumped → all future agents see the update
```

Every change is git-tracked with full provenance (who, what, when, why) for audit and rollback.
