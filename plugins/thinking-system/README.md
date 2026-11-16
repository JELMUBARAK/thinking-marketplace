# Thinking System

A structured thinking coach for hard problems and decisions, with long-term memory.

## What's inside

**Skills**
- **thinking-coach** - clarity gate (including a check that the facts behind the problem are true) and framing loop, stakes check, sorting the situation (clear / complicated / complex / chaotic), the D.A.R.E. first-principles loop, hard limits, pre-mortem, independent red team, and a decision based on lowest expected cost among safe options. Saves each decision to the journal.
- **decision-review** - after you act, compares expected with actual, computes the gap, writes the lesson to the journal and updates your calibration.

**Subagents** (full mode only, for big decisions)
- **researcher** - outside-view data and base rates, with sources.
- **quant** - expected costs, simulations, thresholds and flip points, in code.
- **red-team** - an independent critic on a different model.
- **librarian** - searches your journal for similar past decisions, lessons and your calibration record.

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
