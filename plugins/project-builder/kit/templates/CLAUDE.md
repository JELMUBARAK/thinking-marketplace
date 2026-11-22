# [Project Name]

Project type: [web-app | claude-plugin | ai-pipeline | python-tool]
Built with project-kit. Follow `context/kit/STEPS.md` (version [x.y]) exactly, including every GATE.
Prompts: `context/kit/generate-files.md`. Type add-on: `context/kit/[type].md`.

## Application Building Context

Read the following files in order before implementing anything or making any architectural decision:

1. `context/project-overview.md`: product definition, goals, features and scope
2. `context/architecture.md`: stack, boundaries, storage, access, verify command and invariants
3. `context/ui-context.md`: visual language, or the output contract for projects without a UI
4. `context/code-standards.md`: implementation rules and conventions
5. `context/ai-workflow-rules.md`: workflow, scoping, gates and the "when stuck" rule
6. `context/progress-tracker.md`: current phase, completed work, open questions and **Resume here**
7. `context/specs/00-build-plan.md`: the ordered list of units

Background, read when you need to know why something was decided: `context/_planning-notes.md`
(the answers from the idea conversation).

## Rules

- Work on one unit at a time, from its spec in `context/specs/`. Do not go beyond the spec.
- Stop at every GATE and wait for an explicit "OK".
- Update `context/progress-tracker.md` after every meaningful implementation change.
- If implementation changes the architecture, scope or standards, update the relevant context file
  before continuing.
- Before calling a unit done, run the verify command from `architecture.md`.
