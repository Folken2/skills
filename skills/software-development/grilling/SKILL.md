---
name: grilling
description: Use when a plan, design, decision, or idea needs stress-testing before work starts. Runs a relentless, round-based interview over the design tree until every branch is settled.
version: 1.0.0
author: Matt Pocock (mattpocock/skills), adapted by Nuvel Skills
---

# Grilling

Interview the user relentlessly until you reach a shared understanding. Do not build anything until they confirm that understanding.

The failure this prevents is misalignment: the agent builds something competent that answers a question nobody asked. Grilling is cheap; rebuilding is not.

## The design tree

Map the work being discussed as a **design tree**: every decision branches into the decisions that hang off it. The root is the goal; the leaves are the small choices that only make sense once their parents are settled.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you have not heard yet. A question whose answer depends on another question still open in this round belongs to a *later* round, not this one.

## Workflow

**1. Open a round.** Ask the whole frontier at once. Number each question and attach your own recommended answer to every one.

Format a round like so:

```
❓ **Q1** — **<question title>**: <question body; may be several paragraphs or list the options>

➡️ <your recommended answer>

---
❓ **Q2** — **<question title>**: <question body>

➡️ <your recommended answer>
```

**2. Word each question so that a plain "yes" accepts your recommendation.** A question the user can answer with one word is a question they will actually answer. Never ask an open question when you already hold a defensible default — offer the default and let them veto it.

**3. Wait.** Ask the round, then stop. Do not answer for the user, do not assume a likely answer, and do not keep working while you wait.

**4. Recompute the frontier** from their answers: settled decisions push the frontier outward and unblock the questions that depended on them. Ask the next round.

**5. Stop when the frontier is empty** — every branch of the tree visited, nothing left silently assumed. Summarise the settled decisions back to the user and get explicit confirmation before acting.

## Division of labour: facts vs decisions

**Facts are your job.** Whenever a frontier question needs something from the environment — a file, a schema, an API response, a version, a cost — go find it. Never ask the user for anything a lookup, a search, or a command can answer; asking a question you could have looked up spends their attention on your work.

Dispatch a subagent with a fresh context window for anything expensive to find, and **do not block the round on it**: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait. Ask the rest of the frontier now.

**Decisions are the user's.** Put each one to them and wait. When you find a fact that settles a decision (the dependency is already in the lockfile; the API caps at 100), say so as a *recommendation* — never silently decide on their behalf.

## Pitfalls

- **Reciting the user's own plan back at them.** A question whose answer you already wrote in the brief is a no-op. Drop it.
- **Bundling two decisions into one question.** The user answers the first half and never sees the second. Split it.
- **Asking for permission instead of grilling.** "Shall I proceed?" is not a question about the design; it is you stalling.
- **Grilling forever.** If the frontier keeps producing questions that do not change what you would build, you have the wrong decomposition — collapse the branch and move on.
- **Producing a design document instead of an interview.** The output of this skill is a decision tree the user agreed to, not prose.

## Attribution

Adapted from `grilling` in [mattpocock/skills](https://github.com/mattpocock/skills) (Matt Pocock / AI Hero, MIT). The round-based frontier interview is his method; this version drops the harness-specific invocation mechanics and routes fact-finding through subagents.
