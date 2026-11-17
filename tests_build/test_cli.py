# this_file: tests_build/test_cli.py
"""Checks for the installed documentation build command."""

import os
import subprocess
import tempfile
import unittest
from contextlib import chdir
from pathlib import Path
from unittest.mock import patch

import fire

import fontlab_python_book as book


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.config = self.root / "src_docs/mkdocs.yml"
        self.config.parent.mkdir()
        self.config.write_text("site_name: Test\n")

    def test_build_when_preview_contains_spaces_then_preserves_argument(self) -> None:
        with (
            patch.object(
                book.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
            ) as run,
            patch.dict(os.environ, {"SOURCE_DATE_EPOCH": ""}),
        ):
            book.build(
                config=str(self.config), site_dir="/tmp/book preview", verbose=True
            )
        command = run.call_args.args[0]
        self.assertIn("/tmp/book preview", command)
        self.assertIn("--strict", command)
        self.assertIn("--clean", command)
        self.assertIn("--verbose", command)
        self.assertEqual(run.call_args.kwargs["cwd"], self.root)
        self.assertEqual(run.call_args.kwargs["env"]["SOURCE_DATE_EPOCH"], "0")

    def test_build_when_epoch_is_explicit_then_preserves_it(self) -> None:
        with (
            patch.object(
                book.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
            ) as run,
            patch.dict(os.environ, {"SOURCE_DATE_EPOCH": "123"}),
        ):
            book.build(config=str(self.config))
        self.assertEqual(run.call_args.kwargs["env"]["SOURCE_DATE_EPOCH"], "123")

    def test_build_when_config_missing_then_explains_source_requirement(self) -> None:
        with self.assertRaisesRegex(SystemExit, "Book sources not found"):
            book.build(config=str(self.root / "missing.yml"))

    def test_build_when_properdocs_fails_then_exits_with_same_status(self) -> None:
        with (
            patch.object(
                book.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)
            ),
            self.assertRaises(SystemExit) as error,
        ):
            book.build(config=str(self.config))
        self.assertEqual(error.exception.code, 7)

    def test_fire_when_build_is_default_then_forwards_named_flags(self) -> None:
        with patch.object(
            book.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
        ) as run:
            fire.Fire(
                book.build,
                command=[
                    "--config",
                    str(self.config),
                    "--site-dir",
                    "/tmp/a b",
                    "--verbose",
                ],
            )
        self.assertIn("/tmp/a b", run.call_args.args[0])
        self.assertIn("--verbose", run.call_args.args[0])

    def test_fire_when_no_arguments_then_builds_checkout_config(self) -> None:
        with (
            patch.object(
                book.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
            ) as run,
            chdir(self.root),
        ):
            fire.Fire(book.build, command=[])
        self.assertIn(str(self.config), run.call_args.args[0])

    def test_build_when_outside_checkout_then_finds_editable_source_config(
        self,
    ) -> None:
        expected = Path(book.__file__).resolve().parents[2] / "src_docs/mkdocs.yml"
        foreign = self.root / "foreign"
        foreign.mkdir()
        with (
            patch.object(
                book.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
            ) as run,
            chdir(foreign),
        ):
            book.build()
        self.assertIn(str(expected), run.call_args.args[0])

    def test_main_when_invoked_then_exposes_only_build(self) -> None:
        with patch.object(book.fire, "Fire") as cli:
            book.main()
        cli.assert_called_once_with(book.build)


if __name__ == "__main__":
    unittest.main()
