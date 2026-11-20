# Analogy engine

Turns an abstract concept into an everyday-machine analogy, states where it breaks, and tests it blind on hidden what-if questions.

## Install

```
claude plugin marketplace update thinking-tools
claude plugin install analogy-engine@thinking-tools
```

## Use in a chat

```
/analogy-engine:transform entropy
/analogy-engine:transform inflation sense: consumer prices
```

Files go to `analogy-runs/` in the folder you started Claude in. Open `<concept>.card.html` for the learner card: the analogy, how it lines up, and where it breaks, with no scores. To redraw a card from a record: `python scripts/render_card.py <folder> <concept>`.

Machines with an interactive drawing are listed in `drawings/index.json` (so far: chain of people). Add a drawing as an HTML fragment in `drawings/` and list the machine-name fragments it serves. About 3 agent calls and $0.80 per concept.

## Eval runs (scores that count)

A chat run reads that folder's `CLAUDE.md` and project memory, which can bias it. For scores you want to trust, use the eval script. It runs each concept in a clean temporary folder and copies the results into one folder:

```
python scripts/eval.py --out C:\path\to\analogy-runs entropy "immune system" p-value
```

Options: `--budget 4` (USD cap per concept), `--model sonnet`, `--one-at-a-time`, `--dry-run`. It prints a table of cost, outcome and test score. Check the records with `python evals/check.py <out folder>`.
