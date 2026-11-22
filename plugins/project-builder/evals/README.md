# project-builder evals

There are 7 single-turn cases. Each one targets a rule the skills must keep:

| Case | Rule |
|---|---|
| 01 | A fresh start stops at the Step 0 gate and creates nothing |
| 02 | "Skip planning" does not skip planning |
| 03 | A project with no UI gets the Output contract, and only one step is done |
| 04 | No code before the build plan, even when asked |
| 05 | Scope creep goes to Open Questions instead of into the code |
| 06 | A second failed fix leads to a spec change, not a third patch |
| 07 | Resume gives a one-line status and a gate, and does no work |

Each case runs in a fresh project folder in the system temp dir. The folder is set up from
`fixtures/` in the case's state (empty, planning at step 3 or 6, unit 01 approved, unit 01 stuck).

## Run

```sh
EVAL_CLI=/path/to/current/claude python run.py            # all cases
python run.py 05-scope-creep 06-stuck-twice              # some cases
```

Use a current CLI. The cost is roughly $0.10–0.40 per case on Sonnet, capped at $1 per case.

## Compare against a baseline

Copy the previous plugin version somewhere, then run both:

```sh
EVAL_OUT=base EVAL_PLUGIN=/path/to/old/project-builder python run.py
EVAL_OUT=new python run.py
```

## Grade

Open `<EVAL_OUT>/<case>.json`. Check `result`, `files_changed`, `branches` and `tools` against the case's
`pass` list in `cases.json`. Grade by hand: each case runs once, so treat one failure as a signal to look
closer, not as proof.

## Not covered

Multi-turn flows (a whole planning run), real web-app scaffolding, and pushing or merging.
