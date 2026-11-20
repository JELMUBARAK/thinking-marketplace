"""Build a concept's run record in one fixed layout.

The orchestrator writes only its own part, <slug>.analogy.json. This script
adds the researcher's facts and rules and the test what-ifs (copied, never
printed), works out the result from the test counts, and writes <slug>.json.
It prints "ok" or a list of problems for the orchestrator to fix in
<slug>.analogy.json, then rerun. It never prints questions.

Usage: python build_record.py <analogy-runs dir> <slug>

<slug>.analogy.json layout:
{
  "input": {"concept": "", "sense": ""},
  "gate": {"sense": "", "type": "physical|formal|social-normative", "visible": false,
           "dispute_kind": "none|evidence|values|layered", "safety_topic": false,
           "prerequisites": [], "assumptions": []},
  "route": "analogy|values|contested|simulate_first",
  "candidates": [
    {"id": "C1", "machine": "", "definition": null, "analogy": "",
     "mapping": [{"rule": "R1", "source": "what the machine does, or null for a break",
                  "target": "", "fact_ids": ["F1"], "break": null}]}
  ],
  "practice_counts": {"C1": {"match": 0, "miss": 0, "gap": 0, "flip": 0, "told": 0, "disqualified": false}},
  "practice_fixes": ["R3: what changed"],
  "test_counts": {"C1": {"match": 0, "miss": 0, "gap": 0, "flip": 0, "told": 0, "disqualified": false}},
  "split": {"seed": 0, "warnings": []},
  "agent_calls": 3,
  "notes": []
}
"""
import datetime
import json
import os
import re
import sys

VERDICTS = ("match", "miss", "gap", "flip", "told")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def decide(c, total):
    """Rubric: pass >= 7/8 (80%), no flip, no gap; rough >= 5/8 (60%), no flip."""
    if c.get("disqualified") or total == 0:
        return "fail"
    frac = c.get("match", 0) / total
    if c.get("flip", 0) == 0 and c.get("gap", 0) == 0 and frac >= 0.8 - 1e-9:
        return "pass"
    if c.get("flip", 0) == 0 and frac >= 0.6 - 1e-9:
        return "rough_model"
    return "fail"


def main():
    d, slug = sys.argv[1], sys.argv[2]
    p = lambda name: os.path.join(d, f"{slug}.{name}.json")
    problems, warnings = [], []

    try:
        a = load(p("analogy"))
    except Exception as e:
        print(json.dumps({"ok": False, "problems": [f"cannot read {slug}.analogy.json: {e!r}"]}))
        sys.exit(1)
    r = load(p("research"))
    test = load(p("test"))
    test = test.get("whatifs", test) if isinstance(test, dict) else test

    facts = {f["id"]: f for f in r.get("facts", [])}
    verified = {k for k, f in facts.items() if f.get("verified") is True}
    rules = {x["id"]: x for x in r.get("rules", [])}
    if len(rules) > 11:
        warnings.append(f"{len(rules)} rules, limit is 11")

    for k in ("input", "gate", "route", "candidates", "test_counts"):
        if k not in a:
            problems.append(f"missing '{k}'")
    cands = a.get("candidates") or []
    if not isinstance(cands, list):
        problems.append("'candidates' must be a list")
        cands = []

    for c in cands:
        cid = c.get("id")
        if not cid:
            problems.append("a candidate has no id")
            continue
        own_def = c.get("definition")
        for row in c.get("mapping", []):
            m = re.match(r"\s*(R\d+[a-z]?)\b", str(row.get("rule", "")))
            if not m:
                problems.append(f"{cid}: row rule '{row.get('rule')}' is not a rule id like R3")
                continue
            row["rule"] = m.group(1)
            if row["rule"] not in rules:
                problems.append(f"{cid}: row cites unknown rule {row['rule']}")
            if row.get("source") is not None:
                for fid in row.get("fact_ids") or []:
                    if fid not in verified:
                        problems.append(f"{cid}: {row['rule']} rests on {'unknown' if fid not in facts else 'unverified'} fact {fid}")
                if not row.get("fact_ids"):
                    problems.append(f"{cid}: {row['rule']} has a machine source but cites no fact")
        mapped = {row.get("rule") for row in c.get("mapping", [])}
        for rid, rule in rules.items():
            rdef = rule.get("definition")
            if rdef and own_def and rdef != own_def:
                continue  # another definition's rule
            if rid not in mapped:
                problems.append(f"{cid}: rule {rid} has no row (map it, or add a row with source null and a break line)")
        for key in ("practice_counts", "test_counts"):
            counts = (a.get(key) or {}).get(cid)
            if key == "test_counts" and counts is None:
                problems.append(f"{cid}: no test counts")
            if counts:
                for v in VERDICTS:
                    counts.setdefault(v, 0)

    if problems:
        print(json.dumps({"ok": False, "problems": problems, "warnings": warnings}))
        sys.exit(1)

    # Result, worked out from the test counts per the rubric.
    verdicts = {}
    for c in cands:
        tc = a["test_counts"][c["id"]]
        total = sum(tc.get(v, 0) for v in VERDICTS)
        verdicts[c["id"]] = {"outcome": decide(tc, total), "match": tc["match"], "of": total}
    route = a["route"]
    if route in ("values", "contested") or len(cands) > 1:
        outcome = "side_by_side"
        picked = None
        shown = [c["id"] for c in cands]
        label = "; ".join(f"{c['id']} ({c.get('definition') or c.get('machine')}): {verdicts[c['id']]['outcome']} "
                          f"{verdicts[c['id']]['match']}/{verdicts[c['id']]['of']}" for c in cands)
        if any(v["outcome"] != "pass" for v in verdicts.values()):
            label += "; not all pass, so show all as text only"
    else:
        c0 = cands[0]["id"]
        v = verdicts[c0]["outcome"]
        outcome = {"pass": "pass", "rough_model": "rough_model"}.get(v) or (
            "simulation_only" if a["gate"].get("type") == "formal" else "reject")
        picked = c0 if v in ("pass", "rough_model") else None
        shown = [c0]
        label = "rough model" if v == "rough_model" else None

    breaks = [{"candidate": c["id"], "rule": row["rule"], "break": row.get("break") or ""}
              for c in cands for row in c.get("mapping", []) if row.get("source") is None or row.get("break")]

    rec = {
        "schema_version": "0.5",
        "created": datetime.date.today().isoformat(),
        "input": a["input"],
        "gate": a["gate"],
        "facts": r.get("facts", []),
        "rules": r.get("rules", []),
        "status": r.get("status", {}),
        "dispute_kind": r.get("dispute_kind"),
        "definitions": r.get("definitions", []),
        "misconceptions": r.get("misconceptions", []),
        "neighbours": r.get("neighbours", []),
        "whatifs": test,
        "route": route,
        "candidates": cands,
        "practice_counts": a.get("practice_counts", {}),
        "practice_fixes": a.get("practice_fixes", []),
        "test_counts": a["test_counts"],
        "result": {"outcome": outcome, "picked": picked, "shown": shown, "label": label,
                   "per_candidate": verdicts, "breaks": breaks},
        "trace": {"agent_calls": a.get("agent_calls"), "split": a.get("split", {}),
                  "research_gaps": r.get("gaps", []), "fetches": r.get("fetches"),
                  "warnings": warnings + list((a.get("split") or {}).get("warnings", [])),
                  "notes": a.get("notes", [])},
    }
    with open(os.path.join(d, f"{slug}.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
    print(json.dumps({"ok": True, "outcome": outcome, "per_candidate": verdicts, "warnings": rec["trace"]["warnings"]}))


if __name__ == "__main__":
    main()
