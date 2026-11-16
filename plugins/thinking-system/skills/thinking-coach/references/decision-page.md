# Decision page

At the Close, the whole process becomes one page the user can keep and share. You write the content as JSON; `scripts/render.py` lays it out. Don't write the HTML yourself.

## Steps (after the journal `add` has returned the id)
1. Build the JSON below from what was established in this conversation. Use the user's real figures and your tagged estimates exactly as they were shown. Never fill a stage that didn't run.
2. Render it. Pass the JSON on stdin with a heredoc, as one command that starts with `python3` (no temp file, no `cat` pipe, no `cd` first):
   ```
   python3 "<skill dir>/scripts/render.py" - --out "<path>.html" <<'EOF'
   { ...the JSON... }
   EOF
   ```
   - Out path: `<scratchpad>/<journal id>.html` when your system prompt lists a scratchpad directory; otherwise leave `--out` off (it goes to the journal's `pages` folder).
   - If the journal was declined in this conversation, add `--no-archive`.
   - The script prints `html:` and `process_file:` paths. If it prints `publish: off`, don't publish: give the user the HTML path instead.
3. Publish it with the Artifact tool, automatically, without asking: `file_path` = the html path, `icon: "compass"`, and a one-sentence `description` (the decision and its review date). Then tell the user in one line: the page is private on claude.ai until they share it, with the link.
4. Save the link: `journal.py update ID` with `{"artifact_url": "<url>", "process_file": "<process_file path>"}`.
5. No Artifact tool here, or the publish fails: rerun with `--local` and give the user the local path to open in a browser. Say so in one line.

Leave out of the page anything the user asked to keep out of the journal, passwords, and personal identifiers of other people.

## Format
```json
{
  "page": "decision",
  "title": "Stuck pipe response",
  "journal_id": "20261116-stuck-pipe-response",
  "status": "final",
  "tier": "Deep - safety-related",
  "summary": {
    "decision": "Jar down for 4 hours, then spot acid if free length < 300 m",
    "system_type": "Complicated (80%)",
    "expected_cost": "$90k / $140k / $310k (low / likely / high)",
    "key_assumption": "Differential sticking, not pack-off",
    "hard_limits": ["No operation outside the well-control procedure", "Engineer signs off on acid"],
    "top_risk": "Pack-off misread as differential sticking (25%, my guess)",
    "warning_signal": "Circulation pressure rising while jarring",
    "red_team": "Fragile: ranking flips if P(free within 4 h) < 40%",
    "resort_signal": "Any gain in pit volume makes it chaotic",
    "review_date": "2026-12-15",
    "reaudit_triggers": ["New mud system", "Rig rate above $60k/day"]
  },
  "stages": {
    "clarity": {"note": "Score 5/6 (failed: Decision)", "blocks": [{"type": "text", "text": "Problem card: ..."}]},
    "sort": {"blocks": [{"type": "kv", "items": [["Type", "Complicated"], ["Confidence", "80%"]]}]},
    "decompose": {"blocks": [
      {"type": "tree", "root": {"label": "Stuck pipe", "children": [{"label": "Mechanism", "children": ["Differential", "Pack-off"]}, {"label": "Cost", "children": ["Short term: rig time", "Long term: sidetrack"]}]}},
      {"type": "loops", "items": [{"text": "Time stuck raises filter cake, which raises sticking force", "kind": "reinforcing"}]}
    ]},
    "audit": {"blocks": [{"type": "table", "columns": ["Assumption", "Class", "Before", "Evidence", "After"], "rows": [["Differential sticking", "unknown", "60%", "Pipe static 20 min", "75%"]]}]},
    "recombine": {"blocks": [
      {"type": "table", "columns": ["Option", "P success", "Cost low / likely / high", "Weak point"], "rows": [["A: Jar + acid", "65%", "$90k / $140k / $310k", "Acid permit time"]]},
      {"type": "math", "text": "E[A] = 0.65 x $120k + 0.35 x $180k = $78k + $63k = $141k"},
      {"type": "callout", "tone": "warn", "text": "Flip point: B wins if P(A succeeds) < 40%."}
    ]},
    "redteam": {"status": "not_run"}
  }
}
```

- `status`: `final`, or `provisional` when the close was provisional. The page is marked provisional automatically if any required stage is missing or `not_run`.
- `stages` keys, in process order: `clarity`, `framing` (optional), `stress_test` (optional), `stakes`, `sort`, `signals` (optional), `decompose`, `audit`, `limits`, `recombine`, `premortem`, `experiment`, `redteam`. A required stage you leave out shows as "Not run" with a line on what it would have checked. Use `{"status": "not_applicable", "note": "why"}` when a stage didn't apply (for example the red team on a small, easy-to-undo decision).
- Each stage: optional `status` (`done`, `not_run`, `not_applicable`), optional `note`, and `blocks`.
- Block types: `text` {text}, `list` {items, ordered?}, `kv` {items: [[key, value], ...]}, `table` {columns, rows}, `tree` {root: {label, note?, children}}, `loops` {items: [{text, kind: reinforcing|balancing}]}, `math` {text, for arithmetic}, `callout` {text, tone: info|ok|warn|critical}. Any block can carry a `caption`.
- Keep the title a short name (2-4 words), since it becomes the artifact's name.

## Review page (decision-review)
Same command, `"page": "review"`. Add `decision_url` (the decision's `artifact_url` from the journal) so the page links back. Summary keys: `decision`, `outcome`, `cost_gap`, `decision_quality`, `lesson`. Stage keys: `gap`, `diagnosis`, `lesson`, `calibration` (optional), `reaudit` (optional). Publish it as its own artifact (`icon: "checklist"`), then `journal.py update ID` with `{"review_artifact_url": "<url>"}`.
