"""Render a learner card from a run record.

Reads <slug>.json (written by build_record.py) and writes <slug>.card.html,
kept short on purpose: the drawing or simulation first, then one plain line.
Everything else (the full story, how it lines up, where it breaks) sits behind
one "More" toggle. A rough model shows its breaks openly. Scores never appear
on the card. Drawings come from ../drawings/ (index.json maps file -> names).

Usage: python render_card.py <analogy-runs dir> <slug>
"""
import html
import json
import os
import re
import sys

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAWINGS = os.path.join(PLUGIN, "drawings")
RULE_TAG = re.compile(r"\s*\(R\d+[a-z]?\)")

CSS = """
:root{--bg:#f6f5f1;--card:#fff;--text:#1f1e1c;--muted:#6b6a65;--border:rgba(0,0,0,.12);
--warn-bg:#faeeda;--warn:#854f0b;--info-bg:#eeedfe;--info:#3c3489;
--node:#eeedfe;--node-line:#534ab7;--node-text:#3c3489;--base:#e1f5ee;--base-line:#0f6e56;--base-text:#085041;
--bad:#fcebeb;--bad-line:#a32d2d;--bad-text:#791f1f;--back:#1d9e75}
@media (prefers-color-scheme:dark){:root{--bg:#1c1c1a;--card:#262624;--text:#ecebe6;--muted:#a3a29c;--border:rgba(255,255,255,.14);
--warn-bg:#633806;--warn:#fac775;--info-bg:#3c3489;--info:#cecbf6;
--node:#3c3489;--node-line:#afa9ec;--node-text:#eeedfe;--base:#085041;--base-line:#5dcaa5;--base-text:#e1f5ee;
--bad:#791f1f;--bad-line:#f09595;--bad-text:#fcebeb;--back:#5dcaa5}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;padding:16px}
.card{max-width:640px;margin:0 auto;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px}
.top{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.concept{color:var(--muted);font-size:14px;margin:0}
.pill{font-size:12px;padding:2px 10px;border-radius:8px}
.rough{background:var(--warn-bg);color:var(--warn)}.info{background:var(--info-bg);color:var(--info)}
h1{font-size:20px;font-weight:600;margin:10px 0 4px;text-align:center}h3{font-size:15px;font-weight:600;margin:26px 0 2px}
.line{font-size:18px;font-weight:500;text-align:center;margin:12px 0 4px}
.story{margin:6px 0;font-size:15px}.grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);font-size:14px;border-top:1px solid var(--border);margin-top:8px}
.grid div{padding:7px 10px 7px 0;border-bottom:1px solid var(--border)}.grid .head{color:var(--muted)}
.breaks{margin-top:12px;padding:10px 14px;border-radius:8px;background:var(--warn-bg);color:var(--warn);font-size:14px}
.breaks ul,.more ul{margin:4px 0 0;padding-left:18px;font-size:14px}.drawing{margin:6px 0 0}
.note{color:var(--muted);font-size:13px}summary{cursor:pointer;margin:14px 0 4px;color:var(--muted);font-size:14px}
"""


def esc(s):
    return html.escape(str(s or ""), quote=True)


def clean_break(s):
    return re.sub(r"^\s*where this breaks:\s*", "", str(s or ""), flags=re.I).strip()


def read_drawing(fname):
    try:
        return open(os.path.join(DRAWINGS, os.path.basename(fname)), encoding="utf-8").read()
    except Exception:
        return None


def find_drawing(name):
    """drawings/index.json maps a drawing file to name fragments it serves."""
    try:
        index = json.load(open(os.path.join(DRAWINGS, "index.json"), encoding="utf-8"))
    except Exception:
        return None
    m = (name or "").lower()
    for fname, keys in index.items():
        if any(k.lower() in m for k in keys):
            return read_drawing(fname)
    return None


def breaks_box(breaks):
    items = "".join(f"<li>{esc(b)}</li>" for b in breaks)
    return f'<div class="breaks"><strong>Where it breaks</strong><ul>{items}</ul></div>'


def machine_block(c, rules, show_heading, rough):
    rows = c.get("mapping", [])
    mapped = [r for r in rows if r.get("source")]
    breaks = [clean_break(r.get("break")) for r in rows if r.get("break") or not r.get("source")]
    breaks = [b for b in breaks if b]
    out = []
    if show_heading:
        out.append(f"<h3>{esc(c.get('definition') or c.get('machine'))}</h3>")
    drawing = find_drawing(c.get("machine"))
    if drawing:
        out.append(f'<div class="drawing">{drawing}</div>')
    sents = []
    if c.get("analogy"):
        story = re.split(r"\s*where this breaks:", c["analogy"], flags=re.I)[0]
        sents = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", RULE_TAG.sub("", story).strip())
        name = lower_first(c.get("machine"))
        if name.split(" ", 1)[-1].lower() not in sents[0].lower():  # skip a heading that the line repeats
            out.append(f"<h1>Think of it as {esc(name)}</h1>")
        out.append(f'<p class="line">{esc(sents[0])}</p>')
    if breaks and rough:
        out.append(breaks_box(breaks))
    more = []
    if len(sents) > 1:
        more.append(f'<p class="story">{esc(" ".join(sents[1:]))}</p>')
    if mapped:
        more.append('<div class="grid"><div class="head">In everyday life</div>'
                    f'<div class="head">In {esc(c.get("_concept"))}</div>')
        for r in mapped:
            target = r.get("plain") or r.get("target") or rules.get(r.get("rule"), {}).get("rule", "")
            more.append(f"<div>{esc(r.get('source'))}</div><div>{esc(target)}</div>")
        more.append("</div>")
    if breaks and not rough:
        more.append(breaks_box(breaks))
    if more:
        out.append(f'<details class="more"><summary>More</summary>{"".join(more)}</details>')
    return "\n".join(out)


def lower_first(s):
    s = re.sub(r"\s*\(.*?\)\s*$", "", str(s or "")).strip()
    if not s:
        return "an everyday machine"
    s = s[0].lower() + s[1:]
    return s if re.match(r"^(a|an|the|two|one)\b", s) else f"a {s}"


def main():
    d, slug = sys.argv[1], sys.argv[2]
    rec = json.load(open(os.path.join(d, f"{slug}.json"), encoding="utf-8"))
    concept = rec.get("input", {}).get("concept", slug)
    res = rec.get("result", {})
    outcome = res.get("outcome")
    per = res.get("per_candidate", {})
    rules = {r["id"]: r for r in rec.get("rules", [])}
    cands = rec.get("candidates", [])
    for c in cands:
        c["_concept"] = concept

    pill = {"rough_model": '<span class="pill rough">Rough picture: check the breaks</span>',
            "side_by_side": '<span class="pill info">People define this differently</span>',
            "simulation_only": '<span class="pill info">No everyday comparison fits well</span>',
            "reject": '<span class="pill info">No everyday comparison fits well</span>'}.get(outcome, "")
    body = [f'<div class="top"><p class="concept">{esc(concept)}</p>{pill}</div>']

    if outcome == "direct_simulation":
        sim = rec.get("simulation") or {}
        drawing = read_drawing(sim.get("drawing", ""))
        if drawing:
            body.append(f'<div class="drawing">{drawing}</div>')
        body.append(f'<p class="line">{esc(sim.get("caption"))}</p>')
        plain = {}
        for c in cands:
            for r in c.get("mapping", []):
                plain.setdefault(r.get("rule"), r.get("plain"))
        items = [plain.get(rid) or rules.get(rid, {}).get("rule") for rid in sim.get("rule_ids") or []]
        items = [i for i in items if i]
        if items:
            body.append('<details class="more"><summary>More</summary><ul>'
                        + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul></details>")
    elif outcome in ("pass", "rough_model"):
        picked = next((c for c in cands if c.get("id") == res.get("picked")), cands[0] if cands else None)
        if picked:
            body.append(machine_block(picked, rules, False, outcome == "rough_model"))
    elif outcome == "side_by_side":
        body.append('<p class="note">Each definition gets its own picture. None is ranked above the others.</p>')
        for c in cands:
            label = per.get(c.get("id"), {}).get("outcome")
            if label in ("pass", "rough_model"):
                body.append(machine_block(c, rules, True, label == "rough_model"))
            else:
                body.append(f"<h3>{esc(c.get('definition') or c.get('machine'))}</h3>"
                            '<p class="note">No everyday comparison held up for this definition.</p>')
    else:
        body.append(f"<h1>{esc(concept)}, in plain rules</h1>")
        body.append('<p class="note">No everyday comparison predicted well enough, so here are the rules directly.</p><ul>')
        body.extend(f"<li>{esc(r.get('rule'))}</li>" for r in rec.get("rules", []))
        body.append("</ul>")

    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{esc(concept)}</title><style>{CSS}</style></head>"
            f'<body><div class="card">{"".join(body)}</div></body></html>')
    out = os.path.join(d, f"{slug}.card.html")
    open(out, "w", encoding="utf-8").write(page)
    print(json.dumps({"ok": True, "card": out, "outcome": outcome}))


if __name__ == "__main__":
    main()
