"""Render a learner card from a run record.

Reads <slug>.json (written by build_record.py) and writes <slug>.card.html:
one standalone page with the analogy, how it lines up (no rule ids), where it
breaks, and a label from the test result. Scores never appear on the card.
If the matched machine has a drawing in ../drawings/, it is embedded.

Usage: python render_card.py <analogy-runs dir> <slug>
"""
import html
import json
import os
import re
import sys

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAWINGS = os.path.join(PLUGIN, "drawings")

CSS = """
:root{--bg:#f6f5f1;--card:#fff;--text:#1f1e1c;--muted:#6b6a65;--border:rgba(0,0,0,.12);
--ok-bg:#eaf3de;--ok:#3b6d11;--warn-bg:#faeeda;--warn:#854f0b;--info-bg:#eeedfe;--info:#3c3489;
--node:#eeedfe;--node-line:#534ab7;--node-text:#3c3489;--base:#e1f5ee;--base-line:#0f6e56;--base-text:#085041;
--bad:#fcebeb;--bad-line:#a32d2d;--bad-text:#791f1f;--back:#1d9e75}
@media (prefers-color-scheme:dark){:root{--bg:#1c1c1a;--card:#262624;--text:#ecebe6;--muted:#a3a29c;--border:rgba(255,255,255,.14);
--ok-bg:#27500a;--ok:#c0dd97;--warn-bg:#633806;--warn:#fac775;--info-bg:#3c3489;--info:#cecbf6;
--node:#3c3489;--node-line:#afa9ec;--node-text:#eeedfe;--base:#085041;--base-line:#5dcaa5;--base-text:#e1f5ee;
--bad:#791f1f;--bad-line:#f09595;--bad-text:#fcebeb;--back:#5dcaa5}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;padding:16px}
.card{max-width:640px;margin:0 auto;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px}
.top{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.concept{color:var(--muted);font-size:14px;margin:0}
.pill{font-size:12px;padding:2px 10px;border-radius:8px}
.ok{background:var(--ok-bg);color:var(--ok)}.rough{background:var(--warn-bg);color:var(--warn)}.info{background:var(--info-bg);color:var(--info)}
h1{font-size:21px;font-weight:600;margin:6px 0 10px}h2{font-size:15px;font-weight:600;margin:20px 0 6px}
h3{font-size:15px;font-weight:600;margin:26px 0 2px}
.story{margin:0 0 6px}.grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);font-size:14px;border-top:1px solid var(--border)}
.grid div{padding:7px 10px 7px 0;border-bottom:1px solid var(--border)}.grid .head{color:var(--muted)}
.breaks{margin-top:16px;padding:10px 14px;border-radius:8px;background:var(--warn-bg);color:var(--warn);font-size:14px}
.breaks ul{margin:4px 0 0;padding-left:18px}.drawing{margin:10px 0 4px}
.note{color:var(--muted);font-size:13px}summary{cursor:pointer;margin-bottom:4px}
"""


def esc(s):
    return html.escape(str(s or ""), quote=True)


def clean_break(s):
    return re.sub(r"^\s*where this breaks:\s*", "", str(s or ""), flags=re.I).strip()


def find_drawing(machine):
    """drawings/index.json maps a drawing file to name fragments it serves."""
    try:
        index = json.load(open(os.path.join(DRAWINGS, "index.json"), encoding="utf-8"))
    except Exception:
        return None
    m = (machine or "").lower()
    for fname, keys in index.items():
        if any(k.lower() in m for k in keys):
            try:
                return open(os.path.join(DRAWINGS, fname), encoding="utf-8").read()
            except Exception:
                return None
    return None


def machine_block(c, rules, show_heading, show_drawing=True):
    rows = c.get("mapping", [])
    mapped = [r for r in rows if r.get("source")]
    breaks = [clean_break(r.get("break")) for r in rows if r.get("break") or not r.get("source")]
    breaks = [b for b in breaks if b]
    out = []
    if show_heading:
        out.append(f"<h3>{esc(c.get('definition') or c.get('machine'))}</h3>")
    out.append(f"<h1>Think of it as {esc(lower_first(c.get('machine')))}</h1>")
    drawing = find_drawing(c.get("machine")) if show_drawing else None
    if drawing:
        out.append(f'<div class="drawing">{drawing}</div>')
    if c.get("analogy"):
        story = re.split(r"\s*where this breaks:", c["analogy"], flags=re.I)[0]
        sents = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", story.strip())
        out.append(f'<p class="story">{esc(" ".join(sents[:2]))}</p>')
        if len(sents) > 2:
            out.append(f'<details><summary class="note">Read the whole story</summary>'
                       f'<p class="story">{esc(" ".join(sents[2:]))}</p></details>')
    if mapped:
        out.append('<h2>How it lines up</h2><div class="grid"><div class="head">In everyday life</div>'
                   f'<div class="head">In {esc(c.get("_concept"))}</div>')
        for r in mapped:
            target = r.get("plain") or r.get("target") or rules.get(r.get("rule"), {}).get("rule", "")
            out.append(f"<div>{esc(r.get('source'))}</div><div>{esc(target)}</div>")
        out.append("</div>")
    if breaks:
        items = "".join(f"<li>{esc(b)}</li>" for b in breaks)
        out.append(f'<div class="breaks"><strong>Where it breaks</strong><ul>{items}</ul></div>')
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

    body = []
    if outcome == "pass":
        pill = '<span class="pill ok">Tested: predicts well</span>'
    elif outcome == "rough_model":
        pill = '<span class="pill rough">Rough picture: check the breaks</span>'
    elif outcome == "side_by_side":
        pill = '<span class="pill info">People define this differently</span>'
    else:
        pill = '<span class="pill info">No everyday comparison fits well</span>'
    body.append(f'<div class="top"><p class="concept">{esc(concept)}</p>{pill}</div>')

    if outcome in ("pass", "rough_model"):
        picked = next((c for c in cands if c.get("id") == res.get("picked")), cands[0] if cands else None)
        if picked:
            body.append(machine_block(picked, rules, False))
    elif outcome == "side_by_side":
        body.append('<p class="note">Each definition gets its own picture. None is ranked above the others.</p>')
        # Drawings only when every candidate passes (rough_model is not a pass, as in build_record.py),
        # so the presentation favours none (SKILL.md step 6).
        all_pass = bool(cands) and all(per.get(c.get("id"), {}).get("outcome") == "pass" for c in cands)
        for c in cands:
            label = per.get(c.get("id"), {}).get("outcome")
            block = machine_block(c, rules, True, show_drawing=all_pass)
            if label == "rough_model":
                block += '<p class="note">Rough picture for this definition.</p>'
            if label in ("pass", "rough_model"):
                body.append(block)
            else:
                body.append(f"<h3>{esc(c.get('definition') or c.get('machine'))}</h3>"
                            '<p class="note">No everyday comparison held up for this definition.</p>')
    else:
        body.append(f"<h1>{esc(concept)}, in plain rules</h1>")
        body.append('<p class="note">We tested everyday comparisons and none predicted well enough, so here are the rules directly.</p><ul>')
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
