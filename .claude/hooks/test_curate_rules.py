"""Unit tests for the rule-curator Stop trigger (curate_rules.py).

Stdlib unittest, no framework — mirrors test_validate_rules.py. Loads the hook by
path, then asserts observable behavior: the change-detection predicate, and main's
exit-code contract (block once, then step aside under the stop_hook_active guard).

Run: uv run python -m unittest discover -s .claude/hooks -p 'test_*.py'
     uv run python .claude/hooks/test_curate_rules.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import unittest
from pathlib import Path
from unittest import mock

_spec = importlib.util.spec_from_file_location(
    "curate_rules", Path(__file__).with_name("curate_rules.py")
)
assert _spec and _spec.loader
curate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(curate)


class RulesChangedTests(unittest.TestCase):
    def test_true_for_modified_rule(self) -> None:
        self.assertTrue(curate.rules_changed(" M rules/foo.md\n"))

    def test_true_for_untracked_rule(self) -> None:
        self.assertTrue(curate.rules_changed("?? rules/new.md\n"))

    def test_false_for_empty_output(self) -> None:
        self.assertFalse(curate.rules_changed(""))

    def test_false_for_blank_lines_only(self) -> None:
        self.assertFalse(curate.rules_changed("\n   \n"))


class MessageTests(unittest.TestCase):
    def test_names_the_curator_subagent(self) -> None:
        self.assertIn("rule-curator", curate.MESSAGE)


class MainTests(unittest.TestCase):
    def _run(self, *, changed: bool, stop_active: bool) -> tuple[int, str]:
        stderr = io.StringIO()
        payload = f'{{"stop_hook_active": {str(stop_active).lower()}}}'
        status = " M rules/foo.md\n" if changed else ""
        with (
            mock.patch.object(curate.sys, "stdin", io.StringIO(payload)),
            mock.patch.object(curate, "git_status", return_value=status),
            contextlib.redirect_stderr(stderr),
        ):
            code = curate.main()
        return code, stderr.getvalue()

    def test_blocks_once_when_rules_changed(self) -> None:
        code, err = self._run(changed=True, stop_active=False)
        self.assertEqual(code, 2)
        self.assertIn("rule-curator", err)

    def test_steps_aside_when_already_active(self) -> None:
        # Loop guard: the nudge still prints, but the stop is allowed so it can't loop.
        code, _ = self._run(changed=True, stop_active=True)
        self.assertEqual(code, 0)

    def test_silent_when_rules_unchanged(self) -> None:
        code, err = self._run(changed=False, stop_active=False)
        self.assertEqual(code, 0)
        self.assertEqual(err, "")


class SelfTestTests(unittest.TestCase):
    def test_bundled_selftest_passes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            curate.selftest()  # asserts internally; raises if the predicate regresses


if __name__ == "__main__":
    unittest.main()
