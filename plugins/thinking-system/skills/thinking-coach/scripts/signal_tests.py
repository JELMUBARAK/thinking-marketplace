#!/usr/bin/env python3
"""Test whether a pattern in a table is a real signal or could be chance.

Standard library only. Works on a CSV (for example one written by extract.py).
Columns are named by header text (case-insensitive) or 1-based number.

Commands:
  power   --test compare|corr --n N (--effect D | --diff X --sd S | --p1 A --p2 B | --r R) [--tests M]
          Can N rows detect the smallest effect that would change the decision?
  trend   FILE --y COL [--x COL]           does Y rise or fall with X (or row order)?
  compare FILE --y COL --group COL         do groups differ on Y (numeric, or 0/1 theme codes)?
  assoc   FILE --a COL --b COL             are two categorical columns linked (theme vs outcome)?
  change  FILE --y COL [--x COL]           is there a step change in Y along X (or row order)?
  scan    FILE [--cols A,B,C]              every pair of numeric columns, corrected for the number tested
Options: --perms N (shuffles, default 5000; scan 2000), --seed N (default 1).

Method: shuffle tests (the pattern is recomputed on shuffled data many times to
see how often chance alone matches it) and a split-half check (does the pattern
point the same way in two random halves of the rows?). Grades follow this
plugin's conventions, not universal rules:
  strong = p < 0.01 after correcting for the number of patterns tested, and the
           same direction in both halves
  weak   = p < 0.05 before correction, but not strong: treat as a hypothesis to test
  noise  = p >= 0.05: no reliable pattern
Shuffle tests assume rows are independent. Rows in time order that follow each
other closely (autocorrelation) make patterns look stronger than they are; the
script warns when it sees this.
"""
import csv
import math
import random
import re
import sys
from statistics import NormalDist, mean, pstdev

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

Z = NormalDist()
MIN_N = 8


# ---------- data ----------

def to_num(s):
    s = str(s).strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")")
    try:
        v = float(re.sub(r"[\s,$€£¥%()]", "", s))
    except ValueError:
        return None
    return -v if neg else v


def to_x(s):
    """Numbers, or ISO dates as day counts, for ordering."""
    v = to_num(s)
    if v is not None:
        return v
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(s).strip())
    if m:
        y, mo, d = map(int, m.groups())
        return (y * 372 + mo * 31 + d) * 1.0
    return None


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.reader(f) if any(c.strip() for c in r)]
    if not rows:
        sys.exit("empty file")
    return rows[0], rows[1:]


def col(header, name):
    if name.isdigit() and 1 <= int(name) <= len(header):
        return int(name) - 1
    low = [h.strip().lower() for h in header]
    if name.strip().lower() in low:
        return low.index(name.strip().lower())
    sys.exit(f"column '{name}' not found. Columns: {', '.join(header)}")


def pairs(rows, i, j, fx=to_num, fy=to_num):
    out = []
    for r in rows:
        if max(i, j) < len(r):
            a, b = fx(r[i]), fy(r[j])
            if a is not None and b is not None:
                out.append((a, b))
    return out


# ---------- statistics ----------

def ranks(xs):
    order = sorted(range(len(xs)), key=lambda k: xs[k])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def pearson(x, y):
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else 0.0


def perm_test(stat, x, y, n_perm, rng):
    """Two-sided shuffle test of stat(x, y) by shuffling y."""
    obs = stat(x, y)
    ys = list(y)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(ys)
        if abs(stat(x, ys)) >= abs(obs) - 1e-12:
            hits += 1
    return obs, (hits + 1) / (n_perm + 1)


def split_half(stat, x, y, rng):
    idx = list(range(len(x)))
    rng.shuffle(idx)
    h = len(idx) // 2
    out = []
    for part in (idx[:h], idx[h:]):
        xs, ys = [x[k] for k in part], [y[k] for k in part]
        try:
            out.append(stat(xs, ys))
        except (ValueError, ZeroDivisionError):
            out.append(0.0)
    return out


def lag1(v):
    if len(v) < 4 or pstdev(v) == 0:
        return 0.0
    return pearson(v[:-1], v[1:])


def grade(p_adj, p_raw, halves):
    same = bool(halves) and (all(h > 0 for h in halves) or all(h < 0 for h in halves))
    if p_adj < 0.01 and same:
        return "strong"
    if p_raw < 0.05:
        return "weak (a hypothesis to test, not a finding)"
    return "noise (no reliable pattern)"


def halves_txt(halves, fmt="{:+.2f}"):
    same = all(h > 0 for h in halves) or all(h < 0 for h in halves)
    return f"{fmt.format(halves[0])} and {fmt.format(halves[1])} ({'same direction' if same else 'direction flips'})"


def too_few(n):
    if n < MIN_N:
        print(f"Only {n} usable rows: too few to test (minimum {MIN_N}). Treat any pattern as a guess.")
        return True
    return False


# ---------- commands ----------

def cmd_power(o):
    test = o.get("test", "compare")
    n = int(o["n"])
    m = int(o.get("tests", 1))
    alpha = 0.05 / m
    zc = Z.inv_cdf(1 - alpha / 2)
    zb = Z.inv_cdf(0.8)
    if test == "corr":
        r = float(o["r"])
        eff = math.atanh(abs(r))
        power = Z.cdf(eff * math.sqrt(max(n - 3, 0)) - zc)
        need = ((zc + zb) / eff) ** 2 + 3
        what = f"correlation r = {r}"
        arith = f"atanh({abs(r)}) x sqrt({n} - 3) - {zc:.2f}"
    else:
        if "p1" in o:
            p1, p2 = float(o["p1"]), float(o["p2"])
            eff = abs(2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2)))
            what = f"a share of {p1:.0%} vs {p2:.0%} (effect h = {eff:.2f})"
        elif "diff" in o:
            eff = abs(float(o["diff"]) / float(o["sd"]))
            what = f"a difference of {o['diff']} with spread (SD) {o['sd']} (effect = {eff:.2f} SD)"
        else:
            eff = abs(float(o["effect"]))
            what = f"an effect of {eff} SD"
        power = Z.cdf(eff * math.sqrt(n) / 2 - zc)
        need = 4 * ((zc + zb) / eff) ** 2
        arith = f"{eff:.2f} x sqrt({n}) / 2 - {zc:.2f}, two equal groups"
    print(f"Power to detect {what} with {n} rows" + (f", {m} tests (alpha {alpha:.4f})" if m > 1 else "") + ":")
    print(f"  power = {power:.0%}  [normal approximation: Phi({arith}); a little optimistic below ~30 rows]")
    print(f"  rows needed for 80% power: about {math.ceil(need)}")
    if power < 0.8:
        print("  Verdict: too few to tell. A test this size will often miss an effect that matters, so "
              "'no pattern found' would not mean 'no effect'. Use the light path: state the expectation, "
              "look, and say the data can't settle it.")
    else:
        print("  Verdict: enough data to test for an effect of this size.")


def cmd_trend(f, o, rng, n_perm):
    header, rows = load(f)
    yi = col(header, o["y"])
    if "x" in o:
        xi = col(header, o["x"])
        data = pairs(rows, xi, yi, fx=to_x)
        data.sort()
        xname = header[xi]
    else:
        data = [(k, v) for k, v in enumerate(to_num(r[yi]) for r in rows if yi < len(r)) if v is not None]
        xname = "row order"
    n = len(data)
    print(f"Trend of {header[yi]} against {xname}: {n} usable rows")
    if too_few(n):
        return
    x = ranks([a for a, _ in data])
    y = ranks([b for _, b in data])
    obs, p = perm_test(pearson, x, y, n_perm, rng)
    halves = split_half(pearson, x, y, rng)
    print(f"  rank correlation (Spearman) = {obs:+.2f}; shuffle test p = {p:.4f} ({n_perm} shuffles)")
    print(f"  split-half: {halves_txt(halves)}")
    ys = [b for _, b in data]
    ac = lag1(ys)
    if abs(ac) > 0.3:
        print(f"  warning: neighbouring rows are correlated (lag-1 = {ac:+.2f}); in time-ordered data this "
              "inflates the result. Treat p as too small.")
    print(f"  grade: {grade(p, p, halves)}")


def mean_diff(g, y):
    a = [v for k, v in zip(g, y) if k == 1]
    b = [v for k, v in zip(g, y) if k == 0]
    return mean(a) - mean(b) if a and b else 0.0


def between(g, y):
    m = mean(y)
    groups = {}
    for k, v in zip(g, y):
        groups.setdefault(k, []).append(v)
    return sum(len(v) * (mean(v) - m) ** 2 for v in groups.values())


def cmd_compare(f, o, rng, n_perm):
    header, rows = load(f)
    yi, gi = col(header, o["y"]), col(header, o["group"])
    data = [(r[gi].strip(), to_num(r[yi])) for r in rows if max(yi, gi) < len(r)]
    data = [(g, v) for g, v in data if g and v is not None]
    labels = sorted({g for g, _ in data})
    n = len(data)
    print(f"{header[yi]} by {header[gi]}: {n} usable rows, groups: " +
          ", ".join(f"{lab} (n={sum(1 for g, _ in data if g == lab)}, mean {mean([v for g, v in data if g == lab]):.3g})"
                    for lab in labels))
    if too_few(n) or len(labels) < 2:
        if len(labels) < 2:
            print("  only one group: nothing to compare")
        return
    y = [v for _, v in data]
    if len(labels) == 2:
        g = [1 if lab == labels[1] else 0 for lab, _ in data]
        obs, p = perm_test(mean_diff, g, y, n_perm, rng)
        halves = split_half(mean_diff, g, y, rng)
        sd = pstdev(y) or 1
        print(f"  difference in means ({labels[1]} minus {labels[0]}) = {obs:+.3g} "
              f"(= {obs / sd:+.2f} SD of all rows); shuffle test p = {p:.4f} ({n_perm} shuffles)")
        print(f"  split-half differences: {halves_txt(halves, '{:+.3g}')}")
        print(f"  grade: {grade(p, p, halves)}")
    else:
        g = [labels.index(lab) for lab, _ in data]
        obs, p = perm_test(between, g, y, n_perm, rng)
        print(f"  {len(labels)} groups; shuffle test on between-group spread p = {p:.4f} ({n_perm} shuffles)")
        print("  split-half not run for 3+ groups: compare two groups at a time to see which ones differ")
        print(f"  grade: {grade(p, p, [1, 1]) if p < 0.01 else grade(1, p, [])}")


def chi2(a, b):
    n = len(a)
    ca, cb, cab = {}, {}, {}
    for u, v in zip(a, b):
        ca[u] = ca.get(u, 0) + 1
        cb[v] = cb.get(v, 0) + 1
        cab[(u, v)] = cab.get((u, v), 0) + 1
    s = 0.0
    for u in ca:
        for v in cb:
            e = ca[u] * cb[v] / n
            s += (cab.get((u, v), 0) - e) ** 2 / e
    return s


def cmd_assoc(f, o, rng, n_perm):
    header, rows = load(f)
    ai, bi = col(header, o["a"]), col(header, o["b"])
    data = [(r[ai].strip(), r[bi].strip()) for r in rows if max(ai, bi) < len(r)]
    data = [(u, v) for u, v in data if u and v]
    n = len(data)
    print(f"{header[ai]} vs {header[bi]}: {n} usable rows")
    if too_few(n):
        return
    a, b = [u for u, _ in data], [v for _, v in data]
    bl = sorted(set(b))
    for u in sorted(set(a)):
        shares = ", ".join(f"{sum(1 for x, y in data if x == u and y == v) / b.count(v):.0%} of {v}" for v in bl)
        print(f"  {header[ai]} = {u}: in {shares}")
    obs, p = perm_test(chi2, a, b, n_perm, rng)
    print(f"  chi-square = {obs:.2f}; shuffle test p = {p:.4f} ({n_perm} shuffles)")
    sign = lambda x, y: chi2(x, y) if len(set(x)) > 1 and len(set(y)) > 1 else 0.0
    if len(set(a)) == 2 and len(set(b)) == 2:
        a1, b1 = sorted(set(a))[1], sorted(set(b))[1]
        diff = lambda x, y: (sum(1 for u, v in zip(x, y) if u == a1 and v == b1) / max(1, sum(1 for v in y if v == b1))
                             - sum(1 for u, v in zip(x, y) if u == a1 and v != b1) / max(1, sum(1 for v in y if v != b1)))
        halves = split_half(diff, a, b, rng)
        print(f"  split-half (share of {header[ai]}={a1} in {b1} minus in others): {halves_txt(halves, '{:+.0%}')}")
    else:
        halves = split_half(sign, a, b, rng)
        halves = [1, 1] if all(h > 0 for h in halves) else [1, -1]
        print("  split-half for multi-category tables only checks that a link appears in both halves")
    print(f"  grade: {grade(p, p, halves)}")


def best_split(x, y):
    n = len(y)
    seg = max(3, n // 10)
    total, sd = sum(y), pstdev(y) or 1
    best, at, left = 0.0, None, 0.0
    for k in range(1, n):
        left += y[k - 1]
        if k < seg or n - k < seg:
            continue
        ml, mr = left / k, (total - left) / (n - k)
        s = abs(ml - mr) * math.sqrt(k * (n - k) / n) / sd
        if s > best:
            best, at = s, k
    return best, at


def cmd_change(f, o, rng, n_perm):
    header, rows = load(f)
    yi = col(header, o["y"])
    if "x" in o:
        xi = col(header, o["x"])
        data = sorted(pairs(rows, xi, yi, fx=to_x))
        xs = [r[xi] for r in rows if max(xi, yi) < len(r) and to_x(r[xi]) is not None and to_num(r[yi]) is not None]
        xs = sorted(xs, key=to_x)
    else:
        data = [(k, v) for k, v in enumerate(to_num(r[yi]) for r in rows if yi < len(r)) if v is not None]
        xs = [str(k + 2) + " (file row)" for k in range(len(data))]
    y = [b for _, b in data]
    n = len(y)
    print(f"Step change in {header[yi]}: {n} usable rows")
    if too_few(n):
        return
    obs, at = best_split(None, y)
    if at is None:
        print("  too few rows to place a split")
        return
    ys, hits = list(y), 0
    for _ in range(n_perm):
        rng.shuffle(ys)
        if best_split(None, ys)[0] >= obs - 1e-12:
            hits += 1
    p = (hits + 1) / (n_perm + 1)
    print(f"  biggest step at {xs[at] if at < len(xs) else at}: mean {mean(y[:at]):.3g} before, "
          f"{mean(y[at:]):.3g} after ({at} and {n - at} rows)")
    print(f"  shuffle test p = {p:.4f} ({n_perm} shuffles; the search over every split point is included, "
          "so no extra correction is needed)")
    ac = lag1([v - (mean(y[:at]) if k < at else mean(y[at:])) for k, v in enumerate(y)])
    if abs(ac) > 0.3:
        print(f"  warning: after removing the step, neighbouring rows are still correlated (lag-1 = {ac:+.2f}); "
              "a slow drift can look like a step. Treat p as too small.")
    print(f"  grade: {grade(p, p, [1, 1]) if p < 0.01 else grade(1, p, [])}")
    print("  split-half not used here: a step is a single event in time. Confirm it with a known cause "
          "(a change made on that date) or new data after it.")


def cmd_scan(f, o, rng, n_perm):
    header, rows = load(f)
    if "cols" in o:
        idx = [col(header, c) for c in o["cols"].split(",")]
    else:
        idx = []
        for i in range(len(header)):
            vals = [r[i] for r in rows if i < len(r) and r[i].strip()]
            if vals and sum(to_num(v) is not None for v in vals) >= 0.8 * len(vals):
                idx.append(i)
    tests = [(i, j) for a, i in enumerate(idx) for j in idx[a + 1:]]
    m = len(tests)
    if m == 0:
        print("fewer than 2 numeric columns: nothing to scan")
        return
    print(f"Scan of {len(idx)} numeric columns: {m} pairs tested")
    print(f"  expected false hits by chance at p < 0.05: {m} x 0.05 = {m * 0.05:.1f}")
    res = []
    for i, j in tests:
        d = pairs(rows, i, j)
        if len(d) < MIN_N:
            continue
        x, y = ranks([a for a, _ in d]), ranks([b for _, b in d])
        r, p = perm_test(pearson, x, y, n_perm, rng)
        res.append([header[i], header[j], len(d), r, p, x, y])
    res.sort(key=lambda t: t[4])
    k = len(res)
    for rank, t in enumerate(res):   # Holm correction
        t.append(min(1.0, t[4] * (k - rank)))
    for rank in range(1, k):
        res[rank][7] = max(res[rank][7], res[rank - 1][7])
    shown = [t for t in res if t[4] < 0.05][:4]
    if not shown:
        print("  no pair reached p < 0.05: no reliable pattern")
        return
    for a, b, n, r, p, x, y, padj in shown:
        halves = split_half(pearson, x, y, rng)
        print(f"  {a} ~ {b}: rank r = {r:+.2f}, n = {n}, p = {p:.4f}, corrected (Holm) p = {padj:.4f}; "
              f"split-half {halves_txt(halves)}")
        print(f"    grade: {grade(padj, p, halves)}")
    rest = sum(1 for t in res if t[4] < 0.05) - len(shown)
    if rest > 0:
        print(f"  ... {rest} more pairs below p < 0.05 (parked)")
    print("  A correlation found by scanning is a hypothesis. Common causes, reverse cause and "
          "selection effects are not ruled out.")


def parse(argv):
    o, pos, i = {}, [], 0
    while i < len(argv):
        if argv[i].startswith("--"):
            o[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            pos.append(argv[i])
            i += 1
    return pos, o


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd = sys.argv[1]
    pos, o = parse(sys.argv[2:])
    rng = random.Random(int(o.get("seed", 1)))
    try:
        if cmd == "power":
            cmd_power(o)
            return
        fn = {"trend": cmd_trend, "compare": cmd_compare, "assoc": cmd_assoc,
              "change": cmd_change, "scan": cmd_scan}.get(cmd)
        if not fn or not pos:
            sys.exit(__doc__)
        n_perm = int(o.get("perms", 2000 if cmd == "scan" else 5000))
        fn(pos[0], o, rng, n_perm)
    except KeyError as e:
        sys.exit(f"missing option --{e.args[0]}. See --help.")


if __name__ == "__main__":
    main()
