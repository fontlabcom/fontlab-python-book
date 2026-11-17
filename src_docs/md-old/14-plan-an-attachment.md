---
this_file: src_docs/md/14-plan-an-attachment.md
---

# Plan an attachment before building it

An accent can use the right source glyph and still sit in the wrong place. Before changing its offset, identify the base, the mark, the master and the two points that should meet.

This chapter calculates proposals from fictional Python records. **Native component construction, interpolation, Undo/Redo and save/reopen behavior remain unverified for this chapter.** The draft remains provisional pending independent review and semantic-map integration.

## Give each part a role

A **component** refers to another glyph used as part of a drawing. Its transformation places that source drawing in the composite. An **anchor** is a named attachment point. A **recipe** specifies which parts to assemble and how to place them; an anchor alone does not select those parts.

For a simple accented letter, the base might be `a` and the mark `acutecomb`. A common attachment uses `top` in the base and `_top` in the mark. Moving the mark until those two points coincide establishes the placement. The names describe the intended relationship; they do not require the anchor to be at the highest outline point. [FontLab manual: Anchors for Positioning](https://help.fontlab.com/fontlab/9/articles/anchors-for-positioning/index.html).

Names are only part of the native decision. Anchors have participation settings, and construction can use explicit mappings between different names. Several preceding components may offer an attachment point. Record the intended pair instead of assuming that any matching name is the right one.

## Decide what should remain linked

A component reference and its placement are separate relationships. An ordinary, unanchored manual component can continue to reflect its source drawing while keeping the offset calculated when it was placed. A later source-anchor move need not recalculate that offset.

An individually **Anchored** component can keep its placement controlled by attachment points. An **auto layer** retains a recipe and rebuilds its construction from its sources. Those are different choices: a manual layer can contain an Anchored component without making the whole layer automatic. Copied anchors from a one-time build are not necessarily live inherited anchors afterward.

The inspected native component builder reflects these distinctions: it tracks source dependencies, builds included shapes and can update transforms during automatic attachment. The Scriptmix alignment tool explicitly works with manual placements and checks for unsupported transforms and automatic dependencies before writing. These are source findings, not a tested construction procedure for your installed FontLab. [Scriptmix: Align By Anchor](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/main/Scripts/Components/Align%20By%20Anchor.py); [shared component writer](https://github.com/fontlabcom/fontlab-fontlabapp/blob/main/src/fontlabapp/components/writer.py).

## Calculate a translation

Start with the restricted case from [Chapter 12](12-transform-a-recording.md): both parts have their original scale and orientation. They may move, but neither is scaled, slanted or rotated.

Suppose the base anchor is at `(250, 700)` and the base itself has offset `(0, 0)`. Its anchor therefore appears at `(250, 700)` in the composite. The mark's attachment anchor is at `(100, 0)` in its own source. The mark needs offset `(150, 700)`, because `(100 + 150, 0 + 700)` reaches the base anchor.

For each coordinate, the calculation is:

**mark offset = base offset + base anchor − mark anchor**

This gives the mark's proposed absolute offset in the composite, not a distance to add to its current offset. All coordinates use the same font-unit scale. With scaling, slant or rotation, the relevant anchor points must first be mapped through the linear parts of the transforms; the simple subtraction alone is insufficient. Scriptmix's inspected planner restricts this arithmetic to translations and rounds its proposals. Our exercise keeps the arithmetic result without adding a rounding rule.

## Report proposals from fictional records

Each record below names a master, a base and a mark. Its two anchor dictionaries describe those source glyphs in that master. `Medium` deliberately lacks the mark anchor; the example reports that omission instead of copying the value from Light or Bold.

`attachment_proposals` is a function defined for this book, not a FontLab API. The exercise runs in external Python 3.11 and imports no library. Its inputs are assumed to contain the shown keys, finite numeric coordinate pairs, unique anchor names and translation-only placement. It does not validate arbitrary imported data, discover layers or model native anchor participation settings.

The function returns report lines before the final loop prints them. The `continue` statement skips the rest of the current loop iteration after a missing anchor has been reported. `not in` tests that a dictionary key is absent; a present `(0, 0)` point is still a valid point. Coordinate unpacking follows [Chapter 7](07-choose-the-drawing.md), and the `f` strings use the braces explained in [Chapter 4](04-work-in-the-scripting-panel.md).

```python
def attachment_proposals(records: list, anchor_name: str) -> list:
    lines = []
    mark_anchor = "_" + anchor_name
    for record in records:
        label = f"{record['master']} {record['base']} + {record['mark']}"
        base = record["base_anchors"]
        mark = record["mark_anchors"]
        if anchor_name not in base:
            lines.append(f"{label}: missing base {anchor_name}")
            continue
        if mark_anchor not in mark:
            lines.append(f"{label}: missing mark {mark_anchor}")
            continue
        dx, dy = record["base_offset"]
        bx, by = base[anchor_name]
        mx, my = mark[mark_anchor]
        proposed = (dx + bx - mx, dy + by - my)
        lines.append(f"{label}: propose mark offset {proposed}")
    return lines


records = [
    {
        "master": "Light", "base": "a", "mark": "acutecomb",
        "base_offset": (0, 0),
        "base_anchors": {"top": (250, 700)},
        "mark_anchors": {"_top": (100, 0)},
    },
    {
        "master": "Bold", "base": "a", "mark": "acutecomb",
        "base_offset": (0, 0),
        "base_anchors": {"top": (300, 720)},
        "mark_anchors": {"_top": (110, 0)},
    },
    {
        "master": "Medium", "base": "a", "mark": "acutecomb",
        "base_offset": (0, 0),
        "base_anchors": {"top": (275, 710)},
        "mark_anchors": {},
    },
]

for line in attachment_proposals(records, "top"):
    print(line)
```

Expected output:

```text
Light a + acutecomb: propose mark offset (150, 700)
Bold a + acutecomb: propose mark offset (190, 720)
Medium a + acutecomb: missing mark _top
```

The code preserves the input records and their order. It reports the first missing attachment side in a record; it is not an exhaustive validator. If a required metadata key such as `master` is missing, ordinary dictionary access raises `KeyError`. That malformed record does not acquire a guessed master name.

Try changing Light's `base_offset` to `(20, -10)`. Its proposal becomes `(170, 690)`: moving the base also moves the attachment point the mark must reach. No FontLab object changes when you run or alter this exercise.

## Match sources before interpolating

Interpolation combines corresponding source values. Under a simple linear model, halfway between the Light proposal `(150, 700)` and the Bold proposal `(190, 720)` is `(170, 710)`. This arithmetic does not fill the missing Medium anchor record or establish a valid FontLab instance.

The source glyphs and their intended attachment names must exist in the relevant masters. Outline correspondence also matters: equal point counts do not tell you that the same parts of a letter are paired. Open or closed contour state, segment types, order and intended matches need their own checks. See [Chapter 3](03-understand-font-data.md) for master and contour terminology.

The inspected FontLabapp preview checks contour counts and sequences of on-curve/off-curve flags before blending coordinates. Its snapshot compatibility helper explicitly excludes components and open/closed state. A successful result from that limited check is therefore not complete native interpolation or export validation. Fontport's designspace inspector reads source and instance locations; inspecting those locations does not generate an interpolated font. [FontLabapp preview model](https://github.com/fontlabcom/fontlab-fontlabapp/blob/main/src/fontlabapp/masters/interpolation/model.py); [snapshot compatibility limits](https://github.com/fontlabcom/fontlab-fontlabapp/blob/main/src/fontlabapp/masters/interpolation/outlines.py); [Fontport designspace source](https://github.com/fontlabcom/fontlab-fontport/blob/main/src/fontlab_fontport/designspace.py).

## Inspect the result of a native rebuild

A native construction check can do more work than our Python proposal. The inspected `build_glyph` implementation creates and populates a temporary native layer before its `dry_run` return. Its write branch replaces target shapes, anchors and advance width, then sends change and update notifications. The dry-run branch precedes target replacement, but that ordering alone does not prove that all earlier native reads and builders leave internal state untouched. Scriptmix's recipe tool acknowledges possible internal glyph-data refresh. [Scriptmix: Build From Recipes](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/main/Scripts/Components/Build%20From%20Recipes.py).

Return values also need a precise interpretation. In the inspected native composite builder, `update()` can return `true` after an unsuccessful internal build clears the destination contours; the `#instance` case has a separate condition. A returned success flag alone does not establish that the component has valid geometry. This is a source finding, not an observed result in an installed application.

Ownership matters after a rebuild. Native wrappers can refer to shared source data, and decomposition can replace a component with outlines and invalidate an adapter's cached identity. Glyport explicitly manages these changes and attempts recovery after some failures; recovery can itself fail. Do not keep an old wrapper and assume that it now represents the replacement drawing. [Glyport component edits](https://github.com/fontlabcom/fontlab-glyport/blob/main/src/fontlab_glyport/model/component_edits.py).

Before adopting a native construction script, use a disposable source copy and verify the intended master, source references, transformed placement, missing-data behavior and automatic dependencies. Inspect the actual resulting shapes, anchors and width. Then check failure handling, Undo/Redo and a saved-and-reopened result separately, as described in [Chapter 8](08-keep-a-recoverable-source.md). The fictional proposals in this chapter establish none of those native outcomes.
