"""Validate the Moster Rules.

Enforces three invariants the prose can't:
  1. every rules/*.md has the canonical 8-part shape, headings in order;
  2. rules/README.md mirrors each rule's blockquote verbatim in the index;
  3. every '## Related' link resolves to a real rule file.

Exit 2 with messages on stderr when anything drifts, so Claude Code surfaces it.
Run with --selftest to exercise the parser on synthetic input.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Anchored to the repo root (…/.claude/hooks/validate_rules.py → repo/) so the
# hook works regardless of Claude Code's working directory when it fires.
RULES = Path(__file__).resolve().parents[2] / "rules"
README = RULES / "README.md"

# Canonical section headings, in order, after the H1 title and one-line blockquote.
SECTIONS = [
    "## Principle",
    "## Why it matters for agentic development",
    "## How to apply",
    "## Trade-offs",
    "## Litmus test",
    "## Related",
    "## References",
]

# Local Markdown link target ending in .md: bare, ./-prefixed, <angled>, or #anchored.
LINK_RE = re.compile(r"\]\(<?(?:\./)?([a-z0-9-]+\.md)(?:#[^)>]*)?>?\)")


def rule_files() -> list[Path]:
    return sorted(p for p in RULES.glob("*.md") if p.name != "README.md")


def blockquote(text: str) -> str | None:
    """The opening one-line blockquote: the first non-empty line after the H1.

    Anchored to the title so a later '> ' (e.g. the Litmus test) can't stand in
    for a missing opening quote.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            after = next((ln for ln in lines[i + 1 :] if ln.strip()), "")
            return after[2:].strip() if after.startswith("> ") else None
    return None


def check_shape(path: Path, text: str, errors: list[str]) -> None:
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        errors.append(f"{path}: missing an '# Title' heading on line 1")
    if blockquote(text) is None:
        errors.append(
            f"{path}: missing a '> ' one-line blockquote right after the title"
        )
    headings = [ln.rstrip() for ln in lines if ln.startswith("## ")]
    if headings != SECTIONS:
        errors.append(
            f"{path}: '## ' sections do not match the canonical shape\n"
            f"      expected: {SECTIONS}\n"
            f"      found:    {headings}"
        )


def check_related(path: Path, text: str, names: set[str], errors: list[str]) -> None:
    in_related = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_related = line.strip() == "## Related"
            continue
        if in_related:
            for target in LINK_RE.findall(line):
                if target not in names:
                    errors.append(
                        f"{path}: '## Related' links to a missing rule '{target}'"
                    )


def check_index(rules: list[Path], errors: list[str]) -> None:
    readme = README.read_text(encoding="utf-8")
    rows = [ln for ln in readme.splitlines() if ln.lstrip().startswith("|")]
    names = {p.name for p in rules}
    for path in rules:
        quote = blockquote(path.read_text(encoding="utf-8"))
        if quote is None:
            continue  # already flagged by check_shape
        row = next((r for r in rows if f"({path.name})" in r), None)
        if row is None:
            errors.append(f"README.md: no index row links to {path.name}")
        elif quote not in row:
            errors.append(
                f"README.md: index row for {path.name} is missing its blockquote verbatim\n"
                f"      blockquote: {quote}"
            )
    # Reverse direction: an index row must not link to a rule that no longer exists.
    for row in rows:
        for target in LINK_RE.findall(row):
            if target not in names:
                errors.append(
                    f"README.md: index row links to a missing rule '{target}'"
                )


def validate() -> list[str]:
    rules = rule_files()
    if not README.exists():
        # No index and no rules → nothing to validate (not the rules repo).
        # Rules with no index is exactly the drift this guards against.
        return [f"{README}: rules exist but the index is missing"] if rules else []
    names = {p.name for p in rules}
    errors: list[str] = []
    for path in rules:
        text = path.read_text(encoding="utf-8")
        check_shape(path, text, errors)
        check_related(path, text, names, errors)
    check_index(rules, errors)
    return errors


def selftest() -> None:
    body = "\n\n".join(f"{s}\ntext" for s in SECTIONS)
    good = f"# X\n\n> One line.\n\n{body}"
    errs: list[str] = []
    check_shape(Path("x.md"), good, errs)
    assert errs == [], errs
    errs = []
    check_shape(Path("x.md"), good.replace("## Trade-offs", "## Oops"), errs)
    assert errs, "expected a shape error when a heading is wrong"
    # A later '> ' (e.g. the Litmus test) must not satisfy the opening-quote check.
    errs = []
    no_open = f"# X\n\n{body}".replace(
        "## Litmus test\ntext", "## Litmus test\n> quote"
    )
    check_shape(Path("x.md"), no_open, errs)
    assert errs, "expected a shape error when the opening blockquote is missing"
    # Bare, ./-prefixed, <angled>, and #anchored links are all validated.
    for form in ("missing.md", "./missing.md", "<missing.md>", "missing.md#s"):
        errs = []
        check_related(Path("x.md"), f"## Related\n- [a]({form})\n", set(), errs)
        assert errs, f"expected a missing-link error for {form}"
    print("selftest ok")


def main() -> int:
    if "--selftest" in sys.argv:
        selftest()
        return 0
    # Always block on drift. A second Stop hook (curate_rules.py) also runs, and
    # stop_hook_active is turn-wide, not per-hook: if that hook blocks first, honoring
    # the flag here would skip validation on the continuation and let an invalid rule
    # through. Structural errors are deterministic and agent-fixable, so re-blocking
    # until fixed is safe — it won't loop in practice.
    errors = validate()
    if errors:
        print("Moster Rules validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
