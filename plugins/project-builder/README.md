# project-builder

A standard, gated way to build any project with an AI coding agent. It is based on the JavaScript Mastery
"Six-File Context System" and extended to four project types: web apps, Claude plugins, AI pipelines and
Python tools.

| Skill | Covers |
|---|---|
| `/project-builder:new-project <idea>` | STEPS 0–8: set-up, idea conversation, six context files, build plan |
| `/project-builder:build-unit [NN\|resume]` | STEPS 9–11: one unit at a time (spec → build → verify → close), the "when stuck" rule, and resuming a session |

Claude stops at a **gate** after every step and continues only on an explicit OK. No code is written before
the build plan is approved.

`kit/` is a synced copy of the master kit. Do not edit it here. Edit the master and run its `sync.ps1`.
Each new project gets its own pinned copy of the standard in `context/kit/`.

Evals: see `evals/README.md`.
