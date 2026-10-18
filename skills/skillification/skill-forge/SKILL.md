---
name: skill-forge
description: "Improve a skill's bundled scripts by propose/probe/compose — every edit is kept only if two executions visibly differ, so nothing lands on opinion."
version: 1.0.0
author: Nuvel Skills
---

# Skill Forge

## When to use this

Use when a skill ships an executable script and you want to improve it against
evidence rather than judgement. This is the third member of the skillification
meta-layer: [[skill-promotion]] decides whether a skill enters the repo,
[[skill-evaluation]] measures how well existing skills hold up, and **skill-forge**
changes a skill's behaviour and proves the change did something.

Reach for it when a skill's script has bugs you suspect but cannot reproduce by
hand, when you want a regression net around a script before refactoring it, or
when a skill keeps producing wrong output on messy real-world input.

## The idea

An agent is a model plus a **harness** — the prompts, scripts, and tools around a
frozen model. Skill-forge treats a skill's executable surface as that harness and
improves it in five stages:

| Stage | What it does |
|---|---|
| **probe** | Runs the skill against a fixed eval set and returns an *outcome vector*: PASS/FAIL per case. |
| **propose** | A model reads `SKILL.md`, the editable files, and each failing case's **raw input bytes**, then emits candidate edits scoped `invariant` (general robustness) or `domain` (one named failure). |
| **probe2** | Each candidate is applied to a **pristine** copy and re-probed on its own. |
| **compose** | Keeps only edits whose outcome vector **differs** from base, then merges survivors while the pass count strictly improves. |
| **reflect** | Writes `cue / lesson / evidence` into a library file for review. |

Nothing is adopted on the strength of its rationale. An edit that reads well but
changes no observable behaviour is discarded — which is what makes the loop safe
to run unattended.

## Two rules that are not optional

**1. The eval set must encode the contract, never the implementation.**
Write the expected values from what `SKILL.md` *promises*. If you copy them from
what the script currently does, a defective case will report PASS and the loop
becomes decorative. This is a silent failure mode: the tooling looks like it is
working, and it is structurally incapable of finding anything.

**2. The proposer must be shown raw inputs, not just symptoms.**
A proposer given only a failure list invents causes that cannot fire — header
aliases for a column that is already correct, a refactor of logic that was never
reached. Supplying the actual bytes of the failing inputs is the difference
between a run that fixes nothing and one that fixes everything.

## Methodology

### Phase 1: Write the contract down

1. Read the target `SKILL.md`. Extract its promised behaviour into a table —
   inputs, computed outputs, and every edge case the skill claims to handle.
2. If the contract is vague or self-contradictory, **fix the contract first**.
   You cannot test a skill against a contract that does not say what it means.

### Phase 2: Build the eval set

1. One directory per case under `evalset/`, each holding exactly one input file
   and an `expected.json`:
   ```json
   {"hard": true, "note": "why this case exists",
    "expected": [{"employee_id": "E001", "net_pay": 700.0}]}
   ```
2. Derive every expected value **from the Phase 1 contract**, by hand or from a
   separate reference implementation written from the contract.
3. Include cases that pass. They are the regression net — a candidate that fixes
   one case by breaking another must be caught.
4. Set `"hard": false` for cases that encode an interpretation rather than a
   documented guarantee. The loop reports them but never adopts an edit for them.
5. Name case directories neutrally (`case-01`). The proposer sees symptoms only;
   a name like `bom-header` hands it the diagnosis, and you learn nothing about
   whether the loop can find real defects.

### Phase 3: Write the config

```json
{
  "skill": "../skills/hr/payroll-processor",
  "cases": "evalset",
  "run": ["{python}", "{skill}/scripts/payroll_processor.py", "{input}",
          "--output-dir", "{output}", "--quiet"],
  "result_file": "{output}/payroll_report.json",
  "rows_path": "paystubs",
  "key_field": "employee_id",
  "value_field": "net_pay",
  "tolerance": 0.011,
  "editable": ["scripts/payroll_processor.py"]
}
```

The skill's script must emit a JSON result the config can point at. `rows_path`
may be dotted (`report.rows`). `editable` lists the files the proposer may touch.

### Phase 4: Measure the baseline

```bash
python3 scripts/skillforge.py probe --config forge.json --out ./run
```

Record the pass count. If it is already full marks the loop has nothing to do —
go write harder cases.

### Phase 5: Forge

```bash
export OPENROUTER_API_KEY=...
python3 scripts/skillforge.py forge --config forge.json --out ./run --k 2
```

Watch the *status column*, not the rationales. `NO-OBSERVABLE-EFFECT` on every
candidate means the eval set is not exercising the defect, or the proposer can
not see it — check the observation surface before blaming the model.

### Phase 6: Review before landing (mandatory)

1. Read the composed diff in `candidates/final/` and the
   `library/EXPERIENCE.md` lessons.
2. Ask what the eval set **does not** cover, and test that case explicitly. A
   composed fix is only proven against the cases that existed.
3. Run a held-out set the loop never saw. If the fix is real it generalises; if
   it fitted the eval set, this is where you find out.
4. Only then hand-edit if needed, bump the skill's `version`, and PR it.

## Running it

```bash
python3 scripts/skillforge.py --help
python3 scripts/skillforge.py probe --config forge.json --out ./run
python3 scripts/skillforge.py forge --config forge.json --out ./run --k 2
python3 scripts/skillforge.py forge --config forge.json --out ./run --k 2 \
  --model google/gemini-3.1-flash-lite
```

- Python 3.10+, standard library only. The bundled script shells out to the
  skill under test and speaks HTTP with `urllib`.
- `probe` is entirely local — no key, no network, no cost.
- `forge` needs `OPENROUTER_API_KEY`. `SKILLFORGE_MODEL` and
  `SKILLFORGE_BASE_URL` point it at any OpenAI-compatible endpoint.
- Use a **flash-tier** proposer. This is a diagnosis task, not a writing task,
  and a full two-scope run costs a fraction of a cent.

## Output

```
run/
├── base.json                  outcome vector before any edit
├── candidates/<id>/           pristine copy + that candidate's probe, harness.diff
├── candidates/final/          composed harness — review this, it is the deliverable
├── library/EXPERIENCE.md      cue / lesson / evidence per adopted edit
└── forge.json                 full run: base, every candidate, composed list, spend
```

## Interpreting results

- **Every candidate `NO-OBSERVABLE-EFFECT`** → the eval set does not reach the
  defect, or the proposer lacks the inputs to see it. Fix the observation surface
  first; it is the cheaper of the two.
- **A candidate passes but the diff looks wrong** → read the diff, not the score.
  Fixing a case by special-casing the case is a real outcome the loop cannot
  distinguish from a real fix.
- **`REJECTED(malformed edit)`** → the model's `find` string did not match the
  file exactly once. Harmless; the candidate is skipped.
- **Compose adopts nothing** → a correct and useful outcome. It means the loop
  found no evidence, and it says so instead of inventing a change.

## Pitfalls

- **Never derive expectations from the implementation.** A reference that agrees
  with the code under test cannot detect a defect in it. See "Two rules" above.
- **A validated loop only proves it fixed what the cases covered.** A run that
  went 7/9 → 9/9 shipped a fix that read `0.2%` as 20% tax — a 100x error — purely
  because no case covered a sub-1 percent. Always add the counterexample you find
  during review as a regression case.
- **Namespace candidate ids by scope.** Both scopes can emit `inv1`; without a
  prefix they collide on one directory and one silently overwrites the other.
- **Neutral case names.** Naming a case after its bug hands the proposer the
  answer and tells you nothing about the loop's diagnostic ability.
- **Search/replace, not unified diffs.** Models author diffs badly and a bad diff
  fails opaquely. `find` must occur exactly once; anything else is rejected with
  a reason, and the `.diff` artifact is computed from before/after instead.
- **Small eval sets are the ceiling.** Ten cases is enough to find a known defect
  and nowhere near enough to certify a skill. Grow the set every time review
  finds something the loop missed.
