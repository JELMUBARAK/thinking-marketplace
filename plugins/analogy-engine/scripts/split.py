"""Split a concept's 16 what-ifs into a practice set and a test set at random.

Balanced by definition, then kind, so both sets get the same mix and neither
is easier by the author's choice. Prints counts only, never the questions.

Usage: python split.py <analogy-runs dir> <slug> [seed]
Reads  <slug>.questions.json   (JSON array of 16 what-ifs)
Writes <slug>.practice.json, <slug>.test.json (8 each, renumbered P1.., T1..)
"""
import json
import os
import random
import sys
from collections import Counter, defaultdict

d, slug = sys.argv[1], sys.argv[2]
seed = int(sys.argv[3]) if len(sys.argv) > 3 else random.SystemRandom().randrange(10**6)
rng = random.Random(seed)

qs = json.load(open(os.path.join(d, f"{slug}.questions.json"), encoding="utf-8"))
if isinstance(qs, dict):
    qs = qs.get("whatifs", [])

groups = defaultdict(list)
for q in qs:
    groups[q.get("definition")].append(q)

# Greedy balance: each definition splits in half; within that, each question
# goes to the set holding fewer of its kind so far (ties broken at random).
practice, test = [], []
sets = (practice, test)
keys = list(groups)
rng.shuffle(keys)
for key in keys:
    g = groups[key]
    rng.shuffle(g)
    # Core kinds first, so they split evenly before capacity runs short.
    core = ("threshold", "stress", "misconception_trap")
    g.sort(key=lambda q: q.get("kind") not in core)
    cap = [len(g) // 2, len(g) // 2]
    if len(g) % 2:
        cap[0 if len(practice) <= len(test) else 1] += 1
    used = [0, 0]
    for q in g:
        open_ = [i for i in (0, 1) if used[i] < cap[i]]
        k = q.get("kind")
        counts = [sum(1 for x in sets[i] if x.get("kind") == k) for i in (0, 1)]
        best = min(open_, key=lambda i: (counts[i], len(sets[i]), rng.random()))
        sets[best].append(q)
        used[best] += 1

for prefix, items, name in (("P", practice, "practice"), ("T", test, "test")):
    rng.shuffle(items)
    out = [dict(q, id=f"{prefix}{i + 1}") for i, q in enumerate(items)]
    json.dump(out, open(os.path.join(d, f"{slug}.{name}.json"), "w", encoding="utf-8"))

def kinds(items):
    return dict(Counter(q.get("kind") for q in items))

warnings = []
if len(qs) != 16:
    warnings.append(f"{len(qs)} what-ifs, expected 16")
allk = Counter(q.get("kind") for q in qs)
for k in ("threshold", "stress", "misconception_trap"):
    if allk[k] < 4:
        warnings.append(f"only {allk[k]} {k}, expected 4")
defs = Counter(q.get("definition") for q in qs)
named = [k for k in defs if k is not None]
if named:
    # Values dispute: 4 neutral, then 6 per definition (2 definitions) or 4 per definition (3), 16 in all.
    per_def = {2: 6, 3: 4}.get(len(named))
    if per_def is None:
        warnings.append(f"{len(named)} definitions, expected 2 or 3")
    elif defs[None] != 4 or any(defs[k] != per_def for k in named):
        warnings.append(f"uneven definitions {dict(defs)}, expected 4 neutral and {per_def} per definition")

print(json.dumps({"seed": seed, "warnings": warnings, "total": len(qs), "practice": len(practice), "test": len(test),
                  "practice_kinds": kinds(practice), "test_kinds": kinds(test)}))
