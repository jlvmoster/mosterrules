# mosterrules

The repo's product is the **Moster Rules** in `rules/` — see [`rules/README.md`](rules/README.md) for the index and per-rule format before adding or editing a rule. The rest is the Python toolchain that enforces them, managed with [uv](https://docs.astral.sh/uv/); the code lives in `.claude/hooks/`.

## Environment
- Python **3.14.3** (pinned in `.python-version`)
- Dependencies and virtualenv are managed by `uv` (see `pyproject.toml` / `uv.lock`)

## Common commands
- Sync deps / create venv: `uv sync`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type check: `uv run ty check`
- Run tests: `uv run python -m unittest discover -s .claude/hooks -p 'test_*.py'`
- Validate rules: `uv run python .claude/hooks/validate_rules.py`
- Check Claude↔Codex mirrors: `uv run python .claude/hooks/check_mirrors.py`
- Add a dependency: `uv add <package>`
- Add a dev dependency: `uv add --dev <package>`

## Conventions
- Use `uv` for all dependency and environment operations; do not call `pip` directly.
- Run `ruff check`, `ruff format`, `ty check`, the test suite, `validate_rules.py`, and `check_mirrors.py` before committing — CI runs them all.
- Type checking uses [ty](https://docs.astral.sh/ty/) (not mypy/pyright); `uv run ty check` is the CLI gate. Fix type errors rather than suppressing them; if you must suppress, use a rule-specific `# ty: ignore[rule]`.
- `.claude/agents/*.md` and `.claude/skills/*/SKILL.md` are the source of truth for agent/skill prose. Codex counterparts (`.codex/agents/*.toml`, `.codex/skills/*/SKILL.md`) must match on name, description, and body; format-specific keys (`tools`, `sandbox_mode`, `disable-model-invocation`, `agents/openai.yaml`) stay local. [`.claude/hooks/check_mirrors.py`](.claude/hooks/check_mirrors.py) is the CI gate — edit the Claude file first, then the Codex counterpart, in the same commit.

## Testing
- Each hook script has a stdlib `unittest` suite beside it in `.claude/hooks/test_*.py`: `uv run python -m unittest discover -s .claude/hooks -p 'test_*.py'` (note the `-s` — the hooks dir is hidden and has no `__init__.py`). No hook runs them, but [CI](.github/workflows/ci.yml) does on every push and PR. Follow [Test-Driven Development](rules/test-driven-development.md): write the failing test first, or when adding tests to existing code, mutate the code to confirm the new test actually goes red.
- No `pytest` is configured; there is no `uv run pytest` workflow until one is added.

## Adding or editing a rule
- New rule: **`/new-rule` in Claude Code or `$new-rule` in Codex** — user-invoked only; it scaffolds the shape `validate_rules.py` enforces and registers the index row.
- **`rule-reviewer`** (one rule) and **`rule-curator`** (corpus ripples) are read-only and propose rather than edit. Dispatch the reviewer yourself before committing a new or reworked rule; the Stop hook prompts for the curator whenever `rules/` changes.

## Automated checks (hooks)
These run automatically in both Claude Code (`.claude/settings.json`) and Codex (`.codex/hooks.json`) — they're not optional style notes. (In Codex, project hooks load only after you trust the workspace and its hook definitions — review them via `/hooks` on first use.)
- **On edit** (PostToolUse): `ruff check --fix`, `ruff format`, `ty check` run after every file-edit tool call (Claude's `Edit`/`Write`, Codex's `apply_patch`) — edits made via the shell don't trigger it, so files may be reformatted right after you write them. `.claude/hooks/guard_new_rule.py` also runs: when you write a **new** `rules/*.md`, it surfaces every existing rule's blockquote and asks you to confirm you aren't duplicating one (DRY/YAGNI) — extend an existing rule instead of adding a near-copy. It's a reminder, not a hard block (the write already happened); it stays silent for edits to existing rules and non-rule files.
- **On stop** (Stop): `.claude/hooks/validate_rules.py` runs and **blocks the turn from ending** if any `rules/*.md` drifts from the shape it enforces, or `rules/README.md` stops mirroring a rule's blockquote verbatim, or a `## Related` link points to a missing rule. Then `.claude/hooks/curate_rules.py` runs: if `rules/` has uncommitted changes, it blocks once (guarded by `stop_hook_active`) asking you to dispatch the **`rule-curator`** subagent, then apply any fixes it proposes. Each script runs directly; `--selftest` exercises each. Claude↔Codex agent/skill prose is a CI check (`check_mirrors.py`), not a Stop hook.
- **Editing a hook?** Anchor paths to the repo root: the script uses `Path(__file__).resolve().parents[2]`; the hook command uses `${CLAUDE_PROJECT_DIR}` (Claude) or `$(git rev-parse --show-toplevel)` (Codex). A hook's cwd is *not* guaranteed to be the project root, and a cwd-relative path that fails will exit non-zero and block Stop.
