---
this_file: src_docs/md/15-identify-the-location.md
---

# Identify the location before calculating a design

“Weight 500” identifies a location only when you know the coordinate system. It does not mean that a stem is 500 units wide, that a master called Medium exists, or that an interpolated font has been generated.

This chapter uses fictional source records to calculate one glyph's width along one linear axis. **Native interpolation, master creation, variable-font export and save/reopen behavior remain unverified for this chapter.** The draft remains provisional pending independent review and semantic-map integration.

## Name the axis and its coordinates

An **axis** describes a dimension of change, such as weight or width. A **location** supplies coordinates on the relevant axes. The **designspace** is the space those axes define. A master places a source design at a location; a style name is a label for people. Renaming Light to Medium does not move its location or redraw its glyphs. [FontLab manual: The Variation Model](https://help.fontlab.com/fontlab/9/articles/the-variation-model/index.html).

FontLab's axis identifiers have different roles:

| Identifier | Weight example | Role |
| --- | --- | --- |
| Name | Weight | Human-readable label |
| Code | `wt` | FontLab location strings and expressions |
| Tag | `wght` | Axis identifier in the exported font |

Keep the coordinate space explicit too:

- **Design coordinates** locate the source designs in FontLab's working model.
- **User coordinates** provide the scale exposed to applications.
- **Normalized coordinates** express positions relative to the default for variation calculations; the default is zero, with the usual endpoint scale running from -1 to +1.

A mapping connects user and design coordinates. For example, a linear map can associate user weights 300 and 700 with design values 0 and 100. User 500 then maps to design 50. The scales are linear but their numbers are different. Axis coordinates also differ from outline coordinates: user weight 700 does not place a point at x = 700 or prescribe a 700-unit stem. [FontLab manual: Axes and Master Locations](https://help.fontlab.com/fontlab/9/articles/axes-and-master-locations/index.html).

Do not assume every API uses the same mapping direction. The inspected FontLab `flAxis` map stores design-to-user pairs. Fontport reverses those pairs when creating a fontTools designspace, whose axis maps use user input and design output. A dictionary of numbers needs its direction documented. [Fontport designspace source](https://github.com/fontlabcom/fontlab-fontport/blob/main/src/fontlab_fontport/designspace.py); [fontTools axis mapping](https://fonttools.readthedocs.io/en/latest/designspaceLib/xml.html#map-element).

## Say what kind of instance exists

An instance definition can name a location without containing any generated outlines. Keep that record separate from the design calculated there:

| Item | What it represents |
| --- | --- |
| Source master | Source design data at a location |
| Named instance definition | A location with naming and output properties |
| Dynamic preview | A displayed calculation at the current location |
| Generated static source | An independent, editable result of a calculation |
| Exported static font | An installable fixed style |
| Exported variable font | An installable font containing data for variation |

An independently generated source does not automatically follow later edits to the original masters. A preview can change as you move through the designspace without creating such a source. Adding an instance definition does not add another master drawing. [FontLab manual: The Variation Model](https://help.fontlab.com/fontlab/9/articles/the-variation-model/index.html).

A variable font can offer named instances and other locations within its supported range. Its compiled variation data is a different artifact from the native editing project or a `.designspace` document. Preserve the source project as well as testing the delivered font. [OpenType Font Variations overview](https://learn.microsoft.com/en-us/typography/opentype/spec/otvaroverview).

## Calculate one fictional width

The exercise uses two records for the same fictional glyph, `a`. Light has user coordinate 300, design coordinate 0 and advance width 500 font units. Bold has user coordinate 700, design coordinate 100 and advance width 700 font units.

First calculate how far the requested user value lies between the endpoints:

**fraction = (requested user value − first user value) / (last user value − first user value)**

Then apply that fraction to each difference. For user 400, the fraction is 0.25. A quarter of the way from design 0 to 100 is 25; a quarter of the way from width 500 to 700 is 550.

This is a deliberately restricted, two-endpoint linear model. It has no intermediate masters, nonlinear mapping, additional axes, substitutions or outline compatibility checks. The width calculation assumes corresponding measurements of the same glyph in the same font-unit scale. It neither constructs outlines nor validates a family.

`sample_width` is a book-defined function. Run the example in external Python 3.11; it imports only `isfinite` from the standard library. The source dictionaries are assumed to contain the shown keys and finite numeric values. The function validates the requested value and the ordering of the user endpoints, then rejects requests outside their range. It does not silently extrapolate or repair missing source fields.

The finite-number check follows [Chapter 8](08-keep-a-recoverable-source.md). The result is a new dictionary: named fields keep the user coordinate, design coordinate, fraction and width separate. The two source names are retained as a tuple. No FontLab object is read or changed.

```python
from math import isfinite


def sample_width(user: float, first: dict, last: dict) -> dict:
    if type(user) not in (int, float) or not isfinite(user):
        raise ValueError("User coordinate must be a finite number")
    start, end = first["user"], last["user"]
    if start >= end:
        raise ValueError("User endpoints must increase")
    if not start <= user <= end:
        raise ValueError("User coordinate is outside the source range")
    fraction = (user - start) / (end - start)
    return {
        "sources": (first["name"], last["name"]),
        "user": user,
        "fraction": fraction,
        "design": first["design"] + fraction * (last["design"] - first["design"]),
        "width": first["width"] + fraction * (last["width"] - first["width"]),
    }


light = {"name": "Light", "user": 300, "design": 0, "width": 500}
bold = {"name": "Bold", "user": 700, "design": 100, "width": 700}

print(f"Fictional a: {light['name']} to {bold['name']}")
for user in [300, 400, 500, 700]:
    result = sample_width(user, light, bold)
    print(f"user {result['user']}: design {result['design']}, "
          f"fraction {result['fraction']}, width {result['width']} font units")
```

Expected output:

```text
Fictional a: Light to Bold
user 300: design 0.0, fraction 0.0, width 500.0 font units
user 400: design 25.0, fraction 0.25, width 550.0 font units
user 500: design 50.0, fraction 0.5, width 600.0 font units
user 700: design 100.0, fraction 1.0, width 700.0 font units
```

The two formatted strings in `print(...)` sit next to each other and form one output string; the line break keeps the code readable. Each pair of braces inserts the named result field, as described in [Chapter 4](04-work-in-the-scripting-panel.md).

Try user 450.5. The design value becomes 37.625 and the width 575.25 font units. A request for 750 raises `ValueError` because it exceeds this exercise's source range. That refusal is a rule of our helper, not a statement that FontLab never supports extrapolation.

The fraction is **not an OpenType normalized coordinate**. In a model whose default is user 400, that default would normalize to zero, while our fraction at 400 is 0.25. The example does not define or build the source arrangement needed to compile that model. Normalization around a default and a fraction between two endpoints answer different questions. [OpenType coordinate normalization](https://learn.microsoft.com/en-us/typography/opentype/spec/otvaroverview#coordinate-scales-and-normalization).

## Check participation and correspondence separately

A master can exist without participating in a particular interpolation. Hiding its overlay changes what you see; excluding it from the calculation changes the available sources. The inspected native `can_interpolate(master_name)` reads that participation flag. Despite its name, it does not test the glyph outlines for compatibility.

That native implementation also falls back to the key master's participation or location when the supplied master name is empty or unknown. A later native reporting script must verify the intended master instead of assuming that a misspelled name will raise an error. These are findings from the inspected source; no call is prescribed here.

Correspondence remains a separate requirement. [Chapter 14](14-plan-an-attachment.md) showed why matching anchor names and point counts cannot establish correct interpolation. The current stored-layer comparison helper checks ordered point types and anchor/component name sets. It excludes component order, multiplicity and transforms, contour closure, coordinates and other data. Its “compatible” result means those particular comparisons passed; it does not certify a native instance or variable-font export. [Source comparison](https://github.com/fontlabcom/fontlab-fontlabapp/blob/main/src/fontlabapp/fontui/source_comparison.py); [comparison limits](https://github.com/fontlabcom/fontlab-fontlabapp/blob/main/src/fontlabapp/masters/layers/compatibility/model.py).

## Read the operation behind the name

Fontport's `Designspace.instance(...)` returns a location record. It does not interpolate a font. Its designspace exporter writes a document and master UFOs, with an explicit loss list; named instances are listed without generated instance UFOs. The exporter shares some key-master data across the master UFOs and writes several files in sequence. File creation is not variable-font compilation or a guarantee of a complete roundtrip. [Fontport location records](https://github.com/fontlabcom/fontlab-fontport/blob/main/src/fontlab_fontport/designspace.py); [designspace export](https://github.com/fontlabcom/fontlab-fontport/blob/main/src/fontlab_fontport/designspace_io.py).

The inspected native `interpolateInstance(...)` follows a different path: it generates a new package and can optionally round its coordinates. Even generating a separate result can initialize source rules or internal data. The native `interpolateMaster(...)` instead adds a generated master to the existing package and updates composites. These methods are not interchangeable with a Python location record or a passive preview.

Nor does every native return value establish complete output. In the inspected master-generation implementation, cancellation can break the glyph loop before the function later returns `true`. A caller must inspect what was actually produced. This is source evidence, not a verified result in an installed FontLab build.

Before using native generation, verify the installed API, exact source/master identities, coordinate spaces and participation. Inspect representative glyphs throughout the range and check whole-font coverage, including widths, anchors, kerning and components. Test cancellation, source preservation and ownership of the generated result. For source mutations, verify Undo/Redo; for retained results, save and reopen them. Finally, inspect an exported variable font and its behavior in the intended applications. None of those acceptance steps is established by the arithmetic exercise above.
