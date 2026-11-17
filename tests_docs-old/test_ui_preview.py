# this_file: tests_docs/test_ui_preview.py
"""Verify preview data logic without constructing or importing any GUI."""

import ast
import contextlib
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/11-choose-a-ui-approach.md"


class UIPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        code = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(code), 1)
        self.code = code[0]
        self.namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), self.namespace)
        self.output = output.getvalue()
        expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(expected), 1)
        self.expected = expected[0] + "\n"

    def test_exact_sample_matches_expected_output_without_gui_imports(self) -> None:
        self.assertEqual(self.output, self.expected)
        self.assertFalse(
            any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(ast.parse(self.code)))
        )
        self.assertEqual(self.namespace["sample_text"], " A  A.alt\nspace smile ")

    def test_empty_and_whitespace_input_has_an_explicit_prompt(self) -> None:
        for text in ("", " ", "\t\n\r "):
            with self.subTest(text=text):
                self.assertEqual(
                    self.namespace["preview_text"](text), "Enter at least one glyph name."
                )

    def test_short_and_exact_limit_inputs_do_not_claim_hidden_names(self) -> None:
        for text, expected in (
            ("A", "Supplied names: 1\nA"),
            ("A space B", "Supplied names: 3\nA\nspace\nB"),
        ):
            with self.subTest(text=text):
                self.assertEqual(self.namespace["preview_text"](text), expected)

    def test_mixed_whitespace_duplicates_and_unicode_keep_input_order(self) -> None:
        text = "  A\tA\nΩ\rspace\nA.alt  "
        before = text
        self.assertEqual(
            self.namespace["preview_text"](text),
            "Supplied names: 5\nA\nA\nΩ\nNot shown: 2",
        )
        self.assertEqual(text, before)

    def test_repeated_requests_return_independent_results_without_printing(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            first = self.namespace["preview_text"]("A B C D")
            empty = self.namespace["preview_text"]("")
            again = self.namespace["preview_text"]("A B C D")
        self.assertEqual(first, again)
        self.assertEqual(empty, "Enter at least one glyph name.")
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
