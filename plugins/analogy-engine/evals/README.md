# analogy-engine evals

Seven concepts: five that broke v1 (quantum superposition, entropy, recursion, democracy, p-value) and two regression checks (inflation, immune system). `cases.json` says what "handled right" means for each.

## How a run is judged (v0.4, rule tables with practice and test sets)
- The researcher writes a rule table that covers every verified fact, plus 16 hidden what-ifs split into a practice set and a test set. The orchestrator never sees either.
- The orchestrator matches the rules to a machine from `references/machines.md`.
- Practice run: the scorer names the weak rules; the orchestrator fixes them once.
- Test run: the scorer tests the fixed analogy on the test set. **Pass** at 7/8 with no flip and no gap. Nothing is fixed after this.
- `check.py <records>` checks the mechanical rules: every mapping row cites a verified fact, every rule is mapped or stated as a break, and the agent-call budget is kept.

## History
- `gate1-results.md`: first full run (v0.1). Expensive, and the scorers disagreed.
- `lean-vs-baseline.md`: lean pipeline (v0.2). Cheaper, but candidates were written with the answer key in view.
- `rule-table-test.md`: hidden key plus rule tables (v0.3). 72% on unseen what-ifs, against 48% for the earlier analogies. Fixes tuned to one question set didn't carry over to a fresh set, which led to the practice/test split (v0.4).

Use a current Claude CLI for real plugin runs; the `claude` on PATH here was 2.0.76 on 20 Nov 2026.
