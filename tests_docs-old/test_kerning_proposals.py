# this_file: tests_docs/test_kerning_proposals.py
"""Verify fictional kerning proposals, with no native source or destination."""

import ast
import contextlib
from copy import deepcopy
import io
import math
from pathlib import Path
import re
import unittest

CHAPTER = Path(__file__).resolve().parents[1] / "src_docs/md/13-report-kerning-proposals.md"


class KerningProposalTests(unittest.TestCase):
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

    def test_exact_example_and_import_boundary(self) -> None:
        self.assertEqual(self.output, self.expected)
        imports = [node for node in ast.walk(ast.parse(self.code))
                   if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 1)
        self.assertIsInstance(imports[0], ast.ImportFrom)
        self.assertEqual(imports[0].module, "math")

    def test_explicit_zero_wins_and_removing_it_reveals_class_value(self) -> None:
        lookup = self.namespace["first_stored"]
        source = deepcopy(self.namespace["masters"]["Regular"])
        candidates = self.namespace["requests"][0]["candidates"]
        self.assertEqual(lookup(source, candidates), (("A", "V"), 0))
        del source["A", "V"]
        self.assertEqual(
            lookup(source, candidates),
            (("public.kern1.A", "public.kern2.V"), -70),
        )

    def test_candidate_order_and_absence_remain_explicit(self) -> None:
        lookup = self.namespace["first_stored"]
        candidates = [("A", "V"), ("A", "group2"), ("group1", "V")]
        values = {("A", "group2"): 15, ("group1", "V"): -20}
        self.assertEqual(lookup(values, candidates), (("A", "group2"), 15))
        self.assertEqual(lookup(values, []), (None, None))
        self.assertEqual(lookup({}, candidates), (None, None))

    def test_master_scope_is_named_and_missing_master_raises(self) -> None:
        report = self.namespace["proposal_lines"]
        masters, requests = self.namespace["masters"], self.namespace["requests"]
        bold = report(masters, "Bold", requests[:1])
        self.assertIn("A/V: explicit absent; effective -90", bold)
        self.assertIn("  propose set explicit 0", bold)
        self.assertEqual(report(masters, "Regular", []), ["Master: Regular (fictional)"])
        with self.assertRaises(KeyError):
            report(masters, "Missing", [])

    def test_proposals_preserve_inputs_order_and_distinguish_noop(self) -> None:
        report = self.namespace["proposal_lines"]
        masters, requests = self.namespace["masters"], self.namespace["requests"]
        before = deepcopy((masters, requests))
        lines = report(masters, "Regular", requests)
        self.assertIn("  keep explicit 0", lines)
        self.assertIn("  propose set explicit -60", lines)
        self.assertIn("  propose set explicit 0", lines)
        self.assertLess(lines.index("A/V: explicit 0; effective 0"),
                        lines.index("Aacute/W: explicit absent; effective -70"))
        self.assertEqual((masters, requests), before)
        self.assertEqual(report(masters, "Regular", requests), lines)

    def test_invalid_late_proposal_or_missing_metadata_prints_nothing(self) -> None:
        report = self.namespace["proposal_lines"]
        for value in (math.nan, math.inf, -math.inf, True, "0"):
            requests = deepcopy(self.namespace["requests"])
            requests[-1]["proposed"] = value
            output = io.StringIO()
            with self.subTest(value=value), contextlib.redirect_stdout(output):
                with self.assertRaisesRegex(ValueError, "Proposed value must be a finite number"):
                    for line in report(self.namespace["masters"], "Regular", requests):
                        print(line)
            self.assertEqual(output.getvalue(), "")
        requests = deepcopy(self.namespace["requests"])
        del requests[-1]["candidates"]
        with self.assertRaises(KeyError):
            report(self.namespace["masters"], "Regular", requests)


if __name__ == "__main__":
    unittest.main()
