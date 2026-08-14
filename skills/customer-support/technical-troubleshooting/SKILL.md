---
name: technical-troubleshooting
description: "Use when a customer reports something not working and you need a structured path from symptom to resolution — capture, knowledge-base search, reproduce/isolate/test diagnosis, fix or workaround or escalate, and evidence-backed handoff. Triggers on 'it's not working', 'I get an error', 'broken', 'can't log in', 'reproduce the issue', 'escalate to engineering'."
version: 1.0.0
author: Nuvel Skills
---

# Technical Troubleshooting

## Overview

Technical support fails in two directions: guessing at fixes without understanding the problem, and escalating everything to engineering to avoid thinking. The core principle: **diagnose systematically — reproduce, isolate, test one hypothesis at a time — and escalate only with the evidence that lets the next person start where you stopped.** A disciplined troubleshooter resolves most tickets at their tier and makes the rare escalation land cleanly.

This skill is a general playbook that works for any product surface — web app, mobile, hardware, API, or integration. It does not assume a specific stack; it assumes a symptom and a method.

## When to use

- A customer reports an error, failure, or unexpected behavior in a product.
- You need to reproduce and diagnose a fault before offering a fix.
- You must decide between a fix, a workaround, and an escalation.
- You are preparing an escalation to a higher tier or engineering and need the evidence packaged.

## When NOT to use

- The ticket is not yet classified or prioritized → run [[ticket-triage]] first.
- The issue is about an order, shipment, refund, or payment → use [[order-management]].
- Nothing is broken; the customer needs wording or de-escalation → use [[customer-communication]].

## Workflow

1. **Capture the symptom precisely.** Get **what** happens (exact error text/screenshot, not a paraphrase), **when** it started, **where** (which screen/action/endpoint), **how often** (always/intermittent), and the **environment** (device, OS, browser/app version, account, region). "It's broken" is not a symptom — drive to a concrete, observable failure.
2. **Search the knowledge base first.** Check existing articles, known-issue lists, and recent similar tickets before investigating from scratch. Most inbound issues are already solved; matching to a known solution is faster and more reliable than a fresh diagnosis. If it matches a known issue, jump to the documented resolution.
3. **Reproduce.** Attempt to recreate the failure using the captured steps and environment. A reproduction is the ground truth of troubleshooting — it confirms the problem is real, reveals details the customer omitted, and gives you a way to verify any fix. If you cannot reproduce, gather more environment specifics before theorizing.
4. **Isolate.** Narrow the fault: does it happen on another account, device, network, or browser? With one variable changed at a time, separate customer-specific/config causes from product-wide ones. Changing several variables at once tells you nothing about which one mattered.
5. **Test one hypothesis at a time.** Form a specific, falsifiable hypothesis ("it fails because the session token expired"), test it, and record the result before forming the next. Do not shotgun multiple changes — you will fix it without knowing why, and it will recur.
6. **Confirm the root cause, then choose a resolution path.** With the cause confirmed, pick: a **fix** (resolve and verify against your reproduction), a **workaround** (restore the customer now, flag the underlying issue for a permanent fix), or **escalate** (beyond your tier's tools/permissions). Prefer a verified fix; a workaround is a bridge, not a destination.
7. **Escalate with evidence.** When escalating, package: exact reproduction steps, the affected environment, relevant logs/screenshots/IDs, the hypotheses already tested and ruled out, and the impact/severity. An escalation without evidence bounces back and costs a full cycle — see [[ticket-triage]] for the severity and handoff format.
8. **Follow up after resolution.** Confirm with the customer that the fix holds in their environment, not just yours. Document the root cause and solution in the knowledge base so the next occurrence is a step-2 match, not a fresh investigation.

## Common Pitfalls

- **Fixing before understanding.** Trying random remedies may make the symptom vanish without fixing the cause, so it returns. Reproduce and confirm the root cause first.
- **Changing multiple variables at once.** If you swap browser, network, and account together and it works, you have learned nothing. Isolate one variable at a time.
- **Skipping the knowledge base.** Re-diagnosing a known issue wastes time and risks a worse answer than the documented one. Search before you investigate.
- **Escalating without evidence.** A bare "engineering, please help" forces the next tier to redo your work. Attach reproduction, environment, logs, and ruled-out hypotheses.
- **Declaring victory on your machine.** A fix that works in your environment may not in the customer's. Confirm with the customer before closing.

## Verification Checklist

- [ ] Symptom captured with exact error, timing, location, frequency, and environment.
- [ ] Knowledge base and similar tickets searched before fresh investigation.
- [ ] Issue reproduced — or, if not reproducible, additional environment data gathered.
- [ ] Fault isolated by changing one variable at a time (account/device/network/version).
- [ ] Root cause confirmed via single-hypothesis testing, not a batch of simultaneous changes.
- [ ] Resolution path chosen (fix / workaround / escalate) with a verified fix preferred.
- [ ] Any escalation includes reproduction steps, environment, logs/screenshots, tried hypotheses, and impact.
- [ ] Customer confirmed the resolution holds, and the root cause + solution were documented for reuse.
