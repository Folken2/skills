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
