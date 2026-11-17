---
this_file: src_docs/md/17-test-the-promise.md
---

# Test the promise, then test the host

A script prints “Done.” What did it finish: calculating a proposal, changing the open font, or saving a result that survives reopening?

A useful test states an input, an expected result and the environment in which that result matters. This chapter tests fictional width records in external Python 3.11. **Native UI behavior, dirty-state tracking, Undo/Redo and save/reopen remain unverified for this chapter.** The draft remains provisional pending independent review and semantic-map integration.

## Give a small function a precise job

Suppose a report needs the difference between two advance-width measurements. Keep that arithmetic separate from code that reads a FontLab object. It can then be tested without opening a font.

The fictional records below represent the same glyph, master and font-unit scale before and after an imaginary change. They contain a string `glyph` and an ordinary finite numeric `width`. The function checks that the glyph names match, then subtracts. A missing key raises `KeyError`; different glyph names raise `ValueError`.

This is a deliberately small comparison. It does not validate every possible input type or numerical range, identify a real font or decide whether a width is suitable. Zero and negative differences are valid results. No native object is read or changed.

Create a folder for the exercise, then save this file as **`width_report.py`**:

```python
# this_file: width_report.py

def width_change(before: dict, after: dict) -> float:
    """Compare fictional measurements of one glyph in one master and unit scale."""
    if before["glyph"] != after["glyph"]:
        raise ValueError("Measurements must name the same glyph")
    return after["width"] - before["width"]
```

## Write down the expected behavior

Python's standard library includes `unittest`. A **test case** checks a particular response; a **test suite** groups cases; a **test runner** executes them and reports the result. A **fixture** supplies the starting data and any preparation or cleanup. Here, the fixtures are small dictionaries. [Python unittest](https://docs.python.org/3.11/library/unittest.html#basic-example).

The next file introduces class syntax. `class TestWidthChange(unittest.TestCase):` defines a group that inherits unittest's checking methods. Each method receives `self`, the current test-case object. A method whose name starts with `test_` is discovered as a test.

`self.assertEqual(actual, expected)` compares values. `assertAlmostEqual` allows a small numerical difference, useful when floating-point arithmetic cannot represent a decimal exactly. `with self.assertRaises(KeyError):` expects the indented operation to raise that exception. If it does not, the test fails. An expected exception is a checked result, not an ignored failure. [Python assertion methods](https://docs.python.org/3.11/library/unittest.html#assert-methods).

Save **`test_width_report.py`** beside the first file:

```python
# this_file: test_width_report.py
import unittest

from width_report import width_change


class TestWidthChange(unittest.TestCase):
    def test_increase(self) -> None:
        before = {"glyph": "a", "width": 500}
        after = {"glyph": "a", "width": 540}
        self.assertEqual(width_change(before, after), 40)

    def test_equal_and_zero_widths(self) -> None:
        record = {"glyph": "a", "width": 0}
        self.assertEqual(width_change(record, record), 0)

    def test_decrease(self) -> None:
        before = {"glyph": "a", "width": 500}
        after = {"glyph": "a", "width": 480}
        self.assertEqual(width_change(before, after), -20)

    def test_fractional_difference(self) -> None:
        before = {"glyph": "a", "width": 500.1}
        after = {"glyph": "a", "width": 500.4}
        self.assertAlmostEqual(width_change(before, after), 0.3)

    def test_missing_width_raises(self) -> None:
        before = {"glyph": "a", "width": 500}
        with self.assertRaises(KeyError):
            width_change(before, {"glyph": "a"})

    def test_different_glyphs_raise(self) -> None:
        before = {"glyph": "a", "width": 500}
        with self.assertRaises(ValueError):
            width_change(before, {"glyph": "b", "width": 500})

    def test_inputs_are_preserved(self) -> None:
        before = {"glyph": "a", "width": 500}
        after = {"glyph": "a", "width": 540}
        width_change(before, after)
        self.assertEqual(before, {"glyph": "a", "width": 500})
        self.assertEqual(after, {"glyph": "a", "width": 540})
```

Open a terminal in that folder. Use an external Python 3.11 interpreter; in the following commands, `python` must refer to that interpreter. Check its version first, using its full executable path if needed. [Chapter 10](10-organize-reusable-scripts.md) explains the separate external and embedded environments.

```bash
python --version
python -m unittest -v
```

Unittest discovers the `test_` file, imports it and runs seven tests. The final result should say `Ran 7 tests` and `OK`; the timing and displayed test names depend on the invocation. No FontLab, Fontport or Glyport installation is needed for this exercise. [Python test discovery](https://docs.python.org/3.11/library/unittest.html#test-discovery).

## Make sure a wrong result is detected

Temporarily change the expected `40` in `test_increase` to `41`, then rerun. The test should report a failure with `AssertionError: 40 != 41` and a nonzero process exit status. Restore `40` and confirm all seven tests pass again. The wrong value belongs in the test expectation; changing the helper to return it would break the intended behavior.

A **failure** means an assertion did not hold. An **error** means an unexpected exception interrupted a test. For example, removing `width` from the first test's `after` record would produce a `KeyError` error there. The same exception is expected in `test_missing_width_raises`, so that test passes. Syntax errors occur earlier, when Python parses the code. [Python test results](https://docs.python.org/3.11/library/unittest.html#unittest.TestResult); [Python errors and exceptions](https://docs.python.org/3.11/tutorial/errors.html).

Read the exception type and message, then use the traceback's files, lines and calls to locate the operation. The line where Python detects an error is not always where its cause began. Preserve the original error if cleanup also fails. Fontport's driver tests explicitly simulate both failures and check that they remain separate; those tests use a fake client, not FontLab. [Driver error tests](https://github.com/fontlabcom/fontlab-fontport/blob/main/tests/test_native_driver.py).

## Ask what the test replaces

A **test double** replaces part of a system with chosen behavior. It might record method calls, return a prepared value or raise a controlled exception. This makes hard-to-trigger cases repeatable, but the replacement knows only what its author gave it.

FontLab App's component tests replace FontLab and PythonQt objects with doubles. They check call order, readback, refusal before writes and simulated partial failures. The source explicitly says these tests do not prove native Undo/Redo. One recorded notification is not evidence that FontLab restored the entire font correctly. [Component writer tests](https://github.com/fontlabcom/fontlab-fontlabapp/blob/main/tests/test_component_writer.py).

Testing a native runner also differs from running it natively. Glyport's verifier tests inject a function that reports fictional successes and one failure. That checks how the report counts outcomes. Without a runner, its fixture targets remain blocked; creating a report does not make them pass. [Verifier tests](https://github.com/fontlabcom/fontlab-glyport/blob/main/tests/test_verify_runtime.py).

Keep the evidence surfaces explicit:

| Check | What it can establish |
| --- | --- |
| Pure function test | Results for the supplied data and cases |
| Adapter test with doubles | Behavior against the modeled host contract |
| External installed-package test | That artifact's behavior in that interpreter |
| Native UI test | Observed behavior in the identified application/build and document state |
| Save, close and reopen | What the reopened artifact actually retains |
| Export and target-application test | Behavior of the identified delivered font |

A passing row cannot stand in for the rows below it. A well-formed report or a filename containing `native` cannot supply missing observations.

## Prepare a native acceptance case

A **native fixture** is an owned disposable source with known starting data, opened in the real application for a specific check. Its identity matters: record the source file, glyph, master or layer and intended result. A glyph name alone is insufficient when two open fonts contain that name. Existing Fontport tests cover that ownership distinction with doubles. [History-scope tests](https://github.com/fontlabcom/fontlab-fontport/blob/main/tests/test_host_history_scope.py).

For a future native edit, distinguish these observations:

1. The intended value changes in the open model, and relevant UI views reflect it.
2. The document's modified or **dirty state** agrees with the operation. That indicator records unsaved-change state; it does not prove the saved file contains the edit.
3. Actual Undo restores the baseline and Redo restores the intended result, including relevant surrounding font data.
4. Saving, closing and reopening preserves the result. Use fresh handles after reopening; cached wrappers can refer to closed native objects.
5. Exported output retains the intended data and works in the target application, if export is part of the script's purpose.

Fontport's native driver source separates readback, Undo, Redo and reopened readback into distinct phases. Its lifecycle driver separately checks stale handles after closure. These are examples of checks to design, not evidence that the drivers passed here or that every listed field remains writable. [Metadata phases](https://github.com/fontlabcom/fontlab-fontport/blob/main/tests/native_drivers/info_steps.py); [lifecycle phases](https://github.com/fontlabcom/fontlab-fontport/blob/main/tests/native_drivers/round10_lifecycle_steps.py).

Test no-font, closed-font, invalid-input and partial-failure cases too. An exception after a write does not mean nothing changed. Inspect the state before retrying; a timed-out native operation may still be running. [Chapter 8](08-keep-a-recoverable-source.md) explains why update, Undo and saving need separate evidence.

## Record the runtime with the result

The inspected Fontport and Glyport sources distinguish the embedded Python 3.11 arm64 target from external Python environments. Package metadata permitting Python 3.11 or later is not a promise that every interpreter, binary dependency or UI binding works inside FontLab. A terminal installation does not establish what the host can import. [Fontport runtime requirements](https://github.com/fontlabcom/fontlab-fontport/blob/main/README.md); [Glyport runtime requirements](https://github.com/fontlabcom/fontlab-glyport/blob/main/README.md).

Retain the script revision, interpreter/platform, package versions and loaded paths, fixture identity, expected and observed results, and any output artifact. Record failed, blocked and unexecuted checks separately. The seven fictional tests above establish their comparison behavior in external Python; native behavior and persistence still require their own acceptance work.
