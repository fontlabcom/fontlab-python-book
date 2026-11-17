---
this_file: src_docs/md/08-keep-a-recoverable-source.md
---

# 8. Keep a recoverable source before you change a font

A script can stop after changing only part of a font. A refreshed window can show a change that has not been saved. An Undo label can exist without proving that every affected object will be restored. Treat these as separate results to check.

This chapter explains that separation and provides a **proposal-only** Python exercise. It changes no font and writes no file. The FontLab explanations come from current documentation and inspected source. **Native writer acceptance remains pending.** A bounded native experiment below shows why Python read-back alone cannot establish persistence. The chapter also awaits semantic-map integration.

## Keep the script, source and result distinct

| Item | What it preserves |
| --- | --- |
| A Python script file, usually `.py` | The code you intend to run. |
| A native FontLab source file, `.vfc` or `.vfj` | Editable font data at a saved point. |
| The font open in the editor | The current working state, which may include unsaved changes. |
| An exported font, such as `.otf` or `.ttf` | A production result; it does not replace the editable source. |

Saving the script does not save the font. Saving the font does not establish which script version produced it. Keep both identities clear when testing a change. Native files preserve editable design data, but session and workspace information depends on save options; they are not an unconditional recording of the entire application. [FontLab manual: Saving and closing fonts](https://help.fontlab.com/fontlab/9/articles/saving-and-closing-fonts/index.html).

## Establish a checkpoint you can inspect

Before testing a script that changes a font, work from a separately named copy. A **checkpoint** here means a deliberately retained source file whose contents you can verify. It is not a Python variable holding a font wrapper.

Use this checklist before the modifying script runs:

1. Identify the intended font and the source file you want to preserve. Include any unsaved work you need in the checkpoint.
2. Use **File > Save Font As...** to choose a native VFC or VFJ destination with a new, unused filename. Confirm that saving succeeded and check the actual destination.
3. Verify that the retained file exists and opens with the expected data. A filename alone is not proof of a usable checkpoint.
4. Establish a separately named experiment copy, also at an unused destination. Keep the checkpoint unchanged while testing.
5. Before running the script, check the current font, glyph/layer scope and experiment file identity again. Save Font As establishes a new continuing destination, so do not assume the old path is still current.

These steps describe the manual's save workflow and the verification needed before relying on it. They have not been exercised natively for this book. The example below does not require saving or opening a font.

Existing-file preferences are not interchangeable safeguards:

| Save policy | What happens to an existing destination file |
| --- | --- |
| Overwrite | The older file is replaced without a backup through this mechanism. |
| Move to trash | The older file is moved to the Trash or Recycle Bin. |
| Rename | The older file is retained under a dated name. An optional setting uses a subfolder named after the file, with `.backup` appended: for example, `OrchardSans-Regular.backup` for `OrchardSans-Regular.vfc`. The folder must exist or be created successfully. |

Check the configured policy and the actual retained file rather than assuming a backup exists. Autosave recovery copies have a separate purpose and do not replace your deliberate checkpoint. **Save All** affects all open fonts, so it is broader than preserving the one font being tested. [FontLab manual: Saving and closing fonts](https://help.fontlab.com/fontlab/9/articles/saving-and-closing-fonts/index.html).

## Compute a proposal before applying anything

A proposed change should say what it would affect and how the value would change. This small exercise treats dictionary values as fictional advance widths in font units. Its rules require finite, nonnegative source and proposed widths. These are teaching constraints for this example, not a complete validator for every font or writing system.

The script imports Python's standard `math` module. `math.isfinite(value)` returns false for infinity and for NaN, the floating-point value called “not a number.” That catches values a simple less-than-zero check would miss. [Python reference: math.isfinite](https://docs.python.org/3.11/library/math.html#math.isfinite).

Run the code in Python 3.11. If you use FontLab's Scripting panel, first preserve existing editor work and establish an empty script using [Chapter 4](04-work-in-the-scripting-panel.md). Enter only this example. It imports no FontLab module.

```python
import math


def propose_widths(widths, adjustment):
    if not math.isfinite(adjustment):
        raise ValueError("Adjustment must be finite")
    plan = []
    for name, old_width in widths.items():
        if not math.isfinite(old_width) or old_width < 0:
            raise ValueError(f"Invalid sample width for {name}")
        new_width = old_width + adjustment
        if not math.isfinite(new_width) or new_width < 0:
            raise ValueError(f"Invalid proposed width for {name}")
        if new_width != old_width:
            plan.append((name, old_width, new_width))
    return plan


def show_plan(widths, adjustment):
    plan = propose_widths(widths, adjustment)
    print(f"Proposed changes: {len(plan)}")
    for name, old_width, new_width in plan:
        print(f"{name}: {old_width} -> {new_width}")


sample_widths = {"A": 600, "space": 250}
show_plan(sample_widths, 20)
```
```text
Proposed changes: 2
A: 600 -> 620
space: 250 -> 270
```

`widths.items()` supplies each name and value in dictionary insertion order. The first function builds a new list of three-value tuples; it never assigns into the input dictionary. The second prints only after the complete plan has been checked. An adjustment of zero produces no proposed changes. An empty dictionary also produces a zero count. [Python tutorial: Dictionaries](https://docs.python.org/3.11/tutorial/datastructures.html#dictionaries).

For a harmless error exercise, change only the final adjustment from `20` to `-300`. A would have a proposed width of 300, but space would have a proposed width of −50. The function raises `ValueError` for space before any plan is printed. The original dictionary still contains 600 and 250. No partial change needs Undo because this example never applies the proposal.

This structure is useful preparation for a writer, but it is not a native transaction. A future writer must recheck its live targets before applying a plan: the font or selection may have changed since inspection. It also needs its own history, update and failure behavior. Adding setters to this example would require new source checks and native tests.

## An update can do more than redraw

A **refresh** sounds like a display operation. FontLab's update interfaces can also process changes to the underlying objects. Their effects depend on the exact call and object type.

In the inspected binding, `fontlab.Update()` dispatches to the changes controller. With an `fgGlyph`, it can synchronize stored FontGate data back into the editor glyph. With an `fgFont`, it visits every glyph before notifying the package. `UpdateAll()` uses a preview path that processes queued object updates. These implementation details are why a report should not acquire a blanket update call merely to make its output appear. [FontLab API reference](https://fontlabcom.github.io/fontlab-python-docs/reference/fontlab.html#fontlab.Update).

An update call is not evidence of a file save, an Undo step or a rollback. A real writer needs the update protocol appropriate to its objects and scope. The proposal-only exercise needs none of these calls.

## A changed Python value may not reach the saved font

A bounded experiment on 13 November 2026 tested this distinction in **FontLab 9.0.9809, build 9809, with embedded Python 3.11.6**. It used a byte-identical owned copy of the GetGo CC0 GG Vize source, with no other fonts open. A setter-only attempt to increase A's `fgGlyph.width` by 10 produced different observations:

| Observation | A's width in font units |
| --- | --- |
| Initial Python read and independent native metrics | 606 |
| Python read immediately after the setter, and in a later state probe | 616 |
| Independent native metrics after the setter | 606 |
| Python read and independent native metrics after saving to a new VFJ and reopening it | 606 |

The control glyph B stayed at 520 in these checks. Before and after the setter, the dirty flag remained false and the called history-state value remained 0. They were also false and 0 after reopening. Native A/B glyph responses were identical before and after the setter; their layer payloads matched the initial ones after reopening. Saving reported success, but the intended increase was absent from the reopened font.

**This setter-only procedure did not persist the increase in this fixture and runtime.** It does not establish that all setters fail, or that another object path or version behaves the same way. No explicit `fontlab.Update()` or history-publication sequence was tested, and Undo/Redo was not invoked. The setter's own inspected implementation calls an internal owner update; that does not establish the effect of a separate editor update.

Native snapshots preceded the assignment and may have affected wrapper or cache state. Installed-binary correspondence with the inspected source, Scripting panel UI, other masters, dependencies and whole-font preservation remain unverified. This is a recorded result, not a runnable mutation recipe. Qualify an explicit writer and its persistence separately before relying on it.

## Undo, stopping and saving answer different questions

| Result | What still needs checking |
| --- | --- |
| The script returned or printed success | Did it affect the intended targets, and did it leave unrelated data intact? |
| A history entry appears | Does Undo restore all intended state, and does Redo restore the change correctly? |
| The window displays the change | Is the underlying data correct, and has the intended source file been saved? |
| Saving reports success | Does the actual saved file reopen with the expected data? |

A **history notification** tells FontLab about an editing operation and its objects. The inspected implementation has different paths for canvas and package history, and notifications can also refresh contour data or trigger dependent work. There is no general rule that one script creates exactly one complete Undo step. The current App writer examples deliberately separate history preparation, mutation, notification and read-back, and retain explicit native qualification limits. [Native scripting guide: Writer results and failures](https://fontlabcom.github.io/fontlab-python-docs/guide/native.html#handle-writer-results-and-failures).

An exception can occur after earlier changes have succeeded. Do not automatically rerun a failed writer: it may apply those earlier changes twice. Do not put a global Undo, Revert or Save in a catch-all error handler. Retain the error details, inspect what happened and choose recovery using the verified source copy and the actual history state.

Debugger Stop is not rollback. A native call can finish before the debugger regains control, and stopping does not undo edits already made. Normal Run also ignores breakpoints. [FontLab manual: Debugging Python scripts](https://help.fontlab.com/fontlab/9/articles/debugging-python-scripts/index.html).

**Revert Font** reloads the font's file and discards later unsaved work. It is a whole-font operation, not a substitute for undoing one selected edit. Rewind is different again: it explores a geometric blend between recorded forms rather than replaying ordinary Undo steps. Neither is an automatic recovery step in this chapter. [FontLab manual: Saving and closing fonts](https://help.fontlab.com/fontlab/9/articles/saving-and-closing-fonts/index.html), [Reviewing glyph history](https://help.fontlab.com/fontlab/9/articles/reviewing-glyph-history/index.html).

## Qualify a writer on copies

Before relying on a future native writer, retain separate observations for these checks:

- **Apply:** compare intended changes and unrelated data, including the target glyphs, layers and selection.
- **Failure:** test a refusal before changes and a failure after some work; ensure the report describes any partial result honestly.
- **Undo and Redo:** inspect the data after each action. A counter named `undo_steps` is not proof that either action restored the expected state.
- **Save and reopen:** write to the intended experiment destination, reopen it and compare the result. Keep the original checkpoint available.
- **Context:** repeat for the window and target scope the writer supports. Do not infer multi-glyph safety from a successful one-glyph case.

These are acceptance requirements, not results established by the fictional exercise. Python tests can verify its arithmetic, errors and unchanged input. They cannot establish native mutation safety, complete Undo coverage or saved-file preservation.
