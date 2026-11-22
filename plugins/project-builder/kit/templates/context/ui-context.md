# UI Context

Use **Part A** if the project has a visual UI. Use **Part B** if it has no UI (skills, pipelines, CLI tools).
Some projects need both (for example a skill that renders HTML cards). Delete whichever part you don't use.

---

## Part A: Visual UI

### Theme

[The overall visual language, e.g. dark only, technical workspace, near-black layered surfaces,
vivid accent colours for interactive elements.]

### Colors

All components must use these tokens. Never use hardcoded hex values.

| Role            | CSS Variable       | Value    |
| --------------- | ------------------ | -------- |
| Page background | `--bg-base`        | `#[hex]` |
| Surface         | `--bg-surface`     | `#[hex]` |
| Primary text    | `--text-primary`   | `#[hex]` |
| Muted text      | `--text-muted`     | `#[hex]` |
| Primary accent  | `--accent-primary` | `#[hex]` |
| Border          | `--border-default` | `#[hex]` |
| Error           | `--state-error`    | `#[hex]` |
| Success         | `--state-success`  | `#[hex]` |

### Typography

| Role      | Font   | Variable      |
| --------- | ------ | ------------- |
| UI text   | [font] | `--font-sans` |
| Code/mono | [font] | `--font-mono` |

### Border Radius

| Context           | Class            |
| ----------------- | ---------------- |
| Inline / small UI | `rounded-[size]` |
| Cards / panels    | `rounded-[size]` |
| Modals / overlays | `rounded-[size]` |

### Component Library

[e.g. shadcn/ui on Tailwind. Components live in components/ui/. Add new ones with the CLI.]

### Layout Patterns

- [e.g. Editor: full-viewport split with a left sidebar, centre canvas and right sidebar]
- [e.g. Modals: centred overlay with a backdrop blur]

### Icons

[e.g. Lucide React, stroke icons only. h-4 w-4 inline, h-5 w-5 in buttons.]

---

## Part B: Output Contract

The exact shape of everything the project outputs. The agent never invents a format.

### Outputs

| Output | Who reads it | Format | Example |
| ------ | ------------ | ------ | ------- |
| [e.g. Reply to user] | [user] | [e.g. one-line answer + short table] | [link or snippet] |
| [e.g. Run record] | [scripts, me] | [e.g. JSON, schema in references/] | [path] |
| [e.g. CLI output] | [terminal] | [e.g. one line per item, exit code 0/1] | [snippet] |

### Style Rules

- [e.g. Lead with the answer; keep detail behind "More"]
- [e.g. No walls of text; at most N lines before a table or picture]
- [e.g. Errors: one line saying what failed and what to do next]

### Schemas

[Link or inline any JSON schema, file layout or record format that outputs must match.]
