---
this_file: src_docs/md/03-understand-font-data.md
---

# 3. Understand the font data before you script it

“Check this glyph” sounds precise until you ask what to check. Its character assignment? The outline in one layer? Its spacing against a particular neighbor? A useful script begins with a clear answer.

The [previous chapter](02-python-basics.md) used strings and lists that you supplied yourself. This chapter introduces the font concepts needed to describe a real task. Its examples are illustrative data and arithmetic, not FontLab API calls. No native operation is tested or prescribed here. The chapter remains provisional pending the semantic map and editorial review.

## Text and its visible forms

A **character** belongs to text. A **glyph** is a form a font supplies for representing text. A text engine uses the characters, font data and layout rules to choose and position glyphs. These are different stages, so their counts need not match.

A font may contain several forms of the same character. It may also contain a ligature glyph that an application uses for a sequence such as *f* followed by *i*. The source text can retain both characters when the application displays one ligature glyph. An alternate or ligature can have no direct Unicode assignment and still be available through the font's layout rules. [FontLab manual: Fonts and encodings](https://help.fontlab.com/fontlab/9/articles/fonts-and-encodings/index.html).

Visible drawing is not a requirement for every glyph. A space glyph can contribute advance width without an outline. A font can also contain bitmap or color representations. A script that finds no contours has learned something about the representation it inspected; that result alone does not prove that the glyph is missing or broken. [FontLab manual: Font structures](https://help.fontlab.com/fontlab/9/articles/font-structures/index.html).

## Give each identifier one job

Three identifiers answer different questions:

| Identifier | Question it answers | Limit |
| --- | --- | --- |
| Glyph name | Which working glyph are we referring to? | A name does not prove a character assignment. |
| Unicode codepoint | Which encoded character is involved? | A glyph may have no direct assignment, or several. |
| Glyph index, or GID | Where is the glyph in this font's glyph order? | The index can change when the order changes. |

Unicode assigns codepoints to characters independently of their drawing. For example, `U+0041` identifies the Latin capital letter A. The `U+` prefix introduces hexadecimal notation. UTF-8 concerns how character data is represented as bytes; it does not select a font's drawing. [FontLab manual: Glyph identity](https://help.fontlab.com/fontlab/9/articles/glyph-identity/index.html) and [Fonts and encodings](https://help.fontlab.com/fontlab/9/articles/fonts-and-encodings/index.html).

Here is an invented working-font example. The indices illustrate positions, not a required glyph order:

| Glyph name | Direct Unicode assignment | Example GID |
| --- | --- | --- |
| `A` | U+0041 | 12 |
| `A.alt` | None | 37 |

The name `A.alt` suggests an alternate to a person reading it. The suffix does not by itself create a substitution rule. Reordering the glyphs can change their indices while leaving their names and character relationships intact. Another font can use GID 12 for an entirely different glyph. [FontLab manual: Glyph identity](https://help.fontlab.com/fontlab/9/articles/glyph-identity/index.html).

Return to the earlier Python list of names. Counting its items counts strings in that list. It does not establish how many Unicode characters a font supports, how many glyphs exist in the font, or whether the names are unique.

## Follow the drawing into a layer

A FontLab glyph can have several **layers**, each holding data for one drawing state. A layer can contain elements, advance width, anchors and guides. An **element** holds drawing content within the layer. For ordinary outlines, the containment relationship is:

```text
Glyph
└── Layer
    └── Element
        └── Contour
            └── Nodes and handles
```

This is a conceptual diagram, not a sequence of Python attributes. Image and SVG elements hold their own kind of content instead of ordinary contours. Corresponding font masters organize font-wide values and kerning; kerning is not simply another drawing object inside each glyph layer. [FontLab manual: Layers and masters](https://help.fontlab.com/fontlab/9/articles/layers-and-masters/index.html).

A **font master** coordinates corresponding glyph layers for a source design. For example, Light and Bold masters can supply drawings for an intermediate weight. **Interpolation** calculates that intermediate design by combining corresponding data from the sources; the drawings need compatible structures and correctly matched parts. [FontLab manual: Interpolation and compatibility](https://help.fontlab.com/fontlab/9/articles/interpolation-and-compatibility/index.html).

A glyph can also have an auxiliary layer, such as a mask used as a tracing reference. Showing the mask does not make it contribute to the calculation. Hiding the Bold drawing on screen does not stop Bold from contributing. Visibility controls what you see; participation controls which sources the calculation uses. [FontLab manual: Layers and masters](https://help.fontlab.com/fontlab/9/articles/layers-and-masters/index.html).

For a scripting task, “the glyph's outline” therefore needs a scope. Reading one chosen layer and reading every layer are different operations. A loop over glyphs does not automatically answer which layers the loop should inspect.

## Read the parts of an outline

A **contour**, also called a path, is a continuous sequence of segments. A **segment** joins neighboring nodes and can be a line or a curve. A **node** is an on-curve point. A **handle**, or control point, is an off-curve point that influences a curve's shape.

In a cubic curve, the direction and length of a handle help determine how the curve approaches or leaves its node. The curve does not normally pass through the handle. TrueType curves use a different arrangement of off-curve points, including implied on-curve positions, so the cubic model is not a complete description of every outline. [FontLab manual: Contours, nodes and handles](https://help.fontlab.com/fontlab/9/articles/contours-nodes-and-handles/index.html).

A simple outline *o* can have two closed contours, one outside and one around its **counter**, the enclosed space inside the *o*. That is an example, not a universal contour count. A closed contour returns to its first node; an open contour has endpoints without a closing segment. Its **start point** determines where the stored sequence begins. Changing the start point of a closed contour can change point order without changing the visible shape. [FontLab manual: Contours, nodes and handles](https://help.fontlab.com/fontlab/9/articles/contours-nodes-and-handles/index.html).

This makes “same appearance” a different question from “same structure.” A future comparison script will need to say which question it answers.

## Know the unit before using the number

FontLab expresses glyph coordinates in **font units**. **Units per em**, or **UPM**, establishes the scale: in a 1000-UPM font, one font unit is one thousandth of an em. The em is a reference size, not a box that must contain every drawing.

The glyph's **origin** is `(0, 0)`. Its horizontal baseline is at y = 0. Increasing x moves right; increasing y moves up. Font units are not screen pixels, and canvas zoom does not change the stored coordinates. [FontLab manual: The em and the coordinate system](https://help.fontlab.com/fontlab/9/articles/the-em-and-the-coordinate-system/index.html).

For an illustrative calculation, a height of 600 font units is 60% of the em at 1000 UPM, but 30% at 2000 UPM. Those are proportions, not claims about a particular font's cap height or its rendered pixels. Keep the UPM and measurement scope with any numerical report.

## Separate shape from spacing

The following model concerns ordinary upright, horizontal measurement before kerning or other positioning adjustments. The **advance width** is the distance between successive glyph origins. The **drawing width** measures the horizontal extent of the drawing itself. The **sidebearings** relate that extent to the advance boundaries.

For a glyph with measurable drawing bounds:

```text
advance width = left sidebearing + drawing width + right sidebearing
```

The **bounding box** encloses the relevant drawing; its width excludes sidebearings. It is not simply the glyph's advance interval. [FontLab manual: Designing the whitespace](https://help.fontlab.com/fontlab/9/articles/designing-the-whitespace/index.html).

Consider an invented drawing from x = 30 to x = 490 with an advance of 560 font units:

| Measurement | Calculation | Result in font units |
| --- | --- | --- |
| Drawing width | 490 − 30 | 460 |
| Left sidebearing | 30 − 0 | 30 |
| Right sidebearing | 560 − 490 | 70 |
| Advance width | 30 + 460 + 70 | 560 |

Moving that drawing 10 units right while retaining its advance gives sidebearings of 40 and 60. Increasing the advance by 20 units while leaving the original drawing in place instead gives sidebearings of 30 and 90. These are different changes.

Sidebearings can be negative when a drawing overhangs its advance boundaries. A space glyph can have advance without visible bounds, and a visible mark can have zero advance. Equal numerical bearings also need not look equally spacious. The table is a geometric example, not an optical-spacing rule or a definition of what a native bounds API returns for an empty layer. [FontLab manual: Designing the whitespace](https://help.fontlab.com/fontlab/9/articles/designing-the-whitespace/index.html).

## Decide whether the adjustment belongs to a pair

Default glyph spacing applies across different neighbors. **Kerning** adjusts particular combinations. For a simple horizontal example, a pair adjustment of −40 font units reduces separation by 40 units; +40 increases it. Neither sign alone says whether the result looks right. [FontLab manual: The kerning model](https://help.fontlab.com/fontlab/9/articles/the-kerning-model/index.html).

FontLab's editable kerning model includes individual pairs, classes and exceptions. A **kerning class** groups glyphs that share treatment on one side, so a stored class pair can affect many glyph combinations. An **exception** supplies a narrower correction. Kerning belongs to masters in a varying design, and its editable representation differs from compiled font layout data. [FontLab manual: The kerning model](https://help.fontlab.com/fontlab/9/articles/the-kerning-model/index.html).

A report should therefore identify what it counts: stored records, effective glyph-pair values, or visible gaps in a particular text sample. Those are different results, even when each is labelled “kerning.” This chapter does not define API access, exception precedence, export behavior or text-direction handling.

## Describe a task before choosing its API

Try these distinctions before writing code:

1. **A list contains `A` and `A.alt`. Does it prove two Unicode characters are supported?** No. The entries are names, and the alternate may have no direct assignment. A coverage report needs character-mapping evidence.
2. **One layer has no contours. Is the glyph missing?** Not necessarily. The inspected layer may be empty or hold another representation; the glyph may also have other layers. State the layer and representation being checked.
3. **A glyph looks loose against many neighbors. Should every pair receive a correction?** First inspect its default spacing. Pair-specific kerning addresses combinations; repeated corrections can conceal a default-spacing problem. Visual judgment still requires suitable text and size.

The next useful specification is a sentence with an explicit target and result: “Report the advance widths of these named glyphs in this chosen layer.” Before turning it into an executable script, you still need a verified way to identify that font, resolve its layers and read the intended values.
