---
this_file: src_docs/md/12-transform-a-recording.md
---

# Transform a drawing before changing a font

A drawing can travel as a sequence of calls: start here, draw a line there, end the contour. A script can record those calls or change their coordinates before sending them onward. What happens next depends on the object receiving them.

This chapter introduces pen protocols and coordinate transformations. Its exercise uses fictional Python data and imports no library. **Native drawing, Undo/Redo and save/reopen behavior remain unverified for this chapter.** The draft remains provisional pending independent review and semantic-map integration.

## A pen receives drawing calls

A **protocol** is a set of expected calls. In the fontTools segment pen protocol, a drawing sends calls to a **pen**, an object that receives them. That object might record the calls, measure the outline or write contours into a destination. A pen is not necessarily a tool that draws on the screen. [fontTools: Segment pen protocol](https://fonttools.readthedocs.io/en/latest/pens/basePen.html).

For a simple contour, these calls have distinct jobs:

| Call | Meaning in the segment protocol |
| --- | --- |
| `moveTo((x, y))` | Start a contour at this position. |
| `lineTo((x, y))` | Add a straight segment to this position. |
| `curveTo(...)` | Describe cubic curve controls and an endpoint. |
| `closePath()` | Close the contour. |
| `endPath()` | End an open contour. |

Closing a contour is different from closing a pen session or saving a document. The protocol describes drawing operations; it does not define a universal commit or Undo mechanism.

A **point pen** receives individual point records through `beginPath()`, `addPoint(...)` and `endPath()`. These calls can carry segment type, smoothness and point names. This is useful when the point records matter, as they did in [Chapter 7](07-choose-the-drawing.md). Segment and point pens use different calls; adapters such as `PointToSegmentPen` and `SegmentToPointPen` translate between the two protocols. Translation does not guarantee that every destination stores all the supplied metadata. [fontTools: Point pens](https://fonttools.readthedocs.io/en/latest/pens/pointPen.html).

## Record first, choose the destination explicitly

fontTools' `RecordingPen` collects segment calls in its `value` list. Each ordinary entry holds an operation name and a tuple of arguments. Calling `replay(other_pen)` sends those calls to another pen. A **filter pen** receives calls, changes or examines them, then forwards them. `TransformPen` is a filter that changes coordinates before forwarding them. [fontTools: Recording pens](https://fonttools.readthedocs.io/en/latest/pens/recordingPen.html) and [Transform pens](https://fonttools.readthedocs.io/en/latest/pens/transformPen.html).

The destination matters. Replaying into another recording pen produces another recording. Replaying into a native writer can change native data. A recording alone is neither a saved font nor a promise that replay can be undone.

A **component** refers to a base glyph and carries a placement transform. A recording can keep that reference without containing the base glyph's outline. Resolving the reference into contours is called **decomposition**; it needs access to the base glyph. Moving a component placement and transforming the base drawing are different operations. If both are transformed without a suitable policy, the result can receive the transformation twice.

## Read the six transformation values

An **affine transformation** can translate, scale, rotate or shear coordinates. Translation moves positions by an offset; scaling multiplies coordinates; shearing slants one coordinate direction relative to the other. fontTools and the inspected Pens implementation use six values in this order:

`(xx, xy, yx, yy, dx, dy)`

They map a point `(x, y)` to:

- `new_x = xx * x + yx * y + dx`
- `new_y = xy * x + yy * y + dy`

The **identity** transform, `(1, 0, 0, 1, 0, 0)`, leaves coordinates unchanged. `(2, 0, 0, 3, 10, -5)` doubles x, triples y, then adds 10 to x and subtracts 5 from y. It maps `(4, 7)` to `(18, 16)`. [fontTools: Transform](https://fonttools.readthedocs.io/en/latest/misc/transform.html).

A displacement, or **vector**, describes a difference between positions. A vector transformation omits the translation offset. This matters when choosing a spacing policy: shifting a drawing by 10 units does not by itself specify a new advance width. The inspected Fontport detached-transform function uses vectors for advance values, but that is a policy of that function, not a rule for every font-editing command.

Order also matters. Starting at `(4, 7)`, doubling both coordinates and then adding 10 to x gives `(18, 14)`. Adding 10 to x first and then doubling gives `(28, 14)`. When reading a transformation chain, establish which operation happens first. fontTools transforms return new transform values; do not assume that a similarly named native or compatibility object has the same behavior.

## Transform a fictional recording

The following list represents an open contour with two straight segments. It is written directly as Python data; no font or pen library creates it. The helper handles only `moveTo`, `lineTo` and `endPath`. It is a small exercise in the recording format, not a complete pen implementation or a validator for arbitrary outlines.

In `("moveTo", ((4, 7),))`, the outer tuple holds an operation and its arguments. `((4, 7),)` is a one-item tuple containing the point; the trailing comma makes it a tuple. `()` contains no arguments. The assignments to `xx, xy, ...` and `x, y` unpack sequences into individual names, as in the point-record loop from [Chapter 7](07-choose-the-drawing.md). [Python tutorial: Tuples and sequences](https://docs.python.org/3.11/tutorial/datastructures.html#tuples-and-sequences).

```python
def transform_recording(recording: list, matrix: tuple) -> list:
    xx, xy, yx, yy, dx, dy = matrix
    result = []
    for operation, arguments in recording:
        if operation in ("moveTo", "lineTo"):
            x, y = arguments[0]
            point = (xx * x + yx * y + dx, xy * x + yy * y + dy)
            result.append((operation, (point,)))
        elif operation == "endPath":
            result.append((operation, ()))
        else:
            raise ValueError("This exercise supports moveTo, lineTo and endPath only.")
    return result


recording = [
    ("moveTo", ((4, 7),)),
    ("lineTo", ((14, 7),)),
    ("lineTo", ((14, 17),)),
    ("endPath", ()),
]
matrix = (2, 0, 0, 3, 10, -5)
transformed = transform_recording(recording, matrix)
for operation, arguments in transformed:
    print(operation, arguments)
```

Expected output:

```text
moveTo ((18, 16),)
lineTo ((38, 16),)
lineTo ((38, 46),)
endPath ()
```

The helper builds a new list and returns it before the final loop prints anything. The original recording remains unchanged. The final `endPath` still describes an open contour; transforming positions has not closed it.

Try the identity matrix, then an empty recording. Identity returns equal coordinates in a new list; empty input returns an empty list. A `curveTo`, `addComponent` or `closePath` entry raises an error because this exercise does not implement that operation. Production code should use the appropriate library adapter rather than extend this helper into a general geometry system.

## Distinguish the FontLab adapters

The inspected **Pens** package implements selected fontTools-compatible operations under `fontlab_pens`. Its transform and recording classes work with Python data; its native adapters have additional target and lifecycle rules. Compatibility with selected calls does not mean complete fontTools coverage. [Pens source](https://github.com/fontlabcom/fontlab-python-pens).

The following table describes the inspected source, not tested behavior in your installed FontLab:

| Adapter | Destination | When the inspected code writes |
| --- | --- | --- |
| Pens `fontlab_pens.fontlab.FlPointPen` | An explicit `flLayer` or `flShape` element. | Stages contours, constructing native objects along the way; attaches them on `close()` or successful context exit. A native failure during attachment or notification can leave partial geometry. |
| Pens `fontlab_pens.fontgate.FontGatePointPen` | An explicit `fgLayer` or `fgShape` element. | Appends each completed contour at `endPath()`. Closing the session does not roll back contours written before an exception. |
| Fontport `fontlab_fontport.pens.FontGatePointPen` | An `fgGlyph`, resolved through its working layer and first element. | Writes completed contours through its adapter and stores components at glyph level. This is a different class from the layer/element pen above. |
| Glyport's `LayerPen`, returned by layer `getPen()` or `getPointPen()` | The layer's draft or live collection route. | Appends completed contours and components. Finishing the session balances its live history scope; it does not undo earlier appends. |
| Native `fontgate.fgPen` | A glyph's work shape. | Its inspected closing path appends the contour and marks FontGate data modified. It is not Pens' `FontGatePen`. |

In a `with` statement, a **context manager** performs setup and cleanup around a block of code. What cleanup does is defined by that object. The presence of `with`, `close` or a history group does not establish an all-or-nothing change. [Python reference: The with statement](https://docs.python.org/3.11/reference/compound_stmts.html#the-with-statement).

Metadata support differs too. The inspected Pens and Fontport native writers refuse unsupported identifiers; Glyport's LayerPen accepts identifier arguments without storing them. The point protocol's ability to carry a value does not prove that a particular adapter preserves it. [Fontport source](https://github.com/fontlabcom/fontlab-fontport); [Glyport source](https://github.com/fontlabcom/fontlab-glyport).

## Keep coordinate space and persistence separate

An element's stored points can have a separate transform, as explained in [Chapter 7](07-choose-the-drawing.md). The inspected Pens readers map coordinates through the relevant element or layer matrices. Their writers can use an inverse matrix to map supplied coordinates into the destination's stored space. A matrix that collapses a dimension can have no inverse; accepting a drawing operation requires more than recognizing a six-item tuple.

Fontport's inspected `transform_glyph` operates on a detached UFO glyph copy. Its whole-font counterpart also adjusts component matrices to account for transformed base glyphs. Applying detached results back to FontLab is a separate write route with its own limitations. Native layer access can also prepare internal FontGate data, so obtaining source geometry has not been established as passive merely because the Python code contains no assignment.

The exercise above verifies a much smaller result: predicted coordinates and operation order in ordinary Python data. Before offering a native recipe, verify the exact installed adapter, selected layer and coordinate space; intended geometry and metadata; failure behavior; history and unrelated-data preservation; and the saved artifact after reopening it. Those are separate acceptance checks. A correct recording or successful replay alone establishes none of them.
