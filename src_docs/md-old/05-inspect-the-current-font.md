---
this_file: src_docs/md/05-inspect-the-current-font.md
---

# 5. Inspect the current font

The lists in earlier chapters contained fictional names. To read an open font, a script needs an object supplied by FontLab. The first question is whether that object exists; the second is which interface it supports.

This chapter introduces a small inspection script for FontLab 9. Its API calls have been checked against reference material and implementation source. Offline tests use **test doubles**: small Python objects standing in for native results. A separate bounded native test verified both branches through `run_python` on FontLab 9.0.9809 with embedded Python 3.11.6; its exact scope is recorded below. **Scripting panel UI verification remains pending**, as does integration with the book's semantic map. The example contains no font-editing or saving call.

## A module gives access to objects

A **module** groups names that Python can import. In `import fontlab`, the name `fontlab` becomes available to the script. The expression `fontlab.CurrentFont()` then looks up `CurrentFont` in that module and calls it. The parentheses matter: they request the function's result. [Python tutorial: Modules](https://docs.python.org/3.11/tutorial/modules.html).

An **object** combines data with the operations available for that kind of data. A **class** describes a kind of object. For example, the ordinary Python list has operations for working with its items; a native font object exposes operations defined by FontLab's bindings, the code that connects Python to the application.

The FontLab environment has several related interfaces. The `fontlab` module exposes editor and workspace objects, while `fontgate` exposes the underlying font-engine objects. An object from one interface does not automatically support members from another. [FontLab manual: The Python API and libraries](https://help.fontlab.com/fontlab/9/articles/the-python-api-and-libraries/index.html).

Here is one crossing between those interfaces: `fontlab.CurrentFont()` returns a **`fontgate.fgFont`** object for the current font, or `None` when it cannot obtain one. It does not return a `fontlab.flPackage`. The function's module tells you where to find the function; it does not determine the class of its result. The current implementation establishes this return distinction; the captured reference describes the function but does not provide a complete return annotation. [FontLab reference: CurrentFont](https://fontlabcom.github.io/fontlab-python-docs/reference/fontlab.html#fontlab.CurrentFont), [FontGate reference: fgFont](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgFont.html#fontgate.fgFont).

The name `font` in the example below is our variable, not an API name. It refers to the returned native wrapper around the current font data. Assigning that result to a variable does not create a separate font document or a backup.

## Read members in their own interface

A **member** is a name available through a module or object. A **method** is an operation attached to an object. In `font.keys()`, the dot looks up `keys` on this particular font object, and the parentheses call that method.

For an `fgFont`, `keys()` returns a Python list containing the names of all glyphs in the font. The list holds strings, not glyph objects. The current binding also supports `len(font)`, which reads the number of glyphs. That count concerns the whole font's glyph collection; it does not count selected cells, characters in a text string, layers or contours. [FontGate reference: keys](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgFont.html#fontgate.fgFont.keys).

These are the only font-data operations used in this chapter:

| Expression | Result used here |
| --- | --- |
| `fontlab.CurrentFont()` | A current `fgFont` wrapper, or `None`. |
| `len(font)` | The number of glyphs in that font. |
| `font.keys()` | A list of glyph-name strings. |

Do not turn the conceptual hierarchy from [Chapter 3](03-understand-font-data.md) into guessed Python attributes. A font, glyph, layer and contour describe different scopes; the exact member names and return types still come from the API reference and its implementation.

## Handle a missing font before reading it

`None` is Python's value for absence. It is not a font with zero glyphs. [Python reference: None](https://docs.python.org/3.11/library/constants.html#None).

The condition `font is None` checks for that specific absence. Using only `if font:` would test truth instead. Container objects can be false when their length is zero, so a truth test can confuse an empty collection with a missing result. Keep these cases separate. [Python reference: Truth value testing](https://docs.python.org/3.11/library/stdtypes.html#truth-value-testing).

For the available-font branch, make the intended font window active before running the script. The script asks FontLab for its current font once and retains that returned reference for the report. It does not select the first item from a list of open fonts or choose a font by filename. If you change the active document, run the complete script again to obtain the current reference; do not reuse an earlier console variable as if it tracked your window choice.

## Inspect a count and a few names

Follow the preservation and empty-editor procedure in [Chapter 4](04-work-in-the-scripting-panel.md). Enter only the script below in the Scripting editor. Use FontLab's Python environment; the ordinary external Python used for the earlier fictional lists does not supply FontLab's running application objects.

```python title="Native inspection: bounded runtime test recorded below"
import fontlab

font = fontlab.CurrentFont()
if font is None:
    print("No current font. Open a font and run again.")
else:
    print(f"Glyphs in the current font: {len(font)}")
    glyph_names = font.keys()
    for glyph_name in glyph_names[:5]:
        print(f"Name: {glyph_name}")
    print("Read-only report finished")
```

The slice `glyph_names[:5]` takes at most the first five items from the returned list. It starts at the beginning and stops before index 5. This limits the printed name lines; `keys()` still retrieves the full name list. The example does not establish that this list follows the Font window's displayed sort or filter.

With no current font, the expected branch prints:

```text
No current font. Open a font and run again.
```

An available font with zero glyphs should instead print a count of zero followed by the completion message. For a fictional seven-glyph result whose first five names are `A`, `B`, `space`, `a.alt` and `f_i`, the report would be:

```text
Glyphs in the current font: 7
Name: A
Name: B
Name: space
Name: a.alt
Name: f_i
Read-only report finished
```

The seven-glyph output is fictional and remains an offline test case. The no-current-font message was also observed in the bounded native test below. A real font supplies its own count and names. Use **Run** and **Output** as described in Chapter 4 only after checking the entire editor. If an API call fails, retain the error and the installed FontLab version for investigation; do not replace the failed read with an invented zero or an empty list.

## Understand what the report proves

The script requests the current font, reads its glyph count and names, and prints a limited report. It does not traverse glyph layers, inspect outlines or change the Font window selection. Reading names also does not establish that a font has Unicode mappings or usable outlines; those are separate questions introduced in Chapter 3.

A native wrapper remains connected to application data. This example does not test what happens to that wrapper after its document is closed, nor does it establish an atomic snapshot across document changes. Keep the run short, keep the target document stable, and obtain a fresh reference for another run.

The automated Python checks cover a missing result, a present but empty result, a seven-name result limited to five printed names, and a read that raises an error. They verify the script's branching and output with test doubles. They remain separate from the native observations below.

## Bounded native verification

On 13 November 2026, the exact script above ran through the `run_python` automation route in **FontLab 9.0.9809, build 9809, with embedded Python 3.11.6**. This exercised the installed Python binding, not the Scripting panel's editor or Run button.

With no fonts open, it printed the no-current-font message without error. An owned copy of the GetGo CC0 **GG Vize** VFJ fixture was then opened as the sole font. The script reported **101 glyphs** and the first five names `.notdef`, `space`, `exclam`, `quotedbl` and `numbersign`, followed by the completion message. An independent native `list_glyphs` query agreed with the count and those five names. Supplementary introspection reported an `fgFont` result and a Python `list` from `keys()`.

After the report, the fixture's Font window had `windowModified` equal to `False` and no modification indicator in its title. **No before-run dirty-state capture succeeded**, so this is a post-run observation, not a before/after preservation comparison. The owned font was closed without saving; no fonts remained open. Source and copy file hashes matched before the test and remained unchanged afterward. No font edits, saves or preference changes were performed.

This test did not cover a native font with zero glyphs, multiple open fonts, changes of active document, wrapper use after closure, Scripting panel interactions, Undo/Redo, export or save/reopen. It does not establish the Font window's displayed sorting order, complete view/history preservation, broad API compatibility or acceptance of later chapters. Those checks remain open.
