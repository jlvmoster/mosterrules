"""Guard against duplicate Moster Rules (DRY / YAGNI).

A PostToolUse tripwire: when a *new* rules/*.md is written, surface every existing
rule's blockquote so the overlap reflex fires before a redundant rule takes root. It
does no semantic matching — it lists the corpus and lets the agent (the semantic
engine) judge. Exit 2 with the reminder on stderr so Claude Code / Codex surface it;
the write already happened, so this is feedback, not a block.

Run with --selftest to exercise the pure helpers on synthetic input.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# Same repo-root anchor as validate_rules.py (…/.claude/hooks/x.py → repo/), so the
# hook works regardless of the tool's working directory when it fires.
ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "rules"


# ponytail: a local blockquote read instead of `import validate_rules` — the bare
# import resolves at runtime (same dir) but the type checker may not find it, and
# duplicating this stable one-liner parse is cheaper than fighting that.
def blockquote(text: str) -> str:
    """The rule's one-line summary: the first '> ' line after the H1 title."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            after = next((ln for ln in lines[i + 1 :] if ln.strip()), "")
            return after[2:].strip() if after.startswith("> ") else ""
    return ""


def rule_files() -> list[Path]:
    return sorted(p for p in RULES.glob("*.md") if p.name != "README.md")


def written_path(payload: dict) -> str | None:
    """The file an Edit/Write touched, or None if the payload doesn't carry one."""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    path = tool_input.get("file_path")
    return path if isinstance(path, str) and path else None


def is_rule(path: str) -> bool:
    """A rule file directly under rules/ (not the README index)."""
    p = Path(path)
    p = p if p.is_absolute() else ROOT / p
    try:
        rel = p.resolve().relative_to(RULES.resolve())
    except ValueError:
        return False
    return p.suffix == ".md" and p.name != "README.md" and len(rel.parts) == 1


def is_tracked(path: str) -> bool:
    """True if git already tracks the file (an edit, not a brand-new rule)."""
    p = Path(path)
    rel = str(p.resolve().relative_to(ROOT)) if p.is_absolute() else path
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", rel],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def untracked_rules() -> set[str]:
    """Names of untracked rules/*.md — the fallback when no path is in the payload.

    --untracked-files=all overrides a repo/user status.showUntrackedFiles=no, which
    would otherwise hide brand-new rules from --porcelain and blind the guard.
    """
    result = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            "rules",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    names = set()
    for line in result.stdout.splitlines():
        name = line[3:]
        if line[:2] == "??" and name.endswith(".md") and Path(name).name != "README.md":
            names.add(Path(name).name)
    return names


# Codex's apply_patch delivers the raw patch instead of a file_path; it introduces
# new files with "*** Add File: <path>" markers we can read directly.
ADD_FILE_RE = re.compile(r"^\*\*\* Add File: (.+)$", re.MULTILINE)


def patch_text(payload: dict) -> str:
    """The apply_patch body, or '' if absent.

    Freeform apply_patch carries it on `input`; the JSON tool schema uses
    `command` as ["apply_patch", "<patch>"]. Both are checked because the
    shape depends on which tool variant the model picked.
    """
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    for value in (tool_input.get("input"), tool_input.get("command")):
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            # ADD_FILE_RE is MULTILINE, so the leading "apply_patch" element is inert.
            return "\n".join(v for v in value if isinstance(v, str))
    return ""


def added_rules(patch: str) -> set[str]:
    """Rule filenames the patch *creates* via '*** Add File:' — scoped to this edit."""
    return {
        Path(m.strip()).name for m in ADD_FILE_RE.findall(patch) if is_rule(m.strip())
    }


def new_rule_names(payload: dict) -> set[str]:
    """Names of brand-new rule files this tool call is creating (empty if none)."""
    path = written_path(payload)
    if path is not None:
        # Claude Edit/Write: one concrete path — new only if it's an untracked rule.
        if is_rule(path) and not is_tracked(path):
            return {Path(path).name}
        return set()  # a non-rule write, or an edit to an existing rule
    patch = patch_text(payload)
    if patch:
        # Codex apply_patch: the patch names exactly what it adds, so an update-only
        # patch (README, reciprocal links, an existing rule) correctly yields nothing
        # — no re-nagging on every later edit while a new rule sits uncommitted.
        return added_rules(patch)
    return untracked_rules()  # no path and no patch — last-resort scan for untracked


def render(entries: list[tuple[str, str]]) -> str:
    lines = [
        "A new Moster Rule is being created — first confirm it isn't already covered (DRY / YAGNI).",
        "",
        "Existing rules:",
    ]
    lines += [f"  - {name} — {quote}" for name, quote in entries]
    lines += [
        "",
        "A principle has one home (Single Source of Truth). If one of the above already covers",
        "this, extend its How to apply / Related instead of adding a file (Minimum Necessary",
        "Complexity / YAGNI). If it is genuinely new, proceed.",
    ]
    return "\n".join(lines)


def entries_for(new_names: set[str]) -> list[tuple[str, str]]:
    out = []
    for p in rule_files():
        if p.name in new_names:
            continue
        out.append(
            (p.name, blockquote(p.read_text(encoding="utf-8")) or "(no blockquote)")
        )
    return out


def selftest() -> None:
    assert is_rule("rules/foo.md")
    assert is_rule(str(RULES / "foo.md"))
    assert not is_rule("rules/README.md")
    assert not is_rule("main.py")
    assert not is_rule(".claude/hooks/guard_new_rule.py")
    assert not is_rule("rules/sub/foo.md")
    assert written_path({"tool_input": {"file_path": "rules/x.md"}}) == "rules/x.md"
    assert written_path({}) is None
    assert written_path({"tool_input": {}}) is None
    out = render([("a.md", "First."), ("b.md", "Second.")])
    assert "  - a.md — First." in out
    assert "DRY / YAGNI" in out
    assert "Single Source of Truth" in out
    print("selftest ok")


def main() -> int:
    if "--selftest" in sys.argv:
        selftest()
        return 0
    payload: dict = {}
    if not sys.stdin.isatty():
        try:
            loaded = json.load(sys.stdin)
            payload = loaded if isinstance(loaded, dict) else {}
        except ValueError, AttributeError:
            pass  # no/invalid JSON piped in — nothing to guard
    new_names = new_rule_names(payload)
    if not new_names:
        return 0
    entries = entries_for(new_names)
    if not entries:
        return 0  # first rule in the repo — nothing to duplicate
    print(render(entries), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
