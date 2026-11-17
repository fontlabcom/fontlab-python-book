---
this_file: src_docs/md/04-work-in-the-scripting-panel.md
---

# 4. Work in the Scripting panel

A script has three things worth checking: the code you intend to run, the result it produces, and the file you keep for later. This chapter follows all three through FontLab's Scripting panel.

You need FontLab 9 and the Python basics from [Chapter 2](02-python-basics.md). The examples use fictional glyph names and ordinary Python; they need no open font and make no font changes. The panel instructions have been checked against current documentation and application source. The examples have been executed in Python 3.11 outside FontLab. **Native panel testing remains pending.** This draft also awaits integration with the book's semantic map.

## Separate the editor, output and file

Open **Window > Panels > Scripting** to work on code, and **Window > Panels > Output** to read printed messages and errors. The Scripting panel also offers a `py>` console for individual commands. Use the main script editor for the examples below. [FontLab manual: Python scripting](https://help.fontlab.com/fontlab/9/articles/python-scripting/index.html).

| Place | What to check |
| --- | --- |
| Script editor | The instructions you are about to execute. |
| Output panel | Messages and errors from execution. |
| Saved `.py` file | The script text you can reopen or share. |

**Run** executes the current editor contents. Selecting a few lines is not a way to restrict this exercise to those lines: inspect the whole editor before running. Saving, running and debugging are separate operations. Treat a successful run as evidence about execution, then check the saved file separately. [FontLab manual: Debugging Python scripts](https://help.fontlab.com/fontlab/9/articles/debugging-python-scripts/index.html).

## Start with an empty editor

Preserve any existing work before replacing it, even if it belongs to a different exercise.

1. If the editor is empty, continue with step 3. If it contains code, choose **Save Script As...** from the panel's local menu and use a new `.py` filename.
2. If you saved existing code in step 1, open that file in a text editor and confirm that the file contains the complete script. If it does not, keep the editor contents and resolve the save before continuing.
3. Choose **New Script** from the Scripting panel's local menu.
4. Check that the editor is empty. Enter the following code, including the four spaces before the indented `print` line.

```python
glyph_names = ["A", "B", "space"]
print("Sample report started")
for glyph_name in glyph_names:
    print(f"Name: {glyph_name}")
print(f"Sample report finished: {len(glyph_names)} names")
```
```text
Sample report started
Name: A
Name: B
Name: space
Sample report finished: 3 names
```

The second box is expected output. Copy only the Python code into the editor. These names are strings in a list, not glyph objects read from a font.

The `f` before a string's opening quotation mark makes it an **f-string**. Python evaluates each expression between `{` and `}` and inserts its value into the text. Here `{glyph_name}` supplies the current name, and `{len(glyph_names)}` supplies the number of names. The braces and the `f` are syntax; they do not appear in the printed result. [Python tutorial: Formatted string literals](https://docs.python.org/3.11/tutorial/inputoutput.html#formatted-string-literals).

Confirm that the sample is the only code in the editor, then click **Run**. Look in **Output** for the five lines above. The first and last messages identify the bounds of this report; the last message confirms that execution reached its final statement. It does not independently prove that a future font-editing script performed the right edits.

Change `"B"` to `"C"` in the list and run again. Compare the name lines and the count. This change should produce `Name: C` while retaining a count of three. Restore `"B"` before the saving exercise.

## Save and reopen the script

Use a filename that describes the exercise, such as `sample-name-report.py`.

1. Choose **Save Script As...** and save the sample under that new `.py` filename.
2. Open the saved file in a text editor and compare its complete contents with the Scripting editor. Resolve any missing or different text before replacing the editor contents.
3. Choose **New Script**, then **Open Script** from the panel's local menu and select the verified file.
4. Compare the reopened code with the sample. Click **Run** only after confirming that this is the code you intend to execute.

After editing an already named script, **Save Script** writes to its current filename; **Save Script As...** lets you choose another. Verify the file after a save when its preservation matters. A closed dialog, a familiar title or messages left in Output are not a substitute for checking its contents.

Keep this exercise as `.py`. The manual distinguishes ordinary `.py` files opened for editing from `.vfpy` files that can execute immediately through FontLab's file-opening route. To inspect an unfamiliar script without executing it, open it in a text editor. [FontLab manual: Script library and file types](https://help.fontlab.com/fontlab/9/articles/python-scripting/index.html).

## Keep each run understandable

Python's **context**, or namespace, holds names and their current values. FontLab can retain names from earlier commands or runs. A script that uses an old value without assigning it may therefore appear complete when it is missing an input.

The panel's **Clear Python Context** option resets that namespace before runs when enabled; **Clear Python Context Now** requests a reset immediately. These controls concern Python state. Clearing the Output panel concerns displayed messages. Neither is a procedure for restoring font data. [FontLab manual: Scripting panel and console](https://help.fontlab.com/fontlab/9/articles/python-scripting/index.html).

The sample assigns `glyph_names` on every run, so it does not need a previous command to create that list. Keep that habit as scripts grow: define the inputs they need, and distinguish sample data from objects obtained through FontLab's API. Save code you want to retain before experimenting with its context.

## Read an error without losing the evidence

An **exception** reports a problem encountered during execution. Try one that has no font-editing consequences. First preserve and verify the report file as above. Choose **New Script**, confirm that the editor is empty, and enter only this example:

```python title="Intentional ZeroDivisionError"
print("Sample check started")
print(1200 / 0)
print("Sample check finished")
```

Click **Run**. Python prints `Sample check started`, then raises `ZeroDivisionError` because the divisor is zero. The final `print` is not reached. The diagnostic includes `ZeroDivisionError: division by zero`; the surrounding traceback and filenames depend on the execution environment. These Python results were checked outside FontLab, not captured from its panel.

A **traceback** identifies the chain of calls that led to an exception. Read the exception type and message, then locate the relevant line in your script. Here the failing expression is `1200 / 0`. Replacing its zero with `3` permits all three lines to run and prints `400.0` between the two messages. [Python tutorial: Exceptions](https://docs.python.org/3.11/tutorial/errors.html#exceptions).

A **syntax error** is different: Python cannot parse the instructions. An unfinished call such as `print("Sample"` lacks its closing parenthesis. Fix the syntax before expecting the script to execute. The indicated position helps locate the problem, but the missing punctuation can belong earlier in the statement. [Python tutorial: Syntax errors](https://docs.python.org/3.11/tutorial/errors.html#syntax-errors).

Copy the diagnostic text you need before clearing Output or starting another run. A useful debugging note includes the script version, its inputs, what you expected, and the exact error. An error identifies where execution failed; it does not establish that earlier operations had no effect.

## Plan for completion before relying on Stop

The report loop has three items and no font operations. It finishes on its own. Start with such bounded work while learning the panel.

Normal **Run** and a debugging session are different execution routes. The debugger's **Stop** request belongs to the debugging session. The manual states that debugger Pause and Stop requests must wait for a native call to return; a native call is an operation performed by the application rather than by ordinary Python statements. A long FontLab operation can therefore finish before the debugger responds. [FontLab manual: Debugging Python scripts](https://help.fontlab.com/fontlab/9/articles/debugging-python-scripts/index.html).

This chapter does not establish a dependable interruption procedure for normal **Run**. Do not begin an endless loop as a way to test the controls. Stopping execution is also not a promise to reverse changes already made. No Undo grouping, rollback or recovery behavior has been tested here.

Before a later script changes font data, define its target and expected result, preserve a separate source copy, and verify the particular API's update and Undo requirements. The [data distinctions in Chapter 3](03-understand-font-data.md) help define that target. For now, keep the saved report and its expected output together: they give you a small script whose purpose and result you can explain.
