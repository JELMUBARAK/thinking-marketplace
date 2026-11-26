# Prompts

These are the prompts used in STEPS.md, adapted from the Six-File Context System README. The original's code-standards prompt
was a copy of the overview prompt; it is rewritten here. Wherever a prompt says "the planning notes", give
it `context/_planning-notes.md` and the `context/kit/<type>.md` add-on.

---

## Idea conversation (Step 1)

```
I have an idea for a [web-app | claude-plugin | ai-pipeline | python-tool].
Here's the idea: [2-3 sentences]

Ask me questions one at a time until every item in the project-kit Readiness checklist
has a clear answer. Push back when an answer is vague or you see a problem.
Do not suggest code yet. When done, write the answers into context/_planning-notes.md.
```

## project-overview.md (Step 2)

```
From the planning notes, write context/project-overview.md using the template.
Include: one-paragraph overview, numbered measurable goals, a step-by-step core flow
with no gaps, features by category, in scope, a detailed out-of-scope list, and
success criteria that can be checked ("a user can X"). Plain Markdown, specific, no vague words.
```

## architecture.md (Step 3)

```
From the planning notes and context/kit/<type>.md, write context/architecture.md using the template.
Include: stack table (layer, technology, role), system boundaries with real folder names,
storage model, access model, secrets, the verify command, and at least 4 invariants
written as rules. Use tables where they help. Be specific.
```

## ui-context.md (Step 4)

Projects with a UI: design first, then document.

```
I'm building [app]. The look I want: [dark/light, technical/friendly, minimal/rich].
Generate a full colour palette with semantic token names and hex values, typography,
a border radius scale, and accent variants. Output Markdown tables for ui-context.md Part A.
Then I'll add the component library, layout patterns and icons.
```

Projects without a UI:

```
From the planning notes, fill in ui-context.md Part B (Output contract): every output,
who reads it, its exact format, and an example. Add the style rules and any schemas.
```

## code-standards.md (Step 5)

```
From the planning notes, architecture.md and context/kit/<type>.md, write context/code-standards.md
using the template. Include: general principles, rules for each language used,
framework or platform conventions, styling or output rules, interface rules (routes, skills,
CLI, stages), data and storage rules, error and logging rules, testing rules, and file
organization with real folder names. Write rules ("Do X", "Never Y"), not suggestions.
Every rule must be specific enough that a reviewer can tell whether code follows it.
```

## ai-workflow-rules.md (Step 6)

```
Write context/ai-workflow-rules.md using the template, for this project. Fill in the
split-work concerns and protected files for this project and type. Keep the gate rule and
the when-stuck rule exactly as written. Write direct, imperative rules.
```

## Build plan (Step 8)

```
Using project-overview.md and architecture.md, break the build into units for
context/specs/00-build-plan.md. Each unit: one visible result, one system boundary,
one session, dependencies installed just in time. Merge units that are always done together
and units with no result of their own. Order: dependencies first, security before features,
backend before UI wiring, shells before real data. Output the units table.
```

## Unit spec (Step 9a)

```
Write context/specs/NN-unit-name.md from _spec-template.md for: [unit from the build plan].
Use the context files. If anything is unclear, ask me before writing.
```

## Implement (Step 9b)

```
Read context/specs/NN-unit-name.md. Mark it in progress in progress-tracker.md.
Implement it exactly as specified. Do not go beyond the scope of this unit.
Then run the verify command and the checklist, and report each result.
```

## Correct (Step 10)

```
The [specific element] does not match the spec.
Expected: [what the spec says]. Current: [what was built].
Fix only this. Do not change anything else.
```

## Close (Step 9e)

```
Unit NN is verified. Mark it complete in progress-tracker.md, update Resume here,
and commit on feat/NN-unit-name.
```

## Resume (Step 11)

```
Read CLAUDE.md and resume.
```
