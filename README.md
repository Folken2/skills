# Folken2 Skills

A reusable skills hub — SOPs as executable markdown, harness-agnostic.

Skills are plain-content standard operating procedures written as markdown with YAML frontmatter. They carry no harness-specific packaging: the same `SKILL.md` runs under Hermes, Claude Code, Cursor, Codex, Gemini CLI, or any Agent Skills–compatible tool. Harness packaging belongs at install time, not in the source tree — so every skill lives once under `skills/<name>/`.

## Catalog

| Skill | Category | Description | Author |
|-------|----------|-------------|--------|
| design-checklist-review | Design / Review | Reference UX/UI quality checklists for web app screens; run before shipping. | markfolken |
| docx | Documents | Create, edit, and analyze Word `.docx` files — tracked changes, comments, formatting preservation, text extraction. | community / uncredited |
| email-best-practices | Email | Deliverability, SPF/DKIM/DMARC auth, compliance (CAN-SPAM, GDPR, CASL), webhooks, and transactional vs. marketing decisions. | community / uncredited |
| frontend-design | Frontend | Build distinctive, production-grade frontend interfaces that avoid generic AI aesthetics. | community / uncredited |
| mcp-builder | MCP / Tooling | Guide for building high-quality MCP servers in Python (FastMCP) or Node/TypeScript (MCP SDK). | community / uncredited |
| nextjs-best-practices | Frontend / Next.js | Next.js App Router principles — Server Components, data fetching, routing patterns. | community / uncredited |
| nextjs-supabase-auth | Auth / Next.js | Integrate Supabase Auth with the Next.js App Router — login, middleware, protected routes. | vibeship-spawner-skills (Apache 2.0) |
| pdf | Documents | Extract text and tables, create, merge/split, and fill forms in PDF documents at scale. | community / uncredited |
| pptx | Documents | Create, edit, and analyze PowerPoint `.pptx` files — layouts, comments, speaker notes. | community / uncredited |
| react-email | Email | Build React email templates that render across clients — welcome, password reset, notifications, receipts. | community / uncredited |
| remotion-best-practices | Video | Best practices for Remotion — programmatic video creation in React. | community / uncredited |
| resend | Email | Work with the Resend email platform — sending, receiving, audiences, and broadcasts. | resend |
| seo-audit | SEO | Audit, review, and diagnose technical and on-page SEO issues on a site. | community / uncredited |
| supabase-postgres-best-practices | Database | Postgres performance optimization and best practices from Supabase — queries, schema, configuration. | supabase |
| vercel-react-best-practices | Frontend / Performance | React and Next.js performance optimization guidelines from Vercel Engineering. | vercel |
| web-design-guidelines | Design / Review | Review UI code for Web Interface Guidelines compliance — accessibility, UX, design audits. | vercel |
| webapp-testing | Testing | Interact with and test local web apps using Playwright — screenshots, logs, UI debugging. | community / uncredited |
| xlsx | Documents | Create, edit, and analyze spreadsheets (`.xlsx`, `.xlsm`, `.csv`, `.tsv`) — formulas, formatting, data analysis. | community / uncredited |

## Install

Every skill is self-contained under `skills/<name>/`. Pick the section for your harness.

### Hermes

```bash
hermes skills install https://raw.githubusercontent.com/Folken2/skills/main/skills/<name>/SKILL.md
```

### Claude Code

Copy the skill folder into your user skills directory:

```bash
cp -r skills/<name> ~/.claude/skills/<name>
```

Where a published package exists, `npx skills add <owner>/<repo>` also works.

### Cursor

Copy the skill folder into your project's Cursor skills directory:

```bash
cp -r skills/<name> .cursor/skills/<name>
```

### Codex / Gemini CLI / other Agent Skills tools

These read the neutral standard location. Copy the folder there:

```bash
cp -r skills/<name> .agents/skills/<name>
```

### Manual

Clone this repo and copy the skill folder into your agent's skills directory:

```bash
git clone https://github.com/Folken2/skills.git
cp -r skills/skills/<name> <your-agent-skills-dir>/<name>
```

## Contributing

Add a skill as `skills/<name>/SKILL.md` with YAML frontmatter carrying `name`, `description`, `version`, and `author`, plus any supporting files the skill needs alongside it. Keep it self-contained and harness-agnostic — no install-time or harness-specific packaging in the source tree — so the same file works everywhere.

## License

MIT
