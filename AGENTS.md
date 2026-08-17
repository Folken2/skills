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

### How to propose a fix (via Nuvel)

If you have Nuvel installed:

1. Run `nuvel mcp serve` to start the Nuvel Skills MCP server
2. Call the `propose_improvement` tool with the skill name, version, issue, and suggested fix
3. The tool files a structured GitHub issue

### How to propose a fix (direct GitHub)

1. Open a GitHub issue at https://github.com/Folken2/skills/issues/new
2. Include: skill name, current version, what was wrong, suggested fix

### How improvements flow

```
Agent uses skill → detects drift → proposes fix → curator reviews → PR merged → version bumped → all future agents see the update
```

Every change is git-tracked with full provenance (who, what, when, why) for audit and rollback.

## Role scoping

If you are deployed for a specific role, scope your skills by theme.

Via AGENTS.md — add this at the top of the file:
```yaml
role: hr
```

When `role` is set, only load skills whose `theme` matches.

Via MCP server (requires Nuvel):
```bash
nuvel mcp serve --theme hr
```

Available themes: `software-development`, `growth`, `backoffice`, `hr`, `sales`, `customer-support`, `finance`, `procurement`, `skillification`.
