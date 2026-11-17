# this_file: tests_docs/test_encoding_report.py
"""Execute the exact report with strict metadata-only doubles, never native FontLab."""

import ast
import contextlib
from copy import deepcopy
from dataclasses import dataclass
import io
from pathlib import Path
import re
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/06-find-the-glyph-you-mean.md"


@dataclass(frozen=True, slots=True)
class Glyph:
    _name: object
    _codes: object

    @property
    def name(self):
        if isinstance(self._name, Exception):
            raise self._name
        return self._name

    @property
    def unicodes(self):
        if isinstance(self._codes, Exception):
            raise self._codes
        return self._codes


class Font:
    __slots__ = ("rows", "requests", "failure")

    def __init__(self, rows=(), failure=None):
        self.rows, self.requests, self.failure = tuple(rows), [], failure

    def __len__(self):
        if self.failure == "length":
            raise ValueError("length failed")
        return len(self.rows)

    def __getitem__(self, index):
        if type(index) is not int:
            raise AssertionError("Only numeric lookup is permitted")
        self.requests.append(index)
        if self.failure == "lookup":
            raise ValueError("lookup failed")
        return self.rows[index]


class EncodingReportTests(unittest.TestCase):
    def setUp(self):
        text = CHAPTER.read_text()
        blocks = re.findall(r'```python title="Encoding report: bounded native test recorded below"\n(.*?)\n```', text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.source = blocks[0]
        self.code = compile(self.source, CHAPTER.name, "exec")

    @staticmethod
    def metadata(font):
        return tuple(None if g is None else (g._name, g._codes if isinstance(g._codes, Exception) else deepcopy(g._codes)) for g in font.rows)

    def run_report(self, font, error=None):
        module = ModuleType("fontlab")
        module.CurrentFont = Mock(return_value=font, side_effect=error)
        output = io.StringIO()
        before = self.metadata(font) if font is not None else None
        try:
            with patch.dict(sys.modules, {"fontlab": module}), contextlib.redirect_stdout(output):
                exec(self.code, {})
        finally:
            self.output = output.getvalue()
            module.CurrentFont.assert_called_once_with()
            if font is not None:
                self.assertEqual(self.metadata(font), before)
        return self.output

    def test_native_surface_is_metadata_only(self):
        tree = ast.parse(self.source)
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 1)
        self.assertIsInstance(imports[0], ast.Import)
        self.assertEqual([n.name for n in imports[0].names], ["fontlab"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                self.assertIsInstance(node.ctx, ast.Load)
                self.assertIn(node.attr, {"CurrentFont", "name", "unicodes", "append", "items", "join"})

    def test_no_font_is_distinct_from_empty_present_font(self):
        self.assertEqual(self.run_report(None), "No current font. Open a font and run again.\n")
        output = self.run_report(Font())
        self.assertEqual(output.splitlines()[:4], ["Stored glyphs inspected: 0", "Unencoded glyphs: 0", "Distinct assigned codepoints: 0", "Codepoints assigned to several glyphs: 0"])
        self.assertTrue(output.endswith("Read-only encoding report complete.\n"))

    def test_shared_owners_are_distinct_records_and_zero_is_encoded(self):
        font = Font([Glyph(".notdef", []), Glyph("A", [65]), Glyph("A.alt", [65, 65]), Glyph("null", [0])])
        output = self.run_report(font)
        self.assertEqual(output.splitlines()[:4], ["Stored glyphs inspected: 4", "Unencoded glyphs: 1", "Distinct assigned codepoints: 2", "Codepoints assigned to several glyphs: 1"])
        self.assertIn("U+0041: 2 glyphs; [1] 'A', [2] 'A.alt'", output)
        self.assertEqual(font.requests, [0, 1, 2, 3])

    def test_multiple_assignments_on_one_glyph_are_not_shared(self):
        output = self.run_report(Font([Glyph("space", [32, 160])]))
        self.assertIn("Distinct assigned codepoints: 2", output)
        self.assertIn("Codepoints assigned to several glyphs: 0", output)

    def test_supplementary_codepoints_and_numeric_order_are_preserved(self):
        output = self.run_report(Font([Glyph("first", [0x1F600, 65, 0]), Glyph("second", [0, 65, 0x1F600])]))
        rows = [line for line in output.splitlines() if line.startswith("  U+")]
        self.assertEqual([line.split(":")[0] for line in rows], ["  U+0000", "  U+0041", "  U+1F600"])

    def test_full_scan_counts_last_record_while_bounding_all_samples(self):
        rows = [Glyph(f"empty{i}", []) for i in range(7)]
        rows += [Glyph(f"owner{i}", list(range(65, 72))) for i in range(8)]
        font = Font(rows)
        output = self.run_report(font)
        self.assertEqual(output.splitlines()[:4], ["Stored glyphs inspected: 15", "Unencoded glyphs: 7", "Distinct assigned codepoints: 7", "Codepoints assigned to several glyphs: 7"])
        self.assertEqual(len(output.splitlines()), 17)
        self.assertNotIn("empty5", output)
        self.assertNotIn("owner5", output)
        self.assertNotIn("U+0046", output)
        self.assertIn("U+0041: 8 glyphs", output)
        self.assertEqual(font.requests, list(range(15)))

    def test_last_unencoded_record_is_included_after_many_encoded_records(self):
        rows = [Glyph(f"g{i}", [i]) for i in range(100)] + [Glyph("last", [])]
        output = self.run_report(Font(rows))
        self.assertIn("Stored glyphs inspected: 101", output)
        self.assertIn("Unencoded glyphs: 1", output)
        self.assertIn("  [100] 'last'", output)

    def test_name_escaping_and_shortening_leave_inputs_unchanged(self):
        output = self.run_report(Font([Glyph("a\nb\tc", []), Glyph("x" * 200, [])]))
        labels = [line[2:] for line in output.splitlines() if line.startswith("  ")]
        self.assertEqual(len(labels), 2)
        self.assertIn("\\n", labels[0])
        self.assertIn("\\t", labels[0])
        self.assertEqual(len(labels[1]), 80)
        self.assertTrue(labels[1].endswith("..."))

    def test_same_name_still_counts_separate_glyph_indices(self):
        output = self.run_report(Font([Glyph("same", [65]), Glyph("same", [65])]))
        self.assertIn("U+0041: 2 glyphs; [0] 'same', [1] 'same'", output)

    def test_missing_record_after_valid_record_prints_nothing(self):
        with self.assertRaisesRegex(RuntimeError, "No glyph at index 1; report incomplete"):
            self.run_report(Font([Glyph("A", [65]), None]))
        self.assertEqual(self.output, "")

    def test_native_boundary_errors_propagate_before_output(self):
        cases = [(None, ValueError("current failed")), (Font(failure="length"), None), (Font([Glyph("A", [])], "lookup"), None), (Font([Glyph("ok", []), Glyph(ValueError("name failed"), [])]), None), (Font([Glyph("ok", []), Glyph("bad", ValueError("codes failed"))]), None)]
        for font, error in cases:
            with self.subTest(error=error, font=font):
                with self.assertRaises(ValueError):
                    self.run_report(font, error)
                self.assertEqual(self.output, "")

    def test_formatting_failure_also_prints_no_partial_totals(self):
        with self.assertRaises(ValueError):
            self.run_report(Font([Glyph("first", ["not-an-integer"]), Glyph("second", ["not-an-integer"])]))
        self.assertEqual(self.output, "")

    def test_repeated_runs_are_identical_and_do_not_accumulate(self):
        font = Font([Glyph("A", [65]), Glyph("other", [65])])
        self.assertEqual(self.run_report(font), self.run_report(font))


if __name__ == "__main__":
    unittest.main()
