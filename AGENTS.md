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

## Automated checks (hooks)
These run automatically in both Claude Code (`.claude/settings.json`) and Codex (`.codex/hooks.json`) — they're not optional style notes. (In Codex, project hooks load only after you trust the workspace and its hook definitions — review them via `/hooks` on first use.)
- **On edit** (PostToolUse): `ruff check --fix`, `ruff format`, `ty check` run after every file-edit tool call (Claude's `Edit`/`Write`, Codex's `apply_patch`) — edits made via the shell don't trigger it, so files may be reformatted right after you write them.
- **On stop** (Stop): `.claude/hooks/validate_rules.py` runs and **blocks the turn from ending** if any `rules/*.md` drifts from the canonical 8-part shape, or `rules/README.md` stops mirroring a rule's blockquote verbatim, or a `## Related` link points to a missing rule. Run it directly to check; `--selftest` exercises the parser.
- **Editing a hook?** Anchor paths to the repo root: the script uses `Path(__file__).resolve().parents[2]`; the hook command uses `${CLAUDE_PROJECT_DIR}` (Claude) or `$(git rev-parse --show-toplevel)` (Codex). A hook's cwd is *not* guaranteed to be the project root, and a cwd-relative path that fails will exit non-zero and block Stop.
