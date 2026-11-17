# this_file: tests_docs/test_delivery.py
"""Verify the fictional in-memory artifact comparison without file or native access."""

import ast
import contextlib
from copy import deepcopy
import hashlib
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/20-share-the-files-and-conditions.md"


class DeliveryExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        text = CHAPTER.read_text()
        blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.code = blocks[0]
        self.namespace = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(self.code, CHAPTER.name, "exec"), self.namespace)
        self.output = output.getvalue()
        self.expected = re.findall(r"```text\n(.*?)\n```", text, re.DOTALL)[0] + "\n"
        self.report = self.namespace["delivery_report"]

    def test_exact_output_and_hashlib_only_import(self) -> None:
        self.assertEqual(self.output, self.expected)
        imports = [node for node in ast.walk(ast.parse(self.code))
                   if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 1)
        self.assertIsInstance(imports[0], ast.Import)
        self.assertEqual([item.name for item in imports[0].names], ["hashlib"])
        calls = {node.func.id for node in ast.walk(ast.parse(self.code))
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertEqual(calls, {"delivery_report", "print"})

    def test_known_digest_and_empty_bytes_match(self) -> None:
        expected = {"empty": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
        self.assertEqual(self.report(expected, {"empty": b""}),
                         ["empty: matches recorded digest"])

    def test_missing_and_changed_are_distinct_in_declared_order(self) -> None:
        digest = hashlib.sha256(b"abc").hexdigest()
        self.assertEqual(self.report({"first": digest, "second": digest}, {"second": b"abd"}),
                         ["first: missing", "second: differs from recorded digest"])

    def test_extra_items_are_reported_after_required_items(self) -> None:
        digest = hashlib.sha256(b"a").hexdigest()
        self.assertEqual(self.report({"required": digest},
                                     {"extra-b": b"b", "required": b"a", "extra-a": b"a"}),
                         ["required: matches recorded digest", "extra-b: unexpected",
                          "extra-a: unexpected"])

    def test_missing_requirements_do_not_declare_success(self) -> None:
        for supplied in ({}, {"something": b"bytes"}):
            self.assertEqual(self.report({}, supplied),
                             ["No required artifacts recorded; nothing verified"])

    def test_binary_bytes_and_newline_changes(self) -> None:
        content = b"\x00\xff\r\n"
        expected = {"data": hashlib.sha256(content).hexdigest()}
        self.assertEqual(self.report(expected, {"data": content}),
                         ["data: matches recorded digest"])
        self.assertEqual(self.report(expected, {"data": content.replace(b"\r\n", b"\n")}),
                         ["data: differs from recorded digest"])

    def test_inputs_unchanged_and_each_result_independent(self) -> None:
        expected = deepcopy(self.namespace["expected"])
        supplied = deepcopy(self.namespace["supplied"])
        before = deepcopy((expected, supplied))
        first = self.report(expected, supplied)
        second = self.report(expected, supplied)
        first.clear()
        self.assertEqual(len(second), 4)
        self.assertEqual((expected, supplied), before)


if __name__ == "__main__":
    unittest.main()
