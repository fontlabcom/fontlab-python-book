# this_file: tests_docs/test_selection.py
"""Exercise the chapter's fictional selection records without importing FontLab."""

import contextlib
import io
import re
import unittest
from copy import deepcopy
from pathlib import Path

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/09-report-selected-glyphs.md"


class SelectionReportTests(unittest.TestCase):
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
        self.snapshot = deepcopy(self.namespace["sample_snapshot"])
        self.metadata = deepcopy(self.namespace["sample_metadata"])

    def render(self) -> str:
        before = deepcopy((self.snapshot, self.metadata))
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                self.namespace["show_selection"](self.snapshot, self.metadata)
        finally:
            self.assertEqual((self.snapshot, self.metadata), before)
        return output.getvalue()

    def test_example_counts_cells_and_qualified_glyphs_without_changing_inputs(self) -> None:
        self.assertEqual(self.output, self.expected)
        self.assertEqual(self.render(), self.expected)
        self.assertIn("700/11 | first cell 0 | A | U+0041", self.output)
        self.assertIn("701/11 | first cell 4 | A | U+0041 U+1F600", self.output)

    def test_valid_empty_chart_and_no_selection_report_zero(self) -> None:
        for cells in ([], deepcopy(self.snapshot["cells"])):
            with self.subTest(cells=cells):
                for cell in cells:
                    cell["selected"] = False
                self.snapshot["cells"] = cells
                self.assertEqual(
                    self.render(),
                    "Selected cells: 0\nSelected empty cells: 0\nDistinct glyphs: 0\n",
                )

    def test_selected_empty_cells_are_counted_without_metadata(self) -> None:
        self.snapshot["cells"] = [self.snapshot["cells"][3]]
        self.metadata = {}
        self.assertEqual(
            self.render(),
            "Selected cells: 1\nSelected empty cells: 1\nDistinct glyphs: 0\n",
        )

    def test_first_selected_occurrence_order_survives_reordering_and_repetition(self) -> None:
        cells = self.snapshot["cells"]
        self.snapshot["cells"] = [cells[4], cells[2], cells[0], cells[4]]
        counts = self.namespace["selected_records"](self.snapshot)
        self.assertEqual(counts, (4, 0, [(700, 12, 4), (701, 11, 4), (700, 11, 2)]))
        lines = self.render().splitlines()[3:]
        self.assertTrue(lines[0].startswith("700/12 | first cell 4"))
        self.assertTrue(lines[-1].startswith("700/11 | first cell 2"))

    def test_unencoded_zero_and_supplementary_assignments_remain_distinct(self) -> None:
        self.metadata[(700, 11)]["unicodes"] = [0, 0x10FFFF]
        output = self.render()
        self.assertIn("A | U+0000 U+10FFFF", output)
        self.assertIn("A.alt | unencoded", output)

    def test_missing_metadata_or_required_fields_prints_no_partial_report(self) -> None:
        for missing in ("metadata", "unicodes", "glyphId", "selected"):
            with self.subTest(missing=missing):
                self.snapshot = deepcopy(self.namespace["sample_snapshot"])
                self.metadata = deepcopy(self.namespace["sample_metadata"])
                if missing == "metadata":
                    del self.metadata[(701, 11)]
                elif missing == "unicodes":
                    del self.metadata[(701, 11)]["unicodes"]
                elif missing == "glyphId":
                    del self.snapshot["cells"][4]["glyphs"][1]["glyphId"]
                else:
                    del self.snapshot["cells"][4]["selected"]
                output = io.StringIO()
                with contextlib.redirect_stdout(output), self.assertRaises(KeyError):
                    self.namespace["show_selection"](self.snapshot, self.metadata)
                self.assertEqual(output.getvalue(), "")

    def test_unsupported_schema_and_invalid_snapshot_are_not_empty_success(self) -> None:
        for key, value, message in (
            ("schema", 2, "Unsupported snapshot schema"),
            ("valid", False, "Snapshot has no chart model"),
        ):
            with self.subTest(key=key):
                snapshot = deepcopy(self.snapshot)
                snapshot[key] = value
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    with self.assertRaisesRegex(ValueError, message):
                        self.namespace["show_selection"](snapshot, self.metadata)
                self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
