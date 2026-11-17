# this_file: tests_docs/test_variation.py
"""Verify a fictional one-axis calculation, without a native variation engine."""

import ast
import contextlib
from copy import deepcopy
import io
import math
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/15-identify-the-location.md"


class VariationIllustrationTests(unittest.TestCase):
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

    def test_exact_output_and_math_only_import(self) -> None:
        self.assertEqual(self.output, self.expected)
        imports = [n for n in ast.walk(ast.parse(self.code))
                   if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 1)
        self.assertIsInstance(imports[0], ast.ImportFrom)
        self.assertEqual(imports[0].module, "math")

    def test_endpoints_and_interior_keep_coordinate_spaces_separate(self) -> None:
        sample = self.namespace["sample_width"]
        left, right = self.namespace["light"], self.namespace["bold"]
        for user, fraction, design, width in [
            (300, 0, 0, 500), (400, 0.25, 25, 550),
            (500, 0.5, 50, 600), (700, 1, 100, 700),
            (450.5, 0.37625, 37.625, 575.25),
        ]:
            with self.subTest(user=user):
                result = sample(user, left, right)
                self.assertEqual(result["user"], user)
                self.assertAlmostEqual(result["fraction"], fraction)
                self.assertAlmostEqual(result["design"], design)
                self.assertAlmostEqual(result["width"], width)

    def test_invalid_requests_do_not_extrapolate_or_accept_boolean(self) -> None:
        sample = self.namespace["sample_width"]
        for user in (299.9, 700.1, math.nan, math.inf, -math.inf, True, "400", None):
            with self.subTest(user=user), self.assertRaises(ValueError):
                sample(user, self.namespace["light"], self.namespace["bold"])

    def test_equal_or_reversed_user_endpoints_are_rejected(self) -> None:
        sample = self.namespace["sample_width"]
        left, right = deepcopy((self.namespace["light"], self.namespace["bold"]))
        right["user"] = left["user"]
        with self.assertRaisesRegex(ValueError, "increase"):
            sample(300, left, right)
        with self.assertRaisesRegex(ValueError, "increase"):
            sample(500, self.namespace["bold"], self.namespace["light"])

    def test_source_names_and_inputs_are_preserved_without_result_aliasing(self) -> None:
        sample = self.namespace["sample_width"]
        left, right = deepcopy((self.namespace["light"], self.namespace["bold"]))
        left["name"], right["name"] = "First source", "Second source"
        before = deepcopy((left, right))
        result = sample(500, left, right)
        self.assertEqual(result["sources"], ("First source", "Second source"))
        result["width"] = -1
        self.assertEqual(sample(500, left, right)["width"], 600)
        self.assertEqual((left, right), before)

    def test_zero_measurement_is_not_missing_and_missing_metadata_raises(self) -> None:
        sample = self.namespace["sample_width"]
        left, right = deepcopy((self.namespace["light"], self.namespace["bold"]))
        left["width"], right["width"] = 0, 100
        self.assertEqual(sample(300, left, right)["width"], 0)
        del right["design"]
        with self.assertRaises(KeyError):
            sample(400, left, right)


if __name__ == "__main__":
    unittest.main()
