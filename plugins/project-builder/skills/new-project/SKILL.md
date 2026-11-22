---
name: new-project
description: Start a new project, or continue one that is still being planned, with the gated project-kit procedure (idea conversation, six context files, build plan). Use when the user wants to start, set up or plan a new app, plugin, skill, pipeline or tool.
argument-hint: "<the idea in a sentence or two>"
---

# New project (STEPS 0–8)

You run the planning half of the project-kit standard. The procedure is `STEPS.md`. Follow it word for word; this skill only adds how to run it.

The kit is in `../../kit/` (relative to this skill's base directory). It holds `STEPS.md`, `templates/`, `types/` and `prompts/generate-files.md`.

## First actions

1. Find out where the project stands.
   - **Existing project:** the working folder, or a folder the user names, contains `context/kit/STEPS.md`. Read `CLAUDE.md`, the project's own `context/kit/STEPS.md`, and the `Resume here` line in `context/progress-tracker.md`. Follow the project's copy of STEPS.md, not the kit's. If `context/specs/00-build-plan.md` already has an approval date, planning is finished, so tell the user to run `/project-builder:build-unit` and stop. Otherwise continue at the step that `Resume here` names.
   - **New project:** read `../../kit/STEPS.md` in full and start at Step 0.
2. Treat the user's argument as the idea. It feeds Step 1. Do not take it as permission to skip anything.

## Gates

Do one step per turn. Do the step's work, write its file, then end your turn at its GATE with this block:

```
**Step N done: <file link>**
<3–6 lines: what is in it>
**Assumed:** <anything you decided without the user, or "nothing">
**Next:** Step N+1, <name>. Reply OK to continue, or tell me what to change.
```

- **Approval** is an explicit go-ahead in the user's next message, such as OK, approved, yes or continue.
- **Feedback** means revise, then show the same gate again.
- **A question** means answer it and stay at the gate.

After each approved gate, set `Resume here` in `context/progress-tracker.md` to `Step N approved; next: Step N+1 <name>`. A new session can then pick up exactly there.

## Step notes

- **Step 0:** Propose the name, the type(s) and the folder in one message, then wait. The default folder is a new one named after the project, inside the current directory. Create nothing before this gate. Once approved:
  - create the folder and run `git init`
  - copy the files exactly as STEPS Step 0 lists, including `context/kit/`
  - fill in the top of `CLAUDE.md`
  - list the files you created, then ask Step 1's first question in the same reply
- **Step 1:** Ask one question per turn, working through the Readiness checklist in STEPS.md and using the "Idea conversation" prompt. Push back on vague answers. Keep a running list of which checklist items are answered.
  - An "I don't know yet" that does not block the build plan becomes an Open Question.
  - One that does block it: offer 2–3 concrete options and ask the user to pick.
  - When every item is answered, write `context/_planning-notes.md` with the checklist headings as sections, then stop at the gate.
- **Steps 2–7:** Use the matching prompt and the type add-on in `context/kit/`. Replace every template placeholder and delete the example brackets. A file is done only when no placeholder is left.
- **Step 4:** For a project with no UI, fill Part B (Output contract) and delete Part A.
- **Step 8:** After approval, write the date into the header of the build plan and set unit statuses to `not started`. Then say: "Planning is complete. Run `/project-builder:build-unit` to write the spec for unit 01."

## Hard line: no code before the build plan

Until the Step 8 gate is approved, the only things you write are the kit's planning files: no project code, no package installs, no framework scaffolding (such as `create-next-app` or `npm init`).

If the user asks to skip planning or start coding, reply in this order:
1. Every project follows every step (STEPS.md).
2. The fastest route is short answers at each step.
3. Continue at the current step.

The standard changes only when the user edits STEPS.md.
