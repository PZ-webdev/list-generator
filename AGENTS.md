# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: App entry (Tkinter launcher).
- `app/`: Source package.
  - `gui/`: Views, scenes, dialogs, and components.
  - `core/`: Business logic (PDF/text/branch services).
  - `utils/`: Helpers (logging, validation, resources, config, notify).
  - `dto/`: Data models.
  - `templates/` and `resources/`: HTML template and assets.
- `config.py`: Runtime configuration defaults.
- `data/`, `logs/`, `example/`: Sample inputs, runtime logs, examples.
- `pyproject.toml`: Packaging and dependencies.
- `.github/workflows/version.yml`: Auto-bumps `VERSION` using commit type.

## Build, Test, and Development Commands
- Target platform: Windows 7 32‑bit, Python 3.8 (32‑bit). The project requires `>=3.8,<3.9`.
- Create venv (Windows): `py -3.8 -m venv .venv` then `.venv\Scripts\activate`.
- Install deps: `pip install .` (reads `pyproject.toml`). If a `requirements.txt` is present in your env, use `pip install -r requirements.txt`.
- Run app: `python main.py` (or `py -3.8 main.py`).
- Build EXE (Win32): `pyinstaller main.spec` and ensure 32‑bit wkhtmltopdf is installed and on `PATH`.
- Lint/format: follow PEP 8; no enforced tool is configured.

## Coding Style & Naming Conventions
- Indentation: 4 spaces; line length ~88–100.
- Naming: `snake_case` for modules/functions/vars, `PascalCase` for classes, constants `UPPER_SNAKE_CASE`.
- Structure: keep UI in `app/gui`, logic in `app/core`, helpers in `app/utils`.
- Type hints: use Python 3.8‑compatible typing. Prefer `Optional[str]` over `str | None`, `List[str]` over `list[str]`. Import from `typing`.
- Docstrings: short, imperative summary; add type hints at public boundaries.

## Testing Guidelines
- Framework: none mandated. Prefer `pytest` for new tests.
- Location: `tests/`, file pattern `test_*.py` (e.g., `tests/test_text_processing.py`).
- Scope: unit-test services in `app/core`; mock GUI.
- Run: `pytest` or `python -m unittest`.

## Commit & Pull Request Guidelines
- Conventional commits: `feat:`, `fix:`, `chore:` observed in history (PR refs like `(#41)`). The version workflow bumps `VERSION` based on commit type.
- Commits: concise, imperative; one logical change per commit.
- PRs: clear description, linked issue, reproduction/run notes; include screenshots for GUI changes.
- Keep `README.md` and examples up to date when behavior changes.

## Security & Configuration Tips
- External dependency: install 32‑bit wkhtmltopdf and ensure it’s on `PATH` for PDF generation.
- PyInstaller: build on a 32‑bit Python 3.8 environment for Windows 7 compatibility.
- Avoid committing secrets; logs may include paths—sanitize before sharing.
- Template: edit `app/templates/pdf_template.html` with care; validate output via sample data in `data/`.
