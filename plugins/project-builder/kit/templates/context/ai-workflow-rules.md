# AI Workflow Rules

## Approach

Build this project incrementally, using a spec-driven workflow that follows `context/kit/STEPS.md`.
The context files define what to build, how to build it, and where things stand. Always implement
against these files and the current unit's spec. Never infer or invent behaviour from scratch.

## Gates

- Stop at every GATE in STEPS.md. Show the result, list any assumptions, and wait for an explicit "OK".
- Never write code before the build plan is approved.
- Silence, a question or vague praise is not approval.

## Scoping Rules

- Work on one unit at a time.
- Implement exactly what the spec says. Make no extra features, refactors or "while I'm here" changes.
- Do not combine unrelated system boundaries in one step.
- Prefer small changes you can check over large speculative ones.

## When to Split Work

Split a step if it combines:

- [e.g. UI changes and backend or background changes]
- [e.g. Several unrelated routes, skills or pipeline stages]
- Behaviour that is not clearly defined in the context files

If a change cannot be checked from end to end quickly, its scope is too broad. Split it.

## Handling Missing Requirements

- Do not invent behaviour that the context files do not define.
- If a requirement is unclear, ask, then record the answer in the relevant context file before
  implementing.
- If a requirement is missing, add it under Open Questions in `progress-tracker.md` and stop at a GATE.

## When Stuck

1. Fix only the named problem (expected vs current). Change nothing else.
2. If the same problem fails twice, stop patching. Explain the likely cause and propose a change to the
   spec. Wait for approval, then rebuild from the corrected spec.
3. If a context file turns out to be wrong, fix that file first, with approval.

## Protected Files

Do not change these unless explicitly told to:

- [e.g. components/ui/*: generated UI library components]
- [e.g. evals/hidden/*: hidden test sets]
- [e.g. third-party library internals, generated files, lock files]

## Keeping Docs in Sync

Update the relevant context file whenever implementation changes:

- architecture or boundaries
- the storage model
- conventions or standards
- scope

## Before Moving to the Next Unit

1. The unit works from end to end within its defined scope.
2. The verify command in `architecture.md` passes. Report its real output.
3. Every item in the spec's "Verify when done" list is checked.
4. No invariant in `architecture.md` was broken.
5. `progress-tracker.md` shows the completed work and an updated **Resume here** line.
6. The user has approved at the unit's final GATE.
