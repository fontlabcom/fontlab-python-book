# this_file: tests_docs/test_testing_chapter.py
"""Run the book's fictional tests externally and verify a real failure is reported."""

import ast
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/17-test-the-promise.md"


class TestingChapterTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        self.blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(self.blocks), 2)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        for name, code in zip(("width_report.py", "test_width_report.py"), self.blocks):
            (self.folder / name).write_text(code + "\n")

    def run_example(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "unittest", "-v"], cwd=self.folder,
            text=True, capture_output=True, timeout=15,
        )

    def test_published_suite_passes_all_seven_tests(self) -> None:
        result = self.run_example()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Ran 7 tests", result.stderr)
        self.assertIn("OK", result.stderr)

    def test_wrong_expectation_produces_failure_and_nonzero_exit(self) -> None:
        path = self.folder / "test_width_report.py"
        original = path.read_text()
        wrong = original.replace("self.assertEqual(width_change(before, after), 40)",
                                 "self.assertEqual(width_change(before, after), 41)")
        self.assertNotEqual(original, wrong)
        path.write_text(wrong)
        result = self.run_example()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AssertionError: 40 != 41", result.stderr)
        self.assertIn("FAILED (failures=1)", result.stderr)

    def test_unexpected_exception_is_reported_as_error(self) -> None:
        path = self.folder / "test_width_report.py"
        path.write_text(path.read_text().replace('"width": 540', '"missing": 540', 1))
        result = self.run_example()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("KeyError: 'width'", result.stderr)
        self.assertIn("FAILED (errors=1)", result.stderr)

    def test_only_unittest_and_local_helper_are_imported(self) -> None:
        modules = []
        for code in self.blocks:
            for node in ast.walk(ast.parse(code)):
                if isinstance(node, ast.Import):
                    modules.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    modules.append(node.module)
        self.assertEqual(modules, ["unittest", "width_report"])


if __name__ == "__main__":
    unittest.main()
