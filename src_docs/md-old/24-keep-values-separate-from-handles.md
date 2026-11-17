---
this_file: src_docs/md/24-keep-values-separate-from-handles.md
---

# Keep values separate from live handles

Putting a glyph into a Python list does not turn it into a saved copy. The list may hold another reference to the same native data. A report that needs to survive a document change should retain the values it needs, with their source identity, instead of assuming its wrappers remain usable.

This chapter explains references and copies through **fictional records in external Python 3.11**. The exercise imports no FontLab module, accesses no document and writes no file. Native source observations were checked on 13 November 2026; they do not establish behavior for every installed build. The chapter remains provisional pending independent review and semantic-map integration.

## A name, a container and a value

An **alias** is another name for the same object. Python assignment binds a name; it does not automatically copy the object. If two names refer to one dictionary, changing that dictionary through either name affects what both names see.

A **shallow copy** creates a new container while retaining references to its contents. Nested mutable objects can therefore remain shared. Copying only selected strings, numbers and tuples of numbers can instead produce a report whose recorded values are independent of later changes to the source container. The exercise below uses that deliberately limited kind of data. [Python: Shallow and deep copy operations](https://docs.python.org/3.11/library/copy.html).

For native scripting, keep several questions separate:

| Description | What it tells you |
| --- | --- |
| Python alias | Two names refer to the same Python object |
| Wrapper or handle | A Python object provides access to another object or native data |
| Retained reference | Some ownership mechanism keeps a particular object referenced |
| Detached value record | The selected ordinary values no longer require access to the source object |
| Saved font | A file contains data that must be checked independently |

A retained native object is not necessarily a complete independent font, and retaining a wrapper does not establish that its document is still open or valid. A new container can also contain live handles. Its type alone cannot answer the ownership question.

## Watch what a shallow copy shares

The original teaching record below describes one fictional glyph. `font_id` is an invented label, not a FontLab identifier. Its points are tuples containing numbers. The function records four selected fields; it is not a font serializer.

```python
def record_values(source: dict) -> tuple:
    return source["font_id"], source["glyph"], source["width"], tuple(source["points"])


source = {
    "font_id": "orchard-1",
    "glyph": "A",
    "width": 600,
    "points": [(0, 0), (10, 20)],
}
alias = source
shallow = source.copy()
record = record_values(source)

source["width"] = 620
source["points"].append((20, 0))
print(f"Alias: width={alias['width']}, points={len(alias['points'])}")
print(f"Shallow copy: width={shallow['width']}, points={len(shallow['points'])}")
print(f"Recorded values: width={record[2]}, points={len(record[3])}")

source = {"font_id": "orchard-2", "glyph": "A", "width": 700, "points": []}
print(f"Current source: {source['font_id']}")
print(f"Alias still refers to: {alias['font_id']}")
```

The output is:

```text
Alias: width=620, points=3
Shallow copy: width=600, points=3
Recorded values: width=600, points=2
Current source: orchard-2
Alias still refers to: orchard-1
```

`source.copy()` makes the shallow dictionary copy. Replacing `source["width"]` changes that dictionary's binding to a number. The separate shallow dictionary still holds 600. However, both dictionaries refer to the same points list, so appending to that list is visible through both.

`tuple(source["points"])` records the current list entries in a tuple. In this example those entries are themselves tuples of immutable numbers, so the recorded geometry stays unchanged. This does **not** make `tuple()` a general deep-copy operation. If the entries were mutable objects or native nodes, a tuple could still hold references to those objects. Python's generic copying machinery can also be customized by a class; do not assume it knows how to detach an arbitrary native wrapper. [Python copy contracts](https://docs.python.org/3.11/library/copy.html).

The final assignment binds `source` to a new dictionary. It does not redirect `alias`, which still refers to the first one. This demonstrates Python names, not FontLab document closing or wrapper invalidation.

The `f` prefix in each output line inserts expressions written inside braces. `len()` counts entries. Index 2 of the recorded tuple contains the width; index 3 contains its points. An empty points list records as an empty tuple. A missing required dictionary key raises `KeyError`; the helper does not silently invent that field. Its contract expects the displayed strings, numbers and point tuples, rather than arbitrary external data. [Python dictionary access](https://docs.python.org/3.11/library/stdtypes.html#mapping-types-dict).

## A native copy name needs its own contract

The inspected FontGate source provides a useful warning about terminology. Its reference-counted `fg::Object::clone()` increments a reference count and returns the same object. Here, **reference counting** tracks retained uses so that an object can be released when its count reaches zero. That method name does not mean a deep copy.

The inspected `DataOwner` class keeps package, glyph and data references. Its editor-owned package path retains a package pointer, while other paths create a package carrier whose font and style can remain shared. Looking up a glyph by name or index creates a Python wrapper using the parent font's ownership context. Putting several such wrappers into a list does not detach their underlying font data.

There is a separate `fgGlyph` constructor path described in the source as an orphan copy, which constructs a new glyph from another glyph. That distinction is useful, but this chapter does not qualify its dependent data, components or complete independence. Neither “all FontGate glyphs are copies” nor “all copies are live editor glyphs” follows from these paths.

Likewise, `CurrentFont()` resolves the active package at the time of the call. A variable that previously received its result should not be assumed to follow every later document switch. Before a later native operation, identify the intended document and obtain valid current handles through a separately verified path. Do not experiment with dereferencing old wrappers after closing their document.

These are findings from the inspected `fontgatelib.cpp`, `fgglyph.cxx`, `fgfont.cxx` and native `python_gate.cpp` implementations. They are not new runtime tests or a supported native copying recipe.

## Frozen does not mean detached

The current App source contains two instructive records. `NativeSource` is a frozen dataclass containing package, layer and glyph handles. *Frozen* prevents ordinary reassignment of its fields; it does not turn the referenced native objects into plain values.

`GlyphSnapshot` instead holds selected contours, anchors, measurements and optional data for computations. Its contour reader explicitly extracts coordinates and flags into records and tuples. That extraction establishes the shape of the resulting data, but capture still traverses native objects and requires its own qualification. The default own-contour path skips components; optional fields and caches affect coverage and freshness. It is not a saved font or proof of an atomic capture. [App snapshot records and capture](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/plugins/snapshot.py).

The snapshot's `source_key` is excluded from its equality comparison. Two snapshots can therefore compare equal in their content without proving that they came from the same source. Keep source identity alongside content and compare the identity when the task depends on it.

App also distinguishes `package.id` from `package.fgId`: they identify objects in different parts of the system. A helper for one namespace must not receive an interchangeable-looking number from the other. Package names alone are not sufficient identity either. [App context and identifier helpers](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/core/scripting.py).

Import conveniences do not remove these boundaries. App can expose native objects lazily; constructing its `Application` accesses the workspace and UI. Some utilities work outside FontLab, but that does not make native application construction an external-Python operation. [App native loading](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/__init__.py); [application context](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/core/application/context.py).

## A read-back value is one observation

[Chapter 8's bounded experiment](08-keep-a-recoverable-source.md#a-changed-python-value-may-not-reach-the-saved-font) used an owned GG Vize copy in FontLab 9.0.9809 with embedded Python 3.11.6. After a setter-only width attempt, Python read A as 616 instead of 606. Independent native metrics and the saved, reopened copy still reported 606. B stayed at 520, and the dirty flag and called history-state value did not change.

That result does not establish the cause. It does not prove that the glyph was detached, that a missing update caused the mismatch, or that another setter or version fails in the same way. In that first experiment, no explicit `fontlab.Update()` or history-publication sequence was tested, and Undo/Redo was not invoked. The earlier native snapshots may have affected wrapper or cache state.

A later comparison on the same FontLab 9.0.9809/Python 3.11.6 runtime used two fresh owned GG Vize copies. One procedure used the setter alone; the other added one explicit `fontlab.Update(glyph)` on the same retained glyph reference immediately afterward. Both returned without an exception. Both read A as 616 in Python, while independent native metrics and saved/reopened Python and native reads remained 606. B stayed at 520; dirty flags remained false and history-state values remained 0.

Within each procedure, native name/advance-width records for all 101 glyphs matched before, after and after reopening. That comparison does not establish preservation of all outlines or metadata outside the separately inspected A/B payloads. Undo/Redo and a history-publication sequence were still not tested. **The explicit update did not resolve the mismatch in these measured conditions.** The result does not establish its cause, cover other update paths or versions, or justify a general claim that updates fail. Both procedures included native observations before assignment, so their materialization and cache effects remain a limit.

The source makes a guessed repair particularly unsuitable. Some data access paths prepare FontGate data before returning it. The inspected width setter calls an internal owner update. The explicit `Update` path can assign FontGate data into editor glyphs, including replacing layers; a font-level path visits all its glyphs. Preview paths can process queued changes. An update therefore needs its own scope and effect checks—it is not a general instruction to make a report correct.

Keep the observations separate: a wrapper's returned value, independent editor data, history behavior and reopened file contents. A successful save status establishes neither the intended value nor complete preservation. Native writer guidance similarly treats partial results, queued updates and host acceptance as explicit concerns. [FontLab native scripting guide](https://code.fontlab.com/fontlab-python-docs/guide/native.html#handle-writer-results-and-failures).

## Retain the values your report needs

For an offline computation, record the necessary ordinary values while the source is valid. Include the font and glyph identity, layer or master context, units and which data was included. Keep missing data distinct from empty data. An immutable result can still be incomplete or stale.

For a later native action, reacquire and check its live targets rather than treating the earlier report as an owner of the document. Checking identity at the beginning and end can detect some changes, but does not prove that state stayed unchanged throughout capture. The native capture itself may also prepare data.

The tests for this chapter establish only the fictional Python alias, shallow-copy and selected-value behavior. Native lifetimes, post-close handles, getters, synchronization, Undo/Redo and persistence need their own bounded tests on owned fixtures. No native copying or update procedure is offered here.
