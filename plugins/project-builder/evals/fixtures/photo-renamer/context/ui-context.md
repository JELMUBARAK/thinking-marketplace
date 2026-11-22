# UI Context

## Part B: Output Contract

### Outputs

| Output | Who reads it | Format | Example |
| ------ | ------------ | ------ | ------- |
| Rename line | user | `old -> new` one per file | `IMG_0001.jpg -> 2026-05-01_101500.jpg` |
| Skip line | user | `old -> SKIPPED (no date)` | `scan.jpg -> SKIPPED (no date)` |
| Summary | user | `N renamed, M skipped` (+ ` (dry run)`) | `12 renamed, 1 skipped (dry run)` |
| Error | user (stderr) | `error: <what> - <what to do>` | `error: folder not found - check the path` |

### Style Rules

- No colours, no progress bars.
- Exit code 0 on success, 1 on error.
