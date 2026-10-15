---
name: installer-transaction-design
description: "Use when building or hardening an installer that writes agent config or installs skills. Reviewed plan/apply/doctor transaction: approval gates, conservative merges, immutable backups, fail-closed validation."
version: 1.0.0
author: Mark Folken
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Installers, Agent-Config, MCP, Skills, Reliability]
    related_skills: [agent-skill-provisioning, coding-agent-skill-provisioning, skills-hub-maintenance]
---

# Installer Transaction Design

Use when you are **building the thing that installs** — a CLI that registers an MCP
server into a client config, deploys skills into a harness directory, or wires a bot's
profile — not when you are only running someone else's installer.

The contract below is what makes an installer trustworthy enough to point at a user's
existing configuration. It is derived from a mature implementation (REA, `rea-agents`)
and is executable via `scripts/install_transaction.py`.

## The four states

An installer that only knows "done" and "error" cannot be automated against or debugged.

| Surface | Meaning |
|---|---|
| `plan` | Read-only. Prints exact targets, operation (`install`/`update`/`noop`), backup path. Writes nothing, ever. |
| `apply` | Refuses without explicit approval; backs up, writes atomically, verifies the result. |
| `doctor` | Re-reads the world and reports `aligned` / `missing` / `drifted` per action. |
| `blocked` | Unsafe or malformed input. Aborts the **whole** transaction before the first byte. |

Exit codes carry the state: `0` planned/applied/healthy, `1` `needs_confirmation` or
failed, `2` blocked. Every surface has a `--json` mode whose statuses are stable enough
for automation to branch on.

## Rules

1. **Nothing is written before approval, and approvals do not compound.** Answering yes
   to a package download is not permission to modify a config; `--yes` with no explicit
   scope applies only to entries the installer already owns, never to newly detected
   clients. Ungoverned scope is how an installer writes into a tool the user forgot it
   could see.
2. **Detection is not permission.** A detected client is context for the plan, listed but
   unselected. Configuring everything you can see requires an explicit flag the user had
   to type (`--all-detected`), and the plan still shows it first.
3. **Merge conservatively — own only your keys.** Preserve unrelated entries, comment-like
   keys, unknown fields and formatting; replace only the keys you declared. Settings the
   user set on your entry (env overrides, extra flags) survive a re-run unless the new
   plan explicitly supersedes them.
4. **The first snapshot is immutable.** Back up before the first write, and never
   overwrite that backup on later runs. When the current bytes differ from the snapshot,
   keep a second copy keyed by content hash (`<path>.backup.<sha256>.recovery`) and
   report both paths. A rollback that fails must report the recovery path and the
   restore failure — not just fail.
5. **Validate everything before the first byte.** Parse every target up front; malformed
   or unsafe configuration blocks the entire transaction, so a partial apply is not a
   state the user can end up in. Refuse symlinks and non-files at managed paths, and
   share those ownership rules between install, update and uninstall.
6. **Be idempotent.** A second run over an already-applied plan applies nothing and
   reports `aligned`. If re-running changes something, the first run lied about its state.
7. **Never claim more than you verified.** Distinguish "unavailable" from "empty"
   (`segments: unavailable` is not `segments: 0`). State what a check does *not*
   establish. On macOS/Windows where a GUI may still hold state, say that a clean exit
   does not prove document closure rather than implying success.
8. **Fail closed on missing dependencies.** When the component that does the real work
   is absent, return a structured, retryable error naming the diagnostic and the fix
   (`provider_unavailable` + `run <cli> doctor`) instead of degrading into a plausible
   empty result.
9. **Pin what you register.** Persistent registrations reference an exact version
   (`pkg@1.2.3`), never a floating tag and never a temp-cache path. Later runs migrate
   older registrations through the normal reviewed transaction.
10. **Errors are data.** `{code, category, retryable, message, remediation, details}` —
    so a caller can branch without parsing prose, and a UI can render the fix.
11. **Uninstall is a first-class mode.** Write an ownership manifest, retain and report
    anything you cannot safely remove, and never delete a file you did not create.

## Use the bundled runner

`scripts/install_transaction.py` (stdlib only) implements the contract for agent-config
writes and skill installs.

```bash
S=scripts/install_transaction.py
python3 $S plan   --manifest install.json --json     # read-only, exit 0
python3 $S apply  --manifest install.json            # exit 1: needs_confirmation
python3 $S apply  --manifest install.json --yes      # backs up, writes, verifies
python3 $S doctor --manifest install.json --json     # aligned | missing | drifted
```

Manifest: `actions[]` where each action is either

- `configure_client` — `path`, `container` (dotted, e.g. `mcpServers`), `name`,
  `value`, optional `preserve_env_keys`; or
- `install_skill` — `target` directory and `source` directory.

Atomic by construction: temp file in the target directory then `os.replace`, with the
skill copy staged and swapped rather than written in place.

## Prove it before you ship it

An installer is the one program whose bugs destroy user state, so it needs a conformance
suite, not a happy-path smoke test. Run it against a sandbox `HOME`. Assert at minimum:

- [ ] `plan` leaves every target byte-identical (`sha256` before/after)
- [ ] `apply` without approval exits non-zero and writes nothing
- [ ] unrelated keys, nested objects and comment-like keys survive the merge
- [ ] declared env overrides survive a re-run; undeclared keys are replaced
- [ ] the first backup holds pre-write bytes and is still intact after drift
- [ ] drift produces a recovery copy containing the drifted bytes
- [ ] a malformed target blocks the transaction with exit 2, no backup, no write
- [ ] a symlinked managed path is refused
- [ ] a second `apply` applies nothing and `doctor` says healthy
- [ ] `--help` exits 0

`references/rea-contract.md` records the observed behaviour of the reference
implementation these rules come from.

## Pitfalls

- **Inventing statuses per command.** `planned` / `ready` / `needs_confirmation` /
  `cancelled` / `blocked` are a vocabulary, not decoration — automation branches on
  them, so reuse the four states above instead of adding a fifth spelling of "done".
- **Testing only the apply path.** Every destructive bug lives in the gap between plan
  and apply: the drift case, the malformed case, the second run. Test those first.
- **Writing a config the client cannot read back.** Validate the merged document by
  re-parsing it *after* the write, not by trusting the serializer's return value.
- **Backing up the file you just wrote.** Snapshot before mutating; a backup taken after
  the write is a copy of the bug.
