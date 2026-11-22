# Unit 01: cli-skeleton

Branch: `feat/01-cli-skeleton`
Depends on: none

## Goal

`photo-renamer <folder> --dry-run` lists every `.jpg` file in the folder and prints `old -> new` using the file's
modified time as the date, then the summary line. Nothing is renamed. (EXIF comes in unit 02.)

## Design

Output follows the Output contract in ui-context.md exactly.

## Implementation

### core/plan.py
`plan_renames(items: list[tuple[str, datetime]]) -> list[tuple[str, str]]`: a pure function that returns
(old, new) pairs, with new = `YYYY-MM-DD_HHMMSS.jpg`.

### io/files.py
`list_photos(folder: Path) -> list[tuple[str, datetime]]`: lists `.jpg` files with their modified time.

### cli.py
argparse with a `folder` argument and a `--dry-run` flag. In this unit, `--dry-run` is required: without it,
print `error: real renames arrive in unit 03 - use --dry-run` and exit 1.

## Out of scope for this unit

- EXIF, real renames, clash handling, any other flags.

## Dependencies

- pytest (dev)

## Verify when done

- [ ] `plan_renames` tested with 2 files
- [ ] `--dry-run` on a tmp folder prints one line per file plus the summary, and renames nothing
- [ ] `pytest` passes (paste the summary line)
- [ ] No invariant from architecture.md broken
