# this_file: tests_docs/test_ownership.py
"""Verify ordinary Python ownership examples, never native wrapper behavior."""

import ast
import contextlib
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/24-keep-values-separate-from-handles.md"


class OwnershipTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.code = blocks[0]
        self.namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), self.namespace)
        self.record = self.namespace["record_values"]
        self.output = output.getvalue()
        self.expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)[0] + "\n"

    def test_output_matches_without_native_or_file_calls(self) -> None:
        self.assertEqual(self.output, self.expected)
        tree = ast.parse(self.code)
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)))
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            if isinstance(call.func, ast.Name):
                self.assertIn(call.func.id, {"record_values", "tuple", "print", "len"})
            else:
                self.assertIsInstance(call.func, ast.Attribute)
                self.assertIn(call.func.attr, {"copy", "append"})

    def test_shallow_copy_shares_points_but_keeps_old_width_binding(self) -> None:
        alias, shallow = self.namespace["alias"], self.namespace["shallow"]
        self.assertIsNot(alias, shallow)
        self.assertIs(alias["points"], shallow["points"])
        self.assertEqual((alias["width"], shallow["width"]), (620, 600))
        self.assertEqual(len(shallow["points"]), 3)

    def test_record_retains_values_after_source_changes(self) -> None:
        self.assertEqual(self.namespace["record"], ("orchard-1", "A", 600, ((0, 0), (10, 20))))

    def test_rebinding_source_does_not_retarget_alias(self) -> None:
        current, alias = self.namespace["source"], self.namespace["alias"]
        self.assertIsNot(current, alias)
        self.assertEqual((current["font_id"], alias["font_id"]), ("orchard-2", "orchard-1"))
        self.assertEqual(alias["width"], 620)

    def test_recording_empty_points_leaves_input_unchanged(self) -> None:
        points = []
        source = {"font_id": "sample", "glyph": "space", "width": 250, "points": points}
        self.assertEqual(self.record(source), ("sample", "space", 250, ()))
        self.assertIs(source["points"], points)
        self.assertEqual(points, [])
        self.assertEqual(source["width"], 250)

    def test_different_source_identity_is_retained_with_equal_measurements(self) -> None:
        first = {"font_id": "one", "glyph": "A", "width": 600, "points": [(0, 0)]}
        second = first.copy()
        second["font_id"] = "two"
        self.assertNotEqual(self.record(first), self.record(second))
        self.assertEqual(self.record(first)[1:], self.record(second)[1:])

    def test_replacing_points_and_rebinding_values_does_not_change_record(self) -> None:
        source = {"font_id": "one", "glyph": "A", "width": 600, "points": [(0, 0)]}
        record = self.record(source)
        source["points"][0] = (999, 999)
        source["glyph"] = "B"
        self.assertEqual(record, ("one", "A", 600, ((0, 0),)))

    def test_missing_required_field_is_not_silently_filled(self) -> None:
        with self.assertRaises(KeyError):
            self.record({"font_id": "one", "glyph": "A", "width": 600})


if __name__ == "__main__":
    unittest.main()
