---
name: skill-promotion
description: "Promote a dogfooded internal skill into the canonical repo — curation gate, versioning, attribution review, PR workflow."
version: 1.0.0
author: Nuvel Skills
---

# Skill Promotion

## When to use this
Use when a skill has been used internally (dogfooded) at least twice and proven its value, and you want to promote it from a local agent skills directory into the canonical Nuvel Skills repo (Folken2/skills).

## Curation gates (MUST ALL PASS)

- [ ] **Owned & opinionated** — encodes a decision your company made, not a vendor's docs reproduced.
- [ ] **Earned by the "asked twice" rule** — encodes a process you've actually run more than once.
- [ ] **Harness-agnostic** — runs the same on Hermes, Claude Code, and future agents. No hard dependency on one runtime's tools.
- [ ] **Composable & single-purpose** — one job, one clear trigger, links to sibling skills instead of duplicating them.
- [ ] **Verifiable exit** — has a definition-of-done / checklist the agent can self-check against.
- [ ] **Portfolio-safe** — you would show it verbatim to an enterprise design partner as evidence of how your company works.

## Promotion workflow

### Phase 1: Preparation
1. Gather the skill's files from its local location (e.g. ~/.hermes/skills/<name>/)
2. Verify it PASSES all 6 curation gates
3. Check skills/index.json for the correct theme (software-development, growth, backoffice, or skillification)
4. If no existing theme fits, discuss with the founder whether a new category is needed

### Phase 2: Bundling
1. Create the theme directory path: skills/<theme>/<name>/
2. Copy SKILL.md and any supporting files (references/, scripts/) from the local location
3. Set frontmatter: name, description, version (bump if re-submitting an update), author: "Nuvel Skills"
4. Attribute third-party sources explicitly (author field or attribution note in SKILL.md)

### Phase 3: Integration
1. Update skills/index.json: add the new entry in the correct theme array, all fields
2. If the skill introduces a new theme (e.g. "skillification")
   - Create the theme directory
   - Add a category object to skills/index.json: "skillification": [{"name": "...", ...}]
3. If the skill touches an existing README section, patch it

### Phase 4: The PR
1. Push a branch to Folken2/skills: git checkout -b feat/<skill-name>
2. git add -A && git commit -m "feat: add <name> skill"
3. git push origin feat/<skill-name>
4. Open PR with gh:
   gh pr create --repo Folken2/skills --head feat/<name> --base main \
     --title "feat: add <name> skill" \
     --body "## Summary\n(what the skill does and why it passes the curation gates)\n## Curation gates checklist\n- [x] Owned & opinionated — ...\n- [x] Earned by asked-twice rule — ...\n..."

### Phase 5: Maintenance
- When a skill updates its deterministic steps (breaking change), bump its version
- When a skill goes stale (>90 days unused), flag it for curation review

## Example: completed promotion
> This skill was dogfooded 4 times in Co-assistant development. It passes all 6 curation gates. The deliverables are: skills/skillification/skill-promotion/ directory, index.json update, PR.
