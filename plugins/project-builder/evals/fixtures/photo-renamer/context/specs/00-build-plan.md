# Build Plan

APPROVAL_LINE

## Units

| #  | Unit | Builds (the result you can see) | Depends on | Status |
| -- | ---- | ------------------------------- | ---------- | ------ |
| 01 | cli-skeleton | `photo-renamer <folder> --dry-run` prints planned names from file modified times | none | UNIT01_STATUS |
| 02 | exif-dates | Planned names use the EXIF date taken; files with no date are skipped | 01 | not started |
| 03 | real-rename | A run without `--dry-run` renames files, with clash suffixes | 02 | not started |

Status values: `not started`, `spec written`, `spec approved`, `in progress`, `verifying`, `complete`.
