# Repository Guidelines

## Project Structure & Module Organization
- `misipwgen/`: package source. Key modules: `misipwgen.py` (generator), `cumulative.py` (weighted selection), `syllable*.py` (domain types), `syllables_loader.py` (CSV loader), `settings.py` (paths like `SYLLABLES_FILE`).
- `misipwgen/it_syllables.csv`: bundled data file (semicolon-separated).
- `tests/`: unit tests (`test_*.py`) and fixtures under `tests/fixtures/`.
- `pyproject.toml`: formatting configuration (Black, isort).

## Build, Test, and Development Commands
- Run example: `python -c "from misipwgen import MisiPwGen; print(MisiPwGen().generate(7))"`.
- Run tests: `python -m unittest -v`.
- Coverage: `coverage run -m unittest -v && coverage report`.
- Format: `black .` (line length 105).
- Sort imports: `isort .` (profile "black").

## Coding Style & Naming Conventions
- Python 3.9+; 4‑space indentation; UTF‑8 files.
- Follow Black formatting (line length 105) and isort config in `pyproject.toml`.
- Modules: `snake_case.py`; classes: `PascalCase`; functions/vars: `snake_case`.
- Keep public API stable under `misipwgen/__init__.py`; avoid breaking renames.

## Testing Guidelines
- Framework: `unittest` (standard library).
- Location/naming: place tests in `tests/`, name files `test_*.py`, test methods `test_*`.
- Use fixtures in `tests/fixtures/`; prefer small, deterministic inputs.
- Aim to maintain or increase current coverage; verify with `coverage report`.

## Commit & Pull Request Guidelines
- Commits: concise, imperative mood (e.g., "add", "fix", "refactor"); group related changes; run formatters/tests before committing.
- PRs: include purpose, brief summary of changes, any linked issues, and notes on testing. Add screenshots or sample output when user-facing behavior changes.

## Security & Configuration Tips
- Do not hardcode secrets or absolute paths; data files should be referenced via `misipwgen/settings.py`.
- If adding assets, commit them under `misipwgen/` and reference with package‑relative paths so tests and imports work consistently.
