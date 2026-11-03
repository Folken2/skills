---
name: to-tickets
description: Use when a plan, spec, or conversation must become implementable work. Breaks it into tracer-bullet vertical slices with declared blocking edges, then publishes them to the issue tracker.
version: 1.0.0
author: Matt Pocock (mattpocock/skills), adapted by Nuvel Skills
---

# To Tickets

Break a plan, spec, or conversation into **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it. Tickets are agent-grabbable by construction — sized for one fresh context window, with edges that say exactly what can start now.

## Workflow

**1. Gather context.** Work from whatever is already in the conversation. If the user passes a reference (a spec path, an issue number or URL), fetch it and read the full body *and* the comments — the comments are usually where the constraints live.

**2. Explore the codebase.** If you have not already, look at the current state of the code before slicing. Ticket titles and descriptions use the project's glossary vocabulary and respect the ADRs in the area being touched. Look for prefactoring that makes the implementation easier: *make the change easy, then make the easy change.* Prefactoring is always the first ticket.

**3. Draft tracer-bullet vertical slices.**

- Each slice cuts a narrow but **complete** path through every layer (schema, API, UI, tests) — vertical, not a horizontal slice of one layer.
- A completed slice is demoable or verifiable on its own.
- Each slice fits in a single fresh context window.
- Any prefactoring comes first.

**4. Give each ticket its blocking edges.** A **blocking edge** points at a ticket that must complete before this one can start. A ticket with no blockers can start immediately. Edges are the whole value: they let several agents work in parallel on the frontier without coordinating.

**5. Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites and no vertical slice can land green. Sequence it as **expand–contract** instead:

- **Expand** — add the new form beside the old so nothing breaks.
- **Migrate** — move call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, with CI green batch to batch because the old form still exists.
- **Contract** — delete the old form once no caller remains, in a ticket blocked by every migrate batch.

When even the batches cannot stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket — green is promised only there.

**6. Quiz the user before publishing.** Present the breakdown as a numbered list. For each ticket show its **title**, its **blocked by** edges, and **what it delivers** (the end-to-end behaviour it makes work). Ask:

- Does the granularity feel right (too coarse / too fine)?
- Are the blocking edges correct — does each ticket depend only on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown. Publishing unapproved tickets puts guesses on the board where other agents will act on them.

**7. Publish in dependency order** (blockers first) so edges can reference real identifiers. Match the shape to the tracker already in use:

- **Local files** → one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order. Each file's "Blocked by" lists the numbers and titles it depends on. One ticket per file, never a single combined file.
- **GitHub** → one issue per ticket via `gh issue create`, applying the repo's agent-ready label, and writing each blocking issue's number into every dependent ticket. Use the platform's native blocking or sub-issue relationship when it has one.
- **Linear / other trackers** → same content, mapped onto the tracker's native parent/blocking fields.

Never close or modify the parent issue or spec — it is the record of the original request.

**8. Work the frontier.** Any ticket whose blockers are all done is startable. For a purely linear chain that means top to bottom. Recompute the frontier as tickets close; do not start a ticket whose blocker is still open.

## Templates

Local ticket file:

```markdown
# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective — not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
```

GitHub issue body:

```markdown
## Parent
A reference to the parent issue (omit if the source was a plain conversation).

## What to build
The end-to-end behaviour this ticket makes work, from the user's perspective.

## Acceptance criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by
- A reference to each blocking ticket, or "None (can start immediately)".
```

In either form, avoid specific file paths or code snippets — they go stale faster than the ticket is worked. The exception: when a prototype produced a snippet that encodes a decision more precisely than prose can (a state machine, a reducer, a schema, a type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Pitfalls

- **Horizontal slices.** "Add the database columns" is not a tracer bullet — nothing is verifiable at the end of it. Cut through the layers instead.
- **Oversized tickets.** If a slice cannot fit in one fresh context window, it is two tickets. Size on what an agent must hold, not on what feels like a day's work.
- **Edges as ordering, not gating.** "It felt natural to do this second" is not a blocking edge; a false edge serialises work that could run in parallel.
- **Emitting a checklist instead of publishing.** The deliverable is tickets on the tracker (or files on disk), not a plan in the chat.
- **Restating an existing tracker item.** Search for the work before creating it; a duplicate ticket is worse than a missing one.

## Attribution

Adapted from `to-tickets` in [mattpocock/skills](https://github.com/mattpocock/skills) (Matt Pocock / AI Hero, MIT). The tracer-bullet vertical-slice method and the expand–contract treatment of wide refactors are his; this version drops the upstream `/setup-matt-pocock-skills` prerequisite and states the tracker mapping explicitly.
