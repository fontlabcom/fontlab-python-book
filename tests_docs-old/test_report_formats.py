# this_file: tests_docs/test_report_formats.py
"""Check fictional JSON/CSV serialization without filesystem or native access."""

import ast
import contextlib
from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/21-make-the-report-reproducible.md"


class ReportFormatTests(unittest.TestCase):
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
        self.render = self.namespace["render_report"]

    def test_exact_output_and_only_serialization_imports(self) -> None:
        self.assertEqual(self.output, self.expected)
        tree = ast.parse(self.code)
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertTrue(all(isinstance(n, ast.Import) for n in imports))
        self.assertEqual({a.name for n in imports for a in n.names}, {"csv", "io", "json"})
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            self.assertTrue(
                isinstance(call.func, ast.Name) and call.func.id in {"render_report", "print"}
                or isinstance(call.func, ast.Attribute) and call.func.attr in {
                    "dumps", "StringIO", "writer", "writerow", "getvalue"
                }, ast.dump(call))

    def test_json_preserves_scope_zero_and_missing_width(self) -> None:
        rows = [{"label": "zero", "width": 0}, {"label": "unknown", "width": None}]
        text, _ = self.render(rows)
        self.assertEqual(json.loads(text), {"schema": 1, "font": "Fictional Orchard",
                                           "master": "Regular", "units": "font units",
                                           "records": rows})
        self.assertTrue(text.endswith("\n"))

    def test_csv_preserves_status_and_quotes_special_labels(self) -> None:
        rows = [{"label": 'é, "sample"\nline', "width": 0},
                {"label": "missing", "width": None}]
        _, text = self.render(rows)
        parsed = list(csv.DictReader(io.StringIO(text, newline="")))
        self.assertEqual(parsed, [{"label": rows[0]["label"], "width": "0", "status": "present"},
                                  {"label": "missing", "width": "", "status": "missing"}])
        self.assertNotIn("\r", text)

    def test_empty_records_keep_schema_and_csv_header(self) -> None:
        text, table = self.render([])
        self.assertEqual(json.loads(text)["records"], [])
        self.assertEqual(table, "label,width,status\n")

    def test_nonfinite_values_are_rejected(self) -> None:
        for width in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(width=width), self.assertRaises(ValueError):
                self.render([{"label": "invalid", "width": width}])

    def test_missing_required_keys_remain_errors(self) -> None:
        for record in ({"label": "no width"}, {"width": 10}):
            with self.subTest(record=record), self.assertRaises(KeyError):
                self.render([record])

    def test_repeated_rendering_preserves_order_inputs_and_bytes(self) -> None:
        rows = [{"label": "z", "width": -10.5}, {"label": "a", "width": 0}]
        before = deepcopy(rows)
        first = self.render(rows)
        self.assertEqual(first, self.render(rows))
        self.assertEqual(rows, before)
        self.assertEqual([r["label"] for r in json.loads(first[0])["records"]], ["z", "a"])
        self.assertEqual(first[0].encode("utf-8"), self.render(rows)[0].encode("utf-8"))

    def test_equal_json_data_can_have_different_bytes(self) -> None:
        text, _ = self.render([{"label": "é", "width": 0}])
        alternate = json.dumps(json.loads(text), ensure_ascii=True, separators=(",", ":"))
        self.assertEqual(json.loads(text), json.loads(alternate))
        self.assertNotEqual(text.encode("utf-8"), alternate.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
