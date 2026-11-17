# this_file: tests_docs/test_name_records.py
"""Check fictional naming comparisons without parsing or changing a font."""

import ast
import contextlib
from copy import deepcopy
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/16-check-output-records.md"


class NameRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.code = blocks[0]
        self.namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), self.namespace)
        self.output = output.getvalue()
        self.expected_output = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)[0] + "\n"
        self.compare = self.namespace["compare_names"]

    def test_exact_stable_output_and_no_imports(self) -> None:
        self.assertEqual(self.output, self.expected_output)
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom))
                             for n in ast.walk(ast.parse(self.code))))
        keys = [(17, 3, 1, 1033), (6, 3, 1, 1033)]
        lines = self.compare(dict.fromkeys(keys, "Name"), {})
        self.assertTrue(lines[0].startswith(str(keys[0])))
        self.assertTrue(lines[1].startswith(str(keys[1])))

    def test_each_record_key_dimension_matters(self) -> None:
        key = (16, 3, 1, 1033)
        for other in [(17, 3, 1, 1033), (16, 0, 1, 1033),
                      (16, 3, 10, 1033), (16, 3, 1, 1031)]:
            with self.subTest(other=other):
                self.assertEqual(self.compare({key: "Name"}, {other: "Name"}),
                                 [f"{key}: missing; expected 'Name'"])

    def test_empty_string_is_present_and_exact_comparison_is_used(self) -> None:
        key = (16, 3, 1, 1033)
        self.assertEqual(self.compare({key: "Name"}, {key: ""}),
                         [f"{key}: differs; expected 'Name', observed ''"])
        self.assertEqual(self.compare({key: ""}, {key: ""}), [f"{key}: matches"])
        self.assertIn("differs", self.compare({key: "Name"}, {key: "name"})[0])

    def test_inputs_preserved_and_repeated_results_independent(self) -> None:
        expected, observed = deepcopy((self.namespace["expected"], self.namespace["observed"]))
        before = deepcopy((expected, observed))
        first = self.compare(expected, observed)
        second = self.compare(expected, observed)
        self.assertEqual(first, second)
        first.clear()
        self.assertEqual(len(second), 3)
        self.assertEqual((expected, observed), before)

    def test_empty_expected_and_extra_observed_records(self) -> None:
        key, extra = (16, 3, 1, 1033), (16, 3, 1, 1031)
        self.assertEqual(self.compare({}, {extra: "Extra"}), [])
        self.assertEqual(self.compare({key: "Name"}, {key: "Name", extra: "Extra"}),
                         [f"{key}: matches"])


if __name__ == "__main__":
    unittest.main()
