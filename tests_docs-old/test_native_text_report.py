# this_file: tests_docs/test_native_text_report.py
"""Execute the published text report with metadata-only doubles; no native calls."""
import ast
import contextlib
import io
from pathlib import Path
import re
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

from tests_docs import test_encoding_report as doubles

Font, Glyph = doubles.Font, doubles.Glyph

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/25-mapping-is-not-shaping.md"


class NativeTextReportTests(unittest.TestCase):
    def setUp(self):
        blocks = re.findall(r'```python title="Text assignment report: bounded native test recorded below"\n(.*?)\n```', CHAPTER.read_text(), re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.source = blocks[0]

    def run_candidate(self, font, text="AVATAR", error=None):
        module = ModuleType("fontlab")
        module.CurrentFont = Mock(return_value=font, side_effect=error)
        output = io.StringIO()
        before = doubles.EncodingReportTests.metadata(font) if font is not None else None
        code = self.source.replace('TEXT = "AVATAR"', "TEXT = " + repr(text), 1)
        try:
            with patch.dict(sys.modules, {"fontlab": module}), contextlib.redirect_stdout(output):
                exec(compile(code, "text-assignment-report.py", "exec"), {})
        finally:
            self.stdout = output.getvalue()
            self.current_calls = module.CurrentFont.call_count
            if font is not None:
                self.assertEqual(doubles.EncodingReportTests.metadata(font), before)
        return self.stdout

    def test_exact_default_reports_distinct_codes_and_occurrences(self):
        out = self.run_candidate(Font([Glyph("A", [65]), Glyph("V", [86]), Glyph("T", [84]), Glyph("R", [82])]))
        self.assertEqual(out.splitlines()[:6], ["Text codepoints: 6", "Distinct text codepoints: 4", "Stored glyphs inspected: 4", "Assigned to one glyph: 4", "Assigned to several glyphs: 0", "Unassigned text codepoints: 0"])
        self.assertIn("U+0041: unique; text occurrences: 3; glyph owners: 1; [0] 'A'", out)
        self.assertTrue(out.endswith("Assignment report complete; shaping was not tested.\n"))

    def test_interrupt_is_not_wrapped_or_reported_as_complete(self):
        with self.assertRaises(KeyboardInterrupt):
            self.run_candidate(None, error=KeyboardInterrupt())
        self.assertEqual(self.stdout, "")

    def test_no_font_and_empty_text(self):
        self.assertEqual(self.run_candidate(None), "No current font. Open a font and run again.\n")
        self.assertEqual(self.current_calls, 1)
        f = Font(failure="length")
        self.assertEqual(self.run_candidate(f, ""), "No sample text. Set TEXT and run again; font not scanned.\n")
        self.assertEqual(f.requests, [])

    def test_empty_font_means_missing_assignments(self):
        out = self.run_candidate(Font(), "ABA")
        self.assertIn("Unassigned text codepoints: 2", out)
        self.assertIn("U+0041: unassigned; text occurrences: 2; glyph owners: 0; (none)", out)

    def test_distinct_record_owners_and_zero_codepoint(self):
        f = Font([Glyph("A", [65]), Glyph("alternate", [65, 65]), Glyph("null", [0]), Glyph("unencoded", [])])
        out = self.run_candidate(f, "A\x00A?")
        self.assertIn("Assigned to one glyph: 1", out)
        self.assertIn("Assigned to several glyphs: 1", out)
        self.assertIn("Unassigned text codepoints: 1", out)
        self.assertIn("U+0041: shared; text occurrences: 2; glyph owners: 2", out)
        self.assertIn("U+0000: unique", out)
        self.assertEqual(f.requests, [0, 1, 2, 3])

    def test_order_counts_are_text_first_occurrence_not_unicode_sort(self):
        out = self.run_candidate(Font([Glyph("B", [66]), Glyph("A", [65])]), "BABA")
        self.assertLess(out.index("U+0042"), out.index("U+0041"))
        self.assertIn("U+0042: unique; text occurrences: 2", out)

    def test_bound_details_and_owners_but_count_all(self):
        f = Font([Glyph(f"g{i}", list(range(65, 76))) for i in range(5)])
        out = self.run_candidate(f, "ABCDEFGHIJK")
        self.assertEqual(len(out.splitlines()), 16)
        self.assertIn("Assigned to several glyphs: 11", out)
        self.assertIn("glyph owners: 5", out)
        self.assertNotIn("U+0049", out)
        self.assertNotIn("'g3'", out)
        self.assertEqual(f.requests, list(range(5)))

    def test_unicode_is_not_normalized_or_clustered(self):
        out = self.run_candidate(Font([Glyph("A", [65]), Glyph("acute", [0x301]), Glyph("smile", [0x1F600])]), "ÁA\u0301\U0001f600")
        self.assertIn("Text codepoints: 4", out)
        self.assertIn("U+00C1: unassigned", out)
        self.assertIn("U+0301: unique", out)
        self.assertIn("U+1F600: unique", out)

    def test_boundary_errors_keep_original_cause_and_empty_stdout(self):
        cause = ValueError("native failed")
        cases = [(None, cause, "current font lookup"), (Font(failure="length"), None, "glyph count"), (Font([Glyph("A", [65])], "lookup"), None, "glyph 0 metadata"), (Font([Glyph("ok", []), Glyph("bad", cause)]), None, "glyph 1 metadata"), (Font([Glyph("ok", []), Glyph(cause, [])]), None, "glyph 1 metadata"), (Font([None]), None, "glyph 0 metadata")]
        for font, error, phase in cases:
            with self.subTest(phase=phase):
                with self.assertRaisesRegex(RuntimeError, phase) as caught:
                    self.run_candidate(font, error=error)
                self.assertIsNotNone(caught.exception.__cause__)
                if error is cause or phase == "glyph 1 metadata":
                    self.assertIs(caught.exception.__cause__, cause)
                self.assertEqual(self.stdout, "")

    def test_invalid_text_is_refused_before_font_lookup(self):
        with self.assertRaisesRegex(RuntimeError, "sample text") as caught:
            self.run_candidate(None, 12)
        self.assertIsInstance(caught.exception.__cause__, TypeError)
        self.assertEqual(self.stdout, "")
        self.assertEqual(self.current_calls, 0)

    def test_label_escape_bound_and_repeatability(self):
        f = Font([Glyph("line\nwith\ttab", [65]), Glyph("x" * 300, [65])])
        out = self.run_candidate(f, "A")
        self.assertIn("line\\nwith\\ttab", out)
        self.assertNotIn("x" * 80, out)
        self.assertEqual(self.run_candidate(f, "A"), out)
        self.assertEqual(f.rows[1]._name, "x" * 300)

    def test_only_verified_native_metadata_surface(self):
        tree = ast.parse(self.source)
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].names[0].name, "fontlab")
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute):
                self.assertIsInstance(n.ctx, ast.Load)
                self.assertIn(n.attr, {"CurrentFont", "name", "unicodes", "get", "append", "items", "extend", "join"})


if __name__ == "__main__":
    unittest.main()
