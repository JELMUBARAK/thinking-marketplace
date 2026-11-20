# Lean pipeline vs baseline (20 Nov 2026)

Same 7 concepts. Baseline records: `analogy-runs/*.json`. Lean records: `analogy-runs/lean/*.json`. Both runs were hand-orchestrated with `general-purpose` subagents (the CLI was too old for the plugin loader). The lean runs used the mid-tier model.

## Cost and speed
| | Baseline | Lean |
|---|---|---|
| Researcher, per concept | 109-124k tokens, top model, 5-7 min | 74-84k tokens, mid-tier model, 1.3-2.6 min |
| Scorer, per call | 80-97k tokens, top model, 1-3 min | 64-66k tokens, mid-tier model, 14-27 s |
| Agent calls, total | 21 (7 research + 14 scoring) | 16 (7 research + 9 scoring) |
| Subagent tokens, total | ~2.4M | ~1.1M |
| Facts per concept | 20-23 | 10-14 |
| Page fetches per concept | 13-30+ | 5-8 |

Tokens fell by about half, the per-token price is lower (mid-tier model), and wall time fell 3-5×. The lean scorer still used about 64k tokens on a brief of only ~9k characters. Most of that is the fixed overhead of the `general-purpose` agent in this test (its system prompt and tool list are re-sent each turn). The plugin's own scorer has one tool and an inline brief, so it should be far cheaper, but that can't be measured until a current CLI runs the plugin.

## Verdicts: they do not agree
| Concept | Baseline | Lean |
|---|---|---|
| entropy | rough model (4/5) | **pass** (5/5) |
| quantum superposition | rough model (4/5, gap) | **pass** (5/5 after patch) |
| recursion | simulation only | **pass** (5/5; simulation primary) |
| democracy | side by side | side by side |
| p-value | pass | pass |
| inflation | rough model | **pass** (5/5) |
| immune system | rough model | **pass** (5/5) |

Agreement on 2 of 7, against the bar of 6 of 7 set beforehand. **The lean pipeline is not shown to be as accurate.** It is more lenient, and five things explain it:
1. **Candidates are written to the test.** The candidate writer (the orchestrator) sees the answer key and was told to give each what-if a row. A 5/5 then shows only that the mapping covers the questions, not that it predicts unseen ones. The baseline had the same leak, less explicitly.
2. **Looser match rule.** "Missing secondary detail is still a match" replaced the baseline's strict reading, under which half a reason counted as a miss plus a gap.
3. **No penalty for minor imports.** Up to 2 are allowed; the baseline subtracted a point for each.
4. **Easier what-ifs.** The lean researcher's what-ifs are shorter and closer to the facts (for example, "demand exceeds capacity, so prices rise").
5. **A different scorer model**, possibly more lenient. Not tested separately.

The disagreement problem persists at a smaller scale: on the democracy patch, a row the patch did not touch went from match to miss.

## What to fix before trusting either pipeline
- **Hide the answer key from the candidate writer.** The researcher writes 8 what-ifs. The orchestrator sees only facts, transitions and misconceptions. The scorer uses all 8. This is the single change that makes the score mean "predicts unseen situations", which is the app's success measure.
- **Restore the strict reading** of `because`, and keep the minor-import limit.
- **Check model leniency** once: score the same candidates with both models and compare.
- Then rerun the 7 concepts.
