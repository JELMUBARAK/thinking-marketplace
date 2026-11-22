"""Run the project-builder eval cases headless, one fresh session and one fresh project folder per case.

Each case builds a throwaway project folder in the system temp dir (outside any repo, so no parent
CLAUDE.md leaks in), puts it in the case's state, runs
`claude -p "/project-builder:<skill> <prompt>"` with this plugin loaded via --plugin-dir, and saves
the reply, every tool call, cost, and what changed in the folder (git status, branches) to
evals/<EVAL_OUT>/<case>.json. Grade by hand against each case's "pass" list in cases.json.

Environment:
  EVAL_CLI     path to the claude binary (default: `claude` on PATH; use a current CLI)
  EVAL_PLUGIN  plugin directory to test (default: this plugin), e.g. an older copy for a baseline
  EVAL_OUT     output folder name (default: out)
  EVAL_MODEL   model alias (default: sonnet)

Usage: python run.py [case_id ...]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.environ.get("EVAL_PLUGIN", os.path.dirname(HERE))
KIT = os.path.join(PLUGIN, "kit")
OUTNAME = os.environ.get("EVAL_OUT", "out")
OUT = os.path.join(HERE, OUTNAME)
WORK = os.path.join(tempfile.gettempdir(), "project-builder-evals", OUTNAME)
CLAUDE = os.environ.get("EVAL_CLI") or shutil.which("claude")
MODEL = os.environ.get("EVAL_MODEL", "sonnet")
FIX = os.path.join(HERE, "fixtures")

APPROVED = "Approved at STEPS.md Step 8 on: 2026-11-21. No code is written before this date."
STUCK_NOTES = (
    "- 2026-11-21: Unit 01 implemented; user found --dry-run renames files.\n"
    "- 2026-11-21 fix attempt 1: --dry-run still renames files. Moved the print before the rename. Still renames.\n"
    "- 2026-11-21 fix attempt 2: --dry-run still renames files. Added a dry-run check before os.rename. Still renames."
)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def set_resume(tracker_text, line):
    return re.sub(r"(## Resume here\n\n)(.*?)(\n\n## )", lambda m: m.group(1) + line + m.group(3),
                  tracker_text, count=1, flags=re.S)


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8").stdout


def build_state(state, d):
    """Put folder d into the named state."""
    if state == "empty":
        return
    shutil.copytree(os.path.join(FIX, "photo-renamer"), d, dirs_exist_ok=True)
    ctx = os.path.join(d, "context")
    kitdir = os.path.join(ctx, "kit")
    os.makedirs(kitdir, exist_ok=True)
    shutil.copy(os.path.join(KIT, "STEPS.md"), kitdir)
    shutil.copy(os.path.join(KIT, "prompts", "generate-files.md"), kitdir)
    shutil.copy(os.path.join(KIT, "types", "python-tool.md"), kitdir)
    shutil.copy(os.path.join(KIT, "templates", "context", "specs", "_spec-template.md"), os.path.join(ctx, "specs"))
    tpl = os.path.join(KIT, "templates", "context")
    tracker = os.path.join(ctx, "progress-tracker.md")
    plan = os.path.join(ctx, "specs", "00-build-plan.md")

    if state.startswith("planning-"):
        blank = {"planning-step3": ["ui-context.md", "code-standards.md", "ai-workflow-rules.md"],
                 "planning-step6": []}[state]
        for name in blank:
            shutil.copy(os.path.join(tpl, name), os.path.join(ctx, name))
        shutil.copy(os.path.join(tpl, "specs", "00-build-plan.md"), plan)
        os.remove(os.path.join(ctx, "specs", "01-cli-skeleton.md"))
        resume = {"planning-step3": "Step 3 approved; next: Step 4 ui-context.md",
                  "planning-step6": "Step 6 approved; next: Step 7 progress-tracker.md + CLAUDE.md"}[state]
        write(tracker, set_resume(read(os.path.join(tpl, "progress-tracker.md")), resume))
    else:
        stuck = state == "unit01-stuck"
        status = "verifying" if stuck else "spec approved"
        resume = ("Unit 01 verifying: fixing --dry-run (attempt 2 failed)." if stuck
                  else "Unit 01 spec approved; next: implement it on feat/01-cli-skeleton.")
        notes = STUCK_NOTES if stuck else "- 2026-11-21: Planning finished; unit 01 spec approved."
        write(plan, read(plan).replace("APPROVAL_LINE", APPROVED).replace("UNIT01_STATUS", status))
        write(tracker, read(tracker).replace("RESUME_PLACEHOLDER", resume).replace("SESSION_NOTES_PLACEHOLDER", notes))
        if stuck:
            shutil.copytree(os.path.join(FIX, "photo-renamer-stuck"), d, dirs_exist_ok=True)

    git(d, "init", "-q", "-b", "main")
    git(d, "config", "user.email", "eval@example.com")
    git(d, "config", "user.name", "eval")
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "fixture")
    if state == "unit01-stuck":
        git(d, "switch", "-q", "-c", "feat/01-cli-skeleton")


def run(case):
    cid = case["id"]
    d = os.path.join(WORK, cid)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    build_state(case["state"], d)
    cmd = [CLAUDE, "-p", f"/project-builder:{case['skill']} {case['prompt']}",
           "--plugin-dir", PLUGIN, "--model", MODEL, "--max-budget-usd", "1",
           "--no-session-persistence", "--output-format", "stream-json", "--verbose",
           "--allowedTools", "Read Write Edit Glob Grep Bash",
           "--disallowedTools", "Task Agent WebSearch WebFetch"]
    p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, encoding="utf-8", timeout=900)
    tools, result, meta, model = [], None, {}, None
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            model = ev.get("model")
        if ev.get("type") == "assistant":
            for blk in ev.get("message", {}).get("content", []):
                if blk.get("type") in ("tool_use", "server_tool_use"):
                    tools.append({"name": blk.get("name"), "input": json.dumps(blk.get("input"))[:300]})
        if ev.get("type") == "result":
            result = ev.get("result")
            meta = {k: ev.get(k) for k in ("num_turns", "total_cost_usd", "permission_denials", "is_error")}
    if os.path.isdir(os.path.join(d, ".git")):
        changed = git(d, "status", "--porcelain", "-uall").splitlines()
        branches = git(d, "branch", "--format=%(refname:short)").split()
        commits = git(d, "log", "--all", "--oneline").splitlines()
    else:
        changed = [os.path.relpath(os.path.join(r, f), d) for r, _, fs in os.walk(d) for f in fs]
        branches, commits = [], []
    data = {"model": model, "result": result, "tools": tools, "meta": meta,
            "files_changed": changed, "branches": branches, "commits": commits, "folder": d,
            "stderr": p.stderr[-1000:] if result is None else ""}
    write(os.path.join(OUT, f"{cid}.json"), json.dumps(data, indent=2, ensure_ascii=False))
    return cid, meta.get("total_cost_usd"), len(tools)


def main():
    if not CLAUDE:
        sys.exit("claude CLI not found: set EVAL_CLI")
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    cases = json.loads(read(os.path.join(HERE, "cases.json")))
    if sys.argv[1:]:
        cases = [c for c in cases if c["id"] in sys.argv[1:]]
    with ThreadPoolExecutor(4) as ex:
        for cid, cost, nt in ex.map(run, cases):
            print(cid, "cost", cost, "tools", nt, flush=True)


if __name__ == "__main__":
    main()
