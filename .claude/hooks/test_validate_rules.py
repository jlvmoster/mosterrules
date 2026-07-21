"""Unit tests for the Moster Rules validator (validate_rules.py).

Stdlib unittest, no framework. The hook lives outside any import package, so we
load it by path, then drive its pure parser functions on synthetic input and
exercise check_index/validate against a temporary rules tree (module globals
RULES/README are rebound per test, then restored).

Run: uv run python -m unittest discover -s .claude/hooks -p 'test_*.py'
     uv run python .claude/hooks/test_validate_rules.py
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
    "validate_rules", Path(__file__).with_name("validate_rules.py")
)
assert _spec and _spec.loader
vr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vr)


# The canonical headings, pinned here independently of the validator's own
# SECTIONS. Building the "good" fixtures from vr.SECTIONS would make the oracle
# tautological — corrupt SECTIONS and the fixtures corrupt with it, so the shape
# tests stay green. test_sections_constant_is_canonical is what keeps the two in
# sync, deliberately.
CANONICAL_SECTIONS = [
    "## Principle",
    "## Why it matters for agentic development",
    "## How to apply",
    "## Trade-offs",
    "## Litmus test",
    "## Related",
    "## References",
]


def make_rule(blockquote: str = "One line.", sections: list[str] | None = None) -> str:
    """A canonically-shaped rule body with the given opening blockquote."""
    secs = CANONICAL_SECTIONS if sections is None else sections
    body = "\n\n".join(f"{s}\ntext" for s in secs)
    return f"# Title\n\n> {blockquote}\n\n{body}"


class BlockquoteTests(unittest.TestCase):
    def test_extracts_opening_quote_after_title(self) -> None:
        self.assertEqual(vr.blockquote("# T\n\n> Hello.\n"), "Hello.")

    def test_tolerates_blank_lines_between_title_and_quote(self) -> None:
        self.assertEqual(vr.blockquote("# T\n\n\n> Hello.\n"), "Hello.")

    def test_none_when_no_h1_title(self) -> None:
        self.assertIsNone(vr.blockquote("## Not a title\n\n> Hello.\n"))

    def test_none_when_first_line_after_title_is_not_a_quote(self) -> None:
        self.assertIsNone(vr.blockquote("# T\n\nParagraph, not a quote.\n"))

    def test_later_quote_does_not_stand_in_for_missing_opening(self) -> None:
        # A '> ' further down (e.g. a Litmus test) must not be mistaken for the
        # opening blockquote the title requires.
        text = "# T\n\nParagraph.\n\n## Litmus test\n\n> A question?\n"
        self.assertIsNone(vr.blockquote(text))


class CheckShapeTests(unittest.TestCase):
    def _errors(self, text: str) -> list[str]:
        errors: list[str] = []
        vr.check_shape(Path("x.md"), text, errors)
        return errors

    def test_canonical_shape_passes(self) -> None:
        self.assertEqual(self._errors(make_rule()), [])

    def test_sections_constant_is_canonical(self) -> None:
        # The independent oracle: if the validator's SECTIONS drifts from the
        # canonical shape, this fails even though everything else stays green.
        # Update both lists deliberately, never one to placate the other.
        self.assertEqual(vr.SECTIONS, CANONICAL_SECTIONS)

    def test_missing_title_on_line_one(self) -> None:
        errors = self._errors(make_rule().replace("# Title", "Title", 1))
        self.assertTrue(any("Title" in e or "line 1" in e for e in errors))

    def test_missing_opening_blockquote(self) -> None:
        errors = self._errors(make_rule().replace("> One line.\n\n", ""))
        self.assertTrue(any("blockquote" in e for e in errors))

    def test_renamed_section_fails(self) -> None:
        self.assertTrue(self._errors(make_rule().replace("## Trade-offs", "## Oops")))

    def test_reordered_sections_fail(self) -> None:
        reordered = [
            CANONICAL_SECTIONS[1],
            CANONICAL_SECTIONS[0],
            *CANONICAL_SECTIONS[2:],
        ]
        self.assertTrue(self._errors(make_rule(sections=reordered)))

    def test_extra_section_fails(self) -> None:
        self.assertTrue(
            self._errors(make_rule(sections=[*CANONICAL_SECTIONS, "## Bonus"]))
        )


class CheckRelatedTests(unittest.TestCase):
    def _errors(self, text: str, names: set[str]) -> list[str]:
        errors: list[str] = []
        vr.check_related(Path("x.md"), text, names, errors)
        return errors

    def test_all_link_forms_flagged_when_missing(self) -> None:
        for form in ("missing.md", "./missing.md", "<missing.md>", "missing.md#anchor"):
            with self.subTest(form=form):
                text = f"## Related\n- [a]({form})\n"
                self.assertTrue(self._errors(text, set()))

    def test_existing_target_passes(self) -> None:
        text = "## Related\n- [a](present.md)\n"
        self.assertEqual(self._errors(text, {"present.md"}), [])

    def test_link_outside_related_section_is_ignored(self) -> None:
        text = "## How to apply\n- see [x](missing.md)\n\n## Related\n- nothing here\n"
        self.assertEqual(self._errors(text, set()), [])

    def test_related_section_ends_at_next_heading(self) -> None:
        text = "## Related\n- [a](present.md)\n\n## References\n- [x](missing.md)\n"
        self.assertEqual(self._errors(text, {"present.md"}), [])


class _TempRulesTest(unittest.TestCase):
    """Base class that points the module's RULES/README globals at a temp tree."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.rules_dir = Path(self._tmp.name)
        # patch.object restores the real globals on cleanup, and takes the attr
        # name as a string so ty doesn't flag a write to the dynamic module.
        for name, value in (
            ("RULES", self.rules_dir),
            ("README", self.rules_dir / "README.md"),
        ):
            patcher = mock.patch.object(vr, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write_rule(self, name: str, text: str) -> Path:
        path = self.rules_dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def write_index(self, *rows: str) -> None:
        header = "# Index\n\n| Rule | Principle |\n|---|---|\n"
        (self.rules_dir / "README.md").write_text(
            header + "\n".join(rows) + "\n", encoding="utf-8"
        )


class CheckIndexTests(_TempRulesTest):
    def test_matching_index_passes(self) -> None:
        path = self.write_rule("foo.md", make_rule("A crisp line."))
        self.write_index("| [Foo](foo.md) | A crisp line. |")
        errors: list[str] = []
        vr.check_index([path], errors)
        self.assertEqual(errors, [])

    def test_missing_index_row(self) -> None:
        path = self.write_rule("foo.md", make_rule("A crisp line."))
        self.write_index("| [Bar](bar.md) | Something else. |")
        errors: list[str] = []
        vr.check_index([path], errors)
        self.assertTrue(any("no index row links to foo.md" in e for e in errors))

    def test_blockquote_not_verbatim_in_row(self) -> None:
        path = self.write_rule("foo.md", make_rule("A crisp line."))
        self.write_index("| [Foo](foo.md) | A paraphrased line. |")
        errors: list[str] = []
        vr.check_index([path], errors)
        self.assertTrue(any("blockquote verbatim" in e for e in errors))

    def test_index_row_linking_to_missing_rule(self) -> None:
        path = self.write_rule("foo.md", make_rule("A crisp line."))
        self.write_index(
            "| [Foo](foo.md) | A crisp line. |",
            "| [Ghost](ghost.md) | Gone. |",
        )
        errors: list[str] = []
        vr.check_index([path], errors)
        self.assertTrue(any("missing rule 'ghost.md'" in e for e in errors))


class ValidateTests(_TempRulesTest):
    def test_valid_tree_has_no_errors(self) -> None:
        self.write_rule("foo.md", make_rule("A crisp line."))
        self.write_index("| [Foo](foo.md) | A crisp line. |")
        self.assertEqual(vr.validate(), [])

    def test_drifted_rule_reports_errors(self) -> None:
        self.write_rule(
            "foo.md", make_rule("A crisp line.").replace("## Trade-offs", "## Oops")
        )
        self.write_index("| [Foo](foo.md) | A crisp line. |")
        self.assertTrue(vr.validate())

    def test_rules_without_index(self) -> None:
        self.write_rule("foo.md", make_rule("A crisp line."))  # no README written
        errors = vr.validate()
        self.assertTrue(any("index is missing" in e for e in errors))

    def test_empty_tree_is_not_the_rules_repo(self) -> None:
        self.assertEqual(vr.validate(), [])


class SelfTestTests(unittest.TestCase):
    def test_bundled_selftest_passes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            vr.selftest()  # asserts internally; raises if the parser regresses


if __name__ == "__main__":
    unittest.main()
