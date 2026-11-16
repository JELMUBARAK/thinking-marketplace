#!/usr/bin/env python3
"""Render a decision page or a review page from a JSON process record.

The thinking coach writes the whole process (every stage that ran) as one JSON
object; this script turns it into a single self-contained HTML page with a
fixed layout, ready to publish as an Artifact. All text is escaped, so content
from journals, web pages or files can't inject markup.

Usage:
  render.py FILE.json [--out OUT.html] [--local] [--no-archive]
  render.py -  ...                     (read the JSON from stdin)

  --out PATH     where to write the HTML (default: <journal dir>/pages/<name>.html)
  --local        write a full standalone document (doctype, html, body) to open
                 in a browser; without it the file is shaped for Artifact publish,
                 which adds that skeleton itself
  --no-archive   don't keep a copy of the JSON in <journal dir>/pages/

Prints the HTML path, the archived JSON path, and "publish: off" when the
THINKING_NO_PUBLISH environment variable is set (the caller must not publish).
The JSON format is described in ../references/decision-page.md.
"""
import html
import json
import os
import re
import sys
from datetime import date

JOURNAL = os.path.expanduser(
    os.environ.get("THINKING_JOURNAL", "~/.claude/thinking-system/journal.jsonl")
)
PAGES = os.path.join(os.path.dirname(JOURNAL), "pages")

# (key, code, title, required, what it would have checked)
DECISION_STAGES = [
    ("clarity", "pre", "Problem clarity", True, "Scores the problem on goal, gap, decision, limits, root and premise."),
    ("framing", "pre", "Framing", False, "Ladders to the real goal and reframes the problem three ways."),
    ("stress_test", "pre", "Stress test", False, "Maps the plan's choices and surfaces stated and unstated assumptions."),
    ("stakes", "pre", "Stakes check", True, "Sizes the decision, its reversibility and who else must agree."),
    ("sort", "0", "System type", True, "Sorts the situation as clear, complicated, complex or chaotic."),
    ("signals", "0b", "Signal check", False, "Tests patterns in the user's data against chance."),
    ("decompose", "1", "Decompose", True, "Breaks the problem into parts, cost branches and feedback loops."),
    ("audit", "2", "Audit", True, "Tests hidden assumptions and runs the trap checks."),
    ("limits", "2b", "Hard limits", True, "Lists what must never be traded for money and rules out ruin."),
    ("recombine", "3", "Options", True, "Builds 3 structurally different options with costs, P and a flip point."),
    ("premortem", "3b", "Pre-mortem", True, "Imagines the leading option failed and finds warning signals."),
    ("experiment", "4", "Tests and decision rule", True, "Designs the cheapest test per option and the rule for choosing."),
    ("redteam", "4b", "Red team", True, "An independent critic rechecks the numbers and attacks assumptions."),
]
REVIEW_STAGES = [
    ("gap", "1", "Expected vs actual", True, "Compares expected and actual result, cost and time."),
    ("diagnosis", "2", "Diagnosis", True, "Separates a wrong assumption or misclassification from bad luck."),
    ("lesson", "3", "Lesson", True, "Writes one reusable pattern for next time."),
    ("calibration", "4", "Calibration", False, "Updates the user's cost bias and probability calibration."),
    ("reaudit", "5", "Re-audit", False, "Checks whether a saved re-audit trigger fired."),
]
DECISION_SUMMARY = [
    ("decision", "Decision or next test"),
    ("system_type", "System type"),
    ("expected_cost", "Expected cost range"),
    ("key_assumption", "Assumption it depends on most"),
    ("hard_limits", "Hard limits"),
    ("top_risk", "Top pre-mortem risk"),
    ("warning_signal", "Its warning signal"),
    ("red_team", "Red-team verdict"),
    ("resort_signal", "Signal to re-sort"),
    ("review_date", "Review date"),
    ("reaudit_triggers", "Re-audit if"),
]
REVIEW_SUMMARY = [
    ("decision", "Decision reviewed"),
    ("outcome", "What happened"),
    ("cost_gap", "Cost gap"),
    ("decision_quality", "Decision quality vs luck"),
    ("lesson", "Lesson"),
]
STATUS_LABEL = {"done": "Done", "not_run": "Not run", "not_applicable": "Not needed"}
TONES = {"info", "ok", "warn", "critical"}


def esc(v):
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        return "; ".join(esc(x) for x in v)
    if isinstance(v, dict):
        return esc(json.dumps(v, ensure_ascii=False))
    return html.escape(str(v), quote=True)


def safe_url(u):
    u = str(u or "").strip()
    return html.escape(u, quote=True) if re.match(r"^https://[^\s\"'<>]+$", u) else ""


def render_tree(node):
    if isinstance(node, str):
        return f"<li><span>{esc(node)}</span></li>"
    if not isinstance(node, dict):
        return f"<li><span>{esc(node)}</span></li>"
    note = f' <em>{esc(node["note"])}</em>' if node.get("note") else ""
    kids = node.get("children") or []
    inner = "<ul>" + "".join(render_tree(k) for k in kids) + "</ul>" if kids else ""
    return f"<li><span>{esc(node.get('label'))}</span>{note}{inner}</li>"


def render_block(b):
    if isinstance(b, str):
        return f"<p>{esc(b)}</p>"
    if not isinstance(b, dict):
        return f"<p>{esc(b)}</p>"
    t = b.get("type", "text")
    cap = f'<p class="cap">{esc(b["caption"])}</p>' if b.get("caption") else ""
    if t == "text":
        return f"<p>{esc(b.get('text'))}</p>"
    if t == "list":
        tag = "ol" if b.get("ordered") else "ul"
        return cap + f"<{tag} class=\"items\">" + "".join(f"<li>{esc(i)}</li>" for i in b.get("items", [])) + f"</{tag}>"
    if t == "kv":
        items = b.get("items") or []
        pairs = items.items() if isinstance(items, dict) else [
            (p[0], p[1]) if isinstance(p, (list, tuple)) and len(p) == 2 else ("", p) for p in items
        ]
        rows = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in pairs)
        return cap + f'<dl class="kv">{rows}</dl>'
    if t == "table":
        cols = b.get("columns") or []
        head = "<tr>" + "".join(f"<th>{esc(c)}</th>" for c in cols) + "</tr>" if cols else ""
        body = "".join(
            "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in (r if isinstance(r, list) else [r])) + "</tr>"
            for r in b.get("rows", [])
        )
        return cap + f'<div class="scroll"><table><thead>{head}</thead><tbody>{body}</tbody></table></div>'
    if t == "tree":
        return cap + f'<ul class="tree">{render_tree(b.get("root", ""))}</ul>'
    if t == "loops":
        out = []
        for i in b.get("items", []):
            i = i if isinstance(i, dict) else {"text": i}
            kind = str(i.get("kind", "")).lower()
            chip = {"reinforcing": ("R", "Reinforcing"), "balancing": ("B", "Balancing")}.get(kind, ("?", "Unmarked"))
            out.append(f'<li><span class="loop" title="{chip[1]}">{chip[0]}</span><span>{esc(i.get("text"))}</span></li>')
        return cap + '<ul class="loops">' + "".join(out) + "</ul>"
    if t == "callout":
        tone = b.get("tone") if b.get("tone") in TONES else "info"
        return f'<div class="callout {tone}">{esc(b.get("text"))}</div>'
    if t == "math":
        return cap + f'<pre class="math">{esc(b.get("text"))}</pre>'
    return cap + f'<pre class="math">{esc(json.dumps(b, ensure_ascii=False, indent=1))}</pre>'


def render_stage(code, title, st, would):
    status = st.get("status", "done") if isinstance(st, dict) else "done"
    status = status if status in STATUS_LABEL else "done"
    note = st.get("note") if isinstance(st, dict) else None
    blocks = st.get("blocks", []) if isinstance(st, dict) else [st]
    sid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    body = ""
    if status == "not_run":
        body = f'<p class="would">Would have checked: {esc(would)}</p>'
        if note:
            body += f"<p>{esc(note)}</p>"
    else:
        if note:
            body += f'<p class="note">{esc(note)}</p>'
        body += "".join(render_block(b) for b in blocks)
    return (
        f'<section class="stage s-{status}" id="{sid}"><header>'
        f'<span class="code">{esc(code)}</span><h2>{esc(title)}</h2>'
        f'<span class="pill p-{status}">{STATUS_LABEL[status]}</span></header>'
        f'<div class="body">{body}</div></section>'
    ), (sid, code, title, status)


def build(data):
    if not isinstance(data, dict):
        sys.exit("error: expected a JSON object")
    kind = data.get("page", "decision")
    if kind not in ("decision", "review"):
        sys.exit('error: "page" must be "decision" or "review"')
    title = str(data.get("title") or "").strip()
    if not title:
        sys.exit('error: "title" is required')
    stages_def = DECISION_STAGES if kind == "decision" else REVIEW_STAGES
    summary_def = DECISION_SUMMARY if kind == "decision" else REVIEW_SUMMARY
    stages = data.get("stages") or {}
    if not isinstance(stages, dict):
        sys.exit('error: "stages" must be an object keyed by stage name')
    provisional = data.get("status") == "provisional"

    sections, nav, not_run = [], [], []
    for key, code, stitle, required, would in stages_def:
        st = stages.get(key)
        if st is None:
            if not required:
                continue
            st = {"status": "not_run"}
        html_s, meta = render_stage(code, stitle, st, would)
        sections.append(html_s)
        nav.append(meta)
        if meta[3] == "not_run":
            not_run.append(stitle)
    known = {k for k, *_ in stages_def}
    for key, st in stages.items():
        if key not in known:
            html_s, meta = render_stage("+", key.replace("_", " ").capitalize(), st, "")
            sections.append(html_s)
            nav.append(meta)
    if not_run and kind == "decision":
        provisional = True

    summ = data.get("summary") or {}
    lead_key = "decision"
    lead = summ.get(lead_key)
    rows = "".join(
        f"<div><dt>{label}</dt><dd>{esc(summ.get(k))}</dd></div>"
        for k, label in summary_def if k != lead_key and summ.get(k) not in (None, "", [])
    )
    eyebrow = "Decision record" if kind == "decision" else "Decision review"
    meta_bits = [b for b in (data.get("date"), data.get("journal_id") and f"journal {data['journal_id']}", data.get("tier")) if b]
    status_pill = (
        '<span class="pill p-prov">Provisional</span>' if provisional
        else '<span class="pill p-final">Final</span>'
    ) if kind == "decision" else '<span class="pill p-final">Reviewed</span>'
    banner = ""
    if provisional and kind == "decision":
        listed = ", ".join(not_run) if not_run else "some stages"
        banner = f'<div class="callout warn">Provisional. Not run: {esc(listed)}. Each is listed below with what it would have checked. No results were assumed for them.</div>'
    link = ""
    dec_url = safe_url(data.get("decision_url"))
    if kind == "review" and dec_url:
        link = f'<p class="back"><a href="{dec_url}" target="_blank" rel="noopener">Open the original decision page</a></p>'
    review_url = safe_url(data.get("review_url"))
    if kind == "decision" and review_url:
        link = f'<p class="back"><a href="{review_url}" target="_blank" rel="noopener">Open the review of this decision</a></p>'
    navhtml = "".join(
        f'<a class="n-{st}" href="#{sid}"><span>{esc(code)}</span>{esc(t)}</a>' for sid, code, t, st in nav
    )
    lead_html = f'<p class="lead">{esc(lead)}</p>' if lead else ""
    footer = (
        "Numbers are estimates unless a source is named. A single outcome can reflect luck: "
        "judge the decision by how it was made as well as how it turned out."
    )
    return f"""<title>{esc(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>
/* Layout: a single-column engineering decision record; summary sheet first, then the stage log in process order. */
:root {{
  --bg: #f6f8f8; --surface: #ffffff; --fg: #17262a; --muted: #5b6d72; --line: #d5dfe1;
  --accent: #0b5f6b; --accent-soft: #e2eff0;
  --ok: #1f7a4d; --ok-soft: #e3f3ea; --warn: #9a5b00; --warn-soft: #fbf0dc; --crit: #b42318; --crit-soft: #fbe6e3;
  --f-display: "IBM Plex Sans Condensed", "Arial Narrow", system-ui, sans-serif;
  --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0f1719; --surface: #152124; --fg: #e3ecee; --muted: #93a6ab; --line: #26363a;
  --accent: #5cc3cf; --accent-soft: #173439;
  --ok: #5fcf95; --ok-soft: #15301f; --warn: #f0b354; --warn-soft: #33270f; --crit: #f2867a; --crit-soft: #3a1a17;
  color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #0f1719; --surface: #152124; --fg: #e3ecee; --muted: #93a6ab; --line: #26363a;
  --accent: #5cc3cf; --accent-soft: #173439;
  --ok: #5fcf95; --ok-soft: #15301f; --warn: #f0b354; --warn-soft: #33270f; --crit: #f2867a; --crit-soft: #3a1a17;
  color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.6 var(--f-body); }}
.wrap {{ max-width: 860px; margin: 0 auto; padding-block: 32px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; grid-template-columns: minmax(0, 1fr); gap: 28px; }}
.eyebrow {{ font: 500 12px/1.4 var(--f-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
  display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: center; }}
h1 {{ font: 600 clamp(28px, 5vw, 40px)/1.15 var(--f-display); margin: 8px 0 0; text-wrap: balance; }}
.sheet {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 20px 22px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 16px; }}
.sheet .label {{ font: 500 12px/1.4 var(--f-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }}
.lead {{ font: 600 20px/1.4 var(--f-display); margin: 0; }}
dl {{ margin: 0; }}
.facts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px 24px; }}
.facts div, .kv div {{ min-width: 0; }}
dt {{ font: 500 12px/1.4 var(--f-mono); color: var(--muted); letter-spacing: .04em; }}
dd {{ margin: 2px 0 0; overflow-wrap: anywhere; }}
nav.stages {{ display: flex; flex-wrap: wrap; gap: 6px; }}
nav.stages a {{ display: inline-flex; gap: 6px; align-items: baseline; padding: 4px 10px; border-radius: 999px;
  border: 1px solid var(--line); color: var(--fg); text-decoration: none; font-size: 13px; background: var(--surface); }}
nav.stages a span {{ font: 500 11px var(--f-mono); color: var(--muted); }}
nav.stages a.n-not_run {{ border-style: dashed; color: var(--muted); background: transparent; }}
nav.stages a.n-not_applicable {{ color: var(--muted); background: transparent; }}
nav.stages a:focus-visible, a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.log {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 14px; }}
.stage {{ border-top: 1px solid var(--line); padding-top: 14px; display: grid; gap: 10px; min-width: 0; }}
.stage header {{ display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }}
.code {{ font: 500 13px var(--f-mono); color: var(--accent); min-width: 2.2em; }}
h2 {{ font: 600 21px/1.25 var(--f-display); margin: 0; flex: 1; text-wrap: balance; }}
.body {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; min-width: 0; padding-left: calc(2.2em + 12px); }}
.body p {{ margin: 0; max-width: 68ch; }}
.note {{ color: var(--muted); }}
.would {{ color: var(--muted); font-style: italic; }}
.s-not_run h2, .s-not_applicable h2 {{ color: var(--muted); }}
.pill {{ font: 500 11px/1 var(--f-mono); letter-spacing: .06em; text-transform: uppercase; padding: 5px 8px; border-radius: 4px; white-space: nowrap; }}
.p-done {{ background: var(--accent-soft); color: var(--accent); }}
.p-not_run {{ background: var(--warn-soft); color: var(--warn); }}
.p-not_applicable {{ background: transparent; color: var(--muted); border: 1px solid var(--line); }}
.p-final {{ background: var(--ok-soft); color: var(--ok); }}
.p-prov {{ background: var(--warn-soft); color: var(--warn); }}
.cap {{ font: 500 12px var(--f-mono); color: var(--muted); }}
ul.items, ol.items {{ margin: 0; padding-left: 1.2em; display: grid; gap: 4px; }}
.kv {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px 20px; }}
.scroll {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 4px; background: var(--surface); }}
table {{ border-collapse: collapse; width: 100%; font-size: 14px; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font: 500 12px var(--f-mono); color: var(--muted); letter-spacing: .04em; white-space: nowrap; }}
tbody tr:last-child td {{ border-bottom: 0; }}
pre.math {{ margin: 0; font: 13px/1.55 var(--f-mono); background: var(--surface); border: 1px solid var(--line);
  border-radius: 4px; padding: 10px 12px; overflow-x: auto; white-space: pre; font-variant-numeric: tabular-nums; }}
ul.tree, ul.tree ul {{ list-style: none; margin: 0; padding-left: 18px; }}
ul.tree {{ padding-left: 0; }}
ul.tree li {{ position: relative; padding-left: 14px; }}
ul.tree ul li::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; border-left: 1px solid var(--line); }}
ul.tree ul li::after {{ content: ""; position: absolute; left: 0; top: .8em; width: 9px; border-top: 1px solid var(--line); }}
ul.tree ul li:last-child::before {{ bottom: calc(100% - .8em); }}
ul.tree > li {{ padding-left: 0; font-weight: 600; }}
ul.tree ul {{ font-weight: 400; }}
ul.tree em {{ color: var(--muted); font-size: 13px; }}
ul.loops {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }}
ul.loops li {{ display: flex; gap: 10px; align-items: baseline; }}
.loop {{ font: 600 12px var(--f-mono); width: 22px; height: 22px; flex: none; display: inline-grid; place-items: center;
  border-radius: 50%; border: 1px solid var(--accent); color: var(--accent); }}
.callout {{ padding: 10px 14px; border-radius: 4px; border: 1px solid var(--line); background: var(--surface); max-width: 68ch; }}
.callout.ok {{ background: var(--ok-soft); border-color: transparent; }}
.callout.warn {{ background: var(--warn-soft); border-color: transparent; }}
.callout.critical {{ background: var(--crit-soft); border-color: transparent; color: var(--fg); }}
.callout.info {{ background: var(--accent-soft); border-color: transparent; }}
.back a {{ color: var(--accent); }}
footer {{ color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); padding-top: 14px; max-width: 68ch; }}
@media (max-width: 560px) {{ .body {{ padding-left: 0; }} .sheet {{ padding: 16px; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto !important; }} }}
</style>
<div class="wrap">
<header>
  <div class="eyebrow"><span>{eyebrow}</span>{"".join(f"<span>{esc(b)}</span>" for b in meta_bits)}{status_pill}</div>
  <h1>{esc(title)}</h1>
</header>
{banner}
<section class="sheet" aria-label="Summary">
  <span class="label">{"Close" if kind == "decision" else "Summary"}</span>
  {lead_html}
  <dl class="facts">{rows}</dl>
  {link}
</section>
<nav class="stages" aria-label="Stages">{navhtml}</nav>
<div class="log">
{"".join(sections)}
</div>
<footer>{footer}</footer>
</div>
"""


def page_name(data):
    base = data.get("journal_id") or re.sub(r"[^a-z0-9]+", "-", str(data.get("title", "decision")).lower()).strip("-")[:40]
    base = re.sub(r"[^A-Za-z0-9_.-]+", "-", base) or "decision"
    return base + ("-review" if data.get("page") == "review" else "")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    src, out, local, archive = args[0], None, False, True
    i = 1
    while i < len(args):
        a = args[i]
        if a == "--out" and i + 1 < len(args):
            out, i = args[i + 1], i + 2
            continue
        if a == "--local":
            local = True
        elif a == "--no-archive":
            archive = False
        else:
            sys.exit(f"error: unknown option {a}")
        i += 1
    try:
        raw = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"error: could not read JSON: {e}")
    data.setdefault("date", date.today().isoformat())
    page = build(data)
    if local:
        page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                '<style>body{margin:0}</style></head><body>\n' + page + "</body></html>\n")
    name = page_name(data)
    out = out or os.path.join(PAGES, name + ".html")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"html: {os.path.abspath(out)}")
    if archive:
        os.makedirs(PAGES, exist_ok=True)
        jpath = os.path.abspath(os.path.join(PAGES, name + ".json"))
        with open(jpath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print(f"process_file: {jpath}")
    if os.environ.get("THINKING_NO_PUBLISH"):
        print("publish: off")


if __name__ == "__main__":
    main()
