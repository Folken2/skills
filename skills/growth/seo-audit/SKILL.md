---
name: seo-audit
description: "Use when auditing, reviewing, or diagnosing SEO on a site — crawl the site, run a scored technical + on-page + keyword audit, and produce a prioritized, effort-estimated fix queue. Also use for 'SEO health check,' 'technical SEO,' 'why am I not ranking,' or 'meta tags review.'"
version: 1.0.0
author: Nuvel Skills
---

# SEO Audit

## Overview

An SEO audit that ends in a long list of "issues found" is a report nobody acts on. This skill produces a *scored, ranked, effort-estimated fix queue* — every finding carries a severity, a score, and an estimate, so the team knows what to fix first and what to ignore.

**Core principle:** Score, then rank, then sequence. An issue with no severity score is un-triaged, and un-triaged findings get worked in whatever order someone happens to read them — which is the same as not prioritizing at all. Crawlability blockers outrank cosmetic on-page nits every time, and the score has to encode that.

## When to use

- A site needs a full or scoped SEO health check before a growth push.
- Organic traffic dropped or plateaued and the cause is unknown.
- Before or after a migration, redesign, or replatform.

## When NOT to use

- **Building pages at scale to target keywords** — that's a production task, not an audit.
- **Pure conversion optimization** — ranking ≠ converting; audit for rankings here, optimize the page separately.
- **A single-page spot check** — steps 1–2 are overkill; jump to the on-page checklist for one URL.

## The workflow

```
STEP 1        STEP 2         STEP 3        STEP 4        STEP 5      STEP 6
crawl      →  technical  →  on-page   →  keyword    →  score    →  report
(inventory)   (indexation)  (content)     (mapping)     (0–100)     (fix queue)
```

### STEP 1 — Crawl and inventory

Run a full crawl (Screaming Frog, Sitebulb, HTTrack, or equivalent). Capture for every URL: status code, redirect target and chain depth, canonical tag, indexability, title, meta description, H1, and word count.
**Exit:** a URL inventory table exists with status codes and redirect chains resolved. Every 3xx/4xx/5xx is listed with its source page.

### STEP 2 — Technical audit

Check, and record pass/fail with evidence for each:
- **Crawlability:** robots.txt (no accidental blocks, sitemap referenced), sitemap.xml (accessible, only canonical indexable URLs), index status vs. expected (`site:` + Search Console coverage).
- **Speed / Core Web Vitals:** LCP < 2.5s, INP < 200ms, CLS < 0.1 (field data, not just lab).
- **Mobile:** responsive, viewport set, tap targets, parity with desktop.
- **HTTPS:** site-wide, valid cert, no mixed content, HTTP→HTTPS redirects.
- **Redirects & canonicals:** no chains > 1 hop, no loops, self-referencing canonicals on unique pages.
- **Structured data:** validates against the Rich Results Test with no errors.

**Exit:** every technical check has a pass/fail verdict with a URL or screenshot as evidence.

### STEP 3 — On-page audit

For sampled and template pages: title tags (unique, 50–60 chars, keyword-forward), meta descriptions (unique, 150–160 chars), heading hierarchy (one H1, no skipped levels), content depth vs. intent and top competitors, internal linking (no orphans, descriptive anchors), image alt text, and URL structure (readable, lowercase, hyphenated).
**Exit:** on-page findings logged per template/page type, with the specific failing element named.

### STEP 4 — Keyword mapping

Map target keywords to URLs. Identify: content gaps (target keyword with no owning page), cannibalization (two+ pages competing for one keyword), and current-rank vs. target-rank deltas.
**Exit:** a keyword→URL map with gaps and cannibalization pairs explicitly listed.

### STEP 5 — Score every issue (0–100)

Assign each finding a severity band and a numeric score. Suggested banding:

| Band | Score | Meaning |
|---|---|---|
| **Critical** | 90–100 | Blocks indexing or ranking (noindex on money pages, sitewide 5xx, redirect loops). |
| **Major** | 60–89 | Materially suppresses ranking (slow CWV, thin content, cannibalization). |
| **Minor** | 30–59 | Marginal impact (single missing alt text, sub-optimal title length). |
| **Info** | 0–29 | Nice-to-have, no ranking effect. |

Flag **quick wins**: any Major/Critical issue with a low effort estimate. These jump the queue.
**Exit:** every finding has a score, a band, and an S/M/L effort estimate; quick wins are tagged.

### STEP 6 — Report and fix queue

Produce: an executive summary (health verdict + top 3–5 issues), the scored findings grouped by area, and a **prioritized fix queue** sorted by score-per-effort, grouped into sprints. Each queue item: issue, evidence, fix, score, effort, owner.
**Exit:** report delivered with a ranked fix queue and a standalone quick-wins list.

## Common Pitfalls

- **Reporting without ranking.** A flat list of 80 issues is not an audit output — the deliverable is the *ordered* queue. If it's not sorted by impact-per-effort, you're not done.
- **Lab-only Core Web Vitals.** A green Lighthouse score with red field data means real users are suffering. Use field/CrUX data for the verdict.
- **Confusing "indexed" with "ranking."** A page can be perfectly indexed and still deserve to rank nowhere. Check content quality, not just crawlability.
- **Scoring by gut.** If two people would score the same issue differently, the banding rubric isn't concrete enough. Tie scores to observable evidence.
- **Auditing every URL by hand.** Sample by template. Ten product pages built from one template share one finding — log it once against the template.

## Verification Checklist

- [ ] Full crawl completed; URL inventory with status codes and resolved redirect chains exists.
- [ ] Every technical check (crawlability, CWV, mobile, HTTPS, redirects/canonicals, structured data) has a pass/fail verdict with evidence.
- [ ] On-page findings logged per template with the failing element named.
- [ ] Keyword→URL map produced; content gaps and cannibalization pairs listed.
- [ ] Every finding carries a severity band, a 0–100 score, and an S/M/L effort estimate.
- [ ] Quick wins tagged (high-impact + low-effort).
- [ ] Prioritized fix queue delivered, sorted by impact-per-effort and grouped into sprints.
- [ ] Executive summary names the top 3–5 issues and the overall health verdict.

## Cross-references

- **content-pipeline** — fixing thin-content and gap findings feeds directly into the content brief stage.
- **analytics-setup** — establish the organic-traffic baseline and conversion tracking used to measure audit fixes.
