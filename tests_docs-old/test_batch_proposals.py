# this_file: tests_docs/test_batch_proposals.py
"""Check fictional target proposals without native execution or file writes."""

import ast
import contextlib
from copy import deepcopy
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/23-name-the-batch-targets.md"


class BatchProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.code = blocks[0]
        namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), namespace)
        self.propose = namespace["propose"]
        self.output = output.getvalue()
        self.expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)[0] + "\n"

    def test_example_output_matches_with_no_imports_or_execution_calls(self) -> None:
        self.assertEqual(self.output, self.expected)
        tree = ast.parse(self.code)
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)))
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            if isinstance(call.func, ast.Name):
                self.assertIn(call.func.id, {"propose", "set", "print"})
            else:
                self.assertIsInstance(call.func, ast.Attribute)
                self.assertIn(call.func.attr, {"get", "add", "append"})

    def test_empty_requests_never_expand_to_all_glyphs(self) -> None:
        self.assertEqual(self.propose([], {"A": {"Regular": "editable"}}), [])

    def test_distinct_target_order_and_duplicates_are_explicit(self) -> None:
        inventory = {"A": {"Regular": "editable"}, "V": {"Regular": "editable"}}
        requests = [("V", "Regular"), ("A", "Regular"), ("V", "Regular")]
        self.assertEqual(self.propose(requests, inventory), [
            ("V", "Regular", "proposed"), ("A", "Regular", "proposed"),
            ("V", "Regular", "duplicate request"),
        ])

    def test_same_glyph_in_two_layers_is_two_targets(self) -> None:
        inventory = {"A": {"Regular": "editable", "Bold": "editable"}}
        self.assertEqual(self.propose([("A", "Bold"), ("A", "Regular")], inventory), [
            ("A", "Bold", "proposed"), ("A", "Regular", "proposed"),
        ])

    def test_missing_glyph_and_missing_layer_remain_distinct(self) -> None:
        self.assertEqual(self.propose([("X", "Regular"), ("A", "Bold")], {"A": {}}), [
            ("X", "Regular", "missing glyph"), ("A", "Bold", "missing layer"),
        ])

    def test_locked_automatic_and_unknown_states_are_not_proposed(self) -> None:
        inventory = {"A": {"Regular": "locked", "Bold": "automatic", "Light": "unknown"}}
        self.assertEqual(self.propose([("A", key) for key in inventory["A"]], inventory), [
            ("A", "Regular", "locked"), ("A", "Bold", "automatic"),
            ("A", "Light", "unsupported state"),
        ])

    def test_duplicate_missing_target_does_not_hide_first_reason(self) -> None:
        self.assertEqual(self.propose([("X", "Regular"), ("X", "Regular")], {}), [
            ("X", "Regular", "missing glyph"), ("X", "Regular", "duplicate request"),
        ])

    def test_inputs_are_unchanged(self) -> None:
        requests = [("A", "Regular"), ("A", "Bold"), ("X", "Regular")]
        inventory = {"A": {"Regular": "editable", "Bold": "automatic"}}
        before = deepcopy((requests, inventory))
        self.propose(requests, inventory)
        self.assertEqual((requests, inventory), before)


if __name__ == "__main__":
    unittest.main()
