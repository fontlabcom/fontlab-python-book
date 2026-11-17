# this_file: tests_docs/test_ecosystem.py
"""Check a fictional requirements inventory without importing host packages."""

import ast
import contextlib
from copy import deepcopy
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/18-choose-the-typerig-layer.md"


class EcosystemInventoryTests(unittest.TestCase):
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
        self.expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)[0] + "\n"
        self.report = self.namespace["requirement_report"]

    def test_exact_output_without_imports(self) -> None:
        self.assertEqual(self.output, self.expected)
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom))
                             for n in ast.walk(ast.parse(self.code))))

    def test_missing_requirements_follow_declared_order(self) -> None:
        entries = [{"name": "Owned example", "requires": ["FontLab", "PythonQt"]}]
        self.assertEqual(self.report(entries, []),
                         ["Owned example: missing from inventory: FontLab, PythonQt"])
        self.assertEqual(self.report(entries, ["FontLab"]),
                         ["Owned example: missing from inventory: PythonQt"])

    def test_present_requirements_still_leave_compatibility_untested(self) -> None:
        entries = [{"name": "Owned example", "requires": ["FontLab"]}]
        self.assertEqual(self.report(entries, ["FontLab"]),
                         ["Owned example: listed requirements present; compatibility untested"])

    def test_none_and_empty_requirements_do_not_claim_compatibility(self) -> None:
        for requirements in (None, []):
            with self.subTest(requirements=requirements):
                entries = [{"name": "Unknown", "requires": requirements}]
                self.assertEqual(self.report(entries, ["FontLab"]),
                                 ["Unknown: requirements not recorded"])
        self.assertEqual(self.report([], []), [])

    def test_inputs_preserved_and_returned_lists_independent(self) -> None:
        entries = deepcopy(self.namespace["examples"])
        available = ["external Python"]
        before = deepcopy((entries, available))
        first = self.report(entries, available)
        second = self.report(entries, available)
        first.clear()
        self.assertEqual(len(second), 3)
        self.assertEqual((entries, available), before)

    def test_labels_are_exact_and_missing_record_keys_raise(self) -> None:
        self.assertEqual(self.report([{"name": "Case", "requires": ["FontLab"]}],
                                     ["fontlab"]),
                         ["Case: missing from inventory: FontLab"])
        with self.assertRaises(KeyError):
            self.report([{"name": "Incomplete"}], [])


if __name__ == "__main__":
    unittest.main()
