# AI Workflow Rules

## Approach

Build this project incrementally, using a spec-driven workflow that follows `context/kit/STEPS.md`.
Always implement against the context files and the current unit's spec.

## Gates

- Stop at every GATE in STEPS.md and wait for an explicit "OK".
- Never write code before the build plan is approved.

## Scoping Rules

- Work on one unit at a time. Implement exactly what the spec says.

## When to Split Work

Split a step if it combines:

- CLI parsing changes and rename logic changes
- Behaviour not defined in the context files

## Handling Missing Requirements

- If a requirement is missing, add it under Open Questions in `progress-tracker.md` and stop at a GATE.

## When Stuck

1. Fix only the named problem.
2. If the same problem fails twice, stop patching and propose a change to the spec. Wait for approval.
3. If a context file turns out to be wrong, fix that file first, with approval.

## Protected Files

- `tests/fixtures/*`

## Before Moving to the Next Unit

1. `pytest` passes. Report the real output.
2. Every "Verify when done" item is checked.
3. No invariant was broken.
4. `progress-tracker.md` is updated.
5. The user has approved.
