# Worked example — forging `hr/payroll-processor`

A complete run, start to finish, with the reasoning at each step. Copy the shapes;
the value is in *why* each piece exists.

The target was a real shipped skill with two silent defects. Both were found by the
loop and fixed. One extra step — Phase 6 review — caught a third problem that the
loop's own eval set could not see.

---

## Phase 1 — Write the contract down

Read the target `SKILL.md` and extract what it **promises**. Not what the script
does. The payroll contract, verbatim from its `## Process` and `## Edge cases`:

| Item | Promised behaviour |
|---|---|
| `gross_pay` | `hours_worked * hourly_rate` |
| `tax_rate` | fraction (`0.20`) **or** percent (`20`); values > 1 are percent |
| `tax_amount` | `gross_pay * tax_rate` |
| `net_pay` | `gross_pay - tax_amount - deductions` |
| messy cells | `$`, thousands separators, and blanks tolerated |
| negative values | clamped to `0` **with a warning recorded** |
| missing identity | `UNKNOWN-<row>` / `Unknown`, warning recorded |

If the contract is vague or self-contradictory, fix the contract before going
further. You cannot test a skill against a contract that does not say what it means.

---

## Phase 2 — Build the eval set

One directory per case. Exactly one input file plus `expected.json`:

```
evalset/
├── case-01/input.csv   expected.json       baseline: clean data, incl. percent form "20"
├── case-02/input.csv   expected.json       spreadsheet export -> UTF-8 BOM on the header
├── case-03/input.csv   expected.json       percent-suffixed tax rate "20%"
├── case-04/input.csv   expected.json       blank line between rows
├── case-05/input.csv   expected.json       "$1,050.50" style messy cells
├── case-06/input.csv   expected.json       negative hours / rate / tax / deductions
├── case-07/input.csv   expected.json       blank employee_id and name
├── case-08/input.csv   expected.json       blank numeric cells
├── case-09/input.csv   expected.json       net below zero after deductions
└── case-10/input.csv   expected.json       quoted names containing commas and quotes
```

```json
{"hard": true,
 "note": "Excel/Sheets export: UTF-8 BOM on the header row",
 "expected": [{"employee_id": "E001", "net_pay": 700.0},
              {"employee_id": "E002", "net_pay": 727.0}]}
```

### Derive expectations from the contract, never from the script

This is the step that decides whether the whole exercise means anything. Write a
**separate** reference implementation straight from the Phase 1 table:

```python
def spec_tax_rate(value):
    """Spec: fraction (0.20) or percent (20); a trailing '%' is a percent."""
    text = str(value).strip().replace("$", "").replace(",", "")
    if text.endswith("%"):
        return max(Decimal(text[:-1]), Decimal("0")) / 100
    rate = messy(text)
    return rate / 100 if rate > 1 else rate
```

**Real failure from this run.** The first version of this function mirrored the
script's own handling of `"20%"` — it fell through to `0.0`. Case-03 therefore
reported **PASS** against a script that taxed nothing, and the defect was invisible
by construction. Nothing about the tooling looked wrong. Rewriting the reference
from the contract turned it into a failing case immediately.

> A reference that agrees with the code under test cannot detect a defect in it.

### Name cases neutrally

`case-02`, not `bom-header`. The proposer is shown only symptoms; a descriptive
name hands it the diagnosis, and you learn nothing about whether the loop can
actually find defects.

### Include passing cases

They are the regression net. A candidate that fixes case-03 by breaking case-01
must be caught. Use `"hard": false` for cases that encode an interpretation rather
than a documented guarantee — the loop reports them but never adopts an edit for
them.

---

## Phase 3 — Write the config

`forge.json`, kept **outside** the skill so the skill ships clean:

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

- `{python}`, `{skill}`, `{input}`, `{output}` are substituted per run.
- `result_file` is where the script writes JSON. `rows_path` may be dotted
  (`report.rows`). `key_field` identifies a row; `value_field` is compared.
- `tolerance` should be about half the smallest unit that matters. For money with
  2 decimals, `0.011` is right — it absorbs float noise without admitting a real
  one-cent error.
- `editable` lists what the proposer may touch. Keep it tight.

---

## Phase 4 — Measure the baseline

```bash
python3 scripts/skillforge.py probe --config forge.json --out ./run
```

```
BASE PROBE  7/9 hard cases pass  (payroll-processor)
  case-01   PASS
  case-02   FAIL  employee_ids got=['UNKNOWN-1','UNKNOWN-2'] want=['E001','E002']
  case-03   FAIL  E001: got 900.00 want 700.00; E002: got 974.50 want 727.00
  case-04   PASS
  ...
vector: 7/9
```

Read the **detail strings**, not just PASS/FAIL. `got=['UNKNOWN-1']` says the rows
were parsed but the identity was lost — that is a header problem, not a data
problem. `got 900.00 want 700.00` on a 1000.00 gross says tax was not applied at
all, not that it was applied wrongly. These hints are what you check the loop's
diagnosis against.

If the baseline is already full marks, the loop has nothing to do — go write harder
cases.

---

## Phase 5 — Forge

```bash
export OPENROUTER_API_KEY=...
python3 scripts/skillforge.py forge --config forge.json --out ./run --k 2
```

Two candidates per scope, four total, ~$0.003.

```
STEP 2  propose
  proposed inv-inv1   [invariant] UTF-8 BOM on the first header column ...
  proposed inv-inv2   [invariant] '%' not stripped by the cell parser ...
  proposed dom-inv1   [domain]    BOM causes the first column name to be misread ...
  proposed dom-inv2   [domain]    tax_rate includes percentage signs ...

STEP 3  probe each candidate on a PRISTINE copy
  inv-inv1     7/9 hard   NO-OBSERVABLE-EFFECT
  inv-inv2     8/9 hard   CHANGED
  dom-inv1     8/9 hard   CHANGED
  dom-inv2     8/9 hard   CHANGED

STEP 4  compose
  kept    inv-inv2     -> 8/9
  kept    dom-inv1     -> 9/9
  FINAL: 9/9  (base was 7/9)
```

Watch the **status column**, not the rationales. `NO-OBSERVABLE-EFFECT` is the loop
doing its job: `inv-inv1` sounded reasonable and changed nothing, so it was
discarded rather than merged.

If *every* candidate reports `NO-OBSERVABLE-EFFECT`, the eval set is not reaching
the defect or the proposer cannot see it. Check the observation surface before
blaming the model:

> **Real failure from this run.** The first attempt showed the proposer only
> `SKILL.md`, the script, and a failure list. It invented header aliases (`id`,
> `tax`) for columns that were already correct — they could not possibly fire, and
> every candidate was discarded. The cause was a UTF-8 BOM, which is simply not
> visible in a failure list. Passing each failing case's **raw input bytes** fixed
> both diagnoses on the next run. This is the single highest-leverage line in the
> whole tool.

---

## Phase 6 — Review before landing (mandatory)

Read `candidates/final/` and `library/EXPERIENCE.md`. The composed fix was:

```diff
-    text = str(value).strip().replace("$", "").replace(",", "")
+    text = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
...
-    with path.open(newline="", encoding="utf-8") as fh:
+    with path.open(newline="", encoding="utf-8-sig") as fh:
```

The BOM fix is idiomatic and correct. **The `%` fix is wrong.**

Stripping `%` in the generic cell parser turns `"0.2%"` into `0.2`, and `0.2` is
not `> 1`, so the percent branch never fires and the value is read as **20% tax** —
a 100× over-taxation. The loop scored 9/9 while carrying a brand-new bug, because
no case covered a sub-1 percent.

```
tax_rate   loop's fix            correct
"20%"      0.20   (20%)          0.20   (20%)
"7.5%"     0.075  (7.5%)         0.075  (7.5%)
"0.2%"     0.20   (20%)  WRONG   0.002  (0.2%)
```

The fix is to handle the sign where it is meaningful — in the tax normaliser, not
the generic parser:

```python
def normalize_tax_rate(raw):
    """Accept a fraction (0.20), a percent (20), or a percent-suffixed value (20%)."""
    text = str(raw).strip().replace("$", "").replace(",", "")
    if text.endswith("%"):
        rate = _to_float(text[:-1], 0.0)     # a trailing '%' is ALWAYS a percent
        if rate < 0:
            return 0.0, True
        return rate / 100.0, False
    rate = _to_float(raw, 0.0)
    if rate < 0:
        return 0.0, True
    if rate > 1:
        return rate / 100.0, False
    return rate, False
```

Note what this does *not* do: it leaves `_to_float` alone. Stripping `%` there would
also silently change `hours_worked = "50%"` into `50` and `deductions = "10%"` into
tens of currency units. Handle the sign only where it carries meaning.

### Then add the counterexample as a regression case

```json
// evalset/case-11/expected.json  — the case the loop could not have written
{"hard": true,
 "note": "sub-1 percent form: a trailing '%' is always a percent",
 "expected": [{"employee_id": "S1", "net_pay": 998.0}]}
```

Every time review finds something the loop missed, the eval set grows by that case.
That is how the ceiling rises.

### And prove it generalises

Run a held-out set the loop never saw:

| Suite | Before | Loop's fix | After review |
|---|---|---|---|
| Eval set (9 hard cases) | 7/9 | 9/9 | 9/9 |
| Held-out (4 unseen cases) | 0/4 | 4/4 | 4/4 |
| Sub-1 percent edge case | wrong | **wrong** | correct |

A fix that only passes the cases it was tuned on is not a fix.

---

## Checklist

- [ ] Contract extracted from `SKILL.md`, vague parts fixed first
- [ ] Every expected value derived from the contract, **never** from the script
- [ ] Case directories named neutrally
- [ ] Passing cases included as a regression net
- [ ] `tolerance` sized to the smallest meaningful unit
- [ ] Baseline probed and recorded
- [ ] Every candidate's *status* inspected, not just its rationale
- [ ] Composed diff read line by line
- [ ] "What does the eval set not cover?" answered, and those cases tested
- [ ] Held-out set run — the fix generalises, or it does not ship
- [ ] New counterexamples added back into the eval set
- [ ] Skill `version` bumped, config and eval set kept out of the skill directory
