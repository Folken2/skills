---
name: troubleshoot
description: "Diagnose and fix enterprise bot issues — inspect logs, verify skill installation, check config, reinstall skills, and escalate to a human when needed."
version: 1.0.0
author: Nuvel Skills
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: []
  commands: [python3, hermes]
  pip_packages: []
metadata:
  hermes:
    tags: [fleet, troubleshoot, enterprise, operations]
---
# Fleet Troubleshoot

When a bot in the fleet misbehaves, this is the diagnostic runbook. Work from
symptom to root cause in a fixed order, fix what is safe to fix, and escalate to
a human when the cause is outside your control.

A bot's state lives in its profile directory: `~/.hermes/profiles/<bot>/`. That
directory holds its config, its installed skills (`skills/`), and its logs. Most
bot problems are visible there.

## When to use

- A bot is failing, hanging, returning errors, or ignoring its skills.
- A bot's health ping (from [[fleet/manage]]) came back unhealthy.
- A skill was added but the bot does not appear to use it.
- You need to confirm a bot is configured the way you think it is.

## Diagnostic commands

### Check bot logs

```bash
nuvel bots logs <bot> -n 50        # via nuvel
hermes -p <bot> logs -n 50         # direct fallback
```

The logs are the first place to look. Read the most recent lines for stack
traces, auth failures, or "skill not found" messages before touching anything.

### Verify skill installation

Installed skills live at `~/.hermes/profiles/<bot>/skills/`. Confirm the skill
directory and its `SKILL.md` actually exist:

```bash
ls ~/.hermes/profiles/<bot>/skills/
ls ~/.hermes/profiles/<bot>/skills/<skill>/SKILL.md
```

A skill that is listed in config but missing on disk is a classic silent failure.

### Check config

```bash
hermes -p <bot> config get model
hermes -p <bot> config get api_key   # verify it is set, do not print secrets
```

Confirm the model is valid and the API key is present and non-empty.

### Reinstall skills

If a skill is corrupted or missing, remove it and re-add it:

```bash
nuvel bots edit <bot> --skills <existing-minus-broken>   # remove
nuvel bots edit <bot> --skills <existing-with-fixed>     # re-add
```

Remember `--skills` replaces the whole set — always pass the full intended list.
Verify the skill is back on disk afterward.

## Common issues

| Symptom                          | Likely cause              | Fix                                             |
|----------------------------------|---------------------------|-------------------------------------------------|
| Auth / 401 errors in logs        | Empty or invalid API key  | Set a valid key in config; **escalate** if none |
| Bot uses wrong behavior/quality  | Wrong or unset model      | `nuvel bots edit <bot> --model <model>`         |
| Bot ignores a skill              | Missing skill on disk     | Verify `skills/<skill>/`, reinstall             |
| "profile not found"              | Profile dir missing       | Recreate the bot / restore the profile          |
| Skill listed but not loading     | Corrupted `SKILL.md`      | Reinstall the skill                             |

## Companion script

`scripts/troubleshoot_bot.py` automates the diagnostics:

```bash
python scripts/troubleshoot_bot.py diagnose <bot-name>      # Full diagnostic
python scripts/troubleshoot_bot.py check-logs <bot> -n 30   # Check recent logs
python scripts/troubleshoot_bot.py verify-skills <bot>      # Verify skill installation
python scripts/troubleshoot_bot.py reinstall <bot> <skill>  # Reinstall a skill
```

It checks the profile directory, verifies files exist, reads logs, and reports a
status per check. Stdlib-only; run `--help` on any subcommand.

## Workflow

1. **Read the logs** — `check-logs` or `nuvel bots logs`. Get the exact error.
2. **Locate the profile** — confirm `~/.hermes/profiles/<bot>/` exists.
3. **Verify config** — model set and valid, API key present and non-empty.
4. **Verify skills** — every configured skill exists on disk with a `SKILL.md`.
5. **Fix what is safe** — reinstall a missing skill, correct the model.
6. **Re-verify** — run `diagnose` again; confirm the symptom is gone.
7. **Escalate** if the cause is outside your control (see below).

## Escalation — when to notify the human

Escalate instead of guessing when:

- The **API key is missing** and you have no authorized source for a new one.
- The **profile directory is gone** and there is no backup to restore.
- A fix would be **destructive or irreversible** (deleting/recreating a bot).
- The error is **unknown** or repeats after a clean reinstall.
- Anything touches **billing, credentials, or access control**.

When you escalate, include: the bot name, the exact error from the logs, the
checks you ran, and what you tried. Do not print secret values.

## Definition of Done

- The original symptom is reproduced, understood, and either fixed or escalated.
- `troubleshoot_bot.py diagnose <bot>` reports the bot healthy, **or** a clear
  escalation was raised with logs and steps attached.
- No secrets were printed or committed anywhere.

## Edge cases

| Situation                         | Behaviour                                            |
|-----------------------------------|------------------------------------------------------|
| `nuvel` not installed             | Use `hermes -p <bot>` directly                       |
| Profile directory missing         | Report `profile not found` → escalate                |
| `skills/` dir empty but config has skills | Reinstall each configured skill               |
| API key blank                     | Flag as critical, escalate — never invent a key      |
| Reinstall does not clear the error| Escalate with full logs                              |
