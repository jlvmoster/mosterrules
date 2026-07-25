# mosterrules

The **Moster Rules** — principles for *Agentic Software Engineering* (building software *with* AI agents and *for* a world where agents read, write, and run your code), plus the [`uv`](https://docs.astral.sh/uv/)-managed toolchain that enforces them in [Claude Code](https://claude.com/claude-code) and Codex.

## What's here

| Path | What it is |
|------|------------|
| [`rules/`](rules/) | The Moster Rules — one principle per file |
| [`AGENTS.md`](AGENTS.md) | Project instructions Claude Code and Codex load automatically |
| [`CLAUDE.md`](CLAUDE.md) | Thin pointer to `AGENTS.md` (what Claude Code loads) |
| [`.claude/`](.claude/) | Claude Code settings: permissions, hooks, agents, the `new-rule` skill, and recommended plugins |
| [`.codex/`](.codex/) | Codex hooks, agents, and skill — mirrors `.claude/` |
| [`.github/`](.github/) | CI workflow and Dependabot config |
| `pyproject.toml` / `uv.lock` | Dependencies and pinned lockfile (managed by `uv`) |

## The Moster Rules

See [`rules/README.md`](rules/README.md) for the full index and the shape every rule follows.

## Getting started

**Prerequisites:** [`uv`](https://docs.astral.sh/uv/getting-started/installation/). Python **3.14.3** is pinned in `.python-version` and installed automatically by `uv`.

```sh
uv sync            # create the venv and install dependencies
```

The full command list and the conventions that go with it live in [AGENTS.md](AGENTS.md#common-commands) — one home, so they can't drift.

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
- **Turn-end validation** — a `Stop` hook validates every rule and the index, and asks for a corpus-level curation pass when `rules/` has uncommitted changes.
- **Protected lockfile** — Claude's `Edit` and `Write` tools are denied on `uv.lock`; changes go through `uv`, which owns it.
- **Pre-allowed commands** — the project's `uv` commands run without a permission prompt (see `permissions.allow`).

[AGENTS.md](AGENTS.md#automated-checks-hooks) documents each hook and what blocks on it. The same hooks run under Codex via [`.codex/hooks.json`](.codex/hooks.json), and [CI](.github/workflows/ci.yml) re-runs the checks on every push and PR.
