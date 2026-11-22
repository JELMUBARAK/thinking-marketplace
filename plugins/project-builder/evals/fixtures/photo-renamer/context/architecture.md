# Architecture Context

Project type: python-tool

## Stack

| Layer     | Technology         | Role                       |
| --------- | ------------------ | -------------------------- |
| Language  | Python 3.12        | Everything                 |
| CLI       | argparse           | Argument parsing           |
| EXIF      | Pillow             | Read the date taken        |
| Tests     | pytest             | Verify command             |
| Packaging | pyproject.toml     | `photo-renamer` entry point |

## System Boundaries

- `src/photo_renamer/cli.py`: argument parsing and printing only
- `src/photo_renamer/core/`: plans renames from (filename, date) pairs; pure, no I/O
- `src/photo_renamer/io/`: reads EXIF, lists files, performs renames
- `tests/`: pytest tests

## Storage Model

None. The tool stores nothing.

## Access Model

- No auth: local tool.

## Secrets

- None.

## Commands

- `photo-renamer <folder> [--dry-run]`: exit 0 on success, 1 on any error.

## Verify Command

```
pytest
```

## Invariants

1. Never overwrite an existing file.
2. `--dry-run` never renames anything.
3. `core/` does no I/O.
4. Tests never touch real user folders. They use `tmp_path`.
