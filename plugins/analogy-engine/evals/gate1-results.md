# Gate 1 results (20 Nov 2026)

Run by hand in a Claude Code session following `skills/transform/SKILL.md`, with fresh researcher and scorer subagents given the agent files verbatim (CLI 2.0.76 was too old for a real plugin-loader run). Records: `analogy-engine/analogy-runs/<concept>.json`.

**Verdict: Gate 1 passes.** 5 of 5 breakers meet their `cases.json` criteria as written (4 of 5 without caveats; democracy carries one). All 7 records pass `check.py`: no mapping rests on an unverified fact.

| Concept | Route | Outcome | Picked | Score | What-if | Rules | Case criteria |
|---|---|---|---|---|---|---|---|
| quantum superposition | analogy (layered) | rough model | P1 spinner arrows | 10.1 | 4/5 | 7 (heavy) | met |
| entropy | analogy (layered) | rough model | P2 penny party | 15.6 | 4/5 (gap W5) | 4 | met |
| recursion | simulate_first | simulation only | none (P1 disqualified) | 13.6 | 3/5 | | met |
| democracy | values | side by side | V1 club (minimalist) + 2 text-only | 15.0 | 5/5 | 4 | met, with caveat |
| p-value | simulate_first | pass (sim primary) | P1 loaded die | 15.6 | 5/5 | 4 | met |
| inflation | analogy | rough model | P1 token market | 12.9 | 5/5 | 5 (heavy) | met |
| immune system | analogy | rough model | P1 garden | 11.1 | 5/5 | 7 (heavy) | met (split not attempted) |

## What worked
- **The answer key came first** every time, from tier 1-3 sources (16-21 verified facts per concept).
- **The blind scorer caught real flaws** the orchestrator missed: the penny party with no volume row, headphones and blended drafts teaching misconceptions, a centimetre-shrinking ruler teaching "every price rises equally".
- **The routes behaved as intended**: recursion and p-value went to simulation, democracy to side by side, and quantum was kept to the settled layer with a "no everyday object does X" line.

## Problems found (fix before Phase 2)
1. **Scorers disagree on identical input.** The same recursion row (1.5 kg never reaches empty) was a match for one scorer and a D3 disqualifier for another. Entropy's split scored 13.2, then 17.3 and failed coverage, because the second scorer added a transition the first didn't. Each scorer rebuilds its own transition list (6 to 12 items), so the denominators move. Suggested fix: the researcher also outputs a frozen transition list and Why elements with the answer key; two scorers per round; a disagreement on any what-if or disqualifier is flagged rather than averaged.
2. **On the values route, the answer key favours one framework.** Democracy's what-ifs came mostly from V-Dem's regime classes, so the electoral/liberal definitions are favoured. My V1 patch passed by importing that distinction into the minimalist definition. Only one definition gets an object, which reads as a ranking. Suggested fix: per-definition what-ifs (2 shared, plus 1-2 per definition), and show either all definitions as objects or none.
3. **Rich models lose to minor-import penalties** (immune garden: 5/5 what-ifs, -6 in penalties). This is arguably right, since each import is a real false lesson, but four of the six picks are rough models. The pass bar of 14 may need checking against learner results (Gate 3) rather than tuned by hand.
4. **Partial-reason matches are unclear.** Several scorers asked whether the right direction with half the `because` counts. Add one rule.
5. **Splits were rarely worth trying.** Only entropy attempted one. Most split hypotheses reused objects that were already in the candidate or had been disqualified.

## Rule changes made during the run
- A gap (wrong answer from a missing row) is patchable; D3 now covers only the object's own wrong behaviour.
- Patch cap: at most 3 added rows and one added sentence. `object_rules` is recorded, and more than 4 is labelled heavy.
- A rough model is total >= 10 and What-if >= 3, either under 14 or with an open gap.
- Each part of a split is scored on what it claims, across all four lenses.
- Candidate ids: V1.. for values, K1.. for contested (D1-D3 are disqualifier codes).

## Cost
Each researcher used about 110-125k subagent tokens and took 5-7 min. Each scorer used about 80-95k tokens and took 1-3 min. The whole run (7 concepts, 21 agent calls) used roughly 2.4M subagent tokens.
