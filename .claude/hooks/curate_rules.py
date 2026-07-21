"""Prompt a corpus-level rule review after Moster Rules change (Stop hook).

Hooks can't spawn subagents, so when rules/ has uncommitted changes this surfaces an
instruction for the main agent to dispatch the `rule-curator` subagent, then lets the
turn end. Mirrors validate_rules.py: exit 2 blocks the stop once, guarded by
stop_hook_active so it's a single nudge, not an infinite loop.

Run with --selftest to exercise the pure helpers on synthetic input.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Same repo-root anchor as validate_rules.py (…/.claude/hooks/x.py → repo/).
ROOT = Path(__file__).resolve().parents[2]

MESSAGE = (
    "Moster Rules changed this turn. Before finishing, dispatch the `rule-curator` "
    "subagent (Claude: the Task tool → rule-curator; Codex: `$rule-curator`) for a "
    "corpus-level pass — reciprocal Related links, emergent overlap, house-voice drift, "
    "and continuous-improvement suggestions — then apply any fixes it proposes.\n"
    "This reminder won't repeat this turn."
)


def rules_changed(porcelain: str) -> bool:
    """True if `git status --porcelain -- rules` reported any change."""
    return any(line.strip() for line in porcelain.splitlines())


def git_status() -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain", "--", "rules"],
        capture_output=True,
        text=True,
    )
    return result.stdout


def selftest() -> None:
    assert rules_changed(" M rules/foo.md\n")
    assert rules_changed("?? rules/new.md\n")
    assert not rules_changed("")
    assert not rules_changed("\n")
    assert "rule-curator" in MESSAGE
    print("selftest ok")


def main() -> int:
    if "--selftest" in sys.argv:
        selftest()
        return 0
    # Stop hooks get JSON on stdin; stop_hook_active is true when we're already inside a
    # hook-driven continuation. Nudge once, then step aside — re-blocking would loop.
    stop_hook_active = False
    if not sys.stdin.isatty():
        try:
            payload = json.load(sys.stdin)
            stop_hook_active = bool(payload.get("stop_hook_active"))
        except ValueError, AttributeError:
            pass  # run standalone (no JSON piped in) — check and nudge normally
    # ponytail: "uncommitted rules/ changes" is turn-agnostic; the stop_hook_active
    # guard bounds it to one nudge per turn-end, which is the behavior we want.
    if not rules_changed(git_status()):
        return 0
    print(MESSAGE, file=sys.stderr)
    return 0 if stop_hook_active else 2


if __name__ == "__main__":
    sys.exit(main())
