"""Unit tests for the Claude↔Codex mirror check (check_mirrors.py).

Stdlib unittest, no framework — mirrors test_validate_rules.py. Loads the checker
by path, drives its parsers on synthetic input, and rebinds ROOT to a temp tree
so pair discovery and drift reporting don't depend on the live repo.

Run: uv run python -m unittest discover -s .claude/hooks -p 'test_*.py'
     uv run python .claude/hooks/test_check_mirrors.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_spec = importlib.util.spec_from_file_location(
    "check_mirrors", Path(__file__).with_name("check_mirrors.py")
)
assert _spec and _spec.loader
cm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cm)


CLAUDE_MD = """\
---
name: demo
description: A one-line description.
tools: Read, Grep
---

You review things.

## Output

A short report.
"""

CODEX_TOML = """\
name = "demo"
description = "A one-line description."
sandbox_mode = "read-only"

developer_instructions = \"""
You review things.

## Output

A short report.
\"""
"""

CLAUDE_SKILL = """\
---
name: new-rule
description: Scaffold a rule.
disable-model-invocation: true
---

# new-rule

Do the thing.
"""

CODEX_SKILL = """\
---
name: new-rule
description: Scaffold a rule.
---

# new-rule

Do the thing.
"""


class ParseMdTests(unittest.TestCase):
    def test_extracts_name_description_body(self) -> None:
        parsed = cm.parse_md(CLAUDE_MD)
        self.assertEqual(parsed["name"], "demo")
        self.assertEqual(parsed["description"], "A one-line description.")
        self.assertEqual(
            parsed["body"], "You review things.\n\n## Output\n\nA short report."
        )

    def test_ignores_format_specific_frontmatter(self) -> None:
        parsed = cm.parse_md(CLAUDE_SKILL)
        self.assertEqual(parsed["name"], "new-rule")
        self.assertNotIn("disable-model-invocation", parsed)

    def test_missing_frontmatter_is_empty(self) -> None:
        parsed = cm.parse_md("# Just a title\n\nBody.\n")
        self.assertEqual(parsed["name"], "")
        self.assertEqual(parsed["body"], "# Just a title\n\nBody.")


class ParseTomlTests(unittest.TestCase):
    def test_extracts_name_description_and_instructions(self) -> None:
        parsed = cm.parse_toml(CODEX_TOML)
        self.assertEqual(parsed["name"], "demo")
        self.assertEqual(parsed["description"], "A one-line description.")
        self.assertEqual(
            parsed["body"], "You review things.\n\n## Output\n\nA short report."
        )

    def test_ignores_sandbox_mode(self) -> None:
        parsed = cm.parse_toml(CODEX_TOML)
        self.assertNotIn("sandbox_mode", parsed)


class CompareTests(unittest.TestCase):
    def test_matching_pair_is_silent(self) -> None:
        self.assertEqual(
            cm.compare(cm.parse_md(CLAUDE_MD), cm.parse_toml(CODEX_TOML), "a", "b"),
            [],
        )

    def test_reports_each_differing_field(self) -> None:
        right = cm.parse_toml(CODEX_TOML)
        right["name"] = "other"
        right["body"] = "Different body."
        errors = cm.compare(cm.parse_md(CLAUDE_MD), right, "left.md", "right.toml")
        self.assertTrue(any("name differs" in e for e in errors))
        self.assertTrue(any("body differs" in e for e in errors))
        self.assertFalse(any("description differs" in e for e in errors))

    def test_body_comparison_is_strip_normalized(self) -> None:
        left = cm.parse_md(CLAUDE_MD)
        right = cm.parse_toml(CODEX_TOML)
        right["body"] = right["body"] + "\n\n"
        self.assertEqual(cm.compare(left, right, "a", "b"), [])


class _TempRootTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        patcher = mock.patch.object(cm, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _write_pair(self) -> None:
        claude_agents = self.root / ".claude" / "agents"
        codex_agents = self.root / ".codex" / "agents"
        claude_skill = self.root / ".claude" / "skills" / "new-rule"
        codex_skill = self.root / ".codex" / "skills" / "new-rule"
        for d in (claude_agents, codex_agents, claude_skill, codex_skill):
            d.mkdir(parents=True)
        (claude_agents / "demo.md").write_text(CLAUDE_MD, encoding="utf-8")
        (codex_agents / "demo.toml").write_text(CODEX_TOML, encoding="utf-8")
        (claude_skill / "SKILL.md").write_text(CLAUDE_SKILL, encoding="utf-8")
        (codex_skill / "SKILL.md").write_text(CODEX_SKILL, encoding="utf-8")


class ExpectedPairsTests(_TempRootTest):
    def test_discovers_agent_and_skill_pairs(self) -> None:
        self._write_pair()
        pairs = cm.expected_pairs(self.root)
        stems = {(left.name, right.name) for left, right in pairs}
        self.assertEqual(stems, {("demo.md", "demo.toml"), ("SKILL.md", "SKILL.md")})

    def test_missing_codex_counterpart_is_an_error(self) -> None:
        self._write_pair()
        (self.root / ".codex" / "agents" / "demo.toml").unlink()
        errors = cm.validate()
        self.assertTrue(any("demo.toml" in e and "missing" in e for e in errors))

    def test_codex_orphan_is_an_error(self) -> None:
        self._write_pair()
        (self.root / ".codex" / "agents" / "ghost.toml").write_text(
            'name = "ghost"\ndescription = "x"\ndeveloper_instructions = "y"\n',
            encoding="utf-8",
        )
        errors = cm.validate()
        self.assertTrue(
            any("ghost.toml" in e and "no Claude source" in e for e in errors)
        )

    def test_matching_tree_is_clean(self) -> None:
        self._write_pair()
        self.assertEqual(cm.validate(), [])

    def test_body_drift_is_reported(self) -> None:
        self._write_pair()
        drifted = CODEX_TOML.replace("You review things.", "You review other things.")
        (self.root / ".codex" / "agents" / "demo.toml").write_text(
            drifted, encoding="utf-8"
        )
        errors = cm.validate()
        self.assertTrue(any("body differs" in e for e in errors))


class LiveRepoTests(unittest.TestCase):
    def test_checked_in_mirrors_agree(self) -> None:
        # The invariant the CI step exists for: Claude and Codex prose match.
        self.assertEqual(cm.validate(), [])


class SelfTestTests(unittest.TestCase):
    def test_bundled_selftest_passes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            cm.selftest()


class MainExitTests(unittest.TestCase):
    def test_blocks_on_drift(self) -> None:
        with (
            mock.patch.object(cm, "validate", return_value=["some drift"]),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(cm.main(), 2)

    def test_clean_tree_exits_zero(self) -> None:
        with mock.patch.object(cm, "validate", return_value=[]):
            self.assertEqual(cm.main(), 0)


if __name__ == "__main__":
    unittest.main()
