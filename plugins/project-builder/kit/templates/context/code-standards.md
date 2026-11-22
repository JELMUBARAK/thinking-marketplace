# Code Standards

## General

- [Principle, e.g. Keep modules small and single-purpose]
- [Principle, e.g. Fix root causes; do not layer workarounds]
- [Principle, e.g. Do not mix unrelated concerns in one file]
- [Principle, e.g. No dead code and no commented-out code]

## Language

[One section per language used, e.g. TypeScript, Python, Markdown for skills.]

- [Rule, e.g. TypeScript strict mode; no `any`]
- [Rule, e.g. Python: type hints on public functions; standard library first]
- [Rule, e.g. Validate unknown external input at system boundaries before trusting it]

## Framework / Platform

[e.g. Next.js, Claude Code plugin, CLI framework]

- [Convention]
- [Convention]

## Styling / Output

- [Rule, e.g. Use only the tokens in ui-context.md; no hardcoded hex values]
- [Rule, e.g. Output must match the Output contract in ui-context.md exactly]

## Interfaces

[API routes, skill triggers, CLI commands, pipeline stage inputs and outputs, whichever apply.]

- [Rule, e.g. Validate input before any logic runs]
- [Rule, e.g. Return consistent, predictable response shapes]

## Data and Storage

- [Rule, e.g. Metadata in the database, large files in blob storage]

## Errors and Logging

- [Rule, e.g. Fail loudly with a clear message; never swallow errors]
- [Rule, e.g. Never log secrets or personal data]

## Testing

- [Rule, e.g. Every unit adds or updates the tests or evals that its verify checklist depends on]

## File Organization

- `[folder]/`: [What belongs here]
- `[folder]/`: [What belongs here]
