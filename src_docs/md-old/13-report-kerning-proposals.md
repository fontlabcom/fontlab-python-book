---
this_file: src_docs/md/13-report-kerning-proposals.md
---

# Report the spacing decision before changing it

A displayed kerning value does not tell you whether the font stores that exact pair. It may come from a class, or it may be an explicit exception—including an exception whose value is zero. Before proposing a change, record which master and which pair record supplied the result.

This chapter uses a fictional, proposal-only Python exercise. **Native spacing edits, kerning edits, Undo/Redo and save/reopen behavior remain unverified for this chapter.** The draft remains provisional pending independent review and semantic-map integration.

## Separate spacing from kerning

Spacing establishes a glyph's default fit. Kerning adjusts particular combinations. For ordinary upright, horizontal bounding-box measurement, advance width equals left sidebearing plus drawing width plus right sidebearing. With bounds from x = 30 to x = 470 and an advance of 550, the drawing width is 440, the left sidebearing is 30 and the right sidebearing is 80. See [Chapter 3](03-understand-font-data.md) for the terms and units.

In a simplified left-to-right pair, a kerning adjustment of -40 changes the next-origin distance from 550 to 510 units. This calculation excludes tracking, mark placement and other shaping adjustments. It does not calculate the final positions of arbitrary text. A problem that occurs against many neighbors may call for a spacing change; a problem specific to a combination may call for kerning. [FontLab manual: Designing the whitespace](https://help.fontlab.com/fontlab/9/articles/designing-the-whitespace/index.html).

Keep the measurement convention explicit. The inspected Glyport implementation compensates italic shear when calculating its sidebearings. Its LSB setter can move outlines and change advance width, while its RSB setter changes width. A sidebearing property is therefore not necessarily an isolated stored number, and the ordinary upright formula does not describe every italic measurement route. [Glyport source](https://github.com/fontlabcom/fontlab-glyport).

## Distinguish a stored pair from the value it supplies

A **kerning class**, also called a kerning group in some APIs, contains glyphs that share treatment on a particular side. A class-to-class pair can supply a value for many glyph combinations. An **exception** supplies a more specific value for a narrower combination. The exception replaces the broader value for that combination; it is not another amount added to it. [FontLab manual: The kerning model](https://help.fontlab.com/fontlab/9/articles/the-kerning-model/index.html).

Use two separate questions in a report:

- **Explicit:** Is this exact pair key stored, and with what value?
- **Effective:** Which applicable pair key supplies the value under the chosen lookup rule?

Suppose a class pair supplies -70 and the exact `A/V` pair stores 0. The effective value for `A/V` is 0 under the lookup rule used below. Removing the explicit zero can expose -70 again. A proposal to set zero is consequently different from a proposal to remove a pair.

The fontTools UFO lookup checks an exact pair first. For glyph-name input with valid group membership, its candidate order is glyph/glyph, glyph/group, group/glyph, then group/group. It returns the first stored value, including zero. A caller can choose `None` as the fallback when no applicable value exists. This describes that lookup function; it does not establish every editor's API behavior or the output of a shaping engine. [fontTools: Kerning lookup](https://fonttools.readthedocs.io/en/latest/ufoLib/kerning.html).

Never use `if value` to determine whether a pair exists: zero is false in a Python condition. Test membership separately. Likewise, an API returning zero for an absent pair needs an additional presence indicator if the report must preserve that distinction.

## Name the master and the side

Regular and Bold can store different kerning. An intermediate preview may show a calculated value rather than another stored pair. Do not turn an absent source pair into zero merely because a preview displays a number. [FontLab manual: Kerning across masters](https://help.fontlab.com/fontlab/9/articles/kerning-across-masters/index.html).

The inspected APIs use different master inputs. Fontport's font-level native kerning route selects the package's default master. Glyport pair methods take a master ID from its compatibility model, which the backend resolves to a native master name. Other native calls default to the current master. A master name, that model's ID and the current UI choice are not interchangeable.

Class-side vocabulary differs too. For the left-to-right examples in this chapter:

| Vocabulary | First glyph in the pair | Second glyph in the pair |
| --- | --- | --- |
| UFO group prefix | `public.kern1.` | `public.kern2.` |
| Glyphs-style group key | `@MMK_L_` | `@MMK_R_` |
| Glyport glyph property supplying that key | `rightKerningGroup` | `leftKerningGroup` |

The property names describe the glyph edge facing its neighbor; the group-key names describe the glyph's position in the pair. UFO's specification uses logical first and second positions and also describes right-to-left text. This exercise stays left-to-right. Its class names do not represent an RTL or vertical-kerning implementation. [UFO specification: Kerning](https://unifiedfontobject.org/versions/ufo3/kerning.plist/); [Glyport source](https://github.com/fontlabcom/fontlab-glyport).

## Prepare a proposal from fictional records

The following data assigns `A` and `Aacute` to a fictional first-side class, and `V` and `W` to a fictional second-side class. The requested pairs contain their candidate keys explicitly, in the order described above. The code does not discover or validate class membership. These are teaching records, not data read from FontLab, a font-file format or a complete kerning engine.

Each request also contains a desired explicit value. The report identifies the current exact-pair state, finds the first stored candidate and prints the proposal. It does not calculate the resulting kerning for every affected glyph combination or apply any proposal.

A dictionary key can be a tuple, such as `("A", "V")`. `key in values` tests whether that key is present. `first_stored` returns two values as a tuple; `source, value = ...` unpacks them, as in [Chapter 7](07-choose-the-drawing.md). The expressions `text if condition else other_text` choose display text; this conditional-expression form was explained in [Chapter 9](09-report-selected-glyphs.md).

`isfinite` rejects infinity and NaN, as in [Chapter 8](08-keep-a-recoverable-source.md). The additional type check excludes text and Boolean values from proposals. The supplied fixture values and candidate lists are assumed to have the structure shown here; this helper is not a validator for arbitrary imported data.

```python
from math import isfinite


def first_stored(values: dict, candidates: list) -> tuple:
    for key in candidates:
        if key in values:
            return key, values[key]
    return None, None


def proposal_lines(masters: dict, master: str, requests: list) -> list:
    values = masters[master]
    lines = [f"Master: {master} (fictional)"]
    for request in requests:
        pair, proposed = request["pair"], request["proposed"]
        if type(proposed) not in (int, float) or not isfinite(proposed):
            raise ValueError("Proposed value must be a finite number")
        source, value = first_stored(values, request["candidates"])
        explicit = str(values[pair]) if pair in values else "absent"
        effective = str(value) if source is not None else "none"
        lines.append(f"{pair[0]}/{pair[1]}: explicit {explicit}; effective {effective}")
        if source is not None:
            lines.append(f"  from {source[0]}/{source[1]}")
        action = "keep explicit" if pair in values and values[pair] == proposed else "propose set explicit"
        lines.append(f"  {action} {proposed}")
    return lines


class_pair = ("public.kern1.A", "public.kern2.V")
masters = {
    "Regular": {class_pair: -70, ("A", "V"): 0},
    "Bold": {class_pair: -90},
}
requests = [
    {
        "pair": ("A", "V"),
        "candidates": [("A", "V"), ("A", "public.kern2.V"),
                       ("public.kern1.A", "V"), class_pair],
        "proposed": 0,
    },
    {
        "pair": ("Aacute", "W"),
        "candidates": [("Aacute", "W"), ("Aacute", "public.kern2.V"),
                       ("public.kern1.A", "W"), class_pair],
        "proposed": -60,
    },
    {
        "pair": ("H", "H"),
        "candidates": [("H", "H")],
        "proposed": 0,
    },
]
for line in proposal_lines(masters, "Regular", requests):
    print(line)
```

Expected output:

```text
Master: Regular (fictional)
A/V: explicit 0; effective 0
  from A/V
  keep explicit 0
Aacute/W: explicit absent; effective -70
  from public.kern1.A/public.kern2.V
  propose set explicit -60
H/H: explicit absent; effective none
  propose set explicit 0
```

The first request needs no explicit change. The second proposes a new exception. The third deliberately distinguishes “no applicable stored value” from a proposed explicit zero; it is not a recommendation to add unnecessary zero pairs. A real writer might normalize such a pair instead of storing it.

The function prepares every line before the outer loop prints. An invalid later proposal therefore raises before any partial report is displayed. No source dictionary changes. An empty request list reports only the named master; a missing master raises `KeyError` instead of silently selecting another one.

Change the requested master to `"Bold"`. The first pair now has no exact entry and inherits -90, so requesting explicit 0 becomes a proposed change. The fixture uses the same class membership in both masters. It does not test fonts whose classes differ by master.

## Keep reports and native edits on different paths

Fontport already has a detached `inspect_kerning` helper that reports explicit presence, explicit value and effective value, and an `edit_kerning` helper that prepares a changed mapping. Its native `RKerning.apply` route replaces the complete explicit-pair mapping. Passing a small selection to a whole-map replacement method can have a much larger scope than the selection suggests. [Fontport source](https://github.com/fontlabcom/fontlab-fontport).

Source inspection also exposes limits that a live report must resolve. Fontport's requested-master pair reader obtains its group routes through an unscoped current-master reader. Glyport's layer-pair lookup combines a layer ID with group properties obtained from the current master. Neither source path establishes correct results for every case where requested and current masters have different classes. The fictional example avoids that unresolved combination.

Native FontGate distinguishes exact stored-map access from lookup that includes class fallback. The inspected native `get_kerning_pair` tool uses the latter; its `has_value` result alone does not prove that the exact glyph pair is stored. Some native setter paths also round values or remove a zero pair unless it must remain an exception. A native getter and setter with familiar names are not equivalent to the dictionary operations above.

History is another boundary. The inspected Fontport write path uses multiple native steps to preserve explicit zeros and checks fractional-history limits. Glyport sends native editing commands and invalidates its cached data after a write attempt, including failure. Acquiring a native kerning history container can itself initialize internal state. These source findings do not establish passive reads, atomic changes or exact restoration of pair structure after Undo.

Before a live proposal can become an editing recipe, verify the installed API and master mapping, explicit/effective distinction, zero and fractional behavior, shared classes, failure readback, Undo/Redo and the saved artifact after reopening. Inspect compiled text separately from stored pair equality. The proposal-only exercise supplies a traceable decision to review; it does not establish any of those native results.
