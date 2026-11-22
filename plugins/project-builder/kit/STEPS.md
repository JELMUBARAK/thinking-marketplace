# Project Build Steps

**Version:** 1.1
**Status:** APPROVED by the user on 2026-11-22 (v1.0). v1.1 is a mechanical change; see the change log.

This is the standard procedure for building any project: a web app, a Claude skill or plugin, an AI pipeline or research project, or a Python tool.
Claude follows these steps **in order and word for word**. It does not skip, merge or reorder steps unless
the user says so in plain words for that project.
**Every project follows every step, whatever its size. There is no shortened route.**

---

## The gate rule

Every step ends at a **GATE**. At a gate, Claude:

1. Shows what it produced (the file, or a short summary with a link to it).
2. Lists anything it assumed or could not decide.
3. **Stops and waits.** It moves on only after the user gives a plain "OK" or "approved".
   Feedback means: revise, then show it again at the same gate.

Silence, "looks interesting" or a question is **not** approval.

---

## Phase 1: Plan (no code)

### Step 0: Set up
- Agree on the project **name** and **type** (`web-app`, `claude-plugin`, `ai-pipeline` or `python-tool`).
  A project can combine types (for example a web app with an AI pipeline). If so, use every type that applies.
- Create the project folder and run `git init`.
- Copy from project-kit into the project:
  - `templates/CLAUDE.md` → project root (rename to `AGENTS.md` if the agent or framework uses that name)
  - `templates/context/` → `context/`
  - `STEPS.md`, `prompts/generate-files.md` and `types/<type>.md` (each type used) → `context/kit/`.
    This pins the project to this version of the standard, so it never depends on the kit changing later.
- Fill in the project name, type and STEPS version at the top of `CLAUDE.md`.
- From here on, "STEPS.md", "the prompts" and "the type add-on" mean the copies in `context/kit/`.
- Open `context/kit/<type>.md`. It lists what to add to each context file for that type.
- **GATE:** confirm name, type, folder.

### Step 1: Idea conversation
- Claude asks **one question at a time** (prompt: `context/kit/generate-files.md` → "Idea conversation").
- Claude pushes back on vague answers.
- Keep going until every item in the **Readiness checklist** (bottom of this file) has a clear answer.
- Claude writes the answers into `context/_planning-notes.md`. This file is the input for Steps 2–7.
  Keep it in the project permanently as the record of why things were decided.
- **GATE:** user confirms the planning notes are complete and correct.

### Step 2: `context/project-overview.md`
- Fill it from the planning notes using the template and the type add-on.
- Goals must be measurable. Success criteria must be checkable ("a user can X"), not "works well".
- **GATE**

### Step 3: `context/architecture.md`
- Must include: stack table, system boundaries (real folder names), storage model, access model, the
  **verify command**, and **at least 4 invariants**, written as rules.
- **GATE**

### Step 4: `context/ui-context.md`
- **Projects with a UI:** colour tokens, typography, radius, component library, layouts, icons.
- **Projects without a UI:** fill in the **Output contract** section instead (the exact format of the replies, cards,
  run records or CLI output).
- **GATE**

### Step 5: `context/code-standards.md`
- **GATE**

### Step 6: `context/ai-workflow-rules.md`
- **GATE**

### Step 7: `context/progress-tracker.md` and `CLAUDE.md`
- Tracker: fill in Current Phase, Current Goal and Resume here.
- `CLAUDE.md`: check that the file list matches the files that actually exist.
- **GATE**

### Step 8: Build plan, `context/specs/00-build-plan.md`
- Break the project into **units** (rules in the template). Order them by:
  1. dependencies first
  2. security before features
  3. backend before UI wiring
  4. shells before real data
  5. install packages only in the unit that first needs them
- Check each unit: does everything it depends on exist in an earlier unit? Are two neighbouring units always
  done together? If so, merge them.
- **GATE.** **No code is written before this gate is passed.**

---

## Phase 2: Build (one unit at a time)

### Step 9: Unit loop (repeat for every unit in the build plan)

**9a. Spec.** Write `context/specs/NN-unit-name.md` from `_spec-template.md`. If anything is unclear,
ask before writing.
**GATE**

**9b. Implement.** Mark the unit "In progress" in the tracker. Create the branch `feat/NN-unit-name`.
Build **exactly** what the spec says. Nothing more, nothing less, and no "while I'm here" changes.

**9c. Verify.** Run the **verify command** from `architecture.md`. Tick every item in the spec's
"Verify when done" list. Report each item as passed or failed, with the real output for any failure.

**9d. User check.** **GATE.** The user tries it and confirms.

**9e. Close.**
- Mark the unit Complete in the tracker and update Resume here.
- Update any context file the unit changed.
- Commit on the unit's own branch `feat/NN-unit-name`. **Push or merge only when the user asks.**

### Step 10: When something is wrong or Claude is stuck
1. Use the correction prompt. Name the element, then write `Expected: <spec>` and `Current: <built>`, and fix only that.
2. If the **same problem fails twice**, stop patching. Claude explains what it thinks the cause is and
   proposes a change to the spec. **GATE.** Then rebuild from the corrected spec.
3. If the problem shows that a context file is wrong (architecture, scope, standards), fix that file first. **GATE.**

### Step 11: Starting a new session
Claude reads `CLAUDE.md`, then all the context files, then the tracker's **Resume here** line. It states in one line where the project stands and what comes next. **GATE** before continuing.

---

## Changing this standard
- Change it only in project-kit. Increase the version number at the top and add a line to the change log below.
- Re-sync the plugin copy: run `sync.ps1` in project-kit.
- Projects already in progress keep the version they started with, unless the user says to upgrade.

## Readiness checklist (Step 1 must answer all of these)

**Product**
- What does it do, in one sentence?
- Who is the main user, and what do they need?
- What is the step-by-step flow, from start to the first useful result?
- What are the 3 most important features of version 1?
- What is explicitly out of scope?

**Technical**
- What is the full stack, and why was each part chosen?
- Where does data live (database, files, cache, run records)?
- How do sign-in and access work (or "none")?
- Which folder owns which job?
- What rules must the code never break?
- What is the **verify command** (what proves a unit works)?

**Design / output**
- UI projects: visual language, component library, layout.
- Projects without a UI: the exact output format.

**Process**
- What are the major features, broken into buildable units?
- In what order?
- What does "done" look like for each?

**Limits** (pipelines and paid APIs)
- Budget per run, time limits, and where secrets live.

## Change log
- 1.1 (2026-11-22): Step 0 also copies STEPS.md, the prompts and the type add-on into
  `context/kit/`, so each project carries its own pinned copy of the standard. No steps or gates changed.
- 1.0 (2026-11-22): Approved by the user.
- 0.1 (review 1): planning notes kept permanently; one branch per unit, push or merge only on request;
  every project follows every step.
- 0.1: First draft, made from the JavaScript Mastery Six-File Context System. Covers 4 project types, a gate after every step, a "when stuck" rule and session resume.
