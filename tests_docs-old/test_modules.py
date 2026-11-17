# this_file: tests_docs/test_modules.py
"""Run the chapter's exact two-file project in external Python processes."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/10-organize-reusable-scripts.md"


class ReusableScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 2)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = self.root / "report_demo"
        self.project.mkdir()
        for name, code in zip(("orchard_report.py", "run_report.py"), blocks):
            self.assertTrue(code.startswith(f"# this_file: report_demo/{name}\n"))
            (self.project / name).write_text(code + "\n")
        expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)
        self.expected = expected[-1] + "\n"
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        self.env.pop("PYTHONPATH", None)

    def run_python(self, *arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", *arguments],
            cwd=cwd or self.project,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )

    def test_launcher_matches_output_from_project_and_unrelated_directory(self) -> None:
        for cwd, argument in (
            (self.project, "run_report.py"),
            (self.root, str(self.project / "run_report.py")),
        ):
            with self.subTest(cwd=cwd):
                result = self.run_python(argument, cwd=cwd)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, self.expected)
                self.assertEqual(result.stderr, "")

    def test_importing_both_files_is_quiet_and_uses_the_local_helper(self) -> None:
        result = self.run_python(
            "-c",
            "import orchard_report, run_report, sys; from pathlib import Path; "
            "assert Path(orchard_report.__file__).resolve() == Path('orchard_report.py').resolve(); "
            "assert not {'fontlab', 'fontgate', 'PythonQt', 'fly', 'fontlabapp'} & set(sys.modules)",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_explicit_main_can_run_twice_after_quiet_import(self) -> None:
        result = self.run_python("-c", "import run_report; run_report.main(); run_report.main()")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self.expected * 2)

    def test_formatter_keeps_empty_duplicate_and_unicode_records_without_mutation(self) -> None:
        probe = '''from copy import deepcopy
from orchard_report import glyph_lines
assert glyph_lines([]) == ["Supplied glyph records: 0"]
records = [
    {"name": "A", "unicodes": [0, 0x1F600]},
    {"name": "A", "unicodes": []},
    {"name": "A", "unicodes": []},
]
before = deepcopy(records)
assert glyph_lines(records) == [
    "Supplied glyph records: 3", "A | U+0000 U+1F600", "A | unencoded", "A | unencoded"
]
assert records == before
'''
        result = self.run_python("-c", probe)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_missing_helper_fails_before_printing_a_report(self) -> None:
        (self.project / "orchard_report.py").unlink()
        result = self.run_python("run_report.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("ModuleNotFoundError", result.stderr)
        self.assertIn("orchard_report", result.stderr)

    def test_missing_record_field_fails_before_any_launcher_output(self) -> None:
        probe = '''from orchard_report import glyph_lines
records = [{"name": "A", "unicodes": [65]}, {"name": "B"}]
for line in glyph_lines(records):
    print(line)
'''
        result = self.run_python("-c", probe)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("KeyError", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
