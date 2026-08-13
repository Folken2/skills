---
name: bug-triage
description: Use when a bug, error, crash, or unexpected behavior is reported and you need to decide how much investigation it warrants before fixing — start simple, expand to deep investigation only when the bug is genuinely complex.
version: 1.0.0
author: Nuvel Skills (inspired by Brandon Bayer / rag.saas-shipkit)
---

# Bug Triage

## Overview

Most bugs are simple. A triage-first workflow gets you to the fix fast without drowning a one-line typo in a full root-cause investigation — while still forcing rigor on the bugs that actually deserve it.

**Core principle:** Capture the exact error first, classify it, act on the classification. Only genuinely complex bugs earn the Deep Investigation phase.

The discipline here is *proportional response*: match the depth of investigation to the actual complexity of the bug, and never skip STEP 1 to save time.

## When to use this vs systematic-debugging

This skill owns the **proportional-response decision** — classify the bug first, escalate only when needed. Use it when you need to decide how much investigation a bug warrants before fixing.

- If STEP 2 classifies the bug as **"complex"** → hand off to `superpowers:systematic-debugging` for the deep investigation. This skill covers the classification and simple-fix path; systematic-debugging handles the full root-cause tracing.
- If STEP 2 classifies as **simple fix / missing import / type / env** → continue with STEP 3 here.

## The Workflow

```
STEP 1 (always)   →  STEP 2 (always)   →  STEP 3 (branch by category)
capture the error    classify it          simple → fix now
                                          complex → Deep Investigation
```

### STEP 1 — Capture Critical Info (never skip)

You cannot fix what you cannot see. Before hypothesizing, get:

- **Exact error text** — the full message or stack trace, copy-pasted, not paraphrased.
- **Trigger** — the specific action that causes it (page load, button click, cron run, API call).
- **Location** — where the error surfaces (browser console, network tab, server logs, terminal, UI).
- **Environment** — dev / staging / prod, runtime version, relevant config.
- **Reproducibility** — always / intermittent / only under specific conditions (describe them).

If any of these are missing, get them before continuing. A guess without the error text is a wasted fix attempt.

- **For intermittent/nondeterministic bugs:** capture the conditions under which the bug appears (time of day, data volume, specific inputs, user session, browser/device, previous actions). If a reliable reproduction is impossible, note this — the bug may need instrumentation or stress testing rather than a single reproduce-then-verify cycle.

### STEP 2 — Classify

Based on the captured error, pick the single best-fit category:

| Category | Signal |
|---|---|
| **Simple fix** | Typo, off-by-one, obvious one-liner, clear syntax error |
| **Missing file/import** | 404, `Cannot find module`, `is not defined`, file-not-found |
| **Type/interface** | Type errors, wrong shape, null/undefined where a value was expected |
| **Environment/config** | Missing API key, wrong URL, DB connection, env var not set |
| **Complex system issue** | Error is a symptom; cause spans multiple components or data flow |

When two categories seem to fit, pick the *simpler* one and try it first — you can escalate, but you cannot un-waste an over-analysis.

### STEP 3 — Immediate Action (branch by category)

**Simple fix** — apply the fix directly, then verify the specific error case is gone.

**Missing file/import** — confirm the file/dependency exists and the path/casing is correct; check it is installed and exported. Fix the reference or install the dependency.

**Type/interface** — locate the type definition; check the actual runtime shape against the declared type; fix whichever is wrong (usually the code, sometimes the type).

**Environment/config** — verify the specific setting exists and is correct in *this* environment; compare against a known-good environment. Never assume a value — read it.

**Complex system issue** — do not guess. Escalate to Deep Investigation below.

## Deep Investigation (complex bugs only)

Only enter here when STEP 2 landed on "complex." This is where you slow down and trace, not pattern-match.

**A. Map the code.** Find all code related to the failing component: its imports/dependencies, what feeds into it (upstream), and what consumes it (downstream). Note any coupling that could carry the fault.

**B. Root-cause analysis.** Trace the full flow from the user action to the error point. At each hop, compare expected state/data/result against actual. The **break point** is the first hop where they diverge; the **root cause** is *why* they diverge there — not the symptom two hops later.

**C. System context.** Is the failing code following the established patterns of the codebase, or is it an outlier? Are there better examples of this pattern elsewhere to align to? Is this component doing too much?

**D. Weigh solution options.** For a non-trivial fix, name 2–3 options (surface fix / systematic fix / refactor). For each: what it does, its risk (low/med/high), and whether it follows codebase best practices. Recommend one, with reasoning.

**E. Assess cascade effects.** What does this fix touch beyond the immediate line? What else needs testing? Any migration or deployment considerations? (For a thorough pass, use the **second-order-impact-analysis** skill.)

## Verification (after any fix)

- [ ] The specific error case from STEP 1 no longer reproduces.
- **For intermittent bugs:** verification means the bug does not appear under the captured conditions after N repeated runs (N >= 5), or monitoring/instrumentation shows the root cause is addressed. Document the test methodology used.
- [ ] No new errors introduced (type-check, lint, tests, relevant runtime path).
- [ ] Checked for the same bug pattern elsewhere in the codebase.
- [ ] For complex fixes: the affected downstream consumers still behave correctly.

## Red Flags — STOP

These thoughts mean you are about to triage badly:

| Thought | Reality |
|---|---|
| "I'll just start fixing, I know what it is" | Not without the exact error text. Do STEP 1. |
| "Let me write a deep root-cause analysis" (for a typo) | Over-analysis. Classify first; most bugs are simple. |
| "The error message is probably X" | Read the actual message. Paraphrased errors mislead. |
| "It works on my machine, so it's an env issue" | Verify the env var/config, don't assume. |
| "I'll fix the symptom and move on" | Find the break point and the root cause, not the surface. |
| "Reproduction steps don't matter" | A fix you can't reproduce-then-verify is a guess. |

## Common Mistakes to Avoid

| Don't | Do |
|---|---|
| Fill out every investigation section for a one-liner | Expand only when STEP 2 says "complex" |
| Speculate without the error details | Get the exact error and repro first |
| Over-analyze simple typos | Start with the simplest explanation |
| Write essays when a quick fix will do | Favor action over analysis |
| Fix the symptom | Trace to the break point and root cause |
| Assume config values | Read the actual value in the actual environment |

**Remember:** Most bugs are simple. Start simple, expand only when the bug earns it.
