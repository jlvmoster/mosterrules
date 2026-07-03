# mosterrules

The **Moster Rules** — principles for *Agentic Software Development* (building software *with* AI agents and *for* a world where agents read, write, and run your code), plus a minimal [`uv`](https://docs.astral.sh/uv/)-managed Python scaffold wired for [Claude Code](https://claude.com/claude-code).

## What's here

| Path | What it is |
|------|------------|
| [`rules/`](rules/) | The Moster Rules — one principle per file |
| [`CLAUDE.md`](CLAUDE.md) | Project instructions Claude Code loads automatically |
| [`.claude/`](.claude/) | Settings: permissions, hooks, and recommended plugins |
| `main.py` | Entry point |
| `pyproject.toml` / `uv.lock` | Dependencies and pinned lockfile (managed by `uv`) |

## The Moster Rules

See [`rules/README.md`](rules/README.md) for the full index. Each rule is a one-line statement, the principle, why it matters for agentic work, how to apply it, and anti-patterns.

| # | Rule | Principle |
|---|------|-----------|
| 1 | [Anti-Foot-Gun](rules/anti-foot-gun.md) | Make the dangerous path hard to take by accident; design footguns out instead of documenting around them. |
| 2 | [Idempotency](rules/idempotency.md) | Make an operation safe to run again and safe to interrupt; running it twice equals running it once. |

## Getting started

**Prerequisites:** [`uv`](https://docs.astral.sh/uv/getting-started/installation/). Python **3.14.3** is pinned in `.python-version` and installed automatically by `uv`.

```sh
uv sync            # create the venv and install dependencies
uv run main.py     # run the app
```

**Common commands:**

| Task | Command |
|------|---------|
| Sync deps / create venv | `uv sync` |
| Run the app | `uv run main.py` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Type check | `uv run ty check` |
| Add a dependency | `uv add <package>` |
| Add a dev dependency | `uv add --dev <package>` |

Use `uv` for all dependency and environment operations — do not call `pip` directly. Type checking uses [`ty`](https://docs.astral.sh/ty/), not mypy/pyright.

## Recommended Claude Code plugins

These are declared in [`.claude/settings.json`](.claude/settings.json), so when you open this repo in Claude Code it will offer to enable them (the two custom marketplaces below are pre-registered in the same file). To browse or install manually, run `/plugin`.

| Plugin | Marketplace | What it gives you |
|--------|-------------|-------------------|
| **ponytail** | [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) | "Lazy senior dev" mode — pushes the simplest solution that works and guards against over-engineering |
| **astral** | [`astral-sh/claude-code-plugins`](https://github.com/astral-sh/claude-code-plugins) | Skills for `uv`, `ruff`, and `ty` — the exact toolchain this repo uses |
| **context7** | official | Fetches up-to-date library/framework/CLI docs via MCP instead of relying on training data |
| **claude-code-setup** | official | Recommends hooks, agents, and skills to improve a project's Claude Code setup |
| **claude-md-management** | official | Audits and improves `CLAUDE.md` files |
| **plugin-dev** | official | Build and validate Claude Code plugins, agents, skills, and hooks |
| **skill-creator** | official | Create and optimize skills |
| **commit-commands** | official | `/commit`, `/commit-push-pr`, and `/clean_gone` git helpers |

*"official"* = the built-in `claude-plugins-official` marketplace.

## Claude Code configuration

The [`.claude/settings.json`](.claude/settings.json) in this repo puts the Moster Rules into practice:

- **Auto-checks on edit** — a `PostToolUse` hook runs `ruff check --fix`, `ruff format`, and `ty check` after every file edit, so lint/format/type gates enforce themselves rather than living in a docstring.
- **Protected lockfile** — direct `Edit`/`Write` to `uv.lock` is denied; changes go through `uv` (which owns it).
- **Pre-allowed commands** — the `uv sync` / `uv run main.py` / `uv run ruff` / `uv run ty` commands run without a permission prompt.
