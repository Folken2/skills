# Reference implementation: REA (`rea-agents`, v6.5.0)

Observed behaviour of the installer this skill's contract is derived from — verified by
running it on a sandbox `HOME`, not read from its docs. Cite it as a worked example, and
re-verify before relying on specifics (the tool moves fast).

## Surfaces

```
rea setup  [--client <id>...|--all-detected] [--skill=false] [--dry-run] [--json] [--yes] [--install-hopper]
rea doctor [--json] [--provider <id>] [--skill]
rea uninstall
```

- `--dry-run` returns `status: planned` with `plannedActions[]`, each carrying `target`,
  `operation` (`install`/`update`/`noop`), and `backupPath`. Exit 0. Detected clients
  stayed unselected: `plannedActions` was empty until a client was named explicitly.
- `--json` on `setup` also returns a compact `.doctor` readiness projection;
  `doctor --json` is the full one.
- `apply` pins the registration to the running version: `npx -y rea-agents@6.5.0 mcp`.

## Doctor projection (automation surface)

```
doctor.healthy                                   -> bool
doctor.identity.skill.state                      -> aligned | missing | unmanaged | unknown
doctor.identity.skill.installed_version          -> "42"
doctor.identity.skill.installed_tool_count       -> 207
doctor.identity.registrations[]                  -> {client, config_path, command, package_reference, state}
doctor.scope.{mode,clients,skill_clients,providers,target}
doctor.providerInspections[]                     -> {id, configured, available, providerVersion, checks[]}
```

`checks[]` entries carry `{name, ok, code, detail, remediation, classification}`, e.g.
`missing_analysis_engine`. `state: unmanaged` is reserved for paths REA refuses to own
(symlinks, non-directories) and it names them.

## Merge behaviour (verified)

Ran against a hand-written `~/.claude.json` holding an unrelated server entry, a nested
preferences object, and a `"// comment-like"` key:

- all three survived the write;
- the managed entry was added as `mcpServers.rea` with the pinned command;
- `~/.claude.json.rea.backup` was created byte-identical to the pre-write file;
- a second `setup --yes` returned `appliedActions: []` with the registration and skill
  both `aligned` — idempotent;
- the skill landed at `~/.claude/skills/reverse-engineer-anything/` as `SKILL.md` plus
  six `references/*.md`, and `doctor` reported `installed_tool_count: 207` — which the
  live server confirmed: `tools/list` returned exactly 207 tools.

## Honesty behaviours worth copying

- Deep analysis without a configured engine returns
  `{code: provider_unavailable, category: unavailable, retryable: true, remediation, details.rejections[]}`
  — listing every candidate provider and why it was rejected. It does not return an
  empty analysis. `binary_overview` still reported real facts about the target.
- Its troubleshooting docs state what is *not* established ("an exit can precede
  output-stream closure; `output_closed: false` keeps that uncertainty explicit"), and
  mark unverified paths explicitly ("live service acceptance is verified only where
  explicitly recorded").
- Invalid tool arguments come back as a structured validation error naming the offending
  key, and results carry `_meta.provenance.untrusted_content: true` for content read out
  of an analysis target.

## Client coverage (install target list)

25+ clients including Claude Code (`~/.claude.json`), Claude Desktop, Codex, Cursor,
Gemini CLI, OpenCode (multi-layer), VS Code, Copilot CLI, and **Hermes**
(`~/.hermes/config.yaml`). Client IDs are also accepted per-client (`--client codex`).
