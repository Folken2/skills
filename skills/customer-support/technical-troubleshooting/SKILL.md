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

## Toolchain

Troubleshooting is only reusable if it is logged. Use these supporting skills to capture and mine the data:

- [[backoffice/xlsx]] — log symptom and environment data into a troubleshooting workbook, search the KB resolution spreadsheet, write the diagnosis and resolution back, and generate a weekly trend report.
- [[backoffice/pdf]] — render a weekly trend report or an escalation evidence package as a PDF.

A runnable example lives in `scripts/generate_troubleshooting_log.py`, which builds a three-sheet workbook (Troubleshooting Log, KB Resolutions, Weekly Trend).

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

1. **Capture the symptom precisely.** Get **what** happens (exact error text/screenshot, not a paraphrase), **when** it started, **where** (which screen/action/endpoint), **how often** (always/intermittent), and the **environment** (device, OS, browser/app version, account, region). Open a new case row in the **Troubleshooting Log** sheet with [[backoffice/xlsx]] and record the symptom and environment columns immediately. "It's broken" is not a symptom — drive to a concrete, observable failure.
2. **Search the knowledge base first.** Search the **KB Resolutions** spreadsheet with [[backoffice/xlsx]] — match the captured symptom against the Symptom Pattern column to find documented Resolution Steps — before investigating from scratch. Most inbound issues are already solved; matching to a known solution is faster and more reliable than a fresh diagnosis. If it matches a known issue, jump to the documented resolution.
3. **Reproduce.** Attempt to recreate the failure using the captured steps and environment. A reproduction is the ground truth of troubleshooting — it confirms the problem is real, reveals details the customer omitted, and gives you a way to verify any fix. If you cannot reproduce, gather more environment specifics before theorizing.
4. **Isolate.** Narrow the fault: does it happen on another account, device, network, or browser? With one variable changed at a time, separate customer-specific/config causes from product-wide ones. Changing several variables at once tells you nothing about which one mattered.
5. **Test one hypothesis at a time.** Form a specific, falsifiable hypothesis ("it fails because the session token expired"), test it, and record the result before forming the next. Do not shotgun multiple changes — you will fix it without knowing why, and it will recur.
6. **Confirm the root cause, then choose a resolution path.** With the cause confirmed, pick: a **fix** (resolve and verify against your reproduction), a **workaround** (restore the customer now, flag the underlying issue for a permanent fix), or **escalate** (beyond your tier's tools/permissions). Prefer a verified fix; a workaround is a bridge, not a destination. Write the Diagnosis, Resolution, Status, Time Spent, and Escalated columns back to the case's row in the Troubleshooting Log with [[backoffice/xlsx]].
7. **Escalate with evidence.** When escalating, package: exact reproduction steps, the affected environment, relevant logs/screenshots/IDs, the hypotheses already tested and ruled out, and the impact/severity. An escalation without evidence bounces back and costs a full cycle — see [[ticket-triage]] for the severity and handoff format.
8. **Follow up after resolution.** Confirm with the customer that the fix holds in their environment, not just yours. Document the root cause and solution as a new row in the KB Resolutions sheet with [[backoffice/xlsx]] so the next occurrence is a step-2 match, not a fresh investigation, and refresh the **Weekly Trend** sheet — cases by product, by issue type, and escalation rate — rendering it to PDF with [[backoffice/pdf]] when reporting up.

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
- [ ] The case was logged (symptom, diagnosis, resolution) in the Troubleshooting Log and the Weekly Trend report reflects it.

## Supporting skills

- [[backoffice/xlsx]] — log cases in the Troubleshooting Log, search the KB Resolutions sheet, and build the Weekly Trend report.
- [[backoffice/pdf]] — render the weekly trend report or escalation evidence package as a PDF.
- [[ticket-triage]], [[order-management]], [[customer-communication]] — severity/handoff format, order-side faults, and customer-facing wording.
