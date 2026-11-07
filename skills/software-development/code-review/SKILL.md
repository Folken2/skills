---
name: code-review
description: Use when reviewing a branch, PR, or work-in-progress changes since a fixed point. Two-axis review — Standards (repo conventions plus a smell baseline) and Spec (does it implement the originating issue) — run as parallel subagents so neither pollutes the other.
version: 1.0.0
author: Matt Pocock (mattpocock/skills), adapted by Nuvel Skills
---

# Code Review

Review the diff between `HEAD` and a fixed point, along two axes:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does it faithfully implement the originating issue / spec?

Both axes run as **parallel subagents** so they don't pollute each other's context; this skill then
aggregates their findings.

## Why two axes

A change can pass one and fail the other:

- Follows every standard, implements the wrong thing → **Standards pass, Spec fail.**
- Does exactly what the issue asked, breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other. Do not merge or rerank the
findings afterwards — that is the failure the separation exists to prevent.

## Workflow

**1. Pin the fixed point.** Whatever the user gave — a commit, branch, tag, `main`, `HEAD~5`. If
none was given, ask. Capture the commands once:

```bash
git rev-parse <fixed-point>            # must resolve, or fail here
git diff <fixed-point>...HEAD          # three-dot: compare against the merge-base
git log <fixed-point>..HEAD --oneline  # the commits under review
```

A bad ref or an empty diff fails now, not inside two subagents.

**2. Find the spec.** In order: issue references in the commit messages (`#123`, `Closes #45`,
`!67`) fetched with the repo's tracker CLI; a path the user passed; a spec file under `docs/`,
`specs/` or `.scratch/` matching the branch name. If there is genuinely no spec, the Spec subagent
skips and says so.

**3. Find the standards.** Anything in the repo that says how code should be written —
`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, the linter config. On top of whatever the
repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of
Fowler smells (_Refactoring_, ch. 3) that applies even when a repo documents nothing. Two rules
bind it:

- **The repo overrides.** A documented repo standard wins; where it endorses something the baseline
  would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never
  a hard violation. Skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix it*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or
  holds. → rename it; if no honest name comes, the design is murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change.
  → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the
  method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be
  born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its
  own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change.
  → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. →
  gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each
  module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't
  have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the
  walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real
  target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it
  inherits. → drop the inheritance, use composition.

**4. Spawn both subagents in parallel** (the harness's delegation mechanism: a subagent tool, a
background agent, or two parallel review runs). Each gets a self-contained brief — it cannot see
this conversation.

**Standards subagent** — the diff command and commit list; the standards-source files found in step
3 **plus the smell baseline pasted in full** (the subagent has no other access to it); and this
brief:

> Report, per file/hunk where relevant, (a) every place the diff violates a documented standard:
> cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the
> hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard,
> but baseline smells are always judgement calls, and a documented repo standard overrides the
> baseline. Skip anything tooling enforces. Under 400 words.

**Spec subagent** — the diff command and commit list; the spec path or its fetched contents; and
this brief:

> Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the
> diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the
> implementation looks wrong. Quote the spec line for each finding. Under 400 words.

**5. Aggregate.** Present the two reports under `## Standards` and `## Spec`, verbatim or lightly
cleaned. End with one line: findings per axis, and the worst issue *within each axis*. Never pick a
single winner across axes.

## Rules

- **Judge the diff, not the author.** Nothing to say about a hunk means nothing to say about it.
- **Evidence or silence.** Every finding quotes the line it is about; a finding without a citation
  is an opinion.
- **A green test suite is necessary, not sufficient.** Passing tests never excuse a spec miss or a
  standard breach.
- **Untouched lines the diff now contradicts are in scope** — a change that makes an existing
  sentence false has introduced a defect, even though the sentence is old.
- **Report the axis's own verdict.** The Standards axis never rules on whether the work is the right
  work; the Spec axis never rules on code quality.
- **Under 400 words per axis.** A review that cannot be read is not a review.

## Attribution

Adapted from `code-review` in [mattpocock/skills](https://github.com/mattpocock/skills) (Matt
Pocock / AI Hero, MIT), which runs the two axes as parallel sub-agents. The Fowler smell baseline is
from Martin Fowler, _Refactoring_ (ch. 3). This version drops the upstream `/setup-matt-pocock-skills`
prerequisite (the tracker comes from the repo) and adds the rules section.
