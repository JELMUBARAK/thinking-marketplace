---
name: "decision-review"
description: "After the user acts on a decision, compare expected vs actual results and costs, compute the gap, extract a reusable lesson and save it to the decision journal. Use when the user says 'review my decision on...' or reports how a decision turned out."
---

# Decision review

The learning step of the thinking model. Use it when the user reports how a decision or experiment turned out, asks to review one, or when the journal shows a decision is due for review.

## Memory
The decision journal is managed by `journal.py` in the thinking-coach skill's `scripts` folder: run `python3 <this skill's base directory>/../thinking-coach/scripts/journal.py <command>`. Commands: `due`, `find WORDS`, `get ID`, `update ID` (JSON on stdin), `stats [TAG]`. If the script can't run in this environment, work from what the user tells you and give the result as a short block they can keep.

## Steps
1. Find the record: run `due` and `find` with the user's words. If one record matches, `get` it and confirm with the user. If none matches, collect the facts directly: the decision, the system type, what was expected (result, cost, time, probabilities) and what happened.
2. Ask only for what's missing: the actual result, the actual cost, and whether each saved prediction came true. Use one short multiple-choice question where possible.
3. Compute the gap: delta = expected - actual, for cost, time and outcome. Show the arithmetic. Say whether it's a better or a worse surprise.
4. Diagnose the gap, in this order:
   - Was the system misclassified (for example, treated as complicated when it was complex)?
   - Which audited assumption was wrong?
   - Was a probability too confident, or a cost underestimated? Run `stats` (and `stats TAG` for the decision's main tag) to check whether this is a consistent pattern in the user's record.
   - Did a trap play out: an incentive trap, a delayed effect, inside-the-train blindness, or the pre-mortem's top risk (did its warning signal appear in time)?
   - Or was it bad luck from a sound decision? Separate the decision quality from the outcome.
5. Write the lesson as one reusable pattern: "When [situation signals], expect [effect]; adjust [estimate or action] by [amount]."
6. Save it: `update ID` with `{"status":"reviewed","actual_result":...,"actual_cost":<number>,"predictions":[{"claim":...,"p":...,"came_true":true/false}],"diagnosis":...,"lesson":...}`. The script computes the delta.
7. Show the updated calibration from `stats` in 1-2 lines, with a caution if there are fewer than 5 reviewed decisions.
8. If the review shows the chosen solution should be re-audited (one of its saved re-audit triggers happened), say so and offer to run the thinking coach on it.

Keep it short: the gap table, the diagnosis in 2-4 bullets, the lesson line, the calibration update. Be honest, not harsh: the aim is to get better at estimating, not to assign blame.
