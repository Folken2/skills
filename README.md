# Nuvel Skills

Nuvel Skills — curated skills for autonomous agents, organized by role. Thin harness, thick skills — each folder is a deployable employee.

## What this is

This repo is a library of **SOPs written as executable markdown**. Each skill is a self-contained `SKILL.md` (plus any supporting files) that teaches an agent how to do one job well. Skills are grouped into **theme folders**, and each theme folder maps to a **role** — an "employee." Pair a theme with an agent harness (Nuvel, Hermes, Claude Code, Cursor, …) and you get a specialist: the harness is thin, the skills carry the expertise.

## Themes

Four themes today — three roles and a meta-layer: **software-development**, **growth**, and **backoffice** are deployable employee roles; **skillification** is the meta-layer that governs how skills themselves get promoted into this repo. Some skills are **owned** (authored/maintained here); others are **vendored-and-attributed** — high-quality upstream skills kept verbatim, credited to their source (see [Attributions](#attributions)).

### software-development — the Engineer

Design review, testing, and framework practices for shipping web apps.

Also depends on superpowers (Jesse Vincent / Prime Radiant, MIT) for core development methodology — TDD, debugging, planning, code review, worktrees.

| Skill | Description | Author |
|---|---|---|
| feature-shaping | Shape a vague idea into a structured spec — problem framing, scope, success metrics, risks. Bridges brainstorming and writing-plans. | Nuvel Skills *(owned)* |
| bug-triage | Triage-first bug workflow — capture the exact error, classify, fix simple bugs fast, escalate complex ones. | Nuvel Skills *(owned)* |
| database-migration-safety | Migration safety protocol — down migrations, round-trip rollback testing, schema diff review, zero-downtime. | Nuvel Skills *(owned)* |
| design-checklist-review | Reference UX/UI quality checklists for web app screens. Run before shipping. | markfolken *(owned)* |
| second-order-impact-analysis | Before declaring a change done, trace ripple effects — upstream/downstream, data, API contract, performance, rollback. | Nuvel Skills *(owned)* |
| frontend-design | Create distinctive, production-grade frontend interfaces that avoid generic AI aesthetics. | Anthropic *(vendored)* |
| mcp-builder | Guide for creating high-quality MCP servers (Python FastMCP or Node/TypeScript MCP SDK). | Anthropic *(vendored)* |
| nextjs-best-practices | Next.js App Router principles — Server Components, data fetching, routing patterns. | community / uncredited |
| nextjs-supabase-auth | Expert integration of Supabase Auth with the Next.js App Router. | community / uncredited |
| vercel-react-best-practices | React/Next.js performance optimization guidelines from Vercel Engineering. | vercel *(vendored)* |
| web-design-guidelines | Review UI code for Web Interface Guidelines compliance (accessibility, UX audit). | vercel *(vendored)* |
| webapp-testing | Interact with and test local web apps using Playwright — verify, debug, screenshot. | community / uncredited |

### growth — the Growth marketer

SEO, email deliverability, and content/video production.

| Skill | Description | Author |
|---|---|---|
| email-best-practices | Deliverability, SPF/DKIM/DMARC, compliance (CAN-SPAM, GDPR, CASL), capture, webhooks. | community / uncredited |
| react-email | Build email templates with React that render across email clients. | community / uncredited |
| remotion-best-practices | Best practices for Remotion — video creation in React. | community / uncredited |
| resend | Work with the Resend email platform — routes to send/receive/audiences/broadcasts. | resend *(vendored)* |
| seo-audit | Audit, review, or diagnose technical + on-page SEO issues on a site. | community / uncredited |

### backoffice — the Ops specialist

Document generation and data operations.

| Skill | Description | Author |
|---|---|---|
| docx | Create, edit, and analyze Word documents — tracked changes, comments, formatting. | Anthropic *(vendored)* |
| pdf | Extract text/tables, create, merge/split, and fill PDF forms at scale. | Anthropic *(vendored)* |
| pptx | Create, edit, and analyze PowerPoint presentations — layouts, speaker notes. | Anthropic *(vendored)* |
| supabase-postgres-best-practices | Postgres performance optimization and best practices from Supabase. | supabase *(vendored)* |
| xlsx | Create, read, and edit spreadsheets — formulas, formatting, data analysis. | Anthropic *(vendored)* |

### skillification — the meta-layer

Skills about skills: promotion, verification, extraction — how skills enter and stay healthy in this repo.

| Skill | Description | Author |
|---|---|---|
| skill-promotion | Promote a dogfooded internal skill into the canonical repo — curation gates, versioning, attribution review, PR workflow. | Nuvel Skills *(owned)* |

## Install

Skills live at `skills/<theme>/<name>/SKILL.md`. Install into whichever harness you run.

**Hermes**

```bash
hermes skills install https://raw.githubusercontent.com/Folken2/skills/main/skills/<theme>/<name>/SKILL.md
# e.g.
hermes skills install https://raw.githubusercontent.com/Folken2/skills/main/skills/software-development/webapp-testing/SKILL.md
```

**Claude Code** — copy the skill folder into your skills dir:

```bash
mkdir -p ~/.claude/skills/<name>
cp -r skills/<theme>/<name>/. ~/.claude/skills/<name>/
```

**Cursor**

```bash
mkdir -p .cursor/skills/<name>
cp -r skills/<theme>/<name>/. .cursor/skills/<name>/
```

**Codex / Gemini**

```bash
mkdir -p .agents/skills/<name>
cp -r skills/<theme>/<name>/. .agents/skills/<name>/
```

**Manual** — copy any `skills/<theme>/<name>/` folder into your agent's skills directory; the whole folder is self-contained.

## Related resources

- [skills.sh](https://www.skills.sh/) — The agent skills directory. 1.2M+ skills searchable across 20+ harnesses. Claude Code has a built-in `/skills` command to search this catalog. Skills from this repo can also be published there.
- [superpowers](https://github.com/obra/superpowers) — Complete software development methodology (MIT, Jesse Vincent / Prime Radiant). Our software-development theme depends on it.
- [Checklist Design](https://checklist.design) — UX/UI reference checklists by George Hatzis.
- [rag.saas-shipkit](https://github.com/rag-saas-shipkit) — Brandon Bayer's pioneering task templates that inspired our bug-triage and migration-safety skills.

## Contributing

Add a skill at `skills/<theme>/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
description: When to use this skill and what it does.
version: 1.0.0
author: your-handle
---
```

- Keep each skill **self-contained** — bundle any supporting files inside its folder.
- **Attribution is required** for vendored content: set `author` to the true source and note it here.
- Update `skills/index.json` (grouped by theme) when you add or move a skill.
- Pick the theme that matches the role the skill serves, not the tool it happens to use.

## License

MIT — see below. Owned skills are provided under MIT. Vendored skills remain under their original licenses.

### Attributions

Several skills are vendored verbatim from upstream sources and credited to their authors. They are used under their respective licenses:

- **Anthropic** — `frontend-design`, `mcp-builder`, and the official document skills `docx`, `pdf`, `pptx`, `xlsx` (from Anthropic's open-source Claude skills).
- **Vercel** — `vercel-react-best-practices` and `web-design-guidelines` (Vercel Engineering / Web Interface Guidelines).
- **Supabase** — `supabase-postgres-best-practices`.
- **Resend** — `resend` (and its sub-skills for sending, receiving, audiences, and broadcasts).
- **Brandon Bayer** ([rag.saas-shipkit](https://github.com/flybayer)) — the owned skills `bug-triage`, `database-migration-safety`, and `second-order-impact-analysis` are Nuvel Skills originals, restructured into modern `SKILL.md` form and inspired by the structured task templates Brandon pioneered in rag.saas-shipkit.

All other skills are owned/maintained in this repo or adapted from community references. If you are a rights holder and want attribution corrected or content removed, open an issue.
