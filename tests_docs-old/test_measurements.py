# this_file: tests_docs/test_measurements.py
"""Verify fictional geometric reports without native or filesystem operations."""

import ast
import contextlib
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/22-measure-space-and-drawing.md"


class MeasurementTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.code = blocks[0]
        namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), namespace)
        self.measure = namespace["measure"]
        self.output = output.getvalue()
        self.expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)[0] + "\n"

    def test_printed_report_matches_and_calls_only_pure_math(self) -> None:
        self.assertEqual(self.output, self.expected)
        tree = ast.parse(self.code)
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 1)
        self.assertIsInstance(imports[0], ast.ImportFrom)
        self.assertEqual(imports[0].module, "math")
        self.assertEqual([n.name for n in imports[0].names], ["isfinite"])
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            self.assertIsInstance(call.func, ast.Name)
            self.assertIn(call.func.id, {"measure", "isfinite", "ValueError", "print"})

    def test_ordinary_bearings_reconstruct_advance(self) -> None:
        drawing, left, right = self.measure(600, (40, 0, 540, 700))
        self.assertEqual((drawing, left, right), (500, 40, 60))
        self.assertEqual(drawing + left + right, 600)

    def test_fractional_and_overhanging_bounds_keep_precision(self) -> None:
        bounds = (-10.25, -20.5, 620.75, 700.5)
        before = tuple(bounds)
        self.assertEqual(self.measure(600.5, bounds), (631.0, -10.25, -20.25))
        self.assertEqual(bounds, before)

    def test_blank_and_zero_advance_have_different_results(self) -> None:
        self.assertEqual(self.measure(300, None), (None, None, None))
        self.assertEqual(self.measure(0, (-20, 400, 30, 500)), (50, -20, -30))
        self.assertEqual(self.measure(0, None), (None, None, None))

    def test_degenerate_box_is_not_relabelled_as_no_bounds(self) -> None:
        self.assertEqual(self.measure(100, (10, 20, 10, 20)), (0, 10, 90))

    def test_invalid_advance_is_rejected_even_without_bounds(self) -> None:
        for value in (-1, float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "advance"):
                self.measure(value, None)

    def test_reversed_or_nonfinite_bounds_are_rejected(self) -> None:
        for bounds in ((10, 0, 0, 20), (0, 20, 10, 0)):
            with self.subTest(bounds=bounds), self.assertRaisesRegex(ValueError, "ordered"):
                self.measure(100, bounds)
        for index in range(4):
            for invalid in (float("nan"), float("inf"), -float("inf")):
                bounds = [0, 0, 10, 20]
                bounds[index] = invalid
                with self.subTest(index=index, invalid=invalid), self.assertRaisesRegex(ValueError, "finite"):
                    self.measure(100, tuple(bounds))

    def test_finite_inputs_that_overflow_differences_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite arithmetic"):
            self.measure(1e308, (-1e308, 0, 1e308, 1))

    def test_wrong_length_bounds_remain_explicit_errors(self) -> None:
        for bounds in ((), (0, 1, 2), (0, 1, 2, 3, 4)):
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                self.measure(100, bounds)


if __name__ == "__main__":
    unittest.main()
