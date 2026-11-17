# this_file: tests_docs/test_inspection.py
"""Check Chapter 5 Python control flow with doubles, never the native FontLab API."""

import contextlib
import io
import re
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/05-inspect-the-current-font.md"


class SampleFont:
    """Owned Python data for branch checks; this does not emulate native ownership."""

    def __init__(self, names: tuple[str, ...]) -> None:
        self.names = names

    def __len__(self) -> int:
        return len(self.names)

    def keys(self) -> list[str]:
        return list(self.names)


class InspectionExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(
            r'```python title="Native inspection: bounded runtime test recorded below"\n(.*?)\n```',
            text,
            re.DOTALL,
        )
        self.assertEqual(len(blocks), 1)
        self.assertEqual(text.count("```python"), 1)
        self.code = compile(blocks[0], CHAPTER.name, "exec")

    def run_sample(self, font: SampleFont | None) -> str:
        module = ModuleType("fontlab")
        module.CurrentFont = Mock(return_value=font)
        output = io.StringIO()
        with patch.dict(sys.modules, {"fontlab": module}):
            with contextlib.redirect_stdout(output):
                exec(self.code, {})
        module.CurrentFont.assert_called_once_with()
        return output.getvalue()

    def test_missing_font_reports_absence_without_accessing_font_data(self) -> None:
        self.assertEqual(
            self.run_sample(None), "No current font. Open a font and run again.\n"
        )

    def test_empty_font_is_reported_as_present_with_zero_glyphs(self) -> None:
        font = SampleFont(())
        self.assertEqual(
            self.run_sample(font),
            "Glyphs in the current font: 0\nRead-only report finished\n",
        )
        self.assertEqual(font.names, ())

    def test_report_limits_name_output_to_five_without_changing_data(self) -> None:
        names = ("A", "B", "space", "a.alt", "f_i", "six", "seven")
        font = SampleFont(names)
        self.assertEqual(
            self.run_sample(font),
            "Glyphs in the current font: 7\n"
            "Name: A\nName: B\nName: space\nName: a.alt\nName: f_i\n"
            "Read-only report finished\n",
        )
        self.assertEqual(font.names, names)

    def test_unexpected_read_failure_is_not_reported_as_success(self) -> None:
        font = SampleFont(("A",))
        with patch.object(font, "keys", side_effect=RuntimeError("read failed")):
            with self.assertRaisesRegex(RuntimeError, "read failed"):
                self.run_sample(font)


if __name__ == "__main__":
    unittest.main()
