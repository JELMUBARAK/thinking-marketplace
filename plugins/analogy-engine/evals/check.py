"""Mechanical checks on analogy-engine records (the part of Gate 1 a script can judge).

For each analogy-runs/*.json record:
  - every mapping row (including split parts) cites at least one fact id
  - every cited fact exists and is verified          <- "no unverified fact carries a mapping"
  - 5 what-ifs (v0.1) or 8 (hidden key), each citing a verified fact
  - each what-if kind present: threshold, stress, misconception_trap
  - the picked / shown candidates are not disqualified by the scorer
  - agent calls <= 3
  - a patch adds at most 3 mapping rows
  - v0.4: every verified fact (non-interpretation) is cited by some rule
  - v0.3: every rule in the rule table has a row (mapped, or source null = stated break)

Judgement criteria (cases.json "pass") are graded by hand.

Usage: python check.py <records_dir_or_files...>
"""
import glob
import json
import os
import sys


def rows(cand):
    for r in cand.get("mapping", []) or []:
        yield cand.get("id"), r
    for i, part in enumerate(cand.get("parts", []) or []):
        for r in part.get("mapping", []) or []:
            yield f"{cand.get('id')}.part{i + 1}", r


def check(path):
    rec = json.load(open(path, encoding="utf-8"))
    problems = []
    facts = {f["id"]: f for f in rec.get("facts", [])}
    verified = {k for k, f in facts.items() if f.get("verified")}

    for cand in rec.get("candidates", []) or []:
        for cid, r in rows(cand):
            ids = r.get("fact_ids") or []
            if not ids and r.get("source") is not None:
                problems.append(f"{cid}: mapping row '{r.get('source')}' cites no fact")
            for fid in ids:
                if fid not in facts:
                    problems.append(f"{cid}: cites unknown fact {fid}")
                elif fid not in verified:
                    problems.append(f"{cid}: mapping '{r.get('source')}' rests on UNVERIFIED {fid}")

    byid = {c.get("id"): c for c in rec.get("candidates", []) or []}
    for cand in byid.values():
        src = byid.get(cand.get("patched_from"))
        if src:
            added = len(cand.get("mapping", [])) - len(src.get("mapping", []))
            if added > 3:
                problems.append(f"{cand['id']}: patch adds {added} rows, cap is 3")

    w = rec.get("whatifs", [])
    if len(w) not in (5, 8):
        problems.append(f"{len(w)} what-ifs, expected 5 (v0.1) or 8 (hidden key)")
    for x in w:
        if not any(fid in verified for fid in x.get("fact_ids", [])):
            problems.append(f"{x.get('id')}: answer cites no verified fact")
    kinds = {x.get("kind") for x in w}
    for k in ("threshold", "stress", "misconception_trap"):
        if w and k not in kinds:
            problems.append(f"no '{k}' what-if")

    res = rec.get("result", {})
    chosen = [c for c in [res.get("picked")] + (res.get("shown") or []) if c]
    dq = set()
    for s in rec.get("scores", []) or []:
        for c in s.get("candidates", []) if isinstance(s, dict) and "candidates" in s else [s]:
            if isinstance(c, dict) and c.get("disqualified"):
                dq.add(c.get("id"))
    for c in chosen:
        if c in dq:
            problems.append(f"chosen candidate {c} was disqualified by the scorer")

    tids = {t["id"] for t in rec.get("transitions", []) or []}
    for cand in byid.values():
        for cid, r in rows(cand):
            for t in r.get("transition_ids", []) or []:
                if tids and t not in tids:
                    problems.append(f"{cid}: cites unknown transition {t}")

    rids = {x["id"] for x in rec.get("rules", []) or []}
    if rids:
        cited = {f for x in rec.get("rules", []) for f in x.get("fact_ids", [])}
        for fid in sorted(verified - cited):
            if facts[fid].get("layer") != "interpretation":
                problems.append(f"verified fact {fid} is in no rule (questions on it would land on 'none')")
    if rids:
        for cand in byid.values():
            mapped = {r.get("rule") for _, r in rows(cand)}
            for rid in sorted(rids - mapped):
                problems.append(f"{cand.get('id')}: rule {rid} has no row (map it or state it as a break)")

    calls = (rec.get("trace") or {}).get("agent_calls")
    if isinstance(calls, int) and calls > 3:
        problems.append(f"{calls} agent calls, max 3")

    summary = f"route={rec.get('route')} outcome={res.get('outcome')} facts={len(facts)} verified={len(verified)}"
    return summary, problems


def main():
    args = sys.argv[1:] or ["analogy-runs"]
    paths = []
    for a in args:
        paths += sorted(glob.glob(os.path.join(a, "*.json"))) if os.path.isdir(a) else [a]
    bad = 0
    for p in paths:
        try:
            summary, problems = check(p)
        except Exception as e:  # malformed record
            summary, problems = "unreadable", [repr(e)]
        bad += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} {os.path.basename(p)}  {summary}")
        for q in problems:
            print("       -", q)
    print(f"\n{len(paths) - bad}/{len(paths)} records pass the mechanical checks")


if __name__ == "__main__":
    main()
