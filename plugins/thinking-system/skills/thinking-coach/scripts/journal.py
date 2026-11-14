#!/usr/bin/env python3
"""Decision journal: the long-term memory of the Thinking System plugin.

Stores one JSON record per line in ~/.claude/thinking-system/journal.jsonl
(override with the THINKING_JOURNAL environment variable).

Commands:
  add            read one JSON record from stdin and append it (prints its id)
  update ID      read JSON fields from stdin and merge them into record ID
  get ID         print one record
  find WORDS     search records (decisions and base rates) by keywords or tags
  due            list open decisions whose review date has passed
  stats [TAG]    calibration and cost-estimate bias from reviewed decisions
  path           print the journal file location
Options:
  due --hook     print nothing unless something is due (for the session-start hook)
"""
import json
import os
import re
import sys
from datetime import date, datetime

PATH = os.path.expanduser(
    os.environ.get("THINKING_JOURNAL", "~/.claude/thinking-system/journal.jsonl")
)


def load():
    if not os.path.exists(PATH):
        return []
    out = []
    with open(PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def save(records):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, PATH)


def read_stdin_json():
    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit("error: expected a JSON object on stdin")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"error: invalid JSON: {e}")
    if not isinstance(obj, dict):
        sys.exit("error: expected a JSON object")
    return obj


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "decision").lower()).strip("-")
    return s[:40] or "decision"


def cmd_add():
    rec = read_stdin_json()
    records = load()
    today = date.today().isoformat()
    rec.setdefault("kind", "decision")
    rec.setdefault("date", today)
    if rec["kind"] == "decision":
        rec.setdefault("status", "open")
    base = rec.get("id") or f"{rec['date'].replace('-', '')}-{slug(rec.get('title') or rec.get('problem_card'))}"
    ids = {r.get("id") for r in records}
    rid, n = base, 2
    while rid in ids:
        rid, n = f"{base}-{n}", n + 1
    rec["id"] = rid
    records.append(rec)
    save(records)
    print(rid)


def cmd_update(rid):
    fields = read_stdin_json()
    records = load()
    for r in records:
        if r.get("id") == rid:
            r.update(fields)
            if r.get("kind") == "decision" and "actual_cost" in fields and r.get("expected_cost"):
                try:
                    r["delta"] = float(r["expected_cost"]) - float(r["actual_cost"])
                except (TypeError, ValueError):
                    pass
            r["updated"] = date.today().isoformat()
            save(records)
            print(json.dumps(r, ensure_ascii=False, indent=2))
            return
    sys.exit(f"error: no record with id {rid}")


def cmd_get(rid):
    for r in load():
        if r.get("id") == rid:
            print(json.dumps(r, ensure_ascii=False, indent=2))
            return
    sys.exit(f"error: no record with id {rid}")


def cmd_find(words):
    terms = [w.lower() for w in words]
    scored = []
    for r in load():
        text = json.dumps(r, ensure_ascii=False).lower()
        tags = [t.lower() for t in r.get("tags", [])]
        score = sum(text.count(t) + 3 * (t in tags) for t in terms)
        if score:
            scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], x[1].get("date", "")))
    if not scored:
        print("No matching records.")
        return
    for score, r in scored[:8]:
        line = f"[{r.get('kind')}] {r.get('id')} | {r.get('title') or r.get('problem_card', '')}"
        if r.get("kind") == "decision":
            line += f" | chosen: {r.get('chosen', '?')} | status: {r.get('status')}"
            if r.get("lesson"):
                line += f" | lesson: {r['lesson']}"
        else:
            line += f" | value: {r.get('value', '?')} | source: {r.get('source', '?')}"
        print(line)


def parse_day(s):
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def cmd_due(hook=False):
    today = date.today()
    due = [
        r for r in load()
        if r.get("kind") == "decision" and r.get("status") == "open"
        and parse_day(r.get("review_date", "")) and parse_day(r["review_date"]) <= today
    ]
    if not due:
        if not hook:
            print("No decisions are due for review.")
        return
    print(f"Thinking System: {len(due)} decision(s) due for review. Say 'review my decision on ...' to close the loop:")
    for r in due:
        print(f"- {r.get('id')}: {r.get('title') or r.get('problem_card', '')} (review date {r.get('review_date')})")


def cmd_stats(tag=None):
    rows = [r for r in load() if r.get("kind") == "decision" and r.get("status") == "reviewed"]
    if tag:
        rows = [r for r in rows if tag.lower() in [t.lower() for t in r.get("tags", [])]]
    print(f"Reviewed decisions{f' tagged {tag}' if tag else ''}: {len(rows)}")
    if not rows:
        print("Not enough data yet. Calibration needs reviewed decisions.")
        return
    # Cost bias: actual vs expected
    ratios = []
    for r in rows:
        try:
            e, a = float(r["expected_cost"]), float(r["actual_cost"])
            if e:
                ratios.append(a / e - 1)
        except (KeyError, TypeError, ValueError):
            pass
    if ratios:
        avg = sum(ratios) / len(ratios)
        word = "over" if avg > 0 else "under"
        print(f"Cost estimates: actual came in {abs(avg) * 100:.0f}% {word} expected on average (n={len(ratios)}).")
    # Probability calibration: predictions [{claim, p, came_true}]
    preds = []
    for r in rows:
        for p in r.get("predictions", []):
            try:
                preds.append((float(p["p"]), bool(p["came_true"])))
            except (KeyError, TypeError, ValueError):
                pass
    if preds:
        brier = sum((p - int(o)) ** 2 for p, o in preds) / len(preds)
        avg_p = sum(p for p, _ in preds) / len(preds)
        hit = sum(int(o) for _, o in preds) / len(preds)
        print(f"Predictions: {len(preds)} | average confidence {avg_p * 100:.0f}% | actually true {hit * 100:.0f}% | Brier score {brier:.3f} (0 = perfect, 0.25 = coin flip)")
        if avg_p - hit > 0.1:
            print("Pattern: overconfident - lower your probabilities.")
        elif hit - avg_p > 0.1:
            print("Pattern: underconfident - you can trust your estimates more.")
        else:
            print("Pattern: well calibrated so far.")
    if len(rows) < 5:
        print("Caution: fewer than 5 reviewed decisions, so treat these patterns as weak.")
    lessons = [r["lesson"] for r in rows if r.get("lesson")][-5:]
    if lessons:
        print("Recent lessons:")
        for l in lessons:
            print(f"- {l}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    cmd, rest = args[0], args[1:]
    if cmd == "add":
        cmd_add()
    elif cmd == "update" and rest:
        cmd_update(rest[0])
    elif cmd == "get" and rest:
        cmd_get(rest[0])
    elif cmd == "find" and rest:
        cmd_find(rest)
    elif cmd == "due":
        cmd_due(hook="--hook" in rest)
    elif cmd == "stats":
        cmd_stats(rest[0] if rest else None)
    elif cmd == "path":
        print(PATH)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
