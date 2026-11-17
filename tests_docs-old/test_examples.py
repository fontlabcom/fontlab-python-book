# this_file: tests_docs/test_examples.py
"""Execute the authored Python chapter examples against their printed results."""

import contextlib
import io
import re
import unittest
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "src_docs/md"
CHAPTERS = ("02-python-basics.md", "04-work-in-the-scripting-panel.md")


class ChapterExampleTests(unittest.TestCase):
    def test_each_example_when_run_independently_matches_its_output(self) -> None:
        for chapter in CHAPTERS:
            self.check_examples(DOCS / chapter)

    def check_examples(self, chapter: Path) -> None:
        text = chapter.read_text()
        examples = re.findall(
            r"```python\n(.*?)\n```\s*```text\n(.*?)\n```", text, re.DOTALL
        )
        self.assertTrue(examples, "The chapter must contain runnable examples")
        self.assertEqual(len(examples), text.count("```python\n"))
        for index, (code, expected) in enumerate(examples, 1):
            with self.subTest(chapter=chapter.name, example=index):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exec(compile(code, f"{chapter.name}:example-{index}", "exec"), {})
                self.assertEqual(output.getvalue(), expected + "\n")

    def test_intentional_error_stops_before_the_completion_message(self) -> None:
        chapter = DOCS / "04-work-in-the-scripting-panel.md"
        examples = re.findall(
            r'```python title="Intentional ZeroDivisionError"\n(.*?)\n```',
            chapter.read_text(),
            re.DOTALL,
        )
        self.assertEqual(len(examples), 1)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaisesRegex(ZeroDivisionError, "division by zero"):
                exec(compile(examples[0], chapter.name, "exec"), {})
        self.assertEqual(output.getvalue(), "Sample check started\n")


if __name__ == "__main__":
    unittest.main()
