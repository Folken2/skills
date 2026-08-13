---
name: feature-shaping
description: "Shape a vague idea or request into a structured spec before planning or building. Bridges brainstorming and writing-plans."
version: 1.0.0
author: Nuvel Skills
---

# Feature Shaping

Use when you have a vague idea, request, or feature concept that needs to be framed before it can be planned or built. This is the bridge between brainstorming and writing-plans.

## When NOT to use
- When you already have a clear, detailed spec (skip this, go to planning)
- When developing an already-agreed plan (skip this, go to execution)
- For bug fixes (use bug-triage instead)

## Workflow

### 1. Problem framing
- What is the user problem or opportunity? (one sentence)
- Why is it a worthy problem to solve now?
- What happens if we don't do it?

### 2. Context & constraints
- What has been tried before? Why did it work or not work?
- Are there time, budget, or resource limitations?
- What other systems or teams depend on this?

### 3. Scope definition
- **In scope:** explicit list of what this feature includes
- **Out of scope:** explicit list of what it does NOT include (prevents creep)
- **Definition of done:** what does "done" look like for this feature?

### 4. Success metrics
- How will we know if this works? (measurable, not feel-good)
- What targets must we hit? (e.g. < 200ms latency, 90% retention)

### 5. Risk identification
- What could go wrong? (table: risk | impact | likelihood | mitigation)
- What changes might be irreversible or hard to roll back?

### 6. Output
- One-paragraph executive summary (for stakeholders)
- The bullet-listed in-scope / out-of-scope definition
- Definition of done and test targets

Always produce these as the deliverable. If any section is "not applicable," say so plainly rather than fabricating an answer.

## After this
Route to: writing-plans (or superpowers:writing-plans) to turn the spec into an implementable plan.
