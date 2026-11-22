# Type add-on: claude-plugin

Use this for Claude Code skills, agents and plugins (like thinking-system and analogy-engine).

## architecture.md: add
- **Stack rows:** Skills (`skills/<name>/SKILL.md`), Agents (`agents/*.md`), Scripts (`scripts/`, the language),
  References (`references/`), Evals (`evals/`), Marketplace entry (`.claude-plugin/marketplace.json`).
- **System boundaries:** skills orchestrate; agents do one narrow job each and get only the inputs they need;
  scripts do anything deterministic (maths, file building, API calls); references hold fixed knowledge.
- **Triggers:** for each skill, the phrases that should start it and the ones that should NOT.
- **Model and cost:** which model each agent uses, and the expected calls per run.
- **Verify command:** run the eval suite against a copy of the previous version and compare the results
  (e.g. `python evals/run.py --compare previous`). A skill change must not make the evals worse.
- **Example invariants:**
  - No keys, personal data or hidden test sets in a public repo.
  - Agents that grade work never see the author's reasoning or the answer key.
  - Deterministic work is done in scripts, never by asking the model to calculate.
  - The plugin version in `plugin.json` is bumped whenever behaviour changes.

## ui-context.md
- Use **Part B (Output contract):** reply format, card or HTML format, and record schemas. Use Part A as well
  only if the skill renders pages.

## code-standards.md: add
- Write SKILL.md files as direct instructions to an agent (imperative, short, ordered steps).
- Scripts use only the standard library where possible, and run with `python -I`.
- Every SKILL.md change comes with a new or updated eval case.

## Spec "Verify when done": add
- [ ] Eval suite: no case worse than the previous version (paste the comparison)
- [ ] The skill triggers on the intended phrases and not on the excluded ones
- [ ] `plugin.json` version bumped if behaviour changed
