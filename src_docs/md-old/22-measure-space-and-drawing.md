---
this_file: src_docs/md/22-measure-space-and-drawing.md
---

# Measure the space and the drawing separately

A glyph can advance 600 units while its drawing is only 500 units wide. A handle can reach above the curve it controls. Both observations are correct, but a report that calls every number “width” or “bounds” makes them hard to interpret.

This chapter distinguishes those measurements using source inspected on 13 November 2026. **The exercise uses fictional numbers in external Python 3.11; it reads no FontLab document and changes no files.** Native measurement behavior and state preservation were not tested for this chapter. The draft remains provisional pending independent review and semantic-map integration.

## Name the distance

The **advance width** determines the next glyph's origin before kerning or other positioning adjustments. The **drawing width** measures the drawing's horizontal extent. In ordinary upright measurement, the **left sidebearing**, or LSB, is the drawing's left edge relative to x = 0. The **right sidebearing**, or RSB, is the distance from its right edge to the advance boundary.

For example, an advance of 600 with drawing edges at x = 40 and x = 540 gives:

| Measurement | Calculation | Font units |
| --- | --- | --- |
| Drawing width | 540 − 40 | 500 |
| LSB | 40 − 0 | 40 |
| RSB | 600 − 540 | 60 |

The three distances add to the advance: 40 + 500 + 60 = 600. An edge can extend outside that interval, producing a negative sidebearing. A blank space can have a positive advance without a drawing. Equal numerical bearings do not necessarily look equally spaced. [FontLab manual: Designing the whitespace](https://help.fontlab.com/fontlab/9/articles/designing-the-whitespace/index.html).

This is an ordinary horizontal geometry calculation. Italic metrics, a measurement line and pair positioning need their own context; the formula does not identify which mode a native panel used. [Chapter 13](13-report-kerning-proposals.md) separates default spacing from pair adjustments.

Keep units with the numbers. Font units describe the design's coordinate system, not screen pixels. A nominal cap height or x-height is a design reference, not a promise that every relevant outline ends at that height. The top of an accent and the cap-height reference answer different questions. [FontLab manual: The em and coordinate system](https://help.fontlab.com/fontlab/9/articles/the-em-and-the-coordinate-system/index.html); [font and glyph metrics](https://help.fontlab.com/fontlab/9/articles/font-metrics-and-glyph-metrics/index.html).

## Ask what the box encloses

A bounding box is commonly written `(xMin, yMin, xMax, yMax)`: the smallest and largest coordinates of the content being measured. Its meaning depends on which content supplied those coordinates.

**Stored-point bounds** include the recorded points, including off-curve controls. **Curve bounds** follow the segments themselves and account for extrema between their endpoints. An **extremum** is a furthest position in a direction, such as the highest point of a curve. A handle can lie beyond that position.

For a specific quadratic curve from `(0, 0)` through control point `(50, 100)` to `(100, 0)`, the handle reaches y = 100, but the curve reaches only y = 50. Its vertical coordinate is `y = 200 × t × (1 − t)` for a parameter `t` from 0 to 1. At the midpoint, `t = 0.5`, this gives 50; the expression cannot exceed 50 on that interval. Taking the largest stored y coordinate would report the control-point extent instead.

fontTools provides separate `ControlBoundsPen` and `BoundsPen` classes for these jobs. The latter calculates curve extrema, including ones without a stored point at that position. This distinction follows the pen protocols introduced in [Chapter 12](12-transform-a-recording.md); it does not establish that fontTools is installed inside FontLab. [fontTools bounds pens](https://fonttools.readthedocs.io/en/latest/pens/boundsPen.html).

Coordinates also have a scope. A shape may retain a transform separately from its points, and a component refers to another drawing. Bounds of raw points in one contour do not automatically describe every transformed shape, component, stroke or image in the glyph. [Chapter 7](07-choose-the-drawing.md) explains those containers.

## Keep the native object and layer explicit

The inspected interfaces expose several measurements with different contracts:

| Interface | Source-backed distinction |
| --- | --- |
| `flLayer.advanceWidth` | A layer advance; native source can fall back to the glyph's advance when the layer has no explicit value |
| `flLayer.boundingBox` | A rectangle property assembled from transformed shape boxes; not a general promise of tight curve extrema |
| `flLayer.inkBox(...)` | A separate method with native geometry, cache and preference behavior |
| `fgGlyph.width` and its margins | FontGate glyph-level access; not an explicit named `flLayer` report |
| `fgLayer.boundingBox(...)` | A method requiring a matrix argument in the inspected binding, unlike the `flLayer` property |

The reference lists the captured `flLayer` members. Similar names do not make native `flLayer` and FontGate `fgLayer` interchangeable. [FontLab flLayer reference](https://code.fontlab.com/fontlab-python-docs/reference/fontlab/flLayer.html); [FontGate fgLayer reference](https://fontlabcom.github.io/fontlab-python-docs/reference/fontgate/fgLayer.html).

The inspected native implementations make the bounds distinction concrete. In `flcontour.cpp`, the no-argument contour bounding-box path encloses stored nodes; the transform-taking overload calculates segment bounds. An **overload** is a version of an operation selected by its arguments. `fllayer.cpp` combines transformed shape rectangles, while the shape path can account for thickness or non-contour content. Transforming an enclosing rectangle can also leave more space than the transformed drawing needs. A single field named `boundingBox` therefore cannot establish all of these meanings.

The Python helper sources reinforce the need to read the implementation. App's `glyph_metrics.metrics` decomposes affine components and uses `BoundsPen`, then computes geometric bearings. Its node-editor helper instead finds minimum and maximum stored-point coordinates. The spacing studio's `edges` helper uses the native layer box, despite describing the edges as ink. Treat those as distinct measurements. [Geometric metrics helper](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/fontui/glyph_metrics.py); [outline collection](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/fontui/model.py); [node-editor bounds](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/fontui/tglyph_model.py); [spacing studio](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/studios/spacing_studio/session.py).

Record the exact font, glyph and layer alongside the measurement. “Regular” is a layer name in a particular font, not a globally unique identity. Missing glyph, missing layer and existing layer without a drawing must remain distinct outcomes.

## Calculate a fictional report

This exercise receives already supplied outline bounds. **It does not calculate bounds from nodes or validate native geometry.** The tuples are original teaching data, not a FontLab serialization format.

Each record contains a glyph label, an advance and either four bounds coordinates or `None`. For this exercise, advances must be finite and nonnegative; coordinates must be finite and ordered. A finite number is neither infinity nor “not a number”, abbreviated NaN. `math.isfinite` performs that check. [Python math.isfinite](https://docs.python.org/3.11/library/math.html#math.isfinite).

The function returns drawing width, LSB and RSB. When bounds are absent, it returns three `None` values; the caller still retains the advance. It rejects reversed coordinates instead of silently rearranging them. That makes a malformed input visible.

```python
from math import isfinite


def measure(advance: float, bounds: tuple | None) -> tuple:
    if not isfinite(advance) or advance < 0:
        raise ValueError("Expected a finite, nonnegative advance")
    if bounds is None:
        return None, None, None
    left, bottom, right, top = bounds
    for value in bounds:
        if not isfinite(value):
            raise ValueError("Expected finite bounds")
    if right < left or top < bottom:
        raise ValueError("Expected ordered bounds")
    result = right - left, left, advance - right
    for value in result:
        if not isfinite(value):
            raise ValueError("Measurement exceeds finite arithmetic")
    return result


records = [
    ("A", 600, (40, 0, 540, 700)),
    ("space", 300, None),
    ("mark", 0, (-20, 400, 30, 500)),
]
print("Fictional Orchard / Regular / font units")
for name, advance, bounds in records:
    drawing, left, right = measure(advance, bounds)
    print(f"{name}: advance={advance}; drawing={drawing}; LSB={left}; RSB={right}")
```

The output is:

```text
Fictional Orchard / Regular / font units
A: advance=600; drawing=500; LSB=40; RSB=60
space: advance=300; drawing=None; LSB=None; RSB=None
mark: advance=0; drawing=50; LSB=-20; RSB=-30
```

The loop unpacks each record, and the assignment unpacks the function's three returned values. In the final line, the `f` prefix tells Python to insert the values named inside braces. The report labels their meaning and keeps one font/layer/unit context above the rows.

The mark has a drawing despite its zero advance. The space has an advance despite having no supplied bounds. A zero-sized box, such as `(10, 20, 10, 20)`, is a third case: it supplies a position with zero extent. The helper does not relabel that as missing data or claim that it represents a valid rendered glyph.

Fractional values remain fractional; there is no rounding step. The checks raise `ValueError` for non-finite or negative advances, non-finite or reversed bounds, or calculated differences that overflow to infinity. A tuple with the wrong number of coordinates also raises `ValueError` during unpacking. Other input types are outside this small function's declared numeric contract. None of these errors changes the records or a font.

## A getter can prepare data

A **getter** reads a property, but its implementation can do work before returning it. The inspected native `flGlyph.findLayer` path calls import completion. That preparation can attach layer data or fill missing information. The layer bounding-box path can populate a cached rectangle. The ink-box path tracks transform and preference choices and can update an existing centre property.

These are source findings, not proof that every call changes a document. They also prevent claiming universal passivity from Python code that contains no assignment. Avoid resetting a cache or calling an update merely to make an inspection report appear correct: those would add operations requiring their own acceptance checks.

The current GetGo spacing example records a further limit: after its deliberate node edits, it reads back nodes because cached boxes had remained stale. It uses a straight-line, component-free glyph for that check. Taking node minima and maxima would not become an exact-curve solution for arbitrary outlines. The example is mutating and was not run here. [Spacing example and readback](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/lessons/src/fontlab_python_lessons/getgo/spacing.py).

## Qualify a native report separately

[Chapter 7's bounded verification](07-choose-the-drawing.md#what-the-existing-layer-probe-established) concerns an existing layer on one owned Vize fixture. It did not qualify the named-layer and bounds paths discussed here. Its geometry snapshot preceded the layer probe, and first-access history was not captured correctly. It cannot establish that a fresh measurement path leaves native state untouched.

Before publishing a native measurement recipe, test the exact path on a provenance-recorded disposable copy. Capture called history state and dirty state before geometry access, then compare after the first read and a repeat read. Keep a geometry-heavy baseline snapshot separate from that first-access question. Check missing and empty cases, transformed shapes, curves with distant handles and multiple masters independently.

Retain ordinary numbers and text for the report while the document remains valid. Do not keep native wrappers for use after closing or replacing their source. An unchanged printed result, unchanged dirty flag and unchanged disk file each establish a different observation. They do not jointly prove hidden caches absent, native Undo/Redo correct, or saved and exported data equivalent.
