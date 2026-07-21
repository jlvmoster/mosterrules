"""Unit tests for the new-rule dedup guard (guard_new_rule.py).

Stdlib unittest, no framework — mirrors test_validate_rules.py. The hook lives
outside any import package, so we load it by path, drive its pure helpers on
synthetic input, and drive its git-touching helpers with subprocess mocked so the
tests assert observable behavior (return values, exit codes, stderr) rather than
how the parse or the git call is wired.

Run: uv run python -m unittest discover -s .claude/hooks -p 'test_*.py'
     uv run python .claude/hooks/test_guard_new_rule.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_spec = importlib.util.spec_from_file_location(
    "guard_new_rule", Path(__file__).with_name("guard_new_rule.py")
)
assert _spec and _spec.loader
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


def _completed(returncode: int = 0, stdout: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout)


class BlockquoteTests(unittest.TestCase):
    def test_extracts_opening_quote_after_title(self) -> None:
        self.assertEqual(guard.blockquote("# T\n\n> Hello.\n"), "Hello.")

    def test_tolerates_blank_lines_between_title_and_quote(self) -> None:
        self.assertEqual(guard.blockquote("# T\n\n\n> Hello.\n"), "Hello.")

    def test_empty_when_no_h1_title(self) -> None:
        self.assertEqual(guard.blockquote("## Sub\n\n> Hello.\n"), "")

    def test_empty_when_line_after_title_is_not_a_quote(self) -> None:
        self.assertEqual(guard.blockquote("# T\n\nParagraph.\n"), "")

    def test_later_quote_does_not_stand_in_for_opening(self) -> None:
        self.assertEqual(guard.blockquote("# T\n\nPara.\n\n> later.\n"), "")


class WrittenPathTests(unittest.TestCase):
    def test_returns_file_path_from_tool_input(self) -> None:
        self.assertEqual(
            guard.written_path({"tool_input": {"file_path": "rules/x.md"}}),
            "rules/x.md",
        )

    def test_none_when_no_tool_input(self) -> None:
        self.assertIsNone(guard.written_path({}))

    def test_none_when_no_file_path(self) -> None:
        self.assertIsNone(guard.written_path({"tool_input": {}}))

    def test_none_when_file_path_empty(self) -> None:
        self.assertIsNone(guard.written_path({"tool_input": {"file_path": ""}}))

    def test_none_when_tool_input_not_a_dict(self) -> None:
        self.assertIsNone(guard.written_path({"tool_input": "nope"}))


class IsRuleTests(unittest.TestCase):
    def test_rule_under_rules_dir(self) -> None:
        self.assertTrue(guard.is_rule("rules/foo.md"))

    def test_absolute_rule_path(self) -> None:
        self.assertTrue(guard.is_rule(str(guard.RULES / "foo.md")))

    def test_readme_is_not_a_rule(self) -> None:
        self.assertFalse(guard.is_rule("rules/README.md"))

    def test_file_outside_rules_dir(self) -> None:
        self.assertFalse(guard.is_rule("main.py"))
        self.assertFalse(guard.is_rule(".claude/hooks/guard_new_rule.py"))

    def test_nested_under_rules_is_not_a_rule(self) -> None:
        self.assertFalse(guard.is_rule("rules/sub/foo.md"))

    def test_non_markdown_is_not_a_rule(self) -> None:
        self.assertFalse(guard.is_rule("rules/foo.txt"))


class RenderTests(unittest.TestCase):
    def test_lists_each_entry_and_the_dry_instruction(self) -> None:
        out = guard.render([("a.md", "First."), ("b.md", "Second.")])
        self.assertIn("  - a.md — First.", out)
        self.assertIn("  - b.md — Second.", out)
        self.assertIn("DRY / YAGNI", out)
        self.assertIn("Single Source of Truth", out)


class IsTrackedTests(unittest.TestCase):
    def test_true_when_git_exits_zero(self) -> None:
        with mock.patch.object(guard.subprocess, "run", return_value=_completed(0)):
            self.assertTrue(guard.is_tracked("rules/foo.md"))

    def test_false_when_git_exits_nonzero(self) -> None:
        with mock.patch.object(guard.subprocess, "run", return_value=_completed(1)):
            self.assertFalse(guard.is_tracked("rules/foo.md"))


class UntrackedRulesTests(unittest.TestCase):
    def _names(self, stdout: str) -> set[str]:
        with mock.patch.object(
            guard.subprocess, "run", return_value=_completed(0, stdout)
        ):
            return guard.untracked_rules()

    def test_collects_untracked_markdown(self) -> None:
        self.assertEqual(self._names("?? rules/new.md\n"), {"new.md"})

    def test_ignores_modified_rules(self) -> None:
        self.assertEqual(self._names(" M rules/edited.md\n"), set())

    def test_ignores_readme_and_non_markdown(self) -> None:
        stdout = "?? rules/README.md\n?? rules/notes.txt\n?? rules/real.md\n"
        self.assertEqual(self._names(stdout), {"real.md"})


class NewRuleNamesTests(unittest.TestCase):
    def test_new_untracked_rule_from_payload(self) -> None:
        payload = {"tool_input": {"file_path": "rules/new.md"}}
        with mock.patch.object(guard, "is_tracked", return_value=False):
            self.assertEqual(guard.new_rule_names(payload), {"new.md"})

    def test_tracked_rule_edit_is_not_new(self) -> None:
        payload = {"tool_input": {"file_path": "rules/existing.md"}}
        with mock.patch.object(guard, "is_tracked", return_value=True):
            self.assertEqual(guard.new_rule_names(payload), set())

    def test_non_rule_write_is_not_new(self) -> None:
        self.assertEqual(
            guard.new_rule_names({"tool_input": {"file_path": "main.py"}}), set()
        )

    def test_no_path_falls_back_to_git_scan(self) -> None:
        with mock.patch.object(guard, "untracked_rules", return_value={"scanned.md"}):
            self.assertEqual(guard.new_rule_names({}), {"scanned.md"})


class EntriesForTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.rules_dir = Path(self._tmp.name)
        patcher = mock.patch.object(guard, "RULES", self.rules_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _write(self, name: str, quote: str) -> None:
        (self.rules_dir / name).write_text(f"# T\n\n> {quote}\n", encoding="utf-8")

    def test_lists_rules_with_blockquotes_sorted(self) -> None:
        self._write("foo.md", "Foo line.")
        self._write("bar.md", "Bar line.")
        self.assertEqual(
            guard.entries_for(set()),
            [("bar.md", "Bar line."), ("foo.md", "Foo line.")],
        )

    def test_excludes_the_new_rule_being_created(self) -> None:
        self._write("foo.md", "Foo line.")
        self._write("new.md", "New line.")
        self.assertEqual(guard.entries_for({"new.md"}), [("foo.md", "Foo line.")])

    def test_missing_blockquote_becomes_placeholder(self) -> None:
        (self.rules_dir / "foo.md").write_text("# T\n\nno quote\n", encoding="utf-8")
        self.assertEqual(guard.entries_for(set()), [("foo.md", "(no blockquote)")])


class MainTests(unittest.TestCase):
    """The observable contract the harness sees: exit code + stderr feedback."""

    def _run(self, payload_json: str, *, tracked: bool) -> tuple[int, str]:
        stderr = io.StringIO()
        with (
            mock.patch.object(guard.sys, "stdin", io.StringIO(payload_json)),
            mock.patch.object(guard, "is_tracked", return_value=tracked),
            mock.patch.object(guard, "entries_for", return_value=[("foo.md", "Foo.")]),
            contextlib.redirect_stderr(stderr),
        ):
            code = guard.main()
        return code, stderr.getvalue()

    def test_new_rule_blocks_with_feedback(self) -> None:
        code, err = self._run(
            '{"tool_input": {"file_path": "rules/new.md"}}', tracked=False
        )
        self.assertEqual(code, 2)
        self.assertIn("DRY / YAGNI", err)

    def test_edit_to_existing_rule_is_silent(self) -> None:
        code, err = self._run(
            '{"tool_input": {"file_path": "rules/old.md"}}', tracked=True
        )
        self.assertEqual(code, 0)
        self.assertEqual(err, "")


class SelfTestTests(unittest.TestCase):
    def test_bundled_selftest_passes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            guard.selftest()  # asserts internally; raises if a helper regresses


if __name__ == "__main__":
    unittest.main()
