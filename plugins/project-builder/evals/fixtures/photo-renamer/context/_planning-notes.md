# Planning notes

## Product
- One sentence: renames photos in a folder to `YYYY-MM-DD_HHMMSS.jpg` using the date the photo was taken.
- User: me, tidying phone exports on Windows.
- Flow: run `photo-renamer <folder> --dry-run`, check the planned names, run again without `--dry-run`.
- Top 3 features: read the date taken (EXIF), dry-run preview, safe handling of name clashes.
- Out of scope: GUI, cloud folders, video files, editing EXIF.

## Technical
- Python 3.12, argparse, Pillow (EXIF), pytest. Pillow is chosen because it reads EXIF with no extra tools.
- Data: none stored. Reads and renames files only.
- Access: local tool, no auth.
- Boundaries: `cli.py` parses args; `core/` plans renames (pure); `io/` reads EXIF and renames.
- Never: overwrite an existing file; rename anything in dry-run.
- Verify command: `pytest`.

## Design / output
- No UI. CLI output: one line per file, `old -> new`, then a summary line. Exit code 0 / 1.

## Process
- Units: 01 CLI skeleton with dry-run plan, 02 EXIF reading, 03 real rename with clash handling.

## Limits
- None (no paid APIs).
