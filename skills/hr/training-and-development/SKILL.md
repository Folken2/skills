---
name: training-and-development
description: "Manage employee training programs end-to-end — needs assessment, program design, delivery, completion tracking, certification, compliance documentation, and effectiveness evaluation. Triggers on: training program, skills gap, compliance training, LMS, learning plan, certification tracking, employee development."
version: 1.0.0
author: "Nuvel Skills"
---

# Training and Development

## Overview

Turn ad-hoc training requests into a managed program that builds workforce capability, meets compliance deadlines, and produces auditable records. The core principle: **training is infrastructure, not an event.** A training program (ongoing system for multiple topics and roles) is different from a training plan (a single course or session). Building infrastructure requires needs analysis, structured delivery, completion tracking, and effectiveness measurement — not just scheduling classes.

The average employee receives roughly 17 formal learning hours per year (ATD State of the Industry). Every misdirected hour is scrap learning — content delivered but never applied. A skills gap analysis is the required first step to ensure training targets actual deficits rather than assumptions.

## When to use

- You need to close a skills gap — current workforce capability does not meet the level required for a business goal, new process, or technology adoption.
- Compliance training (HazCom, LOTO, data privacy, anti-harassment, industry-specific) must be delivered, tracked, and auditable by a regulatory deadline.
- New-hire onboarding needs a structured ramp beyond what [[employee-onboarding]] covers — role-specific technical training, product knowledge, customer-process training.
- An employee needs a development plan — certification, upskilling, or cross-training.
- You are auditing whether past training completions are current and records are audit-ready.

## When NOT to use

- You are hiring a new employee who needs the basic 30-60-90 ramp → use [[employee-onboarding]].
- You are setting goals and running performance reviews → use [[performance-review-cycle]].
- An employee needs a growth plan outside formal training (mentoring, stretch assignments) → use [[employee-engagement]].
- You are designing compensation around new skills or certifications → use the compensation review process (separate skill).
- The "training need" is actually a process, tool, or documentation problem that training cannot fix → address the root cause, not the symptom.

## Workflow

### Phase 1: Needs Assessment

1. **Identify the business goal.** Every training program must trace to a measurable organizational outcome — reduce incident rate, increase product knowledge score, achieve SOC 2 compliance, shorten onboarding to competency. If no business goal exists, the program has no basis for evaluation later.

2. **Conduct a skills gap analysis.** For each role the program targets, define: (a) the required competency level for each relevant skill, (b) the current measured level, (c) the gap. Sources: performance data, manager input, audit findings, regulatory requirements, survey results. A gap of zero means no training is needed — skip the program and document why.

3. **Determine whether training is the right intervention.** A performance gap has five possible causes: lack of skill (training can fix), lack of knowledge (training can fix), lack of tools/process (fix the tool/process, not the person), lack of motivation (coaching and recognition, not training), or external constraints (policy, legal, structural). Only train for skill and knowledge gaps. Training designed for the wrong cause wastes budget and produces no result.

4. **Define the target audience and training format.** Consider: audience size, location (office, remote, shift-based, field), literacy level, language needs, technology access (desktop, mobile, offline), and preferred learning style. Shift-based and field workers need mobile-accessible content with offline capability; classroom-only delivery leaves coverage gaps.

### Phase 2: Program Design

5. **Write measurable learning objectives.** Each objective follows the format: *"By the end of this training, the employee will be able to [action verb] [task] to [standard]."* Examples:
   - "Identify the three types of HazCom labels and describe the required response for each."
   - "Complete a purchase requisition in the ERP system with zero data errors."
   - "Describe the steps of the incident response process within 30 seconds."
   Vague objectives ("understand", "be aware of", "learn about") produce unverifiable outcomes and are the most common design failure.

6. **Design the delivery method.** Match method to audience, content type, and budget:

   | Method | Best for | Avoid for |
   |--------|----------|-----------|
   | Instructor-led (in-person) | Hands-on skills, role-play, team-building, sensitive topics | Large-scale compliance refreshers |
   | Virtual instructor-led | Distributed teams, interactive sessions | Shift workers across time zones |
   | Self-paced eLearning | Compliance training, onboarding, refreshers | Complex skills needing real-time feedback |
   | Blended (multiple methods) | Deep skill building with theory + practice | When budget or time is constrained |
   | On-the-job / shadowing | Role-specific technical skills | Compliance-required documented training |
   | Microlearning (5-10 min) | Just-in-time reference, refresher, reinforcement | Initial comprehensive training |

### Phase 3: Development and Delivery

7. **Create or source the training materials.** Options: develop in-house, commission from a vendor, purchase off-the-shelf content, use an LMS content library. For regulated content (compliance, safety, certifications), ensure materials are vetted against the current regulatory standard — not last year's version.

8. **Build the assignment matrix.** Map every employee to the programs they require, by role, department, location, and compliance mandate. An LMS automates this; a spreadsheet breaks down beyond ~25 employees. Include: course name, due date or frequency, delivery format, assignment trigger (new hire, annual refresher, role change), and the completion deadline.

9. **Communicate the program.** Employees need to know: why the training matters (connects to their job and the business goal), what is expected (completion date, time commitment, pass/fail threshold), how to access it (LMS link, classroom schedule, manager sign-off), and what happens if they don't complete it (escalation, compliance flag). Manager reinforcement is the strongest predictor of training transfer — include a manager communication template.

10. **Deliver training and track completions.** Use the LMS or a structured tracking system to record: employee name, course name, completion date, score or pass/fail status, expiration/renewal date, and trainer or provider identity. For compliance training, the record must be audit-ready — name, date, and content identifier are the minimum.

### Phase 4: Evaluation and Improvement

11. **Evaluate at four levels (Kirkpatrick Model).**

    | Level | Question | Method |
    |-------|----------|--------|
    | 1. Reaction | Did employees find it relevant and engaging? | Post-training survey (NPS, relevance score) |
    | 2. Learning | Did they acquire the intended knowledge/skill? | Pre/post test, skills demonstration |
    | 3. Behavior | Do they apply it on the job? | Manager observation, 30-day follow-up, performance data |
    | 4. Results | Did it move the business goal? | Incident rate, audit score, productivity metric, retention |

    Level 4 evaluation requires the business goal from Step 1. Without it, you cannot measure results.

12. **Certify and document completions.** Issue certificates or mark completions in the LMS. For compliance-required training, archive the completion record with the employee's personnel file or compliance case file. Set renewal reminders for certifications that expire (annual, biennial, or per regulatory schedule).

13. **Run a program retrospective.** After each program cycle, gather: completion rates, evaluation scores, manager feedback, budget spent, and any compliance findings. Ask: (a) Did the program close the skill gap measured in Step 2? (b) What content was outdated or ineffective? (c) What delivery issues emerged? (d) What should change next cycle? Document the answers and update the program.

14. **Maintain the training catalog.** Keep a live catalog of all active training programs: name, audience, delivery method, frequency, content owner, last review date, next review date. Review each program at least annually or when the underlying regulation, process, or tool changes. A stale catalog is the top source of scrap learning — employees train on obsolete content because nobody checked.

## Red Flags

| Red Flag | Why it matters | Right approach |
|----------|----------------|----------------|
| No needs assessment before building training | Produces scrap learning — content delivered but never applied | Start every program with a skills gap analysis tied to a business goal |
| Training assigned to fix a process or tool problem | Training cannot fix a broken workflow; employees learn to work around the broken tool | Fix process/tool first, then train on the fixed version |
| Learning objectives use "understand" or "be aware of" | Unverifiable — no one can prove "understanding" | Use action verbs: identify, complete, describe, demonstrate, calculate |
| One delivery method for the entire workforce | Classroom-only misses shift workers; eLearning-only misses hands-on skills | Match method to audience, content, and context for each program |
| Completion rates reported as the sole success metric | 100% completion means nothing if behavior didn't change or the business metric didn't move | Measure at Kirkpatrick Level 3 (behavior) or 4 (results) at minimum for strategic programs |
| No manager reinforcement plan | Training transfer drops sharply without manager follow-up — skills degrade within weeks | Include manager coaching, observation, and follow-up in the program design |
| Stale training content reused without review | Employees trained on out-of-date processes or regulations; audit exposure | Annual content review calendar tied to regulatory and process change triggers |
| Compliance training tracked in a spreadsheet past 25 employees | Gaps emerge, audit records take hours to assemble, deadlines get missed | Use an LMS with automated role-based assignment and audit-ready reports |

## Exit Criteria

- [ ] Needs assessment completed: business goal documented, skills gap measured, training confirmed as the right intervention.
- [ ] Learning objectives written for every program module, each with an action verb and measurable standard.
- [ ] Delivery method selected and matched to audience type (office/remote/field/shift).
- [ ] Assignment matrix complete: every employee mapped to required programs with due dates.
- [ ] Training delivered and completions tracked (name, course, date, score, expiration).
- [ ] Level 1 (reaction) evaluation collected; Level 2 (learning) measured if the objective requires demonstration.
- [ ] Level 3 (behavior) or Level 4 (results) evaluation designed and scheduled for strategic programs.
- [ ] Compliance training records audit-ready: trainee name, date, content identifier, trainer/provider.
- [ ] Certification/renewal reminders set where applicable.
- [ ] Program retrospective documented with changes for next cycle.
- [ ] Training catalog entry created or updated with last review date and next review date.
- [ ] Manager reinforcement plan communicated to each participating manager.

## Sources

Synthesized from published training and development practice: **Vector Solutions** (8-step training program framework, needs assessment methodology, Kirkpatrick evaluation), **Infopro Learning** (12 best practices for 2026 — personalized learning paths, manager-led reinforcement, learning analytics, role-based skill mapping), **ATD** (Association for Talent Development — State of the Industry Report, 16.7 average learning hours per employee), **SHRM** (manager reinforcement research, training ROI and retention impact), **Rippling** (training program types, effective program components), and **Kirkpatrick Partners** (Four Levels of Evaluation model). Compliance tracking deadlines and regulatory standards (HazCom, LOTO, OSHA 29 CFR 1910) are referenced from the applicable OSHA standards; verify against your jurisdiction's current regulations.

**Jurisdiction warning:** Compliance training requirements (OSHA in the US, HSE in the UK, EU-OSHA in the European Union, local equivalents elsewhere), mandatory training frequency, record-retention periods, and certification validity windows vary by country and industry. Confirm the applicable regulations for the organization's locations before setting compliance-training deadlines. Anti-harassment and data-privacy training requirements also vary by jurisdiction (state-level in the US; GDPR-required in the EU).