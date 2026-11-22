# Code Standards

## General

- Keep modules small and single-purpose.
- Fix root causes; do not layer workarounds.

## Language

- Python 3.12, type hints on public functions, standard library first.
- Use `pathlib` for all paths.

## Interfaces

- `cli.py` only parses and prints, and calls core and io.

## Errors and Logging

- Errors go to stderr in the Output contract format. Exit code 1.

## Testing

- Each unit adds pytest tests for its behaviour. Tests use `tmp_path`.

## File Organization

- `src/photo_renamer/`: package
- `tests/`: tests
