"""Check that Claude and Codex agent/skill prose stay in lockstep.

`.claude/agents/*.md` and `.claude/skills/*/SKILL.md` are the source of truth.
Each must have a Codex counterpart whose name, description, and body match.
Format-specific keys (Claude `tools` / `disable-model-invocation`, Codex
`sandbox_mode` / `agents/openai.yaml`) stay local and are not compared.

Exit 2 with messages on stderr when anything drifts.
Run with --selftest to exercise the parsers on synthetic input.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

# Anchored to the repo root (…/.claude/hooks/check_mirrors.py → repo/).
ROOT = Path(__file__).resolve().parents[2]

COMPARED = ("name", "description", "body")


def parse_md(text: str) -> dict[str, str]:
    """Pull name, description, and body out of a Markdown file with optional YAML frontmatter."""
    fields: dict[str, str] = {"name": "", "description": "", "body": text.strip()}
    if not text.startswith("---\n"):
        return fields
    rest = text[4:]
    end = rest.find("\n---\n")
    if end < 0:
        return fields
    for line in rest[:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() in ("name", "description"):
            fields[key.strip()] = value.strip()
    fields["body"] = rest[end + 5 :].strip()
    return fields


def parse_toml(text: str) -> dict[str, str]:
    """Pull name, description, and developer_instructions (as body) from a Codex agent TOML."""
    data = tomllib.loads(text)
    return {
        "name": str(data.get("name", "")),
        "description": str(data.get("description", "")),
        "body": str(data.get("developer_instructions", "")).strip(),
    }


def parse_file(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return parse_toml(text) if path.suffix == ".toml" else parse_md(text)


def compare(
    left: dict[str, str], right: dict[str, str], left_path: str, right_path: str
) -> list[str]:
    errors: list[str] = []
    for key in COMPARED:
        if left[key].strip() != right[key].strip():
            errors.append(f"{left_path} ↔ {right_path}: {key} differs")
    return errors


def expected_pairs(root: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for md in sorted((root / ".claude" / "agents").glob("*.md")):
        pairs.append((md, root / ".codex" / "agents" / f"{md.stem}.toml"))
    skills = root / ".claude" / "skills"
    if skills.is_dir():
        for skill_md in sorted(skills.glob("*/SKILL.md")):
            pairs.append(
                (
                    skill_md,
                    root / ".codex" / "skills" / skill_md.parent.name / "SKILL.md",
                )
            )
    return pairs


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def validate() -> list[str]:
    root = ROOT
    pairs = expected_pairs(root)
    errors: list[str] = []
    expected_codex = {right.resolve() for _, right in pairs}
    for left, right in pairs:
        if not right.is_file():
            errors.append(
                f"{_rel(root, right)}: missing Codex counterpart of {left.name}"
            )
            continue
        errors.extend(
            compare(
                parse_file(left),
                parse_file(right),
                _rel(root, left),
                _rel(root, right),
            )
        )
    agents_dir = root / ".codex" / "agents"
    if agents_dir.is_dir():
        for toml in sorted(agents_dir.glob("*.toml")):
            if toml.resolve() not in expected_codex:
                errors.append(f"{_rel(root, toml)}: Codex agent has no Claude source")
    skills_dir = root / ".codex" / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            if skill_md.resolve() not in expected_codex:
                errors.append(
                    f"{_rel(root, skill_md)}: Codex skill has no Claude source"
                )
    return errors


def selftest() -> None:
    md = parse_md("---\nname: x\ndescription: y\n---\n\nBody.\n")
    assert md == {"name": "x", "description": "y", "body": "Body."}, md
    toml = parse_toml(
        'name = "x"\ndescription = "y"\ndeveloper_instructions = "Body."\n'
    )
    assert toml == {"name": "x", "description": "y", "body": "Body."}, toml
    assert compare(md, toml, "a", "b") == []
    drifted = dict(toml, body="Other.")
    assert compare(md, drifted, "a", "b")
    print("selftest ok")


def main() -> int:
    if "--selftest" in sys.argv:
        selftest()
        return 0
    errors = validate()
    if errors:
        print("Claude↔Codex mirror check failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
