# Architecture Context

Project type: [web-app | claude-plugin | ai-pipeline | python-tool]

## Stack

| Layer   | Technology   | Role   |
| ------- | ------------ | ------ |
| [Layer] | [Technology] | [Role] |
| [Layer] | [Technology] | [Role] |

[Add the sections for your type from the type add-on in `context/kit/`. For example, a web app adds Framework, UI, Auth and
Database. A plugin adds Skills, Agents, Scripts and Evals.]

## System Boundaries

- `[folder]/`: [What this folder owns and is responsible for]
- `[folder]/`: [What this folder owns and is responsible for]

## Storage Model

- **[Storage type]**: [What lives here]
- **[Storage type]**: [What lives here]

[Write "None" if the project stores nothing.]

## Access Model

- [How sign-in works, or "No auth: local tool"]
- [Who owns what]
- [Who can change what]

## Secrets

- [Each key or secret, where it is kept (e.g. a user-level environment variable), and the rule
  "never print, never commit"]

## Verify Command

The command (or exact steps) that proves a unit works. Every unit runs this before it is called done.

```
[e.g. npm run build && npm run lint   |   pytest   |   python evals/run.py --compare previous]
```

## Invariants

Rules the codebase must never break. Write them as rules, not guidelines. There must be at least 4.

1. [Invariant one]
2. [Invariant two]
3. [Invariant three]
4. [Invariant four]
