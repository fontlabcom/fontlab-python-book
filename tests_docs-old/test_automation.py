# this_file: tests_docs/test_automation.py
"""Check fictional receipts without a transport, host import or native operation."""

import ast
import contextlib
from copy import deepcopy
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/19-know-where-automation-runs.md"


class AutomationReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.code = blocks[0]
        namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), namespace)
        self.report = namespace["receipt_summary"]
        self.output = output.getvalue()
        self.expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)[0] + "\n"

    def test_exact_output_without_imports(self) -> None:
        self.assertEqual(self.output, self.expected)
        tree = ast.parse(self.code)
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom))
                             for n in ast.walk(tree)))
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            local_call = isinstance(call.func, ast.Name) and call.func.id in {
                "type", "print", "receipt_summary"
            }
            data_read = (
                isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "receipt"
                and call.func.attr == "get"
            )
            self.assertTrue(local_call or data_read, ast.dump(call))

    def test_zero_and_positive_counts_are_completed_records(self) -> None:
        for count in (0, 3, 10**30):
            self.assertEqual(self.report("sample", {"request": "sample", "ok": True,
                                                    "count": count}),
                             f"sample: completed; count {count}")

    def test_missing_or_mismatched_receipt_is_unknown(self) -> None:
        for receipt in (None, {}, {"request": "other", "ok": True, "count": 3},
                        {"ok": True, "count": 3}):
            self.assertEqual(self.report("sample", receipt), "sample: outcome unknown")

    def test_success_requires_actual_boolean_true(self) -> None:
        for value in (None, 1, 0, "true", "false", "", []):
            self.assertEqual(self.report("sample", {"request": "sample", "ok": value,
                                                    "count": 3}),
                             "sample: outcome unknown")

    def test_partial_or_invalid_count_is_unknown(self) -> None:
        for count in (None, -1, True, False, 3.0, "3", []):
            self.assertEqual(self.report("sample", {"request": "sample", "ok": True,
                                                    "count": count}),
                             "sample: outcome unknown")
        self.assertEqual(self.report("sample", {"request": "sample", "ok": True}),
                         "sample: outcome unknown")

    def test_explicit_failure_requires_message(self) -> None:
        self.assertEqual(self.report("sample", {"request": "sample", "ok": False,
                                                "error": "No fixture"}),
                         "sample: reported failure; No fixture")
        for error in (None, "", 42):
            self.assertEqual(self.report("sample", {"request": "sample", "ok": False,
                                                    "error": error}),
                             "sample: outcome unknown")

    def test_failure_does_not_become_success_from_present_count(self) -> None:
        receipt = {"request": "sample", "ok": False, "error": "Stopped", "count": 3}
        self.assertEqual(self.report("sample", receipt), "sample: reported failure; Stopped")

    def test_inputs_are_preserved(self) -> None:
        receipt = {"request": "sample", "ok": True, "count": 3,
                   "extra": {"notes": ["fictional"]}}
        before = deepcopy(receipt)
        self.report("sample", receipt)
        self.assertEqual(receipt, before)


if __name__ == "__main__":
    unittest.main()
