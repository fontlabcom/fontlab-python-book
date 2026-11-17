---
this_file: src_docs/md/06-find-the-glyph-you-mean.md
---

# 6. Find the glyph you mean

A glyph name, a glyph index and a Unicode codepoint can refer to the same glyph. They answer different questions, however, and the Python key you use determines which question you ask.

This chapter builds on the current-font example in [Chapter 5](05-inspect-the-current-font.md). Its lookup rules and metadata reads have been checked against the current binding source and API reference. The first two examples also passed a bounded native test on one FontLab 9 runtime, described below. The complete encoding-report project later in this chapter also passed a separate bounded native test on an owned fixture; its verification note identifies the tested cases. Further Python 3.11 control-flow checks use owned **test doubles**, which do not establish native behavior for those additional cases. The chapter also awaits semantic-map integration. It contains no font-editing, selection-changing or layer-switching call.

## Choose an identifier

| Identifier | Question it answers |
| --- | --- |
| Glyph name, such as `A` | Which glyph has this development name? |
| Glyph index, such as `65` | Which glyph occupies this position in the font's glyph collection? |
| Unicode codepoint, such as `U+0041` | Which glyphs carry an assignment for this character? |

Names are case-sensitive: `A` and `a` differ. Indices start at zero and can change when glyphs are inserted, removed or reordered. Unicode assignments can be absent or multiple. The Font window can arrange cells in an order different from the font's glyph indices. [FontLab manual: Glyph identity](https://help.fontlab.com/fontlab/9/articles/glyph-identity/index.html).

For the `fontgate.fgFont` returned by `fontlab.CurrentFont()`, the inspected binding interprets a string subscript as a name and a numeric subscript as an index. Thus `font["A"]` asks for the glyph named A, while `font[65]` asks for index 65. The latter does **not** look up U+0041, even though that codepoint's decimal value is 65. The class reference identifies the object; these subscript rules come from its implementation. [FontGate reference: fgFont](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgFont.html#fontgate.fgFont).

A missing name returns `None` in this binding. An out-of-range numeric index raises `IndexError`. This differs from the ordinary Python dictionary's missing-key behavior taught in Chapter 2. Similar notation does not make two object types share every rule.

## Find a name before reading its properties

An **attribute** is a named value read from an object. The following glyph attributes are used here:

| Attribute | Meaning |
| --- | --- |
| `glyph.name` | The glyph's name. |
| `glyph.index` | Its glyph index. |
| `glyph.unicodes` | A list of all its assigned integer codepoints. |

These are attribute reads, so they have no trailing call parentheses. The related `glyph.unicode` attribute reports only the first assignment, or `None` when there is no assignment. Use the complete list when a report needs every assignment. [FontGate reference: fgGlyph](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgGlyph.html#fontgate.fgGlyph).

The report below prints codepoints in hexadecimal, base 16. In Python code, `0x0041` is a hexadecimal integer literal equal to decimal 65. Unicode text commonly labels it `U+0041`. In an f-string, `{codepoint:04X}` formats the integer as uppercase hexadecimal with at least four digits, adding leading zeros as needed. Four is a minimum width: `0x1F600` becomes `1F600`, not a truncated four-digit value. [Python reference: Integer literals](https://docs.python.org/3.11/reference/lexical_analysis.html#integer-literals), [Format specifications](https://docs.python.org/3.11/library/string.html#format-specification-mini-language).

Preserve existing editor work and start with an empty script as described in [Chapter 4](04-work-in-the-scripting-panel.md). Enter only this example. It first checks for a current font, then for the chosen glyph name.

```python title="Native name lookup: bounded runtime test recorded below"
import fontlab

target_name = "A"
font = fontlab.CurrentFont()
if font is None:
    print("No current font. Open a font and run again.")
else:
    glyph = font[target_name]
    if glyph is None:
        print(f"No glyph named {target_name}.")
    else:
        print(f"Name: {glyph.name}")
        print(f"Glyph index: {glyph.index}")
        codepoints = glyph.unicodes
        if codepoints:
            for codepoint in codepoints:
                print(f"Unicode: U+{codepoint:04X}")
        else:
            print("No Unicode assignments")
```

If A is absent, the expected result is `No glyph named A.` An existing but unencoded A instead reports its name and index followed by `No Unicode assignments`. Those are different outcomes: an unencoded glyph still exists and may be used by layout rules or as a construction element.

For a fictional test glyph named A at index 0 with the single assignment U+0041, the expected report is:

```text
Name: A
Glyph index: 0
Unicode: U+0041
```

The index and assignments come from the object, not from the spelling of its name. Real font data supplies its own values. A list containing the integer zero is also nonempty: an assignment U+0000 must not be mistaken for no assignment. The condition tests the complete list, rather than the truth of its first codepoint.

## Search the assignments by glyph index

To find glyphs assigned to U+0041, inspect their assignment lists. Do not assume that the glyph must be named A, or that the first matching name is the only match.

The following script visits indices from zero through `len(font) - 1`. Python's `range(len(font))` supplies those indices; for an empty font it supplies none. The test `target_codepoint in glyph.unicodes` checks membership in the assignment list.

If an index unexpectedly yields `None`, `raise RuntimeError(...)` stops the script with an explicit error. The result count is printed only after the complete scan, so that missing glyph is not silently omitted from a supposedly complete result.

Before replacing the previous example, preserve any work you want to keep. Start a new empty script using Chapter 4's procedure, then enter only this code:

```python title="Native Unicode search: bounded runtime test recorded below"
import fontlab

target_codepoint = 0x0041
font = fontlab.CurrentFont()
if font is None:
    print("No current font. Open a font and run again.")
else:
    matches = []
    for glyph_index in range(len(font)):
        glyph = font[glyph_index]
        if glyph is None:
            raise RuntimeError(f"No glyph at index {glyph_index}; report incomplete")
        if target_codepoint in glyph.unicodes:
            matches.append(glyph.name)
    print(f"Matches for U+{target_codepoint:04X}: {len(matches)}")
    for glyph_name in matches[:5]:
        print(f"Name: {glyph_name}")
```

An empty font or a font with no matching assignments should report `Matches for U+0041: 0`. If a glyph named `other` has that assignment and a glyph named A does not, the script should report `other`. The assignment determines membership in this result.

The scan collects all matches but prints at most five names, using the slice explained in Chapter 5. Its total is the full match count. This is a whole-font scan, not a time-bounded operation or a search confined to the Font window's visible cells. Keep the document stable during the run; do not edit, close or reorder it while the report is reading. No atomic snapshot or native object-lifetime guarantee has been established here.

The fictional report and untested cases above describe expected behavior. The following verification note identifies the results observed in FontLab. Unexpected errors should remain visible for investigation, rather than being converted into a reassuring zero.

## What has been verified in FontLab

On 13 November 2026, the two lookup scripts above ran through the `run_python` tool in FontLab 9.0.9809, build 9809, with embedded Python 3.11.6. With no font open, each printed `No current font. Open a font and run again.`

The fixture was an owned, byte-identical copy of the GetGo CC0 GG Vize VFJ, opened as the sole font. The name example reported `Name: A`, `Glyph index: 34` and `Unicode: U+0041`. The Unicode example reported `Matches for U+0041: 1` and `Name: A`. An independent native `list_glyphs` result agreed: 101 glyphs, A at index 34, and exactly one assignment match for U+0041.

A separate diagnostic lookup returned `None` for the absent name `__chapter6_owned_missing_name__`. Numeric indices 101 and 201 raised `IndexError` with the message `The index is out of range!`. That diagnostic caught the exceptions; neither published script was changed to catch them.

Before and after the reports, the current package path matched the owned copy and the Font window's `windowModified` flag was `False`. The source and copy file hashes stayed unchanged. Only the owned copy was closed, without saving, and the final open-font list was empty. These observations cover the measured dirty flag and files; they do not prove that every internal or view state remained unchanged.

This was Python binding acceptance through `run_python`, **not a Scripting panel UI test**. It did not test multiple fonts, an unencoded A, duplicate Unicode assignments, a font with no matching assignment, an empty font, or a missing glyph at an otherwise valid index. The supplementary absent-name and out-of-range results apply to this fixture and runtime. Layer getters, selection changes, mutations, Undo/Redo, save/reopen, other runtime versions and later chapters were not tested in this run. Semantic-map integration remains pending.

## Project: find unencoded and shared assignments

A useful inventory can answer two questions at once: which glyphs have no Unicode assignment, and which codepoints are assigned to several glyphs? Run this report when you want a short list to investigate before changing a font. It supplies complete totals and limited samples from **all stored glyph records**, regardless of the Font window's filter or selection.

Neither category automatically indicates a mistake. `.notdef`, alternates, ligatures and construction glyphs may intentionally be unencoded. A glyph with several assignments also differs from several glyphs sharing one assignment. The report describes stored metadata; it does not determine an exported font's character mapping or apply shaping rules. See [Chapter 25](25-mapping-is-not-shaping.md) for that distinction.

### Group assignments before printing

The `assignments` dictionary maps each integer codepoint to a list of glyph labels. A label includes the scan index and name so two records remain distinguishable even if their names coincide. Each glyph contributes once per codepoint: `set(glyph.unicodes)` removes repeated entries from that one list. A **set** contains distinct values; its order is not used for the final report. [Python tutorial: Sets](https://docs.python.org/3.11/tutorial/datastructures.html#sets).

For example, fictional records `.notdef: []`, `A: [65]`, `A.alt: [65, 65]` and `null: [0]` produce four glyphs, one unencoded glyph, two distinct codepoints and one shared codepoint. U+0041 has two glyph owners, not three. U+0000 remains an assignment, so `null` is encoded.

`assignments.items()` supplies each codepoint and its list together. The loop assigns these two values to `codepoint` and `glyph_labels`. `sorted(shared)` orders shared entries by their first value, the numeric codepoint. A slice limits each printed sample to five entries; `", ".join(...)` joins the sampled labels with comma-space separators. The totals use the complete lists, before slicing.

In a label, `{glyph.name!r}` asks Python for a representation that quotes the name and escapes embedded newlines and tabs. Long labels are shortened to 80 characters, including the index and ending dots. The shortened text is a display aid, not a complete glyph name for a lookup. [Python reference: Format string syntax](https://docs.python.org/3.11/library/string.html#formatstrings).

### Run the complete report

**This exact project has bounded native verification**, recorded below. It uses only the current-font, numeric-lookup, name and Unicode reads introduced above. Offline tests cover additional edge cases with metadata-only doubles; those tests do not establish native behavior for those cases.

Use an owned copy of a font. Preserve existing Scripting editor work and start an empty script using [Chapter 4](04-work-in-the-scripting-panel.md). Enter only the complete code below, then run it. Keep the document open and stable throughout the run. The script requests the current font once and reads no layer, outline, metric, master or selection property.

```python title="Encoding report: bounded native test recorded below"
import fontlab

SAMPLE_LIMIT = 5
LABEL_LIMIT = 80

font = fontlab.CurrentFont()
if font is None:
    print("No current font. Open a font and run again.")
else:
    glyph_count = len(font)
    unencoded = []
    assignments = {}
    for glyph_index in range(glyph_count):
        glyph = font[glyph_index]
        if glyph is None:
            raise RuntimeError(f"No glyph at index {glyph_index}; report incomplete")
        label = f"[{glyph_index}] {glyph.name!r}"
        if len(label) > LABEL_LIMIT:
            label = label[:LABEL_LIMIT - 3] + "..."
        codepoints = set(glyph.unicodes)
        if not codepoints:
            unencoded.append(label)
        for codepoint in codepoints:
            if codepoint not in assignments:
                assignments[codepoint] = []
            assignments[codepoint].append(label)

    shared = []
    for codepoint, glyph_labels in assignments.items():
        if len(glyph_labels) > 1:
            shared.append((codepoint, glyph_labels))

    lines = [
        f"Stored glyphs inspected: {glyph_count}",
        f"Unencoded glyphs: {len(unencoded)}",
        f"Distinct assigned codepoints: {len(assignments)}",
        f"Codepoints assigned to several glyphs: {len(shared)}",
        "Unencoded sample (at most 5; labels shortened to 80 characters):",
    ]
    for label in unencoded[:SAMPLE_LIMIT]:
        lines.append(f"  {label}")
    lines.append("Shared-assignment sample (at most 5 codepoints, 5 glyphs each):")
    for codepoint, glyph_labels in sorted(shared)[:SAMPLE_LIMIT]:
        names = ", ".join(glyph_labels[:SAMPLE_LIMIT])
        lines.append(f"  U+{codepoint:04X}: {len(glyph_labels)} glyphs; {names}")
    lines.append("Read-only encoding report complete.")
    print("\n".join(lines))
```

The script completes the scan **and formats every report line before printing**. A missing glyph at an in-range index raises an error; a failed native read or formatting operation also stops the script. None of those failures prints partial totals or the completion sentence. Keep the exception visible and investigate it; substituting an empty assignment list would falsely count a failed read as an unencoded glyph. A native crash is outside Python's exception handling. A failure while Output itself is receiving the final print can still interrupt delivery: one print is not a transaction with the output panel.

With no current font, only `No current font. Open a font and run again.` is expected. An existing empty font instead produces four zero totals, empty sample sections and completion. Neither case means the same thing as a failed scan.

The report has at most 17 lines: four totals, two sample headings, up to five rows in each section and one completion sentence. Each shared row lists at most five glyph labels, while its count includes every owner. Unencoded samples and owner labels follow glyph-index order; shared codepoints appear in numeric order. Supplementary codepoints retain all hexadecimal digits.

### Read the fixture result and its limits

On 13 November 2026, the exact project ran through `run_python` in FontLab 9.0.9809, build 9809, with embedded Python 3.11.6. With no font open, it printed only `No current font. Open a font and run again.` On a fresh owned copy of the GetGo CC0 GG Vize VFJ, opened as the sole font, it printed:

```text
Stored glyphs inspected: 101
Unencoded glyphs: 1
Distinct assigned codepoints: 100
Codepoints assigned to several glyphs: 0
Unencoded sample (at most 5; labels shortened to 80 characters):
  [0] '.notdef'
Shared-assignment sample (at most 5 codepoints, 5 glyphs each):
Read-only encoding report complete.
```

An independent native metadata list, obtained **after the report**, contained all 101 glyphs. Reconstructing the report from that list matched the complete output above. Obtaining this comparison afterward avoided pre-reading glyphs through that tool before the project ran.

Immediately before and after the report, the measured package identity and path matched the owned copy, the Font window's dirty flag was `False`, and the measured current history-state value was `0`. These probes read workspace, package and window state without glyph or layer getters. Source and copy hashes stayed unchanged. Only the identified owned copy was closed, without saving; the final open-font list was empty. These observations do not establish every hidden cache or native-state invariant.

That first project run accepts the no-font branch and **one 101-glyph, single-master fixture** on the recorded runtime.

A second bounded run used the unchanged script in the same FontLab/Python versions on a separately created, owned disposable font. Its five stored records were `.notdef` with no assignment, `edgeA` and `edgeB` each assigned U+0041, `edgeZero` assigned U+0000, and `edgeUnencoded` with no assignment. The report returned **5 stored glyphs, 2 unencoded glyphs, 2 distinct codepoints and 1 shared codepoint**. Its shared row named `[1] 'edgeA'` and `[2] 'edgeB'` as the two owners of U+0041. U+0000 was retained and correctly counted as an assignment.

The independent full inventory was identical before and after this second report, and its reconstructed output matched the script's complete stdout. Before and after the report, the package identity was stable, the unsaved path was empty, the measured dirty flag was `False`, and the current history-state value was `0`. These baselines were measured **after fixture creation**; they do not describe the effects of creating glyphs. The inventory had also been read before this report, so this is not a first-access test. Only the owned fixture was closed, without saving, and the final font list was empty. No source or saved font file existed for this fixture, so source/copy file hashes do not apply.

These two fixture runs do not establish hidden-state preservation. Repeated assignments within one glyph, long labels, supplementary-plane formatting, missing in-range glyphs, an empty stored-glyph collection and concurrent document changes remain offline-only cases. No Scripting panel UI, source save/reopen, selection preservation or other runtime was tested in these project runs.

For another font, the totals and labels will differ. To investigate a sample, use the name or index lookup taught earlier in this chapter. Retrieve the full name when the label ends in dots. Do not rename, re-encode or delete a glyph merely because it appears in this report.

This scan is not an atomic snapshot. Its time and memory grow with the glyph collection and assignment lists; only the displayed detail is bounded. It does not validate all Unicode values, exported mappings, feature behavior or font correctness. An unchanged file hash alone would not establish native state preservation. The bounded checks above compared full metadata and measured document state on their two owned fixtures. Scripting panel UI behavior, multiple-font changes during execution and broader runtime compatibility remain unverified.

The report currently writes only to Python output. Saving report files is a separate step with its own path and publication checks; [Chapter 21](21-make-the-report-reproducible.md) explains those distinctions.

## Selection changes the question

These examples inspect stored glyph data. They do not read the selection. Before adapting a report, choose its scope explicitly:

| Scope | Important distinction |
| --- | --- |
| All stored glyphs | The collection read by the index loop. |
| Current glyph or cell | The immediate editing context; it need not belong to the selected set. |
| Selected glyphs | Glyph-level membership may combine several displayed cells for one glyph. |
| Displayed cells | The view's arrangement, including its encoding and filter choices. |

A current cell can be deselected. A multi-encoded glyph can appear in several character cells without becoming several glyph records. A selection reader therefore needs a clear contract for context, identity and order; a list of selected glyph names is not automatically an ordered list of selected cells. [FontLab manual: Selecting glyphs](https://help.fontlab.com/fontlab/9/articles/selecting-glyphs/index.html), [Glyph identity](https://help.fontlab.com/fontlab/9/articles/glyph-identity/index.html).

Changing selection changes editor state even when it leaves outlines untouched. This chapter supplies no selection-changing procedure. A future selection example needs its own checks for the active window, empty and filtered views, repeated cells, and preservation of the user's selection.

## A found glyph still has a layer question

Finding a glyph by name or Unicode does not choose which of its drawings you intend to inspect. A glyph can have master layers and auxiliary layers such as masks, and layer sets can differ between glyphs. Visibility and participation in interpolation are separate properties. [FontLab manual: Working with glyph layers](https://help.fontlab.com/fontlab/9/articles/layers-and-masters/index.html).

The `fgGlyph` reference exposes `layer`, `layerName`, `layers` and `activeLayer` separately. Their names do not make them interchangeable. In the inspected implementation, reading some layer attributes **can initialize internal data**. Even the path that avoids creating a missing named layer can still request that initialization. A property read is therefore not, by itself, proof that all native state stays unchanged. [FontGate reference: fgGlyph layers](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgGlyph.html#fontgate.fgGlyph.layers).

The layer collection is not established here as a Python dictionary keyed by layer name, and the wrapper's working-layer name is not established as the currently highlighted panel row. Keep layer enumeration, geometry inspection and layer switching for examples whose exact interface and native effects have been verified.

For this chapter, a useful result is narrower: you can state whether you found a name, a position or an actual Unicode assignment, and you can explain which glyph collection the report inspected.
