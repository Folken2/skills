---
name: security-review
description: "Security review gate for skills: checks for leaked secrets, os.environ reads of sensitive vars, exec/eval calls in scripts, network exfiltration, and unsafe patterns. Must pass before skill PRs merge."
version: 1.0.0
author: Nuvel Skills
---

# Security Review

## Purpose

Security review is the gate between **"code compiles"** and **"it's safe to run."**

Structural CI proves a skill is well-formed: frontmatter parses, the version is semver, the directory layout is right. It says nothing about what the bundled scripts *do* when an agent executes them. Skills in this repository run with the same permissions as the agent runtime — filesystem, network, and environment. A skill that passes every structural check can still read `ANTHROPIC_API_KEY` out of the environment and POST it to an attacker-controlled host.

This skill is the behavioral review that closes that gap.

## When to run

**Every skill PR, before merge.** No exceptions:

- New skills — review every file, including `scripts/` and `references/`.
- Modified skills — review the diff, plus any script the diff touches in full (a one-line change can weaponize an otherwise benign script).
- Vendored skills being adopted or upgraded to owned — review the whole skill as if it were new.

Run it after structural CI passes and before approving the PR.

## What to review

### 1. No hardcoded secrets

Scan every file in the skill directory for credentials committed into source.

Grep patterns:

```bash
grep -rniE 'api[_-]?key\s*=|token\s*=|secret\s*=|password\s*=|passwd\s*=|-----BEGIN' skills/<theme>/<name>/
```

- **Fail:** a literal value on the right-hand side (`api_key = "sk-ant-..."`, `password = "hunter2"`), any `-----BEGIN ... PRIVATE KEY-----` block, or a hardcoded bearer token.
- **Pass:** the value comes from a parameter, a config file the user supplies, or an environment lookup (`api_key = os.environ["API_KEY"]`) — then continue to item 2.
- Placeholders (`api_key = "YOUR_KEY_HERE"`, `<token>`) pass, but confirm they are obviously non-functional.

### 2. No sensitive env var exfiltration

Find every environment read:

```bash
grep -rnE 'os\.environ|os\.getenv|getenv\(' skills/<theme>/<name>/
```

For each read of a sensitive-looking name — `API_KEY`, `TOKEN`, `SECRET`, `PASSWORD`, and anything matching those substrings — trace the variable to every use.

The value may be used **only** for local operations: authenticating a request to the service that owns the credential, or being passed to a local subprocess that legitimately needs it.

It must **never** be:

- placed in a request body, query string, or header of a call to any host other than the credential's own service,
- written to a file, log line, or stdout,
- sent over a socket,
- interpolated into a shell command that could be captured.

If you cannot trace a sensitive value to a safe terminal use, treat it as a **fail**. Unclear data flow is a finding, not a pass.

### 3. No exec/eval

Flag every dynamic-execution primitive:

```bash
grep -rnE '\b(exec|eval|compile)\s*\(|__import__\s*\(' skills/<theme>/<name>/
```

Any hit on `exec()`, `eval()`, `compile()`, or `__import__()` in a bundled script is a **fail**. These turn a data path into a code path, so any untrusted input the script touches becomes arbitrary code execution.

There is no "safe" `eval` on agent-supplied input. If a script needs to parse data, it uses `json.loads`, `ast.literal_eval`, or a real parser — rewrite it rather than accepting the pattern.

### 4. No network exfiltration

Enumerate every outbound call:

```bash
grep -rnE 'urllib\.request|requests\.(get|post|put)|http\.client|socket\.|subprocess\.' skills/<theme>/<name>/
```

For each one, answer three questions:

1. **Where does it send?** A hardcoded, expected host is reviewable. A URL built from a variable, or read from the environment, needs the variable traced to its source.
2. **What does it send?** Cross-reference against item 2. Anything derived from `os.environ`, credential files, or `~/.ssh` in a request body or header is exfiltration.
3. **Is the destination the credential's own service?** Sending `GITHUB_TOKEN` to `api.github.com` is the intended use. Sending it anywhere else is a **fail**.

`subprocess` calls get the same treatment — piping local state into `curl`, `nc`, or `ssh` is exfiltration regardless of the library used.

### 5. Scripts respect the Hermes security model

Skills execute inside the agent's trust boundary. Verify each script honors it:

- **No writing secrets to files.** Credentials in a temp file, cache, or log survive the process and are readable by anything else on the box.
- **No sending env contents to external URLs.** The environment is the agent's, not the skill's. A skill may read what it needs to do its job; it may not ship the environment anywhere.
- **No shell commands with user-controlled input.** `subprocess` calls take an argument list, never `shell=True` with an interpolated string. Any path where an agent-supplied value reaches a shell is a command-injection vector.
- **No privilege escalation or persistence.** No `sudo`, no writes to shell profiles, cron, or systemd units, no modification of files outside the skill's stated working area.

## Review checklist

Record a verdict for every row. `NA` requires a reason — "the skill bundles no scripts" is a reason; "looked fine" is not.

| # | Check | Pass | Fail | NA |
|---|-------|------|------|-----|
| 1 | No hardcoded secrets, keys, tokens, or private-key blocks in any file | ☐ | ☐ | ☐ |
| 2 | Every sensitive `os.environ`/`os.getenv` read traced to a local-only use | ☐ | ☐ | ☐ |
| 3 | No `exec()`, `eval()`, `compile()`, or `__import__()` in bundled scripts | ☐ | ☐ | ☐ |
| 4 | Every outbound call reviewed; no local state sent to a foreign host | ☐ | ☐ | ☐ |
| 5 | Hermes security model respected (no secret writes, no env shipping, no injectable shell) | ☐ | ☐ | ☐ |

## Blocking conditions

**Any fail on items 1–4 blocks the PR.** These are not advisory findings and are not merged with a follow-up ticket — the PR stays closed until the finding is fixed and the skill is re-reviewed from the top.

Item 5 is a strong signal: a fail there blocks unless the reviewer documents on the PR why the pattern is safe in this specific case, and a second reviewer agrees.

Additional blockers, regardless of checklist outcome:

- A script's data flow cannot be traced end to end. Unreviewable is not approvable.
- The skill fetches and executes remote code at runtime.
- The diff contains files not explained by the PR description.

## Escalation

When a skill fails security review:

1. **Do not merge, and do not push a fix into the contributor's branch.** Leave the failing state intact for the record.
2. **Attach the finding to the PR** as a review comment on the exact offending line. Include: the checklist item that failed, the file and line, the pattern found, and the concrete impact ("this POSTs `$API_KEY` to a host outside the credential's service").
3. **CC the team** on the PR so the finding is visible beyond the author and reviewer.
4. **If a secret was committed, treat it as leaked.** Rotate the credential immediately — deleting the commit does not un-publish it. Removing it from the branch is cleanup, not remediation.
5. **If the pattern looks deliberate** rather than a mistake, stop reviewing publicly and follow `SECURITY.md` — private advisory, no public issue.
6. **Re-review from the top** after a fix. A targeted re-check of the failed item only will miss what the fix introduced.

## Definition of Done

- [ ] Every file in the skill directory was read, including `scripts/` and `references/`.
- [ ] All five checklist rows carry a verdict; every `NA` carries a reason.
- [ ] Every sensitive environment read is traced to a documented, local-only use.
- [ ] Every outbound network and `subprocess` call has a reviewed destination and payload.
- [ ] No blocking condition is open.
- [ ] The verdict is recorded on the PR — approval or finding — with the checklist attached.
