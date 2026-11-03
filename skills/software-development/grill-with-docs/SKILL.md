---
name: grill-with-docs
description: Use when a plan or design needs grilling that also writes the project's language down. Runs the round-based interview while maintaining GLOSSARY.md and ADRs inline.
version: 1.0.0
author: Matt Pocock (mattpocock/skills), adapted by Nuvel Skills
---

# Grill With Docs

A relentless interview that sharpens a plan **and** leaves documentation behind: a glossary of the project's language and ADRs for the decisions that deserve one. Run it at the start of a project and before any change big enough to have a design.

This skill is the grilling discipline plus the domain-modeling discipline. If the user only wants the interview and no docs, use `grilling` alone.

## Why the docs are the point

Agents dropped into a project have to guess the jargon as they go, so they spend twenty words where one would do. A glossary fixes that once and keeps paying: consistent names in code, faster navigation, less thinking spent decoding. The compression is the feature — *"a problem with the materialization cascade"* instead of *"a problem when a lesson inside a section of a course is made real"*.

The same interview is the cheapest moment to catch a decision that is hard to reverse and invisible to the next reader. Capture it while it is still live in someone's head.

## Workflow

**1. Grill in rounds.** Build the design tree, compute the frontier, and ask the whole frontier per round with a recommended answer attached to each question — full mechanics in `grilling`. Capture as you go; do not batch the writing to the end of the session.

**2. Challenge terms against the glossary.** The moment the user uses a term that conflicts with an existing `GLOSSARY.md` entry, surface it: *"Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"*

**3. Sharpen fuzzy language.** When a term is vague or overloaded, propose one canonical term: *"You're saying 'account' — do you mean the Customer or the User? Those are different things."* Do not let two names for one thing survive a round.

**4. Probe with concrete scenarios.** Stress-test the model with invented edge cases that force precision about boundaries: partial cancellation, a mid-flight plan change, an entity that belongs to two parents. Inventing the scenario is your job; deciding it is the user's.

**5. Cross-check the model against the code.** When the user states how something works, verify it. *"The code cancels whole Orders, but you said partial cancellation is possible — which is right?"* A silent mismatch becomes a bug in someone's mental model.

**6. Write the term down the moment it is resolved.** Append to `GLOSSARY.md` immediately, in the format below. Never batch: the context that made the term obvious is gone by the end of the session.

**7. Offer an ADR only when all three gates pass.**

- **Hard to reverse** — changing your mind later costs something meaningful.
- **Surprising without context** — a future reader will ask "why on earth is it done this way?"
- **A real trade-off** — genuine alternatives existed and one was picked for specific reasons.

Miss any gate and skip it. An ADR per decision is noise; the file's value is that everything in it mattered.

**8. Confirm the shared understanding** before building. The grilling round loop ends when the frontier is empty; the doc loop ends when every resolved term is in the glossary and every gate-passing decision is an ADR.

## File layout

Create files lazily — only once there is something to write. If there is no `GLOSSARY.md`, create it with the first resolved term. If there is no `docs/adr/`, create it with the first real ADR. A repo with one context:

```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

A repo with several contexts puts a `GLOSSARY-MAP.md` at the root pointing at each context's own glossary and ADR directory:

```
/
├── GLOSSARY-MAP.md
├── docs/adr/                    ← system-wide decisions
└── src/
    ├── ordering/{GLOSSARY.md,docs/adr/}
    └── billing/{GLOSSARY.md,docs/adr/}
```

## GLOSSARY.md format

One entry per term, alphabetical, no implementation detail.

```markdown
# Glossary

## Order
A customer's commitment to buy a set of line items at agreed prices. Has a lifecycle
(draft → placed → fulfilled → cancelled); cancellation is all-or-nothing.

_Avoid_: purchase, basket, cart

## Reservation
A time-boxed hold on stock that has not been paid for. Expires automatically.
```

Rules:

- **One canonical term per concept.** List the rejected synonyms under `_Avoid_` so the next reader (human or agent) stops reaching for them.
- **Glossary only.** No schemas, no endpoints, no "how we plan to build it", no scratch notes. If it describes the implementation rather than the domain, it belongs somewhere else.
- **Definition first, boundaries second.** Say what it is, then where it ends.

## ADR format

```markdown
# 0001 — Event-sourced orders

**Status:** accepted
**Date:** 2026-11-03

## Context
What forced a decision, in two or three sentences.

## Decision
What was chosen.

## Alternatives considered
What else was on the table, and the specific reason each lost.

## Consequences
What becomes easy, what becomes hard, what would make us revisit this.
```

Number sequentially from `0001`. Never edit an accepted ADR's decision — supersede it with a new one and mark the old `superseded by 000N`.

## Pitfalls

- **Writing the glossary from the code.** The glossary is the domain language, not a rename of the schema. If a term only exists because of a table name, it is not a term.
- **Glossary drift.** The glossary is a single source of truth: when a term changes, edit the entry and fix the call sites. Two names for one thing is the bug this skill exists to prevent.
- **ADRs as a change log.** "We added an index" is not an ADR. The three gates exist to keep the file decision-dense.
- **Docs at the end.** Deferred writing loses the reasoning that made the decision obvious, and produces a glossary of whatever code happened to be written.

## Attribution

Adapted from `grill-with-docs` and `domain-modeling` in [mattpocock/skills](https://github.com/mattpocock/skills) (Matt Pocock / AI Hero, MIT). Upstream ships these as separate skills; this version folds the domain-modeling discipline into the body so it stands alone in any harness.
