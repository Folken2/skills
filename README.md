# Skills

A harness-agnostic hub of reusable agent skills — self-contained `SKILL.md` files that teach an AI agent how to do a specific task well. Grouped into categories so both humans and agents can navigate quickly.

Each skill lives at `skills/<category>/<name>/SKILL.md` with YAML frontmatter (`name`, `description`, and where available `version` / `author`). Point an agent at the raw URL, or install into your harness of choice — see [Install](#install).

For a machine-readable version of this catalog, see [`skills/index.json`](./skills/index.json).

## Catalog

### design
Building and reviewing polished, accessible user interfaces.

| Skill | Description | Author |
|-------|-------------|--------|
| [design-checklist-review](./skills/design/design-checklist-review/) | Reference UX/UI quality checklists for web app screens. Run before shipping. | markfolken |
| [frontend-design](./skills/design/frontend-design/) | Create distinctive, production-grade frontend interfaces with high design quality — web components, pages, artifacts, posters, or applications. | community / uncredited |
| [web-design-guidelines](./skills/design/web-design-guidelines/) | Review UI code for Web Interface Guidelines compliance — accessibility, UX, design audits. | vercel |

### documents
Creating, editing, and analyzing office document formats.

| Skill | Description | Author |
|-------|-------------|--------|
| [docx](./skills/documents/docx/) | Word document (.docx) creation, editing, and analysis — tracked changes, comments, formatting, text extraction. | community / uncredited |
| [pdf](./skills/documents/pdf/) | PDF manipulation — extract text/tables, create, merge/split, and fill forms. | community / uncredited |
| [pptx](./skills/documents/pptx/) | Presentation (.pptx) creation, editing, and analysis — layouts, speaker notes, comments. | community / uncredited |
| [xlsx](./skills/documents/xlsx/) | Spreadsheet (.xlsx, .csv, .tsv) creation, editing, and analysis — formulas, formatting, data analysis, visualization. | community / uncredited |

### email
Building, sending, and hardening email features.

| Skill | Description | Author |
|-------|-------------|--------|
| [email-best-practices](./skills/email/email-best-practices/) | Building email features, deliverability (SPF/DKIM/DMARC), compliance (CAN-SPAM, GDPR, CASL), webhooks, transactional vs marketing. | community / uncredited |
| [react-email](./skills/email/react-email/) | Creating email templates with React that render across email clients. | community / uncredited |
| [resend](./skills/email/resend/) | Working with the Resend email platform — sending, receiving, audiences, broadcasts. | resend |

### web
Building, optimizing, and testing web applications.

| Skill | Description | Author |
|-------|-------------|--------|
| [nextjs-best-practices](./skills/web/nextjs-best-practices/) | Next.js App Router principles — Server Components, data fetching, routing. | community / uncredited |
| [vercel-react-best-practices](./skills/web/vercel-react-best-practices/) | React and Next.js performance optimization guidelines from Vercel Engineering. | vercel |
| [nextjs-supabase-auth](./skills/web/nextjs-supabase-auth/) | Integrating Supabase Auth with the Next.js App Router — login, middleware, protected routes. | community / uncredited |
| [webapp-testing](./skills/web/webapp-testing/) | Interacting with and testing local web apps via Playwright — verify UI, debug, screenshots, logs. | community / uncredited |
| [seo-audit](./skills/web/seo-audit/) | Audit, review, or diagnose SEO issues — technical SEO, on-page SEO, meta tags, health checks. | community / uncredited |
| [remotion-best-practices](./skills/web/remotion-best-practices/) | Best practices for Remotion — video creation in React. | community / uncredited |

### data
Databases, queries, and data-layer performance.

| Skill | Description | Author |
|-------|-------------|--------|
| [supabase-postgres-best-practices](./skills/data/supabase-postgres-best-practices/) | Postgres performance optimization and best practices from Supabase. | supabase |

### tooling
Building developer tooling and agent infrastructure.

| Skill | Description | Author |
|-------|-------------|--------|
| [mcp-builder](./skills/tooling/mcp-builder/) | Building high-quality MCP servers — Python (FastMCP) or Node/TypeScript (MCP SDK). | community / uncredited |

## Install

Skills are plain `SKILL.md` files, so any harness that reads skills can consume them. Paths now include the category: `skills/<category>/<name>/SKILL.md`.

**Hermes**
```bash
hermes skills install https://raw.githubusercontent.com/Folken2/skills/main/skills/<category>/<name>/SKILL.md
# e.g.
hermes skills install https://raw.githubusercontent.com/Folken2/skills/main/skills/design/frontend-design/SKILL.md
```

**Claude Code** — copy the skill directory into your skills folder:
```bash
# per-user
git clone https://github.com/Folken2/skills.git /tmp/skills
cp -r /tmp/skills/skills/<category>/<name> ~/.claude/skills/<name>
# e.g.
cp -r /tmp/skills/skills/web/nextjs-best-practices ~/.claude/skills/nextjs-best-practices
```

**Cursor** — copy into the project's Cursor skills folder:
```bash
cp -r /tmp/skills/skills/<category>/<name> .cursor/skills/<name>
```

**Codex / Gemini** — copy into the shared agents skills folder:
```bash
cp -r /tmp/skills/skills/<category>/<name> .agents/skills/<name>
```

**Manual** — open `skills/<category>/<name>/SKILL.md` and paste its contents into your agent's context or system prompt.

## Contributing

1. Add your skill as `skills/<category>/<name>/SKILL.md` (create a new category dir only if none of the existing six fit).
2. Include YAML frontmatter with at least:
   ```yaml
   ---
   name: your-skill-name
   description: One line on when to use it and what it does.
   version: 1.0.0
   author: your-handle
   ---
   ```
3. Keep the skill **self-contained** — bundle any reference files it needs inside its own directory.
4. Update [`skills/index.json`](./skills/index.json) with an entry (name, description, author) under the right category, and add a row to that category's `README.md`.
5. Don't edit unrelated skill bodies.

## License

MIT
