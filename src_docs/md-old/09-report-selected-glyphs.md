---
this_file: src_docs/md/09-report-selected-glyphs.md
---

# Say which glyphs your report covers

A report headed “Selected glyphs: 4” leaves a question unanswered: did it count selected cells or distinct glyphs? This chapter builds a report that states both counts and shows where each glyph first appeared.

The exercise uses fictional Python data. It reads no FontLab window, glyph or layer and changes no font. **Native selection access remains unverified.** This draft is provisional pending the book's semantic map and independent review.

## Choose what to count

In the Font window, the **current cell** supplies the immediate glyph context. **Selected cells** form the selection. A cell can stay current after it is deselected, and a selected cell can be an empty position. The displayed collection also depends on the view and filter. [FontLab manual: Selecting glyphs](https://help.fontlab.com/fontlab/9/articles/selecting-glyphs/index.html).

For this exercise, the report includes each distinct glyph represented by selected cells. It counts selected cells separately, including selected cells with no glyph. An empty selection produces zero glyph rows. It never substitutes the current glyph or all the glyphs in the font.

## Keep identity separate from position

A **package ID** identifies a font package in the inspected source. A **glyph ID** identifies a glyph; pairing it with its package ID keeps glyphs from different packages separate. In our fictional records, `(700, 11)` and `(701, 11)` are different identities, even though both glyphs are named `A`.

A **cell index** identifies a position in the chart. It is not a glyph's index in the font, its glyph ID or a Unicode code point. The [earlier lookup chapter](06-find-the-glyph-you-mean.md) explains why a numeric font subscript must not be guessed from another kind of number.

Our report keeps the order in which each identity first occurs in a selected cell. It also prints that cell's index. A later occurrence of the same identity adds no second row. Two different identities in one cell contribute two rows.

## Understand the source records before using them

The inspected FontLab source defines a Font window method named `fontViewSelectionSnapshot`. Its records separate chart positions from glyph identities:

| Field | Meaning in the inspected source |
| --- | --- |
| `schema` | Record format version, currently `1` in that source. |
| `valid` | Whether a chart model is present. It does not mean that a glyph is selected. |
| `packageIds` | Package IDs recorded by the chart model. |
| `cells` | Cell records in model order, including empty cells. |
| `cellIndex` | The cell's position in that model. |
| `selected` | Whether that cell is selected. |
| `glyphs` | The cell's list of `packageId` and `glyphId` pairs. |

This source path reads stored IDs and selection flags. It does not include glyph names, Unicode assignments, drawing layers or a current-cell field. The [native scripting guide](https://fontlabcom.github.io/fontlab-python-docs/guide/native.html) provides related selection guidance; the field details above were checked against the implementation. Source existence does not establish that the method is available through Python in your installed FontLab. No call to it is prescribed here.

## Build a report from fictional records

The following example supplies its own snapshot and a separate metadata dictionary. A dictionary key such as `(700, 11)` is a Python tuple containing two integers. These tuple keys are our teaching convention, not a FontLab lookup API.

The `seen` set remembers identities already encountered. A set supports membership tests but does not preserve a reporting order, so `records` is a separate list. Each record contains the package ID, glyph ID and first selected cell index. [Python tutorial: Sets and tuples](https://docs.python.org/3.11/tutorial/datastructures.html#sets).

`selected_records` collects identities and counts. `format_rows` joins those identities to the supplied names and Unicode lists. `show_selection` builds every row before printing the totals. A missing required dictionary key raises `KeyError`; it does not silently omit a glyph from a seemingly complete report. The example assumes the supplied fields have the types shown; it is not a parser for arbitrary external data. [Python reference: KeyError](https://docs.python.org/3.11/library/exceptions.html#KeyError).

`format_rows` uses three compact expressions. The **list comprehension** `[f"U+{value:04X}" for value in info["unicodes"]]` makes one formatted string for each Unicode value and collects the strings in a new list. `" ".join(labels)` combines those strings with one space between them. The **conditional expression** `" ".join(labels) if labels else "unencoded"` uses the joined text when the list is nonempty, or the word `unencoded` when it is empty. [List comprehensions](https://docs.python.org/3.11/tutorial/datastructures.html#list-comprehensions), [str.join](https://docs.python.org/3.11/library/stdtypes.html#str.join), [conditional expressions](https://docs.python.org/3.11/reference/expressions.html#conditional-expressions).

```python
def selected_records(snapshot: dict) -> tuple[int, int, list]:
    if snapshot["schema"] != 1:
        raise ValueError("Unsupported snapshot schema")
    if snapshot["valid"] is not True:
        raise ValueError("Snapshot has no chart model")
    selected_count = 0
    empty_count = 0
    seen = set()
    records = []
    for cell in snapshot["cells"]:
        if not cell["selected"]:
            continue
        selected_count += 1
        if not cell["glyphs"]:
            empty_count += 1
        for glyph in cell["glyphs"]:
            identity = (glyph["packageId"], glyph["glyphId"])
            if identity not in seen:
                seen.add(identity)
                records.append((identity[0], identity[1], cell["cellIndex"]))
    return selected_count, empty_count, records


def format_rows(records: list, metadata: dict) -> list[str]:
    rows = []
    for package_id, glyph_id, first_cell in records:
        info = metadata[(package_id, glyph_id)]
        labels = [f"U+{value:04X}" for value in info["unicodes"]]
        assignments = " ".join(labels) if labels else "unencoded"
        rows.append(
            f"{package_id}/{glyph_id} | first cell {first_cell} | "
            f"{info['name']} | {assignments}"
        )
    return rows


def show_selection(snapshot: dict, metadata: dict) -> None:
    selected_count, empty_count, records = selected_records(snapshot)
    rows = format_rows(records, metadata)
    print(f"Selected cells: {selected_count}")
    print(f"Selected empty cells: {empty_count}")
    print(f"Distinct glyphs: {len(rows)}")
    for row in rows:
        print(row)


sample_snapshot = {
    "schema": 1,
    "valid": True,
    "packageIds": [700, 701],
    "cells": [
        {"cellIndex": 0, "selected": True,
         "glyphs": [{"packageId": 700, "glyphId": 11}]},
        {"cellIndex": 1, "selected": False,
         "glyphs": [{"packageId": 700, "glyphId": 12}]},
        {"cellIndex": 2, "selected": True,
         "glyphs": [{"packageId": 700, "glyphId": 11}]},
        {"cellIndex": 3, "selected": True, "glyphs": []},
        {"cellIndex": 4, "selected": True,
         "glyphs": [{"packageId": 700, "glyphId": 12},
                    {"packageId": 701, "glyphId": 11}]},
    ],
}
sample_metadata = {
    (700, 11): {"name": "A", "unicodes": [0x0041]},
    (700, 12): {"name": "A.alt", "unicodes": []},
    (701, 11): {"name": "A", "unicodes": [0x0041, 0x1F600]},
}
show_selection(sample_snapshot, sample_metadata)
```

Expected output under Python 3.11:

```text
Selected cells: 4
Selected empty cells: 1
Distinct glyphs: 3
700/11 | first cell 0 | A | U+0041
700/12 | first cell 4 | A.alt | unencoded
701/11 | first cell 4 | A | U+0041 U+1F600
```

Cell 1 is unselected, so it contributes nothing. The identity `(700, 12)` still appears because selected cell 4 contains it. Cells 0 and 2 contain the same identity, which appears once. Cell 3 contributes to the selected-cell and empty-cell counts but has no glyph row.

The metadata are invented. The glyph name `A` does not imply either of the supplied Unicode lists. As in the [Unicode lookup exercise](06-find-the-glyph-you-mean.md), `:04X` means at least four hexadecimal digits: it prints zero as `0000` and keeps all five digits of `1F600`.

## Try an empty selection

In a fresh copy of the example, set every `selected` value to `False`. All three counts should become zero. Restore the sample, then keep only the record for cell 3 in `cells`: the counts should be one selected cell, one empty selected cell and zero distinct glyphs.

An empty `cells` list with `valid` set to `True` also produces three zero counts. Setting `valid` to `False` raises an error instead: an absent chart model and a valid empty chart are different states. These are exercises on our dictionaries, not observations of FontLab with no font open.

Finally, remove metadata key `(701, 11)` while leaving the original selected cells intact. The example should raise `KeyError` before printing any report. Restore the key before continuing. Missing metadata is not an unencoded glyph: an unencoded glyph has an explicit empty Unicode list.

## Keep the native reader as a separate task

Selection readers can answer different questions. A scan of glyph indices with the legacy `Selected` predicate gives membership in font order, rather than chart-cell occurrence order. Text-block selection is a different scope again. A helper that substitutes `CurrentGlyph` when selection is empty changes the report's meaning; that getter can also prepare internal glyph data. [Native scripting guide](https://fontlabcom.github.io/fontlab-python-docs/guide/native.html); [drawing and data preparation](07-choose-the-drawing.md).

Before connecting this report to FontLab, verify actual Font window method access, returned Python types, no-font and wrong-window behavior, and identity across multiple saved and unsaved fonts. Verify that reading the selection preserves selection, layers and editing history. A separate, source-checked lookup must supply complete name and Unicode metadata for each package/glyph pair. Do not use a glyph ID as a numeric font index or resolve every pair in whichever font happens to be current.

The checked native source includes selection-snapshot test fixtures; they were not compiled or run for this chapter. The book's tests execute the fictional Python example and its variations. They establish its counts, order and unchanged input dictionaries, while installed native behavior remains unverified.
