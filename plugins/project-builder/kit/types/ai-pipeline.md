# Type add-on: ai-pipeline

Use this for multi-stage AI pipelines, research engines and experiments (like analogy-engine runs).

## architecture.md: add
- **Stack rows:** Models (which model runs each stage), External APIs, Orchestrator, Stage scripts,
  Run records, Eval / scoring.
- **Pipeline stages:** a table of each stage with its input, output, model, and expected calls, time and cost.
- **Data:** where inputs come from, where run records go, and which data is **hidden** (test sets the
  pipeline must not see).
- **Budget:** maximum cost and time per run, and what to do if a run goes over.
- **Verify command:** run the eval on the **held-out test set** and report the score, the cost and the time,
  e.g. `python scripts/eval.py --out runs <cases>`. Treat one run as noisy; state the expected spread.
- **Example invariants:**
  - The orchestrator and the author never read hidden questions or the scorer's grids.
  - Nothing is tuned after a test-set run. Fixes are made on the practice set only.
  - Every run writes a record in one fixed format.
  - Keys come from environment variables and are never printed or committed.

## ui-context.md
- Use **Part B:** run-record schema, the summary shown to the user, and the card or report format.

## code-standards.md: add
- One stage, one script, with a clear input and output file.
- Make outputs reproducible: record the model, the prompt version and any seed in each run record.
- Python stdlib HTTP over SDKs where the sandbox (`python -I`) can't see installed packages.

## Spec "Verify when done": add
- [ ] Test-set score reported with cost and time
- [ ] Run record matches the schema
- [ ] No hidden data leaked into any stage that must not see it
