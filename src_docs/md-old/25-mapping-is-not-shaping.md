---
this_file: src_docs/md/25-mapping-is-not-shaping.md
---

# Character mapping is not shaping

A font can contain a glyph named `f_i` while typed `fi` still displays as two glyphs. The drawing exists, but its name alone does not provide the rule that selects it. A useful report distinguishes the characters supplied, their initial glyph mappings and the layout that follows.

The first exercise uses **fictional text and assignment records in external Python 3.11** and imports no font library. The practical project that follows reads assignment metadata from the current FontLab font. That script has bounded native verification on two owned fixtures and the no-font branch, recorded below; additional cases use offline tests. Neither example performs shaping or file operations, and exported-font behavior remains unverified here. Source observations were checked on 13 November 2026; the draft remains provisional pending independent review and semantic-map integration.

## Identify the number before using it

A **codepoint** identifies a position in the Unicode code space. For example, U+0041 identifies Latin capital A. A glyph is a form supplied by a particular font. A font may offer several forms associated with that character, and layout can choose among them.

Several other numbers occur in a scripting report:

| Value | Its context |
| --- | --- |
| Position in a Python string | An index into its sequence of codepoints |
| Unicode codepoint | A value such as U+0041, independent of a font's glyph order |
| Glyph-order index, or GID, in a font binary | An entry in that particular font's ordered glyph collection |
| Native glyph object ID | An identifier used by a particular native API and document context |
| Shaping cluster value | Information associating output glyphs with parts of the supplied input |

These values are not interchangeable. The inspected native glyph-list source returns `glyph_id` and `index` separately. Its `glyph_id` comes from the native FontGate identity; it is not an exported font's glyph-order index. In the inspected FontGate subscription path, a numeric key selects by glyph index. Thus `font[65]` does not mean “find U+0041”. [Chapter 6](06-find-the-glyph-you-mean.md) explains the qualified lookup examples.

Python strings contain codepoints, so a loop over text does not necessarily visit one visible character at a time. A base letter and combining mark can occupy two positions while forming one user-perceived character. Text segmentation has its own rules. [Python text sequences](https://docs.python.org/3.11/library/stdtypes.html#text-sequence-type-str); [Unicode text segmentation](https://www.unicode.org/reports/tr29/).

A shaping cluster is another relationship. A ligature can combine several input characters, and a substitution can split one input into several output glyphs. HarfBuzz records cluster information through these operations. Its cluster values depend on how the caller supplies the input; do not assume every API reports Python indices or byte offsets. [HarfBuzz clusters](https://harfbuzz.github.io/clusters.html); [working with cluster values](https://harfbuzz.github.io/working-with-harfbuzz-clusters.html).

## Separate three uses of encoding

UTF-8 and UTF-16 describe representations of Unicode text. Decoding bytes with the correct encoding recovers a character sequence. Choosing a font is a later decision; changing its outlines does not repair incorrectly decoded text.

A glyph's **Unicode assignments** describe which codepoints initially reach it. In an OpenType font, the `cmap` table supplies character-to-glyph mappings. Those mappings are distinct from layout substitutions and positioning. [OpenType cmap specification](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap).

FontLab also uses **encoding files**, with the `.enc` extension, for ordered glyph-name collections. In the inspected current manual, these define targets for an Encoding filter. They are neither a UTF byte encoding nor a request to assign Unicode values to those glyphs. A target collection can include a name missing from the current font.

Naming resources are separate again. A font-specific `.nam` mapping can help resolve names, but its presence does not establish the contents of an exported `cmap`. When reporting a mismatch, state whether you inspected text bytes, source assignments, a name resource, a view collection or an exported table.

## Multiple assignments do not spell a ligature

One glyph can carry several codepoints as separate default mappings. A fictional space glyph might serve U+0020 SPACE and U+00A0 NO-BREAK SPACE. The shared drawing does not erase the distinction between those characters or their text behavior.

Assigning both U+0066 and U+0069 to one glyph would similarly make it a mapping candidate for either character individually. It would not express the sequence `fi`. A ligature rule instead operates on a glyph sequence during layout. An unencoded glyph such as `f_i` can be an intended substitution result without any direct assignment.

The inspected `fgGlyph.unicode` getter returns the first assignment or `None`; `fgGlyph.unicodes` exposes the list. Looking only at the first value can miss coverage. Their setters change data and call an owner update, so they do not belong in a reporting exercise. [FontGate glyph reference](https://code.fontlab.com/fontlab-python-docs/reference/fontgate/fgGlyph.html).

The current manual also treats **Generate Unicodes** as a modifying operation: it can replace or clear assignments and affect another glyph that carried a conflicting codepoint. Do not run it merely because an audit found an unencoded alternate. First establish whether the glyph should have a direct mapping at all.

## Report the assignments that are actually present

This original exercise uses a dictionary of fictional names and codepoint tuples. `A.backup` deliberately conflicts with `A` so the report can expose ambiguity. `f_i` has an empty tuple. No real font is read or changed.

```python
def assignment_rows(text: str, assignments: dict) -> list:
    rows = []
    for position, character in enumerate(text):
        codepoint = ord(character)
        names = []
        for name, codes in assignments.items():
            if codepoint in codes:
                names.append(name)
        if not names:
            status = "missing"
        elif len(names) == 1:
            status = "unique"
        else:
            status = "ambiguous"
        rows.append((position, codepoint, status, tuple(names)))
    return rows


assignments = {
    "f": (0x0066,),
    "i": (0x0069,),
    "space": (0x0020, 0x00A0),
    "A": (0x0041,),
    "acutecomb": (0x0301,),
    "A.backup": (0x0041,),
    "f_i": (),
}
text = "fi \u00A0A\u0301?"
print("Fictional Orchard / assignment candidates only")
for position, codepoint, status, names in assignment_rows(text, assignments):
    print(f"{position}: U+{codepoint:04X} {status} {names}")
```

The output is:

```text
Fictional Orchard / assignment candidates only
0: U+0066 unique ('f',)
1: U+0069 unique ('i',)
2: U+0020 unique ('space',)
3: U+00A0 unique ('space',)
4: U+0041 ambiguous ('A', 'A.backup')
5: U+0301 unique ('acutecomb',)
6: U+003F missing ()
```

`enumerate()` supplies each zero-based position and its string item. `ord()` returns that item's codepoint. The literal escapes `\u00A0` and `\u0301` make the no-break space and combining acute explicit in the source. Dictionary iteration preserves the inventory order, and the inner loop retains every matching name. [Python enumerate](https://docs.python.org/3.11/library/functions.html#enumerate); [ord](https://docs.python.org/3.11/library/functions.html#ord).

The `f` prefix inserts values inside braces. `04X` formats a number in uppercase hexadecimal, with at least four digits; it does not limit codepoints to four digits or validate their range. The printed names are tuples: `('f',)` contains one name, while `()` contains none.

The two space codepoints reach the same candidate independently. The `f` and `i` remain separate rows even though `f_i` exists. A's conflicting assignments both remain visible; the helper does not choose a winner. “Unique” means one assignment candidate in this inventory, not that the character is correctly rendered or that a language is supported.

Empty text produces no rows. An empty inventory makes every supplied item missing. Repeated characters retain their positions. The helper changes neither input and performs no normalization, substitution, positioning or fallback-font search. Its input contract expects a string and a dictionary of names to codepoint collections; it is not a general validator for imported Unicode data.

## Project: check a sample text against the current font

Before investigating layout, find out whether the font has stored assignments for the text you want to test. This report counts the sample's codepoints, collects their glyph owners and distinguishes missing, unique and shared assignments. It reads the whole stored glyph collection; the Font window's filter and selection do not set its scope.

The sample `AVATAR` contains six codepoints but only four distinct values. A occurs three times. A font might contain one glyph assigned to A, several glyphs sharing that assignment, or none. The report keeps **text occurrences** and **glyph owners** separate. It does not choose between competing owners or predict which glyph an exported font will use.

### Prepare the sample and understand the scan

Change only the `TEXT` string to choose a sample. Keep its quotes, and use Python escapes when needed: `"A\nB"` includes a newline codepoint, while `"A\u0301"` includes a combining acute. Every codepoint counts, including spaces, controls and combining marks. No normalization or text segmentation occurs.

The `occurrences` dictionary records how often each codepoint appears. `occurrences.get(codepoint, 0)` returns its current count, or zero when it has not appeared before. `owners` starts with an empty list for each requested codepoint. Dictionaries preserve insertion order, so detail rows follow each codepoint's first appearance in the sample. [Python dictionaries](https://docs.python.org/3.11/library/stdtypes.html#mapping-types-dict).

The glyph scan uses the same native metadata reads as [Chapter 6's encoding report](06-find-the-glyph-you-mean.md#project-find-unencoded-and-shared-assignments): `CurrentFont()`, `len(font)`, numeric lookup, `name` and `unicodes`. It needs no App, Fontport or shaping-library installation. It uses no layer, outline, metric or selection getter. `set(glyph.unicodes)` prevents a repeated assignment within one glyph from adding another owner; two separate glyph records remain two owners.

The three summary categories count **distinct sample codepoints**. Their totals add up to `Distinct text codepoints`; they need not add up to the length of the text or the number of glyphs. The line `unique = shared = missing = 0` initializes all three counters to zero. Each codepoint increments exactly one counter.

### Run the report

**This exact script has bounded native verification**, recorded below. The default `AVATAR` sample and no-font branch ran on the stated runtime. Metadata-only doubles cover additional cases; their results do not establish native behavior for those cases.

Use an owned font copy. Preserve existing editor work and start an empty script using [Chapter 4](04-work-in-the-scripting-panel.md). Enter only the complete script below, then run it in FontLab. Keep the document open and stable throughout. An external Python interpreter needs a test double for these checks; installing an ordinary Python package does not provide FontLab's native runtime.

```python title="Text assignment report: bounded native test recorded below"
import fontlab

TEXT = "AVATAR"
DETAIL_LIMIT = 8
OWNER_LIMIT = 3
LABEL_LIMIT = 80

phase = "sample text"
try:
    if not isinstance(TEXT, str):
        raise TypeError("TEXT must be a string")
    phase = "current font lookup"
    font = fontlab.CurrentFont()
    if font is None:
        lines = ["No current font. Open a font and run again."]
    elif not TEXT:
        lines = ["No sample text. Set TEXT and run again; font not scanned."]
    else:
        occurrences = {}
        owners = {}
        for character in TEXT:
            codepoint = ord(character)
            occurrences[codepoint] = occurrences.get(codepoint, 0) + 1
            owners[codepoint] = []

        phase = "glyph count"
        glyph_count = len(font)
        for glyph_index in range(glyph_count):
            phase = f"glyph {glyph_index} metadata"
            glyph = font[glyph_index]
            if glyph is None:
                raise RuntimeError(f"No glyph at index {glyph_index}")
            label = f"[{glyph_index}] {glyph.name!r}"
            if len(label) > LABEL_LIMIT:
                label = label[:LABEL_LIMIT - 3] + "..."
            for codepoint in set(glyph.unicodes):
                if codepoint in owners:
                    owners[codepoint].append(label)

        phase = "report formatting"
        unique = shared = missing = 0
        details = []
        for codepoint, labels in owners.items():
            if not labels:
                status = "unassigned"
                missing += 1
            elif len(labels) == 1:
                status = "unique"
                unique += 1
            else:
                status = "shared"
                shared += 1
            if len(details) < DETAIL_LIMIT:
                names = ", ".join(labels[:OWNER_LIMIT]) or "(none)"
                details.append(
                    f"  U+{codepoint:04X}: {status}; "
                    f"text occurrences: {occurrences[codepoint]}; "
                    f"glyph owners: {len(labels)}; {names}"
                )
        lines = [
            f"Text codepoints: {len(TEXT)}",
            f"Distinct text codepoints: {len(owners)}",
            f"Stored glyphs inspected: {glyph_count}",
            f"Assigned to one glyph: {unique}",
            f"Assigned to several glyphs: {shared}",
            f"Unassigned text codepoints: {missing}",
            "First 8 distinct codepoints (at most 3 glyph labels each):",
        ]
        lines.extend(details)
        lines.append("Assignment report complete; shaping was not tested.")
    output = "\n".join(lines)
except Exception as error:
    raise RuntimeError(f"Text assignment report incomplete during {phase}.") from error

print(output)
```

The `phase` string records what the script is trying to read or format. `try` groups that work; `except Exception as error` catches an ordinary failure and gives it report context. `raise ... from error` preserves the original exception as its cause, so the traceback contains both the underlying problem and the report phase. A failing glyph read therefore identifies its scan index without turning the failure into “no assignment”. [Python exception chaining](https://docs.python.org/3.11/tutorial/errors.html#exception-chaining).

The report text is complete before `print(output)` runs. Missing records, failed reads and formatting failures produce no partial totals or completion sentence. Import failure outside FontLab occurs before this handling; keyboard interrupts and native crashes are not converted into report results. Delivery of the final print to Output is also not an atomic transaction.

`lines.extend(details)` adds the prepared detail strings to the report. For each row, `", ".join(...)` joins at most three owner labels; `or "(none)"` supplies the visible empty case when joining an empty list produces an empty string. A label's index identifies the scanned position. `!r` quotes its name and escapes embedded newlines or tabs; labels longer than 80 characters are shortened. A shortened label is not a complete name to paste into a lookup.

Output has at most 16 lines: six totals, a heading, up to eight detail rows and completion. The occurrence and owner counts remain complete even when details are omitted. Only the displayed detail is bounded: reading time and memory still grow with the font and text.

### Interpret the tested result and its limits

On 13 November 2026, the exact default `AVATAR` script ran through `run_python` in FontLab 9.0.9809, build 9809, with embedded Python 3.11.6. With no font open, it printed only `No current font. Open a font and run again.` On a fresh owned copy of the GetGo CC0 GG Vize VFJ, opened as the sole font, it printed:

```text
Text codepoints: 6
Distinct text codepoints: 4
Stored glyphs inspected: 101
Assigned to one glyph: 4
Assigned to several glyphs: 0
Unassigned text codepoints: 0
First 8 distinct codepoints (at most 3 glyph labels each):
  U+0041: unique; text occurrences: 3; glyph owners: 1; [34] 'A'
  U+0056: unique; text occurrences: 1; glyph owners: 1; [55] 'V'
  U+0054: unique; text occurrences: 1; glyph owners: 1; [53] 'T'
  U+0052: unique; text occurrences: 1; glyph owners: 1; [51] 'R'
Assignment report complete; shaping was not tested.
```

An independent complete metadata list, obtained **after the report**, contained 101 glyphs. Reconstructing the output from that list matched the full stdout above, including the indices, order and occurrence counts. The before/after state probes read workspace, package and window state without glyph or layer getters. The package identity and path matched the owned copy, the measured dirty flag was `False`, and the current history-state value was `0` before and after. Source and copy hashes stayed unchanged. Only the identified owned copy was closed, without saving; the final open-font list was empty.

That first run covers the no-font branch and **one owned fixture with the unchanged default sample**. It does not establish every hidden-state invariant.

The A row has three text occurrences and one glyph owner. V, T and R each appear once. This inventory is compatible with beginning a shaping test; it does not establish kerning, substitutions, mark attachment or language support.

A second native run used the unchanged script and `AVATAR` sample on a separately created owned five-glyph font, in the same FontLab/Python versions. It reported **6 text occurrences, 4 distinct codepoints, 0 unique, 1 shared and 3 unassigned**. A appeared three times in the text and had two glyph owners: `[1] 'edgeA'` and `[2] 'edgeB'`. V, T and R each appeared once and had no assigned glyph. These are assignment observations, not automatic instructions to re-encode or delete glyphs.

The second fixture's complete independent inventory was identical before and after the report; reconstructing output from it matched the full stdout. The measured package identity remained stable, its unsaved path was empty, the dirty flag was `False`, and the current history-state value was `0` before and after. These baselines followed fixture creation, and the inventory had already been read. They do not establish the effects of creating glyphs or first-access behavior. Only that owned fixture was closed, without saving; the final font list was empty. No source or saved font file existed for it, so source/copy file hashes do not apply.

The fixture included `edgeZero` assigned U+0000, but `AVATAR` does not contain U+0000. This run therefore does **not** test U+0000 in sample text. Repeated entries within one glyph's assignment list, empty or invalid `TEXT`, supplementary-plane text, long labels, failures during scanning, a zero-glyph font and concurrent document changes remain untested natively for this report. Neither fixture run tests normalization, shaping, rendering, kerning, layout, native save/reopen or Scripting panel UI.

No current font produces only `No current font. Open a font and run again.` An empty `TEXT` string with a present font produces `No sample text. Set TEXT and run again; font not scanned.` A present font with zero stored glyphs and nonempty text would instead report all distinct sample codepoints unassigned. That last case is currently tested only with a double.

The bounded native checks above matched the exact script hash, compared complete metadata and measured before/after document state. Offline edge-case results remain separate from that acceptance. The script does not reserve the document, detect concurrent edits or establish native object lifetimes. Scripting panel UI behavior, hidden state, saved fonts and other runtimes remain unverified. Its result concerns stored assignments only; shaping still needs the context below.

## Shaping needs more than a mapping

A text run supplies context such as script, language, direction, enabled features and variation location. Initial mappings supply glyphs; **GSUB** data describes substitutions, while **GPOS** data describes positioning. Real engines can also normalize or reorder text during script-specific processing. This is a useful separation of tasks, not a promise of one fixed pipeline in every engine. [FontLab: Shaping Text](https://help.fontlab.com/fontlab/9/articles/shaping-text/index.html); [OpenType Layout](https://learn.microsoft.com/en-us/typography/opentype/spec/chapter2).

The feature source is a program describing layout behavior, not a list of encoded characters. A glyph name ending in `.ss01` does not enable a stylistic set by itself. A compiled rule also needs its input glyphs and the appropriate context. Required script behavior, such as joining or essential attachments, cannot be established by checking optional-feature labels alone.

Precomposed `Á` and the sequence `A` plus combining acute illustrate another limit. They are canonically equivalent text forms, but they contain different codepoint sequences. Our inventory reports precomposed U+00C1 as missing while separately finding U+0041 and U+0301. That difference in this elementary report does not predict the result of an actual shaping engine. Preserve the original inputs when comparing them; normalization is a separate operation with defined forms. [Unicode normalization](https://unicode.org/reports/tr15/).

A name lookup can prove that an alternate drawing exists. It cannot prove that a typed sequence reaches it. Similarly, character assignments do not establish mark attachment, kerning, joining or line-breaking behavior. Keep [Chapter 16's distinction between source, compilation and output](16-check-output-records.md) when testing features.

## Interpret preview results within their scope

The current App shaping helper builds a temporary font with empty outlines, selected mappings, advances and feature data. It can add temporary private-use mappings to address glyph names. This is a layout-preview mechanism, not a faithful exported copy or an instruction to assign private-use codes to a working font.

The helper can also retry compilation after discarding invalid feature text and return diagnostics. A result with `shaped=True` then means HarfBuzz ran; it does not prove every requested feature survived compilation. Without the optional shaping dependencies, its fallback reports `shaped=False`. Read diagnostics as well as the flag. [App shaping implementation](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/fontui/shaping.py).

The fallback's Fontport helper performs assignment lookup and pair/group kerning. Its source expressly distinguishes that placement from shaping. Right-to-left placement alone does not establish a full bidirectional text algorithm or a script's joining behavior. No helper was imported or executed here. [Fontport glyph placement](https://github.com/fontlabcom/fontlab-fontport/blob/c0ece90c8b8eaa7a1c6e8787d06294d147e29498/src/fontlab_fontport/glyphrun.py).

For a real shaping check, retain the exact input codepoints, font artifact, engine version and text-run settings. Record resulting glyphs, positions, clusters and diagnostics. Then test the separately exported font with its own glyph order. A mapping report, successful compilation, preview and exported-file result each supply different evidence.
