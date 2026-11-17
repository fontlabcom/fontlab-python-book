# this_file: tests_docs/test_attachments.py
"""Check fictional attachment proposals without loading a native font API."""

import ast
import contextlib
from copy import deepcopy
import io
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/14-plan-an-attachment.md"


class AttachmentProposalTests(unittest.TestCase):
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

    def test_exact_output_and_no_imports(self) -> None:
        self.assertEqual(self.output, self.expected)
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom))
                             for n in ast.walk(ast.parse(self.code))))

    def test_missing_base_and_mark_are_distinct_and_never_zero(self) -> None:
        report = self.namespace["attachment_proposals"]
        record = deepcopy(self.namespace["records"][0])
        record["base_anchors"] = {}
        self.assertEqual(report([record], "top"), ["Light a + acutecomb: missing base top"])
        record["base_anchors"] = {"top": (0, 0)}
        record["mark_anchors"] = {}
        self.assertEqual(report([record], "top"), ["Light a + acutecomb: missing mark _top"])

    def test_zero_negative_fractional_and_nonzero_base_offset(self) -> None:
        record = deepcopy(self.namespace["records"][0])
        record.update(base_offset=(-10.5, 4), base_anchors={"top": (0, -2)},
                      mark_anchors={"_top": (5, 1.5)})
        self.assertEqual(self.namespace["attachment_proposals"]([record], "top"),
                         ["Light a + acutecomb: propose mark offset (-15.5, 0.5)"])

    def test_custom_anchor_and_empty_input(self) -> None:
        report = self.namespace["attachment_proposals"]
        self.assertEqual(report([], "bottom"), [])
        record = deepcopy(self.namespace["records"][0])
        record.update(base_anchors={"bottom": (25, -100)},
                      mark_anchors={"_bottom": (5, 10)})
        self.assertEqual(report([record], "bottom"),
                         ["Light a + acutecomb: propose mark offset (20, -110)"])

    def test_master_order_identity_and_inputs_are_preserved(self) -> None:
        report = self.namespace["attachment_proposals"]
        records = self.namespace["records"]
        before = deepcopy(records)
        lines = report(records, "top")
        self.assertTrue(lines[0].startswith("Light a + acutecomb:"))
        self.assertTrue(lines[1].startswith("Bold a + acutecomb:"))
        self.assertEqual(lines[2], "Medium a + acutecomb: missing mark _top")
        lines.append("unrelated output edit")
        self.assertEqual(report(records, "top"), lines[:-1])
        self.assertEqual(records, before)

    def test_missing_master_metadata_is_not_inferred(self) -> None:
        records = deepcopy(self.namespace["records"])
        del records[-1]["master"]
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(KeyError):
            for line in self.namespace["attachment_proposals"](records, "top"):
                print(line)
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
