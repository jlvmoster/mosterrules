# mosterrules

The repo's product is the **Moster Rules** in `rules/` — see [`rules/README.md`](rules/README.md) for the index and per-rule format before adding or editing a rule. The rest is a Python scaffold managed with [uv](https://docs.astral.sh/uv/); entry point is `main.py`.

## Environment
- Python **3.14.3** (pinned in `.python-version`)
- Dependencies and virtualenv are managed by `uv` (see `pyproject.toml` / `uv.lock`)

## Common commands
- Sync deps / create venv: `uv sync`
- Run the app: `uv run main.py`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type check: `uv run ty check`
- Add a dependency: `uv add <package>`
- Add a dev dependency: `uv add --dev <package>`

## Conventions
- Use `uv` for all dependency and environment operations; do not call `pip` directly.
- Run `ruff check`, `ruff format`, and `ty check` before committing.
- Type checking uses [ty](https://docs.astral.sh/ty/) (not mypy/pyright). The `astral` plugin wires ty as the editor language server; `uv run ty check` is the CLI gate. Fix type errors rather than suppressing them; if you must suppress, use a rule-specific `# ty: ignore[rule]`.

## Testing
- No test suite or test runner is configured yet. There is no `uv run pytest` workflow until one is added.
