# this_file: tests_docs/test_proposals.py
"""Run the exact proposal-only exercise on owned data, without native calls."""

import contextlib
import io
import math
import re
import unittest
from copy import deepcopy
from pathlib import Path

CHAPTER = (
    Path(__file__).resolve().parents[1] / "src_docs/md/08-keep-a-recoverable-source.md"
)


class ProposalExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(blocks[0], CHAPTER.name, "exec"), self.namespace)
        self.output = output.getvalue()
        expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(expected), 1)
        self.expected = expected[0] + "\n"

    def render(self, widths: dict, amount: float) -> str:
        before = deepcopy(widths)
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                self.namespace["show_plan"](widths, amount)
        finally:
            self.assertEqual(widths, before)
        return output.getvalue()

    def test_example_matches_declared_output_and_preserves_sample(self) -> None:
        self.assertEqual(self.output, self.expected)
        self.assertEqual(self.namespace["sample_widths"], {"A": 600, "space": 250})

    def test_empty_input_and_zero_adjustment_have_no_proposals(self) -> None:
        self.assertEqual(self.render({}, 20), "Proposed changes: 0\n")
        self.assertEqual(self.render({"A": 600}, 0), "Proposed changes: 0\n")

    def test_zero_result_is_valid_and_input_order_is_preserved(self) -> None:
        self.assertEqual(
            self.render({"space": 20, "A": 600}, -20),
            "Proposed changes: 2\nspace: 20 -> 0\nA: 600 -> 580\n",
        )

    def test_late_invalid_result_prints_no_partial_success(self) -> None:
        widths = {"A": 600, "space": 250}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaisesRegex(ValueError, "Invalid proposed width for space"):
                self.namespace["show_plan"](widths, -300)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(widths, {"A": 600, "space": 250})

    def test_nonfinite_amount_is_rejected_even_for_empty_input(self) -> None:
        for amount in (math.inf, -math.inf, math.nan):
            with self.subTest(amount=amount):
                with self.assertRaisesRegex(ValueError, "Adjustment must be finite"):
                    self.render({}, amount)

    def test_invalid_source_and_overflow_are_not_normalized(self) -> None:
        for widths, amount, message in [
            ({"A": -1}, 20, "Invalid sample width for A"),
            ({"A": math.inf}, 20, "Invalid sample width for A"),
            ({"A": math.nan}, 20, "Invalid sample width for A"),
            ({"A": 1e308}, 1e308, "Invalid proposed width for A"),
        ]:
            with self.subTest(widths=widths, amount=amount):
                with self.assertRaisesRegex(ValueError, message):
                    self.namespace["propose_widths"](widths, amount)


if __name__ == "__main__":
    unittest.main()
