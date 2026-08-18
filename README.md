# Nuvel Skills

Nuvel Skills — curated skills for autonomous agents, organized by role. Thin harness, thick skills — each folder is a deployable employee.

## What this is

This repo is a library of **SOPs written as executable markdown**. Each skill is a self-contained `SKILL.md` (plus any supporting files) that teaches an agent how to do one job well. Skills are grouped into **theme folders**, and each theme folder maps to a **role** — an "employee." Pair a theme with an agent harness (Nuvel, Hermes, Claude Code, Cursor, …) and you get a specialist: the harness is thin, the skills carry the expertise.

## Themes

Eleven themes today — ten roles and a meta-layer: **software-development**, **growth**, **backoffice**, **hr**, **sales**, **customer-support**, **finance**, **procurement**, **customer**, **ops**, and **audit** are deployable employee roles; **skillification** is the meta-layer that governs how skills themselves get promoted into this repo. Some skills are **owned** (authored/maintained here); others are **vendored-and-attributed** — high-quality upstream skills kept verbatim, credited to their source (see [Attributions](#attributions)).

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

The full-funnel growth loop as executable SOPs — SEO, content, lifecycle email, analytics, and paid — plus email deliverability and video production.

| Skill | Description | Author |
|---|---|---|
| seo-audit | Crawl the site and run a scored technical + on-page + keyword audit into a prioritized, effort-estimated fix queue. | Nuvel Skills *(owned)* |
| content-pipeline | Run content marketing end to end — keyword research → brief → draft → review → publish → distribute → measure. | Nuvel Skills *(owned)* |
| email-lifecycle | Design lifecycle email — auth/hygiene, stage mapping, sequence design, deliverability, and compliance. | Nuvel Skills *(owned)* |
| analytics-setup | Stand up web/product analytics — event taxonomy, property setup, funnels, AARRR dashboards, and data-quality checks. | Nuvel Skills *(owned)* |
| paid-acquisition | Plan and run paid acquisition — channels, campaign structure, creative testing, ROAS/CAC targets, and a scale/stop loop. | Nuvel Skills *(owned)* |
| email-best-practices | Deliverability, SPF/DKIM/DMARC, compliance (CAN-SPAM, GDPR, CASL), capture, webhooks. | community / uncredited |
| react-email | Build email templates with React that render across email clients. | community / uncredited |
| remotion-best-practices | Best practices for Remotion — video creation in React. | community / uncredited |
| resend | Work with the Resend email platform — routes to send/receive/audiences/broadcasts. | resend *(vendored)* |

### backoffice — the Ops specialist

Document generation and data operations.

| Skill | Description | Author |
|---|---|---|
| docx | Create, edit, and analyze Word documents — tracked changes, comments, formatting. | Anthropic *(vendored)* |
| pdf | Extract text/tables, create, merge/split, and fill PDF forms at scale. | Anthropic *(vendored)* |
| pptx | Create, edit, and analyze PowerPoint presentations — layouts, speaker notes. | Anthropic *(vendored)* |
| supabase-postgres-best-practices | Postgres performance optimization and best practices from Supabase. | supabase *(vendored)* |
| xlsx | Create, read, and edit spreadsheets — formulas, formatting, data analysis. | Anthropic *(vendored)* |

### hr — People Operations

Hire, onboard, engage, and retain employees. Full-cycle people ops as executable SOPs — from opening a req to the exit interview.

| Skill | Description | Author |
|---|---|---|
| hiring | Full-cycle hiring from an approved need to a signed offer — requisition approval, scorecard screening, structured interviews, offer management, background check, onboarding handoff. | Nuvel Skills *(owned)* |
| employee-onboarding | New hire lifecycle to day 90 — pre-start equipment/accounts/workspace, day 1 orientation, first-week training and buddy, 30-60-90 milestones, access lifecycle. | Nuvel Skills *(owned)* |
| employee-engagement | Ongoing retention — 1:1 cadence, quarterly/annual reviews, continuous feedback, growth plans, recognition, stay/flight-risk checks, exit interviews. | Nuvel Skills *(owned)* |
| payroll-processor | Calculate net pay from timesheet CSV data (gross → tax → deductions) and generate per-employee paystubs plus a summary report. Bundles a payroll_processor.py script. | Nuvel Skills *(owned)* |

### sales — the Account Executive

Go-to-market SOPs: qualify inbound, run structured discovery, and manage a pipeline that forecasts honestly. Methodology-attributed (BANT, GPCT, CHAMP, SPIN, Sandler, MEDDIC).

| Skill | Description | Author |
|---|---|---|
| lead-qualification | Score and prioritize inbound leads — capture criteria (BANT/GPCT/CHAMP) + ICP fit, score, tier, route, set cadence. Bundles a lead-scorer script. | Nuvel Skills *(owned)* |
| discovery-call | Run a structured discovery call — research, problem ID, need amplification, impact quantification, budget, authority, timeline, decision criteria, debrief. Bundles a call-notes template. | Nuvel Skills *(owned)* |
| pipeline-management | Manage a pipeline end-to-end — stage exit criteria, velocity, coverage ratio, forecasting, deal inspection, stalled-deal recovery, lost-deal analysis, hygiene. Bundles a health-report script. | Nuvel Skills *(owned)* |


### procurement — the Procurement Specialist

Source-to-pay SOPs: qualify suppliers behind a gate, run purchase orders under a 3-way match, negotiate from a BATNA, and plan inventory so stock meets demand without tying up cash.

| Skill | Description | Author |
|---|---|---|
| supplier-qualification | Qualify and onboard a vendor through a gate — identification (RFI, referrals), due diligence (financial, legal, certifications, references, insurance), capability, risk (single-source), weighted scorecard, master record. | Nuvel Skills *(owned)* |
| purchase-order-management | Run the PO lifecycle — budget-checked requisition, numbered PO, approval matrix, order tracking, goods receipt (GRN), 3-way match, exception handling, close-out. | Nuvel Skills *(owned)* |
| vendor-negotiation | Prepare and run a commercial negotiation — market intelligence, BATNA, walk-away point, targets, pricing levers, terms (SLA/liability/renewal), concession matrix, agreement, debrief. | Nuvel Skills *(owned)* |
| inventory-planning | Decide how much to stock and when to reorder — demand forecast, ABC classification, safety stock and reorder points from lead-time variability, EOQ, min/max/par, stockout and overstock handling. | Nuvel Skills *(owned)* |

### customer — Customer Operations

Front-line customer request handling — classify and route incoming requests before they reach a human queue.

| Skill | Description | Author |
|---|---|---|
| triage-agent | Classify incoming requests by urgency (low → critical) and department (billing/tech/support/account) using keyword rules, then route. Bundles a triage_agent.py script. | Nuvel Skills *(owned)* |

### ops — Operations

Keep stock and orders moving — monitor inventory against thresholds and run orders through a fulfillment state machine.

| Skill | Description | Author |
|---|---|---|
| inventory-checker | Monitor stock levels against thresholds, flag OK/LOW/CRITICAL/OUT status, and recommend reorder quantities. Bundles an inventory_checker.py script. | Nuvel Skills *(owned)* |
| order-processor | Run orders through a received → validated → fulfilled → shipped state machine with per-stage validation gates and a processing log. Bundles an order_processor.py script. | Nuvel Skills *(owned)* |

### audit — Audit & Compliance

Automated log review — surface error spikes and compliance anomalies from structured logs.

| Skill | Description | Author |
|---|---|---|
| log-inspector | Parse JSONL/CSV structured logs, detect error-frequency spikes in configurable time windows, and flag compliance anomalies. Bundles a log_inspector.py script. | Nuvel Skills *(owned)* |

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

- **HR best-practice sources** — the owned `hr` skills (`hiring`, `employee-onboarding`, `employee-engagement`) are Nuvel Skills originals whose workflows are aligned with published industry standards, principally **SHRM** (Society for Human Resource Management) guidance and benchmarking on structured hiring, onboarding, retention, and stay/exit interviews, plus **Gallup** onboarding-experience research and the widely used 30-60-90 day onboarding framework. Sources are cited inline in each skill body. Adapt jurisdiction-specific steps (background checks, tax/eligibility forms, data retention) to your local employment law.

- **Sales methodologies** — the owned `sales` skills (`lead-qualification`, `discovery-call`, `pipeline-management`) are Nuvel Skills originals that apply established, publicly-documented sales methodologies, credited inline: BANT (IBM), CHAMP (InsightSquared), GPCT (HubSpot), SPIN Selling (Neil Rackham), the Pain Funnel (David Sandler / Sandler Training), and MEDDIC (Dick Dunkel / Jack Napoli, PTC).

All other skills are owned/maintained in this repo or adapted from community references. If you are a rights holder and want attribution corrected or content removed, open an issue.
