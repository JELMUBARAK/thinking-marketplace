# Scoring rubric (rule-table method)

The success measure is what-if accuracy on situations the analogy was not built for. The analogy is a machine matched to the concept's rule table; the scorer tests it on hidden what-ifs: a practice set of 8 (used to find weak rules) and a test set of 8 (the result, never used for fixing).

## Scorer rules
- D1: a mapping row cites no verified fact. D2: the machine, read naturally, teaches a listed misconception. Either disqualifies.
- Per what-if verdict: `match` (same direction and the whole `because` follows from the machine; half a reason is a `miss`), `flip` (a mapping row or the machine's natural behaviour gives the wrong answer), `gap` (no row covers it; a learner would guess), `miss` (covered, but no clear answer, or the right answer for the wrong reason), `told` (the right answer comes only from a stated break line or a row with no machine source: the text says the real rule, the machine doesn't produce it).
- For every flip, miss, gap or told, name the rule id (R..) it hinges on, or "none".
- At most 3 minor false imports, each with a fact id.
- When unsure, it is not a match.

## Decide (orchestrator, test set only)
| Result | Rule |
|---|---|
| **pass** | not disqualified, at least 7 of 8 match, no flip, no gap |
| **rough model** | not disqualified, at least 5 of 8, no flip. Shown with a "rough model" label and its breaks |
| **fail** | anything else -> simulation only (formal) or reject |

`told` never counts as a match. It is reported separately because a break line that teaches the fact still helps the learner, but the analogy did not predict it.

Values route: each definition's machine is scored only on what-ifs tagged neutral or with its definition; the same thresholds apply as fractions (80% pass, 60% rough).

## Practice fix (before the test run)
After the practice run, fix every rule it names, once: rewrite that rule's sentence and row so the machine itself produces the answer, or mark it as a break. A break line says in one line what the machine gets wrong; questions it answers will score `told`, not `match`, so turning a failure into a break never raises the score. A result of "none" means the rule table is missing a rule: add one only from a verified fact. Then run the test set once. Nothing is fixed after the test run, so the test score measures prediction on unseen situations. The orchestrator never sees the questions or grids, only counts and rule ids.

How the sets are made: the researcher writes 16 what-ifs to one file; `scripts/split.py` splits them at random within each kind (and definition), so neither set is easier by the author's choice. With 8 questions a score still moves by 1-2 from chance alone.

Why two sets: on 2026-11-20, fixes tuned to one set of 8 questions raised that set to 6 of 7 passing, while a fresh set stayed at 2 of 7.
