---
this_file: src_docs/md/07-choose-the-drawing.md
---

# 7. Choose the drawing before counting its points

Finding a glyph does not tell you which drawing to inspect. A Light layer, a Bold layer and a tracing mask can belong to the same glyph. A point count needs a drawing scope as well as a glyph name.

This chapter uses **fictional Python data** to practise that choice. It does not read a FontLab document. The API distinctions below were checked against current documentation and binding source. **A complete native geometry-inspection recipe remains unverified.** A bounded existing-layer probe is recorded below with its limits; it does not validate this fictional example against native geometry. Semantic-map integration remains pending.

## Choose one layer

A **layer** holds one state of a glyph's drawing. A font master coordinates corresponding glyph layers; an auxiliary layer can hold reference material for just one glyph. Different glyphs can have different layer sets. A request for a layer named Light must therefore allow for that layer being absent.

Visibility does not determine participation in interpolation. A hidden Bold overlay can still supply a design used to calculate intermediate weights. A visible mask can remain reference material without supplying such a design. [FontLab manual: Working with glyph layers](https://help.fontlab.com/fontlab/9/articles/layers-and-masters/index.html).

Choose the layer by the purpose of your report: for example, “count the stored points in A's Light drawing.” Keep a missing layer distinct from an existing layer that contains no shapes. Neither case establishes what the entire glyph will render or export.

## Follow the containers

The manual describes the drawing hierarchy as glyph, layer, element, contour, then nodes and handles. An **element** holds drawing content and its placement; some elements hold images or other content instead of ordinary contours. A **contour**, or path, is a sequence of connected segments. A closed contour returns to its start; an open contour has separate endpoints. [FontLab manual: The element model](https://help.fontlab.com/fontlab/9/articles/the-element-model/index.html), [Contours, nodes and handles](https://help.fontlab.com/fontlab/9/articles/contours-nodes-and-handles/index.html).

The FontGate interface uses the following names along one inspection path. This table describes source-verified attributes; it is not an instruction to run them on an open document.

| Object | Attribute | What the inspected binding exposes |
| --- | --- | --- |
| `fgGlyph` | `layers` | A collection of FontGate layers; obtaining it can prepare native data. |
| `fgLayer` | `shapes` | The shapes stored in that layer. |
| `fgShape` | `contours` | The contours stored in that shape. |
| `fgContour` | `nodes` | Stored point records, including off-curve controls. |
| `fgNode` | `x`, `y`, `kind` | Stored coordinates and a point-kind label. |

Use the exact object type when reading a reference. In this binding, `len(layer)` delegates to its shape collection; it does not count contours or layers. Naming the collection explicitly makes a report easier to understand. [FontGate references: fgLayer](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgLayer.html), [fgShape](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgShape.html), [fgContour](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgContour.html).

An element occurrence can retain a transformation separately from its contour points. Raw stored coordinates are therefore not automatically the final positions you see on screen or get in an exported font. Counting direct contours also does not resolve component or image content. This chapter does not flatten drawings or reconstruct exported outlines. [FontLab manual: Element transformations](https://help.fontlab.com/fontlab/9/articles/element-transformations/index.html).

## Distinguish nodes from stored point records

In the drawing instructions, a **node** is an on-curve point: it lies on the path. A **handle** is an off-curve control point that shapes a curve. A curve normally does not pass through its handles. TrueType curves can also imply on-curve positions that are not stored as separate points. [FontLab manual: Contours, nodes and handles](https://help.fontlab.com/fontlab/9/articles/contours-nodes-and-handles/index.html).

FontGate's `fgNode` name covers a broader set of records. Its `kind` labels include `Move`, `On`, `Off` and `Curve`. In the inspected contour conversion, Move and On are treated as on-curve records, while Off and Curve are treated as off-curve controls. In particular, the label Curve does not mean an on-curve endpoint. [FontGate reference: fgNode](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgNode.html).

Keep these counts separate:

- **Contours** count paths, with an optional separate count of open paths.
- **Stored points** count records, including off-curve controls.
- **On-curve and off-curve records** divide those records by their roles.

None of these is automatically a count of visible nodes, segments, implied points or exported points. A useful report states which representation it counted.

## Practise with fictional records

The following dictionary is an original teaching example. Its layer names are dictionary keys because we chose that Python structure. **It is not FontLab's layer interface or an export format.** The small record set lets us practise counting; it does not validate whether every possible point sequence makes a usable outline.

Each shape contains a list of contours. Each contour has an `open` Boolean and a list of point tuples. A tuple such as `("On", 0, 0)` contains a kind label, an x coordinate and a y coordinate. The loop `for kind, x, y in ...` unpacks those three values into names. This report uses only the kind; it leaves the coordinates unchanged. Python permits nested lists, dictionaries and tuples in this way. [Python tutorial: Data structures](https://docs.python.org/3.11/tutorial/datastructures.html).

Run this as ordinary Python 3.11 code. If you use FontLab's Scripting panel, first preserve existing work and establish an empty editor using [Chapter 4](04-work-in-the-scripting-panel.md). Enter only the example. It imports no FontLab module and uses only the records written here.

```python
sample_layers = {
    "Regular": [
        {"contours": [
            {"open": False, "points": [
                ("On", 0, 0), ("On", 100, 0),
                ("Curve", 100, 60), ("Curve", 40, 100), ("On", 0, 100),
            ]},
            {"open": True, "points": [("Move", 20, 20), ("On", 80, 20)]},
        ]},
    ],
    "Sketch": [],
}


def count_records(shapes):
    counts = {"contours": 0, "open": 0, "on": 0, "off": 0}
    for shape in shapes:
        for contour in shape["contours"]:
            counts["contours"] += 1
            if contour["open"]:
                counts["open"] += 1
            for kind, x, y in contour["points"]:
                if kind in ("Move", "On"):
                    counts["on"] += 1
                elif kind in ("Off", "Curve"):
                    counts["off"] += 1
                else:
                    raise ValueError(f"Unknown sample point kind: {kind}")
    return counts


def report_layer(layers, requested_name):
    if requested_name not in layers:
        print(f"No sample layer named {requested_name}.")
        return
    shapes = layers[requested_name]
    counts = count_records(shapes)
    print(f"Layer: {requested_name}")
    print(f"Shapes: {len(shapes)}")
    print(f"Contours: {counts['contours']} (open: {counts['open']})")
    print(f"Stored points: {counts['on'] + counts['off']}")
    print(f"On-curve: {counts['on']}; off-curve: {counts['off']}")


report_layer(sample_layers, "Regular")
```
```text
Layer: Regular
Shapes: 1
Contours: 2 (open: 1)
Stored points: 7
On-curve: 5; off-curve: 2
```

The output covers Regular only. Change the final argument to `"Sketch"` to inspect the existing empty layer; all counts should be zero. Change it to `"Missing"` to get `No sample layer named Missing.` The membership check distinguishes those outcomes before reading any shape records.

The first function makes a new count dictionary. `+= 1` increases a count by one; the input records are never assigned new values. The second function prints only after counting succeeds. An unknown point kind raises `ValueError` instead of being silently discarded from a supposedly complete total. Missing record fields also remain visible as errors.

These are results from fictional data, not native FontLab output. In particular, a shape with no direct contours still counts as a shape. A zero contour count alone cannot establish that a real glyph has no visible content.

## A getter can prepare native data

A **getter** is the part of an API that reads an attribute. Some getters also prepare data before returning it. The inspected `glyph.layers` path calls a validation routine that can ask FontLab to prepare its FontGate representation. A routine supplied by the application can fill that representation and attach it to the glyph. If that routine supplies no data, a fallback path can create FontGate data.

This is why replacing the fictional records above with live objects is a separate task. The absence of an assignment in Python does not prove that all native state remains unchanged. The source establishes a preparation path; it does not establish whether a particular document is marked modified, gains a history entry or changes when saved. [FontGate reference: fgGlyph layers](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgGlyph.html#fontgate.fgGlyph.layers).

The related attributes `layer`, `layerName` and `activeLayer` have different implementations. The wrapper's working-layer name is not established here as the highlighted row in the Layers & Masters panel. Even the `layer` path that avoids creating a missing named layer can still request data preparation. Do not choose an attribute solely because its name sounds like the layer you want.

## What the existing-layer probe established

On 13 November 2026, a separate research probe ran in FontLab 9.0.9809, build 9809, with embedded Python 3.11.6. It used an owned copy of the GetGo CC0 GG Vize VFJ as the sole open font. Glyph A already contained one Regular layer. The probe read the `fgLayers` collection and layer names; `countContours()` and `countShapes()` reported two contours and one shape. The Python layer probe did not enumerate individual point records or run the fictional counting example against the font.

Before and after those reads, the full native `get_glyph` serialized response was identical, including `lastModified`. The `get_glyph_metrics` response was also identical: advance width 606, left sidebearing 12, right sidebearing 18, active layer Regular. The current package path matched the owned copy and the Font window's `windowModified` flag remained `False`. The source and copy file hashes stayed unchanged. Only the owned copy was closed, without saving; the final open-font list was empty.

A repeat layer-count/name probe recorded `currentHistoryState()` as `0` before and after, with the dirty flag `False` both times. **No history-state baseline was captured for the first layer access:** the earlier probe printed the method representation instead of calling it. The repeat result cannot establish first-access history invariance.

The pre-probe native snapshot itself traversed glyph data. Hidden data preparation, caches or effects outside the measured serialization and dirty flag therefore remain possible. No missing-layer case was tested. Nor were `bodyLayer`, `bodyLayerStrict`, `activeLayer` or the named `layer()` getter invoked. This is bounded research on one existing layer and runtime, not Scripting panel UI validation or a general guarantee that getters are passive. No native font was saved; unchanged disk hashes do not establish save/reopen behavior. The source-backed preparation warning above still applies.

## Keep a report separate from its native objects

A **wrapper** is a Python object that gives access to underlying native data. Keeping a wrapper in a Python variable does not by itself make a separate copy of the drawing. In the inspected binding, contour and point wrappers can refer to existing native records. A new Python list returned by `getNodes()` still contains wrappers; the new list is not a detached coordinate snapshot.

For a later native report, extract the numbers and strings you need while the document is stable. Keep those ordinary values as the report. Avoid reusing native wrappers after closing the document or replacing its glyphs, layers or contours until that lifetime behavior has been verified. This is a boundary for the future recipe, not a claim that collecting values is an atomic snapshot.

A native version needs owned fixtures that cover absent and empty layers, multiple shapes, open and closed paths, different curve representations, transformations and non-contour content. It also needs checks of the document and editor state before and after getters prepare data. The Python exercise verifies counting logic; those native checks remain separate.
