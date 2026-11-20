# Rule-table test (20 Nov 2026)

**Question:** do analogies built rule by rule from a machine library predict unseen situations better than analogies written freely and then patched?

**Method:** the same 7 concepts and the same checked facts. For each concept I wrote a 5-11 rule table from the verified facts, picked one machine from `references/machines.md`, and mapped every rule. One scorer call graded all 7 against 8 hidden what-ifs per concept that I never saw.

| Concept | Best earlier analogy (hidden test) | Rule-table analogy (hidden test) |
|---|---|---|
| recursion | 7/8 | **8/8** |
| entropy | 4/8 | 4/8 |
| inflation | 4/8 | **7/8**, but 1 flip |
| immune system | 4/8 | 5/8 |
| p-value | 1/8, flip | 4/8, 1 flip |
| quantum superposition | 3/8 | **6/8** |
| democracy (per definition) | 2/4, 2/4, 2/4 | 4/4, 3/4, 2/4 |
| **Total** | **29/60 (48%)** | **43/60 (72%)** |

**Cost:** 1 scorer call for all 7 concepts, instead of 7 scorer calls plus patch calls. The analogies cost no agent calls (written in this session from saved facts).

**Reading:**
- The rule-table method is clearly better on unseen situations (+24 points). It is still not good enough: only recursion passes the 7 of 8 bar.
- The two flips (inflation, p-value) each come from one wrong rule mapping. The scorer should return the **rule id** behind a flip or miss (never the scenario), so the one rule can be fixed without seeing the test.
- Entropy didn't improve. Its machine may be the wrong one, or its rule table may be missing a rule. A missing rule is a fact-sheet problem, not an analogy problem.
- Where the machine can't do something (quantum: chances that cancel), the mapping says so up front, as a stated break.

## One-rule fix (same day)
A helper read the scorer's grid and reported only which rules caused the failures, plus what was wrong with each rule in concept terms:
- inflation R10 (money-to-prices link stated as tight and universal);
- p-value R1 (the p-value depends on the assumed model), R3 (evenly spread only for continuous measures) and R6 (the general many-tests formula and its independence assumption).

Fixed those rows only and re-tested on all 8 hidden questions:

| Concept | Before fix | After fix |
|---|---|---|
| inflation | 7/8, 1 flip | **7/8, no flip: pass** |
| p-value | 4/8, 1 flip | **8/8: pass** |

Then the same fix for the other four (one helper call to find the rules, one re-test call for all four):

| Concept | Before fix | After fix |
|---|---|---|
| entropy | 4/8 | 6/8: rough model (fix round used up) |
| immune system | 5/8 | **7/8: pass** |
| quantum superposition | 6/8 | **8/8: pass** |
| democracy (electoral / liberal / deliberative) | 4/4, 3/4, 2/4 | **4/4, 4/4, 4/4: all pass, shown side by side** |

**After the fixes, on the questions they were tuned to: 6 of 7 pass.**

## Confirmation on fresh questions (same day)
8 brand-new hidden questions per concept, none repeating the earlier 13, used to test the final analogies:

| Concept | Tuned questions | Fresh questions |
|---|---|---|
| p-value | 8/8 | **8/8: pass** |
| quantum superposition | 8/8 | **7/8: pass** |
| inflation | 7/8 | 5/8: rough model |
| entropy | 6/8 | 5/8: rough model |
| immune system | 7/8 | 5/8: rough model |
| democracy (3 definitions) | 4/4 ×3 | 3/4 ×3: rough model |
| recursion | 8/8 | 4/8: fail (3 gaps with no rule behind them) |
| **Total** | | **43/60 (72%)** |

**Reading:**
- On fresh questions the rule-table method scores 72%, the same as before any fixes. The fixes didn't generalise: they mostly fitted the questions they were tuned to. **Confirmed passes: 2 of 7** (p-value, quantum).
- 8 questions per concept is too few to measure reliably: recursion went 8/8, then 7/8, then 4/8 on three different sets.
- Failures marked "none" mean the rule table is missing a rule. That is a research gap, not an analogy problem.

**Changes this points to:**
1. Keep two question sets: a **practice set** for fixing and a **test set** never used for fixing. Report only the test set.
2. Use 16 questions per concept (8 practice + 8 test) so one question set doesn't swing the result.
3. The researcher must make every verified fact appear in at least one rule (a mechanical check), so that no question lands on "none". Quantum's competing interpretations went in as a stated break, not a mapping, because they belong to the disputed layer. Caveat: the fix was steered by failures on these same 8 questions, so the after-fix scores are somewhat optimistic. A fresh set of questions would confirm them.
