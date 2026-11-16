# thinking-coach evals

18 single-turn test cases for the `thinking-coach` skill. Each case targets one rule in `SKILL.md` (false premise, out-of-reach goal, chaotic emergency, prompt injection, unsourced base rates, safety hard limits, journal review, and so on) and lists its pass criteria. Cases 15–18 are reworded holdouts, so a fix can be checked on prompts it wasn't written for.

## Run

```sh
EVAL_CLI=/path/to/current/claude python3 run.py            # all cases
EVAL_CLI=/path/to/current/claude python3 run.py 12-safety-deep 16-holdout-safety
```

- Use a current CLI. An old `claude` on PATH runs an old model and gives misleading results.
- Each case runs in a fresh session with a throwaway journal, so your real journal isn't touched. Subagents are off.
- The cost is roughly $0.10 per case on Sonnet, about $2 for the full set, capped at $1 per case.

## Compare against a baseline

Copy the previous plugin version somewhere, then run both:

```sh
EVAL_OUT=base  EVAL_PLUGIN=/path/to/old/thinking-system python3 run.py
EVAL_OUT=fixed python3 run.py
```

## Grade

Open each `<EVAL_OUT>/<case>.json`. Check `result` against the case's `pass` list in `cases.json`, and check `tools` to confirm any search or check the reply claims was actually made. Grade by hand: each case runs once, so treat one failure as a signal to look closer, not as proof.

## Not covered

Multi-turn behavior (analysis paralysis, a declined journal command, stage-by-stage flow, "run it all") and subagent use.
