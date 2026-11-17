# this_file: tests_docs/test_lookup.py
"""Check Chapter 6 control flow with owned doubles; never import native FontLab."""

import contextlib
import io
import re
import sys
import unittest
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/06-find-the-glyph-you-mean.md"


@dataclass(frozen=True)
class SampleGlyph:
    name: str
    index: int
    unicodes: list[int]


class SampleFont:
    """Minimal lookup data, not an emulator of native ownership or state."""

    def __init__(self, glyphs: tuple[SampleGlyph | None, ...]) -> None:
        self.glyphs = glyphs
        self.requests: list[str | int] = []

    def __len__(self) -> int:
        return len(self.glyphs)

    def __getitem__(self, key: str | int) -> SampleGlyph | None:
        self.requests.append(key)
        if isinstance(key, int):
            return self.glyphs[key]
        return next((g for g in self.glyphs if g is not None and g.name == key), None)


class GlyphLookupExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(
            r'```python title="Native (name lookup|Unicode search): bounded runtime test recorded below"\n(.*?)\n```',
            text,
            re.DOTALL,
        )
        self.assertEqual(len(blocks), 2)
        self.assertEqual(text.count("```python"), 3)
        self.code = {name: compile(code, CHAPTER.name, "exec") for name, code in blocks}

    def run_example(self, name: str, font: SampleFont | None) -> str:
        before = deepcopy(font.glyphs) if font is not None else None
        module = ModuleType("fontlab")
        module.CurrentFont = Mock(return_value=font)
        output = io.StringIO()
        with patch.dict(sys.modules, {"fontlab": module}):
            with contextlib.redirect_stdout(output):
                exec(self.code[name], {})
        module.CurrentFont.assert_called_once_with()
        if font is not None:
            self.assertEqual(font.glyphs, before)
        return output.getvalue()

    def test_both_examples_handle_no_font_without_lookup(self) -> None:
        for name in self.code:
            with self.subTest(example=name):
                self.assertEqual(
                    self.run_example(name, None),
                    "No current font. Open a font and run again.\n",
                )

    def test_absent_name_has_its_own_result(self) -> None:
        font = SampleFont((SampleGlyph("B", 0, [66]),))
        self.assertEqual(self.run_example("name lookup", font), "No glyph named A.\n")
        self.assertEqual(font.requests, ["A"])

    def test_unencoded_glyph_is_found_but_has_no_assignments(self) -> None:
        font = SampleFont((SampleGlyph("A", 0, []),))
        self.assertEqual(
            self.run_example("name lookup", font),
            "Name: A\nGlyph index: 0\nNo Unicode assignments\n",
        )

    def test_assignments_cover_single_zero_multiple_and_long_codepoints(self) -> None:
        cases = [
            ([65], "Unicode: U+0041\n"),
            ([0, 65, 0x1F600], "Unicode: U+0000\nUnicode: U+0041\nUnicode: U+1F600\n"),
        ]
        for codepoints, expected in cases:
            with self.subTest(codepoints=codepoints):
                font = SampleFont((SampleGlyph("A", 0, codepoints),))
                self.assertEqual(
                    self.run_example("name lookup", font),
                    "Name: A\nGlyph index: 0\n" + expected,
                )

    def test_unicode_search_uses_assignments_and_visits_every_index(self) -> None:
        font = SampleFont((SampleGlyph("A", 0, [66]), SampleGlyph("other", 1, [65, 66])))
        self.assertEqual(
            self.run_example("Unicode search", font),
            "Matches for U+0041: 1\nName: other\n",
        )
        self.assertEqual(font.requests, [0, 1])

    def test_empty_font_and_no_matching_assignment_report_zero(self) -> None:
        for glyphs in [(), (SampleGlyph("A", 0, []),)]:
            with self.subTest(glyphs=glyphs):
                self.assertEqual(
                    self.run_example("Unicode search", SampleFont(glyphs)),
                    "Matches for U+0041: 0\n",
                )

    def test_multiple_matches_are_counted_with_only_five_names_printed(self) -> None:
        font = SampleFont(tuple(SampleGlyph(f"g{i}", i, [65]) for i in range(6)))
        self.assertEqual(
            self.run_example("Unicode search", font),
            "Matches for U+0041: 6\n" + "".join(f"Name: g{i}\n" for i in range(5)),
        )
        self.assertEqual(font.requests, list(range(6)))

    def test_missing_index_result_stops_instead_of_skipping_a_glyph(self) -> None:
        font = SampleFont((SampleGlyph("A", 0, [65]), None))
        with self.assertRaisesRegex(RuntimeError, "No glyph at index 1; report incomplete"):
            self.run_example("Unicode search", font)


if __name__ == "__main__":
    unittest.main()
