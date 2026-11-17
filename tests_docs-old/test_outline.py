# this_file: tests_docs/test_outline.py
"""Exercise Chapter 7's fictional records, without importing native modules."""

import contextlib
import io
import re
import unittest
from copy import deepcopy
from pathlib import Path

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/07-choose-the-drawing.md"


class DrawingReportTests(unittest.TestCase):
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

    def report(self, layers: dict, name: str) -> str:
        before = deepcopy(layers)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.namespace["report_layer"](layers, name)
        self.assertEqual(layers, before)
        return output.getvalue()

    def test_complete_example_matches_declared_output(self) -> None:
        self.assertEqual(self.output, self.expected)

    def test_missing_layer_differs_from_existing_empty_layer(self) -> None:
        self.assertEqual(self.report({}, "Regular"), "No sample layer named Regular.\n")
        self.assertEqual(
            self.report({"Regular": []}, "Regular"),
            "Layer: Regular\nShapes: 0\nContours: 0 (open: 0)\nStored points: 0\nOn-curve: 0; off-curve: 0\n",
        )

    def test_shapes_without_direct_contours_are_still_counted(self) -> None:
        self.assertEqual(
            self.report({"Image": [{"contours": []}]}, "Image"),
            "Layer: Image\nShapes: 1\nContours: 0 (open: 0)\nStored points: 0\nOn-curve: 0; off-curve: 0\n",
        )

    def test_multiple_shapes_and_all_four_point_kinds(self) -> None:
        layers = {
            "Sample": [
                {
                    "contours": [
                        {"open": False, "points": [("On", 0, 0), ("Curve", 1, 2)]}
                    ]
                },
                {
                    "contours": [
                        {"open": True, "points": [("Move", 3, 4), ("Off", 5, 6)]}
                    ]
                },
            ]
        }
        self.assertEqual(
            self.report(layers, "Sample"),
            "Layer: Sample\nShapes: 2\nContours: 2 (open: 1)\nStored points: 4\nOn-curve: 2; off-curve: 2\n",
        )

    def test_unrecognized_kind_stops_before_success_report(self) -> None:
        layers = {
            "Bad": [{"contours": [{"open": False, "points": [("Unknown", 0, 0)]}]}]
        }
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaisesRegex(
                ValueError, "Unknown sample point kind: Unknown"
            ):
                self.namespace["report_layer"](layers, "Bad")
        self.assertEqual(output.getvalue(), "")

    def test_only_requested_layer_is_read(self) -> None:
        self.assertEqual(
            self.report({"Regular": [], "Unrequested": [{"bad": "record"}]}, "Regular"),
            "Layer: Regular\nShapes: 0\nContours: 0 (open: 0)\nStored points: 0\nOn-curve: 0; off-curve: 0\n",
        )


if __name__ == "__main__":
    unittest.main()
