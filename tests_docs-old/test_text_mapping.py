# this_file: tests_docs/test_text_mapping.py
"""Check fictional assignment reporting without running a shaping engine."""

import ast
import contextlib
from copy import deepcopy
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/25-mapping-is-not-shaping.md"


class TextMappingTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.code = blocks[0]
        self.namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), self.namespace)
        self.rows = self.namespace["assignment_rows"]
        self.output = output.getvalue()
        self.expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)[0] + "\n"

    def test_output_matches_and_calls_only_assignment_reporting(self) -> None:
        self.assertEqual(self.output, self.expected)
        tree = ast.parse(self.code)
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)))
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            if isinstance(call.func, ast.Name):
                self.assertIn(call.func.id, {"assignment_rows", "enumerate", "ord", "len", "tuple", "print"})
            else:
                self.assertIsInstance(call.func, ast.Attribute)
                self.assertIn(call.func.attr, {"items", "append"})

    def test_empty_text_and_empty_inventory_remain_explicit(self) -> None:
        self.assertEqual(self.rows("", {"A": (65,)}), [])
        self.assertEqual(self.rows("A", {}), [(0, 65, "missing", ())])

    def test_multiple_assignments_reach_one_name_independently(self) -> None:
        self.assertEqual(self.rows(" \u00a0", {"space": (0x20, 0xA0)}), [
            (0, 0x20, "unique", ("space",)), (1, 0xA0, "unique", ("space",)),
        ])

    def test_ambiguous_assignments_keep_all_names_in_inventory_order(self) -> None:
        self.assertEqual(self.rows("A", {"A.backup": (65,), "A": (65,)}), [
            (0, 65, "ambiguous", ("A.backup", "A")),
        ])

    def test_duplicate_code_in_one_entry_is_still_one_candidate(self) -> None:
        self.assertEqual(self.rows("A", {"A": (65, 65)}), [(0, 65, "unique", ("A",))])

    def test_unencoded_ligature_is_not_selected_by_character_pair(self) -> None:
        rows = self.rows("fi", {"f": (102,), "i": (105,), "f_i": ()})
        self.assertEqual(rows, [(0, 102, "unique", ("f",)), (1, 105, "unique", ("i",))])

    def test_precomposed_and_decomposed_inputs_are_not_normalized(self) -> None:
        inventory = {"A": (65,), "acutecomb": (0x301,)}
        self.assertEqual(self.rows("\u00c1", inventory), [(0, 0xC1, "missing", ())])
        self.assertEqual(self.rows("A\u0301", inventory), [
            (0, 65, "unique", ("A",)), (1, 0x301, "unique", ("acutecomb",)),
        ])

    def test_supplementary_codepoint_is_one_python_position(self) -> None:
        self.assertEqual(self.rows("\U0001f642A", {}), [
            (0, 0x1F642, "missing", ()), (1, 65, "missing", ()),
        ])
        self.assertEqual(f"{0x1F642:04X}", "1F642")

    def test_zero_codepoint_is_not_treated_as_missing_by_truthiness(self) -> None:
        self.assertEqual(self.rows("\x00", {"zero-code-example": (0,)}), [
            (0, 0, "unique", ("zero-code-example",)),
        ])

    def test_repeated_input_keeps_positions_without_changing_inventory(self) -> None:
        inventory = {"A": [65], "A.backup": [65], "B": [66]}
        before = deepcopy(inventory)
        text = "ABA"
        result = self.rows(text, inventory)
        self.assertEqual([row[0] for row in result], [0, 1, 2])
        self.assertEqual([row[1] for row in result], [65, 66, 65])
        self.assertEqual(result[0][2:], result[2][2:])
        self.assertEqual(inventory, before)
        self.assertEqual(text, "ABA")


if __name__ == "__main__":
    unittest.main()
