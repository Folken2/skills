---
name: manage
description: "Manage a fleet of enterprise bots — check status, inspect bots, update models and skills, run health checks, and retire bots."
version: 1.0.0
author: Nuvel Skills
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: []
  commands: [python3, nuvel]
  pip_packages: []
metadata:
  hermes:
    tags: [fleet, manage, enterprise, operations]
---
# Fleet Manage

You are the fleet manager. Your job is to keep the fleet healthy.

A *fleet* is a named group of enterprise bots. Each *bot* is a running agent
profile with a model, a set of installed skills, and its own logs. This skill is
the operational runbook for keeping that fleet running: knowing what is deployed,
inspecting individual bots, changing their configuration, and retiring the ones
you no longer need.

## When to use

- Take stock of a fleet — what bots exist and whether they are healthy.
- Investigate one bot that is misbehaving (details + recent logs).
- Roll a model or skill change across one or more bots.
- Decommission a bot that is no longer needed.

If a bot is *broken* (empty API key, missing skills, profile not found), stop
managing and switch to [[fleet/troubleshoot]] to diagnose and repair it.

## Commands

All commands go through the `nuvel` CLI. If `nuvel` is not installed, the
underlying agent runtime is `hermes` — call `hermes -p <bot>` directly against a
bot's profile.

### Check fleet status

```bash
nuvel fleet status <name>
```

Lists every bot in the fleet with its model, skill count, and up/down state.
Start here — it is your map of the fleet.

### View bot details

```bash
nuvel bots info <bot>            # model, skills, profile path, config
nuvel bots logs <bot> -n 50      # last 50 log lines
```

Use `info` to see how a bot is configured and `logs` to see what it has been
doing. When in doubt, read the logs before changing anything.

### Add skills to a bot

```bash
nuvel bots edit <bot> --skills <existing+new>
```

`--skills` **replaces** the full skill set — it is not additive. Read the
current skills with `nuvel bots info <bot>` first, then pass the existing list
plus the new skill(s). Dropping a skill you meant to keep is the most common
mistake here.

### Update a bot's model

```bash
nuvel bots edit <bot> --model <model>
```

Change one bot at a time and confirm with `nuvel bots info <bot>` before moving
to the next. Verify the bot still responds (a health check) after a model swap.

### Remove a bot

```bash
nuvel bots delete <bot>
```

Destructive and hard to reverse. Confirm the bot name, capture its config
(`nuvel bots info <bot>`) for the record, and make sure nothing depends on it
before deleting.

## Companion script

`scripts/manage_fleet.py` wraps these commands for scripted use:

```bash
python scripts/manage_fleet.py status <fleet-name>        # Show fleet status
python scripts/manage_fleet.py inspect <bot-name>         # Show bot details + logs
python scripts/manage_fleet.py update-model <bot> <model> # Change bot's model
python scripts/manage_fleet.py health <fleet-name>        # Ping all bots, report health
```

It shells out to `nuvel fleet` / `nuvel bots`, and falls back to `hermes -p`
when `nuvel` is not on `PATH`. Stdlib-only; run `--help` on any subcommand.

## Workflow

1. **Map the fleet** — `nuvel fleet status <name>` (or `manage_fleet.py status`).
2. **Health check** — `manage_fleet.py health <name>` to ping every bot.
3. **Inspect** any bot flagged unhealthy — `nuvel bots info` + `logs`.
4. **Change** configuration deliberately — one bot, one attribute at a time.
5. **Verify** after every change — re-run `info` and a health ping.
6. **Escalate** genuinely broken bots to [[fleet/troubleshoot]].

## Definition of Done

- `nuvel fleet status <name>` reflects the intended state of the fleet.
- Every bot you changed was re-inspected and passed a health ping.
- Any bot you could not fix was handed to [[fleet/troubleshoot]] with the
  symptom and the relevant log lines.
- Any deletion was confirmed against the bot's captured config first.

## Edge cases

| Situation                          | Behaviour                                             |
|------------------------------------|-------------------------------------------------------|
| `nuvel` not installed              | Fall back to `hermes -p <bot>` per bot                |
| `--skills` passed without existing | Existing skills are dropped — always include them     |
| Bot unresponsive to health ping    | Treat as broken → [[fleet/troubleshoot]]              |
| Model change breaks a bot          | Revert the model, then troubleshoot                   |
| Deleting the wrong bot             | Not recoverable — confirm name + capture config first |
