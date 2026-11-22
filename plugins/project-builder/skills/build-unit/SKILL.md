---
name: build-unit
description: Build the next unit of a project-kit project (spec, implement, verify, close), fix a unit that does not match its spec, or resume a project-kit project in a new session. Use when the user says next unit, build unit NN, resume the project, or reports that a unit is broken.
argument-hint: "[unit number | next | resume]"
---

# Build unit (STEPS 9–11)

The procedure is the project's own `context/kit/STEPS.md`, Steps 9–11. Follow it word for word. The spec template is `context/specs/_spec-template.md`, and the prompts are in `context/kit/generate-files.md`.

## First actions

1. Read `CLAUDE.md`, every file it lists, `context/kit/STEPS.md` and the type add-on in `context/kit/`. If `context/kit/` is missing, this is not a project-kit project: say so, point to `/project-builder:new-project`, and stop.
2. If the header of `context/specs/00-build-plan.md` has no approval date, planning is not finished: point to `/project-builder:new-project` and stop.
3. **New session, or the argument is `resume`:** this is Step 11. In one line, say where the project stands and what comes next, then stop at a GATE before doing any work.
4. Pick the unit. If the argument is a number, use that unit. Otherwise use the first unit in the build plan whose status is not `complete`. Its status tells you which stage you are at:

| Status | Stage |
|---|---|
| `not started` | 9a: write the spec → GATE |
| `spec written` | show the spec → GATE |
| `spec approved` | 9b implement, 9c verify → GATE (9d) |
| `in progress` / `verifying` | continue from `Resume here` → 9c → GATE (9d) |
| `complete` | move to the next unit |

Every time the stage changes, update the unit's status in the build plan and the `Resume here` line in the tracker.

## Gates

End your turn at every GATE with this block:
- what was done, with file links
- **Assumed:** (anything you decided without the user, or "nothing")
- **Next:** (the next stage). Reply OK to continue, or tell me what to change.

Approval is an explicit go-ahead such as OK, approved, yes or continue. Feedback means revise, then show the same gate again.

## 9a Spec

Fill in `_spec-template.md` as `context/specs/NN-unit-name.md`, using the unit's row in the build plan and the context files. If anything is unclear, ask before you write it. Mark the status `spec written`.

## 9b Implement

- Work on the branch `feat/NN-unit-name` (create it if it does not exist). Mark the status `in progress`.
- Build exactly what the spec says. Anything the spec does not cover goes under Open Questions in the tracker and is raised at the gate. That includes a requested extra, a nice-to-have or a refactor. It gets built only after the spec is updated and approved, usually as its own unit.
- Install only the packages listed in the spec's Dependencies.

## 9c Verify

- Run the verify command from `architecture.md`. Show its real result lines.
- Mark every "Verify when done" item as pass or fail, with evidence. A unit with a failing item is not done: fix it within scope, or report it.
- At the gate, tell the user exactly what to try themselves (9d). Mark the status `verifying`.

## 9e Close (after the user's OK)

- Mark the status `complete`.
- In the tracker, update Completed, `Resume here` and Session Notes (date, results, anything learned).
- Update every context file the unit changed.
- Commit on the branch with the message `Unit NN: <name>`. Push or merge only when the user asks.
- Offer the next unit.

## Step 10: wrong or stuck

- **The user reports a mismatch:** fix only that problem, comparing what was expected with what was built. Add `<date> fix attempt N: <problem>` to Session Notes.
- **A second failed attempt on the same problem** (count the attempts in Session Notes): stop patching. Explain the likely cause and propose a spec change, showing the exact lines that would change. Stop at a GATE, then rebuild from the corrected spec.
- **A context file turns out to be wrong:** propose the fix to that file, stop at a GATE, then continue.
