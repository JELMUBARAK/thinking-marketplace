# Type add-on: python-tool

Use this for Python command-line tools, automation scripts and small libraries.

## architecture.md: add
- **Stack rows:** Python version, CLI (argparse or click), main libraries, Packaging (`pyproject.toml`),
  Tests (pytest).
- **System boundaries:** e.g. `src/<pkg>/cli.py` (argument parsing only), `src/<pkg>/core/` (logic, no I/O),
  `src/<pkg>/io/` (files, network), `tests/`.
- **Commands:** every CLI command, with its arguments, and its output and exit codes.
- **Verify command:** `.venv\Scripts\python -m pytest` (plus `ruff check .` if used).
- **Example invariants:**
  - Core logic does no I/O, so it can be tested without files or network.
  - Tests never call the real network or paid APIs.
  - Exit code is 0 on success and non-zero on any failure.
  - Paths work on Windows and on POSIX (use `pathlib`).
  - Packages are installed only into the project `.venv`, never into the global Python.

## ui-context.md
- Use **Part B:** CLI output format, error message format, and the formats of any files written.

## Environment
- Step 0 creates a project virtual environment: `python -m venv .venv`, and adds `.venv/` to `.gitignore`.
- Install packages only into `.venv`, never into the global Python. Run every command through the
  venv's Python (`.venv\Scripts\python -m pip ...`, `.venv\Scripts\python -m pytest`; on POSIX use `.venv/bin/python`).

## code-standards.md: add
- Type hints on public functions; standard library first.
- Each unit adds tests for the behaviour it introduces.

## Spec "Verify when done": add
- [ ] `pytest` green (paste the summary line)
- [ ] The command runs from a fresh shell with the documented arguments
- [ ] Exit codes are correct for success and failure
