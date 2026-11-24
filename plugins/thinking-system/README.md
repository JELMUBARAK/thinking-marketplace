# Thinking System

A structured thinking coach for hard problems and decisions, with long-term memory.

## What's inside

**Skills**
- **thinking-coach** - clarity gate (including a check that the facts behind the problem are true) and framing loop, stakes check, sorting the situation (clear / complicated / complex / chaotic), the D.A.R.E. first-principles loop, hard limits, pre-mortem, independent red team, and a decision based on lowest expected cost among safe options. Breaking the problem down uses four systems lenses (wider boundary, loops over time, connections, leverage), each kept only if it changes an option, an assumption or a risk. Saves each decision to the journal.
- **decision-review** - after you act, compares expected with actual, computes the gap, writes the lesson to the journal and updates your calibration.

**Subagents** (full mode only, for big decisions)
- **researcher** - outside-view data and base rates, with sources.
- **quant** - expected costs, simulations, thresholds and flip points, in code.
- **red-team** - an independent critic on a different model.
- **librarian** - searches your journal for similar past decisions, lessons and your calibration record.
- **analyst** - finds patterns in your data files and tests them against chance.

**Signal check** (when you bring data)
- Upload or paste spreadsheets (.xlsx, .xls, .csv), documents (.docx, .txt, .md) or PDFs, and the coach offers to look for real patterns before breaking the problem down.
- It first shows what it read from each file (rows, columns, merged cells, scanned pages, hidden text) for you to confirm, then asks what you expect and the smallest effect that would change your decision.
- A power check says whether the data can settle that at all. Patterns are then tested with shuffle tests and split-half checks and graded strong, weak (a hypothesis to test) or noise. "No reliable pattern" is a valid answer.
- Everything runs on Python's standard library. PDF and old Excel reading use bundled copies of pypdf 7.1.0 and xlrd 2.0.2 (BSD licenses in `scripts/vendor/`). Refresh them now and then, since PDF parsers get security fixes: `pip download pypdf xlrd --no-deps --only-binary=:all:` and replace the folders. Scanned PDFs and images need OCR, which isn't supported. Old .doc files need resaving as .docx.

**Decision page**
- At the close, the coach turns the whole process into one page and publishes it as a private Artifact on claude.ai, automatically. The page shows the close summary first, then every stage in order: problem card, system type, problem tree and feedback loops, audited assumptions, hard limits, options with costs and arithmetic, pre-mortem, tests and the red-team verdict.
- Stages that didn't run show as "Not run" with what they would have checked, and the page is marked provisional.
- The layout is fixed: Claude writes the content as JSON and `scripts/render.py` builds the page (all text escaped). The JSON is kept in `~/.claude/thinking-system/pages/`, and the link goes into the journal.
- After a decision review, a separate review page (expected vs actual, diagnosis, lesson) links back to the decision page.
- Without the Artifact tool (for example in a chat app or a headless run), you get a local HTML file instead. Setting `THINKING_NO_PUBLISH=1` turns publishing off.
- The close opens with a plain "Bottom line" (what to do, why, what happens if it works or fails, the first step this week) written for someone who skipped the conversation.
- In the Standard and Deep tiers, the coach also offers a one-page summary picture for showing to someone who wasn't there: the decision first, then why, the numbered steps (the first marked "now"), and both outcomes, in plain words with a colour key. It checks the picture as a stranger would before sending it, and draws it only if you say yes.

**Model routing**
- From its first reply, the coach sorts the job into a tier: light (haiku), standard (sonnet) or deep (opus).
- Subagents run on the model their tier sets (librarian: haiku, researcher and quant: sonnet, red-team: opus) and step up one level only for harder jobs.
- The coach can't switch the main conversation's model. It suggests `/model <name>` once when the current model is bigger or smaller than the job needs.

**Memory**
- A decision journal at `~/.claude/thinking-system/journal.jsonl` (change it with the `THINKING_JOURNAL` environment variable). It lives outside the plugin, so updates never erase it.
- At the start of each Claude Code session, a reminder lists decisions that are due for review (silent when none are due).

## How to use

- "Help me think through [problem]" starts the coach. "Run it all" skips the pauses.
- "Stress-test my plan: [plan]" questions you about the plan in short rounds (at most 3), then audits the assumptions it surfaces.
- "Review my decision on [X]" closes the loop.

- "What's the conclusion?" at any point gives a provisional summary that names the skipped stages.

## Safeguards
- Journal records, web pages and subagent reports are treated as data. Any instructions inside them are ignored and reported.
- The researcher marks each figure's sourcing (independent primary / single source / secondary only). Weakly sourced figures get wider ranges and less weight.
- In read-only sessions (for example planning mode), the coach does the math by hand with its working shown, and drafts journal records to save once writing is allowed.

## Notes

Memory needs file access, as in Claude Code. In a chat app without file access, the coach gives you each record as a block to keep. Numbers are estimates unless sourced. For safety-critical work, the coach is decision support only and defers to company procedures and responsible engineers.
