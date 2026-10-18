#!/usr/bin/env python3
"""skillforge — a propose / probe / compose / reflect loop for harness-agnostic skills.

A skill's behaviour is its *executable* surface: the scripts it bundles and the
contract its SKILL.md promises. This tool improves that surface by treating every
change as a hypothesis and accepting it only when two executions visibly differ.

  probe    run a skill against a fixed eval set -> an outcome vector (PASS/FAIL per case)
  propose  ask a model for candidate edits, scoped invariant (general) or domain (case-specific)
  probe2   apply each candidate to a PRISTINE copy and re-probe it alone
  compose  keep only edits whose outcome vector DIFFERS from base; merge survivors while
           the pass count strictly improves
  reflect  write cue / lesson / evidence into a library file

Two rules are load-bearing and non-negotiable:

1. The eval set must encode the CONTRACT, never the implementation's behaviour. If
   your expected values are copied from what the script currently does, no edit can
   ever look wrong and the loop is decorative.
2. The proposer must be shown raw inputs, not just symptoms. Without the actual bytes
   it invents causes that cannot fire.

Usage:
    skillforge.py probe --config forge.json --out DIR
    skillforge.py forge --config forge.json --out DIR --k 2
    skillforge.py forge --config forge.json --out DIR --k 2 --model google/gemini-3.1-flash-lite

Requires OPENROUTER_API_KEY for `forge`. `probe` is local and needs nothing.

forge.json:
    {
      "skill":  "../skills/hr/payroll-processor",
      "cases":  "evalset",
      "run":    ["{python}", "{skill}/scripts/payroll_processor.py",
                 "{input}", "--output-dir", "{output}", "--quiet"],
      "result_file": "{output}/payroll_report.json",
      "rows_path":    "paystubs",
      "key_field":    "employee_id",
      "value_field":  "net_pay",
      "tolerance":    0.011,
      "editable":     ["scripts/payroll_processor.py"]
    }

Each case directory holds one input file plus expected.json:
    {"hard": true, "note": "why this case exists",
     "expected": [{"employee_id": "E001", "net_pay": 700.0}]}
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

DEFAULT_MODEL = os.environ.get("SKILLFORGE_MODEL", "google/gemini-3.1-flash-lite")
DEFAULT_BASE_URL = os.environ.get("SKILLFORGE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_OVERRIDE = None


# ---------------------------------------------------------------- config

class Config:
    def __init__(self, path: Path):
        self.path = path.resolve()
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        base = self.path.parent
        self.skill = (base / raw["skill"]).resolve()
        self.cases = (base / raw.get("cases", "evalset")).resolve()
        self.run = raw["run"]
        self.result_file = raw["result_file"]
        self.rows_path = raw.get("rows_path", "")
        self.key_field = raw["key_field"]
        self.value_field = raw["value_field"]
        self.tolerance = float(raw.get("tolerance", 0.011))
        self.editable = raw.get("editable") or ["SKILL.md"]
        self.name = self.skill.name

    def expand(self, *, case=None, skill=None, output=None):
        cmd = []
        for part in self.run:
            part = part.replace("{python}", sys.executable)
            part = part.replace("{skill}", str(skill or self.skill))
            if case is not None:
                part = part.replace("{input}", str(case))
            if output is not None:
                part = part.replace("{output}", str(output))
            cmd.append(part)
        return cmd

    def result_path(self, output: Path) -> Path:
        return Path(self.result_file.replace("{output}", str(output)))


def first_input(case_dir: Path) -> Path:
    """The case's single input file (any name, any extension)."""
    inner = case_dir / "input"
    if inner.is_dir():
        files = sorted(p for p in inner.iterdir() if p.is_file())
    else:
        files = sorted(p for p in case_dir.iterdir()
                       if p.is_file() and p.name != "expected.json")
    if len(files) != 1:
        raise SystemExit(f"{case_dir}: expected exactly 1 input file, found {len(files)}")
    return files[0]


# ---------------------------------------------------------------- probe

def run_case(cfg: Config, case_dir: Path, work: Path) -> dict:
    outdir = work / "out"
    shutil.rmtree(outdir, ignore_errors=True)
    try:
        proc = subprocess.run(
            cfg.expand(case=first_input(case_dir), output=outdir),
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    rp = cfg.result_path(outdir)
    if not rp.is_file():
        return {"error": f"rc={proc.returncode} no {rp.name} :: {proc.stderr.strip()[-180:]!r}"}
    try:
        data = json.loads(rp.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": f"bad json: {exc}"}
    rows = data
    for key in filter(None, cfg.rows_path.split(".")):
        rows = rows.get(key, []) if isinstance(rows, dict) else []
    return {"rows": rows if isinstance(rows, list) else []}


def score_case(cfg: Config, observed: dict, expected: dict) -> dict:
    if "error" in observed:
        return {"status": "FAIL", "detail": observed["error"]}
    got = {str(r.get(cfg.key_field)): r for r in observed["rows"]}
    want = {str(e[cfg.key_field]): e for e in expected["expected"]}
    if set(got) != set(want):
        return {"status": "FAIL",
                "detail": f"{cfg.key_field}s got={sorted(got)} want={sorted(want)}"}
    bad = []
    for k, w in want.items():
        have = float(got[k].get(cfg.value_field, 0) or 0)
        if abs(have - float(w[cfg.value_field])) > cfg.tolerance:
            bad.append(f"{k}: got {have:.2f} want {float(w[cfg.value_field]):.2f}")
    return {"status": "FAIL", "detail": "; ".join(bad)} if bad else {"status": "PASS", "detail": ""}


def probe(cfg: Config, work_root: Path, label: str, skill: Path | None = None) -> dict:
    skill = skill or cfg.skill
    results = {}
    for case_dir in sorted(p for p in cfg.cases.iterdir() if p.is_dir()):
        expected = json.loads((case_dir / "expected.json").read_text(encoding="utf-8"))
        observed = run_case_with(cfg, case_dir, work_root / label / case_dir.name, skill)
        r = score_case(cfg, observed, expected)
        r["hard"] = expected.get("hard", True)
        r["note"] = expected.get("note", "")
        r["observed_first"] = (observed.get("rows") or [{}])[0]
        results[case_dir.name] = r
    hard = [k for k, v in results.items() if v["hard"]]
    return {
        "label": label, "results": results,
        "hard_total": len(hard),
        "hard_pass": len([k for k in hard if results[k]["status"] == "PASS"]),
        "failing": [k for k in hard if results[k]["status"] != "PASS"],
    }


def run_case_with(cfg: Config, case_dir: Path, work: Path, skill: Path) -> dict:
    saved = cfg.skill
    try:
        cfg.skill = skill
        return run_case(cfg, case_dir, work)
    finally:
        cfg.skill = saved


def vector_of(p: dict) -> str:
    return json.dumps({k: v["status"] for k, v in p["results"].items()}, sort_keys=True)


# ---------------------------------------------------------------- llm

def llm(prompt: str, system: str = "") -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is required for `forge` (probe needs nothing).")
    payload = {
        "model": MODEL_OVERRIDE or DEFAULT_MODEL,
        "messages": ([{"role": "system", "content": system}] if system else [])
                    + [{"role": "user", "content": prompt}],
        "temperature": 0.4, "max_tokens": 4000,
    }
    req = urllib.request.Request(
        f"{DEFAULT_BASE_URL.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read())
    u = body.get("usage", {})
    return body["choices"][0]["message"]["content"], u


def parse_edits(text: str) -> list:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in reply")
    return json.loads(text[start:end + 1]).get("edits", [])


# ---------------------------------------------------------------- propose

PROPOSE_PROMPT = """You are a harness editor. Below is a SKILL bundle: a SKILL.md
contract and the executable files it ships. The skill was run against a fixed eval
set. Its failures are listed. Every failure is a mismatch between what the skill
does and what its contract promises.

SCOPE: {scope}
{scope_note}

Propose exactly {n} candidate edits for this scope. Each edit is a search/replace
pair against an editable file. Rules:
- `find` MUST be a byte-exact substring of the current file (copy it verbatim).
- `replace` is what it becomes. Keep the edit minimal and surgical.
- Do not rename functions or restructure the file.
- Do not invent new files.
- Each candidate is INDEPENDENT: it will be probed alone on a pristine copy.
- Domain candidates must target one specific observed failure.
- Invariant candidates target a general class of malformed input the contract
  says the skill must tolerate.

Reply with JSON only:
{{"edits":[{{"id":"inv1","file":"{files}","find":"...","replace":"...","rationale":"..."}}]}}

=== SKILL.md ===
{skill_md}

=== EDITABLE FILES ===
{file_dump}

=== BASE PROBE (base = unedited skill) ===
hard cases: {hard_pass}/{hard_total}
{detail}

=== RAW INPUT EVIDENCE FOR EACH FAILING CASE ===
Actual bytes of the inputs the skill read, plus what it produced. Diagnose the
ROOT CAUSE from these raw bytes before proposing an edit.

{evidence}
"""


def failing_evidence(cfg: Config, base: dict, limit: int = 5) -> str:
    blocks = []
    for name in base["failing"][:limit]:
        case = cfg.cases / name
        raw = first_input(case).read_bytes()
        preview = raw[:220].decode("utf-8", "replace")
        observed = base["results"][name].get("observed_first", {})
        blocks.append(
            f"--- {name} ---\n"
            f"input file: {first_input(case).name}\n"
            f"first 220 bytes, as a Python repr:\n  {preview!r}\n"
            f"probe verdict: {base['results'][name]['detail']}\n"
            f"first output row the skill produced:\n{json.dumps(observed, indent=1)}"
        )
    return "\n\n".join(blocks) if blocks else "(no failing cases)"


def propose(cfg: Config, base: dict, scope: str, n: int) -> tuple:
    skill_md = (cfg.skill / "SKILL.md").read_text(encoding="utf-8")
    editable = {rel: (cfg.skill / rel).read_text(encoding="utf-8")
                for rel in cfg.editable if (cfg.skill / rel).is_file()}
    dump = "\n\n".join(f"--- {rel} ---\n{src}" for rel, src in editable.items())
    detail = "\n".join(
        f"  {k}: {v['status']}" + (f"  {v['detail']}" if v["detail"] else "")
        for k, v in sorted(base["results"].items()) if v["hard"]
    )
    scope_note = {
        "invariant": "GENERAL edits that make the skill robust to a whole CLASS of "
                     "malformed input the contract says it must tolerate.",
        "domain": "SPECIFIC edits that fix one named failing case below and nothing else.",
    }[scope]
    prompt = PROPOSE_PROMPT.format(
        scope=scope, scope_note=scope_note, n=n, files=" or ".join(editable) or "SKILL.md",
        skill_md=skill_md, file_dump=dump, hard_pass=base["hard_pass"],
        hard_total=base["hard_total"], detail=detail, evidence=failing_evidence(cfg, base),
    )
    text, usage = llm(prompt, system="Reply with JSON only. No prose, no markdown fences.")
    edits = parse_edits(text)
    for e in edits:
        e["scope"] = scope
    return edits[:n], usage


# ---------------------------------------------------------------- apply

def apply_edits(skill_dir: Path, edits: list) -> tuple:
    log = []
    for e in edits:
        target = skill_dir / e["file"]
        if not target.is_file():
            return False, log + [f"{e.get('id')}: missing {e['file']}"]
        src = target.read_text(encoding="utf-8")
        if src.count(e["find"]) != 1:
            return False, log + [f"{e.get('id')}: find matched {src.count(e['find'])}x (need 1)"]
        target.write_text(src.replace(e["find"], e["replace"], 1), encoding="utf-8")
        log.append(f"{e['id']}: applied")
    return True, log


def materialize(cfg: Config, dest: Path, edits: list) -> tuple:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(cfg.skill, dest)
    return apply_edits(dest, edits)


def diff_of(cfg: Config, a: Path, b: Path) -> str:
    chunks = []
    for rel in cfg.editable:
        fa, fb = a / rel, b / rel
        if fa.is_file() and fb.is_file():
            chunks.append("".join(difflib.unified_diff(
                fa.read_text().splitlines(True), fb.read_text().splitlines(True),
                fromfile=f"current/{rel}", tofile=f"candidate/{rel}")))
    return "".join(chunks)


# ---------------------------------------------------------------- cli

def cmd_probe(args):
    cfg = Config(Path(args.config))
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    p = probe(cfg, out / "work", "base")
    (out / "base.json").write_text(json.dumps(p, indent=2) + "\n", encoding="utf-8")
    print(f"BASE PROBE  {p['hard_pass']}/{p['hard_total']} hard cases pass  ({cfg.name})")
    for k, v in sorted(p["results"].items()):
        print(f"  {k:<28} {v['status']:<5} {v['detail'][:90]}")
    print(f"\nvector: {p['hard_pass']}/{p['hard_total']}")


def cmd_forge(args):
    cfg = Config(Path(args.config))
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    work, cand_root = out / "work", out / "candidates"
    spend = 0.0

    print("=" * 68)
    print(f"STEP 1  reference probe  ({cfg.name}, unedited)")
    print("=" * 68)
    base = probe(cfg, work, "base")
    print(f"  {base['hard_pass']}/{base['hard_total']} hard cases pass")
    print(f"  failing: {base['failing']}")
    base_vec = vector_of(base)

    print("\n" + "=" * 68)
    print("STEP 2  propose  (K candidates per scope)")
    print("=" * 68)
    candidates = []
    for scope in ("invariant", "domain"):
        try:
            edits, usage = propose(cfg, base, scope, args.k)
            spend += usage.get("prompt_tokens", 0) * 0.25e-6
            spend += usage.get("completion_tokens", 0) * 1.5e-6
        except Exception as exc:
            print(f"  {scope}: PROPOSE FAILED ({exc})")
            continue
        for e in edits:
            # Namespace by scope: both scopes may emit "inv1" and would otherwise
            # collide on one directory, silently overwriting each other.
            e["id"] = f"{scope[:3]}-{e.get('id', 'c')}"
            candidates.append({"scope": scope, "edits": [e]})
            print(f"  proposed {e['id']:<10} [{scope}] {str(e.get('rationale'))[:74]}")

    print("\n" + "=" * 68)
    print("STEP 3  probe each candidate on a PRISTINE copy")
    print("=" * 68)
    for c in candidates:
        cid = c["id"] = c["edits"][0]["id"]
        dest = cand_root / cid
        ok, log = materialize(cfg, dest, c["edits"])
        c["applied"], c["apply_log"] = ok, log
        if not ok:
            c["status"] = "REJECTED(malformed edit)"
            print(f"  {cid:<12} REJECTED  {log[-1]}")
            continue
        p = probe(cfg, work, cid, skill=dest)
        c.update(probe=p, vector=vector_of(p), diff=diff_of(cfg, cfg.skill, dest))
        c["observable"] = c["vector"] != base_vec
        c["status"] = "CHANGED" if c["observable"] else "NO-OBSERVABLE-EFFECT"
        print(f"  {cid:<12} {p['hard_pass']}/{p['hard_total']} hard   {c['status']}")

    print("\n" + "=" * 68)
    print("STEP 4  compose  (keep only edits with an observable effect)")
    print("=" * 68)
    keepers = [c for c in candidates if c.get("observable")]
    composed, cur_pass = [], base["hard_pass"]
    for c in sorted(keepers, key=lambda c: -c["probe"]["hard_pass"]):
        trial = composed + [c]
        dest = cand_root / ("try_" + "_".join(x["id"] for x in trial))
        ok, _ = materialize(cfg, dest, [e for x in trial for e in x["edits"]])
        if not ok:
            continue
        p = probe(cfg, work, dest.name, skill=dest)
        if p["hard_pass"] > cur_pass:
            composed, cur_pass = trial, p["hard_pass"]
            print(f"  kept    {c['id']:<12} -> {p['hard_pass']}/{p['hard_total']}")
        else:
            shutil.rmtree(dest, ignore_errors=True)
            print(f"  dropped {c['id']:<12} (no further gain)")
    if not keepers:
        print("  nothing composed — no candidate changed the outcome vector")

    final = cand_root / "final"
    ok, _ = materialize(cfg, final, [e for x in composed for e in x["edits"]])
    fp = probe(cfg, work, "final", skill=final) if ok else None
    print(f"\n  FINAL: {fp['hard_pass'] if fp else '?'}/{fp['hard_total'] if fp else '?'} "
          f"(base was {base['hard_pass']}/{base['hard_total']})")

    print("\n" + "=" * 68)
    print("STEP 5  reflect  (cue / lesson / evidence -> library)")
    print("=" * 68)
    library = out / "library"; library.mkdir(parents=True, exist_ok=True)
    lines = [f"# {cfg.name}", "",
             f"- base: `{base['hard_pass']}/{base['hard_total']}` hard cases",
             f"- adopted: `{'_'.join(x['id'] for x in composed) or 'nothing'}`",
             f"- final: `{fp['hard_pass'] if fp else '?'}/{fp['hard_total'] if fp else '?'}`", ""]
    for c in composed:
        e = c["edits"][0]
        lines += [f"## Edit `{c['id']}` ({c['scope']})",
                  f"rationale: {e.get('rationale')}",
                  f"probe: {base['hard_pass']} -> {c['probe']['hard_pass']} hard cases",
                  f"fixed: {sorted(set(base['failing']) - set(c['probe']['failing']))}", ""]
    lines += ["## Transferable lessons", "",
              "> Review these before landing. A lesson can be right about the case it",
              "> fixed and still be wrong about a neighbouring case the eval set missed.", ""]
    for c in composed:
        fixed = sorted(set(base["failing"]) - set(c["probe"]["failing"]))
        if fixed:
            lines += [f"- **cue**: when a failure matches {fixed[0]}",
                      f"  **lesson**: {c['edits'][0].get('rationale')}",
                      f"  **evidence**: probe {base['hard_pass']} -> "
                      f"{c['probe']['hard_pass']} hard cases", ""]
    (library / "EXPERIENCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {library / 'EXPERIENCE.md'}")
    (out / "forge.json").write_text(json.dumps(
        {"base": base, "candidates": candidates,
         "composed": [c["id"] for c in composed], "final": fp,
         "approx_spend_usd": round(spend, 5)}, indent=2) + "\n", encoding="utf-8")
    print(f"  approx proposer spend: ${spend:.5f}")
    print(f"\nartifacts in {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    p1 = sub.add_parser("probe", help="run the eval set against the unedited skill")
    p1.add_argument("--config", required=True)
    p1.add_argument("--out", required=True)
    p1.set_defaults(fn=cmd_probe)
    p2 = sub.add_parser("forge", help="run the full propose/probe/compose/reflect loop")
    p2.add_argument("--config", required=True)
    p2.add_argument("--out", required=True)
    p2.add_argument("--k", type=int, default=2)
    p2.add_argument("--model", default=None)
    p2.set_defaults(fn=cmd_forge)
    args = ap.parse_args(argv)
    if not getattr(args, "fn", None):
        print(__doc__)
        return 0 if ("-h" in (argv or sys.argv[1:]) or "--help" in (argv or sys.argv[1:])) else 2
    if args.cmd == "forge" and args.model:
        global MODEL_OVERRIDE
        MODEL_OVERRIDE = args.model
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
