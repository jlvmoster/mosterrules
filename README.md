# mosterrules

The **Moster Rules** — principles for *Agentic Software Engineering* (building software *with* AI agents and *for* a world where agents read, write, and run your code), plus a minimal [`uv`](https://docs.astral.sh/uv/)-managed Python scaffold wired for [Claude Code](https://claude.com/claude-code).

## What's here

| Path | What it is |
|------|------------|
| [`rules/`](rules/) | The Moster Rules — one principle per file |
| [`AGENTS.md`](AGENTS.md) | Project instructions Claude Code and Codex load automatically |
| [`CLAUDE.md`](CLAUDE.md) | Thin pointer to `AGENTS.md` (what Claude Code loads) |
| [`.claude/`](.claude/) | Claude Code settings: permissions, hooks, agent, and recommended plugins |
| [`.codex/`](.codex/) | Codex hooks, agent, and skill — mirrors `.claude/` |
| `main.py` | Entry point |
| `pyproject.toml` / `uv.lock` | Dependencies and pinned lockfile (managed by `uv`) |

## The Moster Rules

See [`rules/README.md`](rules/README.md) for the full index. Each rule is a one-line statement, the principle, why it matters for agentic work, how to apply it, its trade-offs, a litmus test, related rules, and references.

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

### Project scope (this repo)

These are declared in [`.claude/settings.json`](.claude/settings.json), so when you open this repo in Claude Code it will offer to enable them (the custom `astral-sh` marketplace below is pre-registered in the same file). To browse or install manually, run `/plugin`.

| Plugin | Marketplace | What it gives you |
|--------|-------------|-------------------|
| **astral** | [`astral-sh/claude-code-plugins`](https://github.com/astral-sh/claude-code-plugins) | Skills for `uv`, `ruff`, and `ty` — the exact toolchain this repo uses |
| **context7** | official | Fetches up-to-date library/framework/CLI docs via MCP instead of relying on training data |
| **claude-md-management** | official | Audits and improves `CLAUDE.md` files |
| **plugin-dev** | official | Build and validate Claude Code plugins, agents, skills, and hooks |
| **skill-creator** | official | Create and optimize skills |

*"official"* = the built-in `claude-plugins-official` marketplace.

### User scope (for applying the rules anywhere)

If you just want to *practice* the Moster Rules in your own projects rather than work on this repo, install these at the user level (`/plugin`, install for your user) so they follow you into every project. Most are on the built-in `claude-plugins-official` marketplace; **ponytail** ships from a custom one you add first.

| Plugin | Marketplace | What it gives you |
|--------|-------------|-------------------|
| **superpowers** | official | Process skills that structure agentic work the way the rules ask for — brainstorming, systematic debugging, test-driven development, and writing/executing plans before touching code |
| **context7** | official | Fetches up-to-date library/framework/CLI docs via MCP instead of relying on training data |
| **ponytail** | [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) | "Lazy senior dev" mode — pushes the simplest solution that works and guards against over-engineering |
| **claude-code-setup** | official | Recommends hooks, agents, and skills to improve your Claude Code setup |
| **commit-commands** | official | `/commit`, `/commit-push-pr`, and `/clean_gone` git helpers |

## Claude Code configuration

The [`.claude/settings.json`](.claude/settings.json) in this repo puts the Moster Rules into practice:

- **Auto-checks on edit** — a `PostToolUse` hook runs `ruff check --fix`, `ruff format`, and `ty check` after Claude's `Edit`/`Write` tools (edits made via Bash don't trigger it), so lint/format/type gates enforce themselves rather than living in a docstring.
- **Protected lockfile** — Claude's file tools can't edit `uv.lock` directly; changes go through `uv` (which owns it).
- **Pre-allowed commands** — the `uv sync` / `uv run main.py` / `uv run ruff` / `uv run ty` commands run without a permission prompt.
