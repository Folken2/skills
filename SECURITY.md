# Security Policy

## Reporting a Vulnerability

This repository ships executable skill scripts that run with the same permissions as the agent runtime. Treat every PR as potentially dangerous.

**Do NOT file a public GitHub issue for security vulnerabilities.**

Instead, send details to **security@nuvel.dev** (or file a private security advisory via GitHub's "Report a vulnerability" tab on this repo).

## What to report

- Skills that read sensitive environment variables (`API_KEY`, `TOKEN`, `SECRET`, `PASSWORD`) and transmit them externally
- Scripts using `exec`/`eval` that could execute arbitrary code
- Hardcoded secrets or tokens in skill files
- Any skill that could exfiltrate data from the agent's environment
- CI/GitHub token exposure or workflow injection vectors

## Response

- Acknowledgement within 48 hours
- Assessment and fix within 7 days
- Public disclosure after fix is deployed (or sooner if the vulnerability is actively exploited)

## Security reviews

Every skill PR goes through an automated security review before merge. See `skills/security/security-review/SKILL.md` for the review checklist. This is in addition to the structural CI checks.
