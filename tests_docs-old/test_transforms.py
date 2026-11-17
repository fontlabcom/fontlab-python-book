# this_file: tests_docs/test_transforms.py
"""Check the fictional recording exercise without importing a native adapter."""

import ast
import contextlib
import copy
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/12-transform-a-recording.md"


class RecordingTransformTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        code = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(code), 1)
        self.code = code[0]
        self.namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), self.namespace)
        self.output = output.getvalue()
        expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(expected), 1)
        self.expected = expected[0] + "\n"

    def test_sample_output_matches_and_imports_no_library(self) -> None:
        self.assertEqual(self.output, self.expected)
        self.assertFalse(
            any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(ast.parse(self.code)))
        )
        self.assertEqual(
            self.namespace["recording"],
            [("moveTo", ((4, 7),)), ("lineTo", ((14, 7),)),
             ("lineTo", ((14, 17),)), ("endPath", ())],
        )

    def test_identity_and_empty_recordings_preserve_scope(self) -> None:
        transform = self.namespace["transform_recording"]
        source = self.namespace["recording"]
        identity = (1, 0, 0, 1, 0, 0)
        result = transform(source, identity)
        self.assertEqual(result, source)
        self.assertIsNot(result, source)
        self.assertEqual(transform([], identity), [])

    def test_shear_fractional_and_negative_coordinates_use_all_six_fields(self) -> None:
        transform = self.namespace["transform_recording"]
        source = [("moveTo", ((-2, 0.5),)), ("endPath", ())]
        self.assertEqual(
            transform(source, (2, 3, 4, 5, -6, 7)),
            [("moveTo", ((-8.0, 3.5),)), ("endPath", ())],
        )

    def test_scale_then_offset_differs_from_offset_then_scale(self) -> None:
        transform = self.namespace["transform_recording"]
        source = [("moveTo", ((4, 7),)), ("endPath", ())]
        scale = (2, 0, 0, 2, 0, 0)
        offset = (1, 0, 0, 1, 10, 0)
        self.assertEqual(transform(transform(source, scale), offset)[0][1], ((18, 14),))
        self.assertEqual(transform(transform(source, offset), scale)[0][1], ((28, 14),))

    def test_unsupported_calls_raise_without_changing_input_or_printing(self) -> None:
        transform = self.namespace["transform_recording"]
        for operation, arguments in (
            ("curveTo", ((1, 2), (3, 4), (5, 6))),
            ("addComponent", ("A", (1, 0, 0, 1, 0, 0))),
            ("closePath", ()),
        ):
            with self.subTest(operation=operation):
                source = [("moveTo", ((1, 2),)), (operation, arguments)]
                before = copy.deepcopy(source)
                output = io.StringIO()
                with contextlib.redirect_stdout(output), self.assertRaisesRegex(
                    ValueError, "supports moveTo, lineTo and endPath only"
                ):
                    transform(source, (2, 0, 0, 2, 10, 0))
                self.assertEqual(source, before)
                self.assertEqual(output.getvalue(), "")

    def test_repeated_transform_returns_independent_results(self) -> None:
        transform = self.namespace["transform_recording"]
        source = self.namespace["recording"]
        before = copy.deepcopy(source)
        first = transform(source, (2, 0, 0, 3, 10, -5))
        second = transform(source, (2, 0, 0, 3, 10, -5))
        first.clear()
        self.assertEqual(len(second), 4)
        self.assertEqual(source, before)


if __name__ == "__main__":
    unittest.main()
