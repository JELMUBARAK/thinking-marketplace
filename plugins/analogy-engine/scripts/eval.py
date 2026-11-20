"""Run concepts through the analogy engine in clean folders.

Each concept runs headless in its own temporary folder, which has no
CLAUDE.md and no project memory, so nothing from your projects can bias the
run. Results are copied into one output folder, and the temp folders are
deleted afterwards.

Usage:
  python eval.py --out <folder> entropy "immune system" p-value
Options:
  --model sonnet     model for the run (default sonnet)
  --budget 4         spending cap per concept, in USD (default 4)
  --one-at-a-time    run concepts in turn instead of all at once
  --dry-run          print the commands without running them

Output: <out>/<slug>.*.json files, <out>/logs/<slug>.out.json, and a table of
cost, outcome and test score per concept.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = "Read Write Edit Glob Grep WebSearch WebFetch Agent Task Bash(python:*)"


def slugify(concept):
    return "-".join(concept.lower().split())


def command(claude, concept, model, budget):
    return [claude, "-p", f"/analogy-engine:transform {concept}",
            "--plugin-dir", PLUGIN, "--add-dir", PLUGIN, "--model", model,
            "--permission-mode", "acceptEdits", "--allowedTools", TOOLS,
            "--max-budget-usd", str(budget), "--output-format", "json"]


def summary(out, slug):
    row = {"concept": slug, "cost": None, "outcome": "no record", "test": ""}
    try:
        log = json.load(open(os.path.join(out, "logs", f"{slug}.out.json"), encoding="utf-8"))
        row["cost"] = round(log.get("total_cost_usd") or 0, 2)
        if log.get("is_error"):
            row["outcome"] = f"error: {log.get('subtype')}"
    except Exception:
        row["outcome"] = "no log"
    try:
        rec = json.load(open(os.path.join(out, f"{slug}.json"), encoding="utf-8"))
        row["outcome"] = rec.get("result", {}).get("outcome", "?")
        row["test"] = ", ".join(f"{v['match']}/{v['of']}" for v in
                                rec.get("result", {}).get("per_candidate", {}).values())
    except Exception:
        pass
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("concepts", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--budget", type=float, default=4)
    ap.add_argument("--one-at-a-time", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude is not on PATH")
    out = os.path.abspath(a.out)
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)

    jobs = []
    for concept in a.concepts:
        slug = slugify(concept)
        cmd = command(claude, concept, a.model, a.budget)
        if a.dry_run:
            print(slug, "->", subprocess.list2cmdline(cmd))
            continue
        work = tempfile.mkdtemp(prefix=f"analogy-{slug}-")
        os.makedirs(os.path.join(work, "analogy-runs"))
        log = open(os.path.join(out, "logs", f"{slug}.out.json"), "w", encoding="utf-8")
        err = open(os.path.join(out, "logs", f"{slug}.err.txt"), "w", encoding="utf-8")
        print(f"started {slug}", flush=True)
        p = subprocess.Popen(cmd, cwd=work, stdout=log, stderr=err, stdin=subprocess.DEVNULL)
        jobs.append((slug, work, p, log, err))
        if a.one_at_a_time:
            p.wait()
    if a.dry_run:
        return

    for slug, work, p, log, err in jobs:
        p.wait()
        log.close()
        err.close()
        runs = os.path.join(work, "analogy-runs")
        for name in os.listdir(runs):
            src = os.path.join(runs, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(out, name))
        shutil.rmtree(work, ignore_errors=True)
        print(f"finished {slug}", flush=True)

    rows = [summary(out, slug) for slug, *_ in jobs]
    print("\n| Concept | Cost ($) | Outcome | Test |\n|---|---|---|---|")
    for r in rows:
        print(f"| {r['concept']} | {r['cost']} | {r['outcome']} | {r['test']} |")
    print(f"\nTotal ${sum(r['cost'] or 0 for r in rows):.2f}. Files in {out}")


if __name__ == "__main__":
    main()
