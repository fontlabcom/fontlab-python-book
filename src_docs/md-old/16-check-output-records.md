---
this_file: src_docs/md/16-check-output-records.md
---

# Check the names and code that reach the output

The editor says Bold. The exported font says Regular. To find the mismatch, identify which record you changed and which artifact you inspected.

This chapter compares fictional naming records and separates feature source from compiled layout. **Native metadata editing, feature compilation, export and save/reopen behavior remain unverified for this chapter.** The draft remains provisional pending independent review and semantic-map integration.

## Identify the naming record

A source filename, a family name and a style name serve different purposes. Renaming `OrchardSans-Bold.vfc` does not establish the internal names of an exported font. A family can also span separately stored source fonts; editing one does not automatically update the others. [FontLab manual: Naming Fonts and Families](https://help.fontlab.com/fontlab/9/articles/naming-fonts-and-families/index.html).

OpenType's `name` table stores strings in numbered categories. A **name ID** identifies a category of string; it is not a glyph ID.

| Name ID | Category |
| --- | --- |
| 1 | Font family name, used with ID 2 for the legacy family grouping |
| 2 | Font subfamily name, used for Regular, Italic, Bold and Bold Italic grouping |
| 4 | Full font name |
| 6 | PostScript name |
| 16 | Typographic family name |
| 17 | Typographic subfamily name |

The typographic names support families broader than a four-style group. Do not generate every name by joining two labels: each category has its own role and constraints. [OpenType naming IDs](https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids).

A name ID alone does not identify a particular record. The record also has a platform ID, encoding ID and language ID. Different language or platform records can contain different strings for the same name ID. Some metadata belongs to the family; other data belongs to a master or instance. Record that source scope separately when collecting values.

For this exercise, a tuple gives the key in this order:

**`(name_id, platform_id, encoding_id, language_id)`**

The fictional records use platform 3, encoding 1 and language 1033: one Windows Unicode BMP, US English combination. This choice is a fixture, not a rule for multilingual fonts. Other combinations and language-tag records need their own handling. [OpenType name records and platform-specific encoding/language IDs](https://learn.microsoft.com/en-us/typography/opentype/spec/name).

## Compare expectations with observations

The following dictionaries are invented. They are not read from FontLab or an exported font. We expect the typographic family `Orchard Sans`, style `Bold` and PostScript name `OrchardSans-Bold`. The fictional observations contain the correct family, the wrong style and no requested PostScript record.

`compare_names` is a book-defined function. It runs in external Python 3.11 and imports no library. Its inputs are dictionaries with four-integer tuple keys and string values. It returns a new list of report lines without changing either dictionary.

The loop follows the insertion order of `expected`. `key not in observed` tests whether the full key is absent. An empty string is still present and must be compared. The `!r` inside an f-string displays a value's Python representation, including quotes around strings; this makes an empty string visible as `''`. [Python dictionaries](https://docs.python.org/3.11/library/stdtypes.html#dict); [formatted string literals](https://docs.python.org/3.11/tutorial/inputoutput.html#formatted-string-literals).

```python
def compare_names(expected: dict, observed: dict) -> list[str]:
    lines = []
    for key, wanted in expected.items():
        if key not in observed:
            lines.append(f"{key}: missing; expected {wanted!r}")
        elif observed[key] == wanted:
            lines.append(f"{key}: matches")
        else:
            lines.append(
                f"{key}: differs; expected {wanted!r}, observed {observed[key]!r}"
            )
    return lines


expected = {
    (16, 3, 1, 1033): "Orchard Sans",
    (17, 3, 1, 1033): "Bold",
    (6, 3, 1, 1033): "OrchardSans-Bold",
}
observed = {
    (16, 3, 1, 1033): "Orchard Sans",
    (17, 3, 1, 1033): "Regular",
}

for line in compare_names(expected, observed):
    print(line)
```

The output is:

```text
(16, 3, 1, 1033): matches
(17, 3, 1, 1033): differs; expected 'Bold', observed 'Regular'
(6, 3, 1, 1033): missing; expected 'OrchardSans-Bold'
```

The complete key remains in each line. A German record with the same name ID would not satisfy the requested English key. An additional observed record is outside the requested comparison; an empty `expected` dictionary produces no lines.

This checks exact strings for requested keys. It does not parse a font, decode name-table bytes, detect duplicate records, validate style linking or decide which translations a family needs. A dictionary has already reduced each key to one value. Even three matches would certify only these comparisons, not the font's identity or readiness for release.

## Check whether a metadata edit persists

A field can be accepted by a Python validator yet lack a working persistent setter. In the inspected Fontport source, `openTypeNameRecords` has structural validation, but the native adapter refuses changes to it. Its reason is specific: the available setter changes regenerated style names rather than the persistent localized-name storage. The corresponding Font Info UI omits that field. [Fontport metadata validation](https://github.com/fontlabcom/fontlab-fontport/blob/main/src/fontlab_fontport/info.py); [native adapter](https://github.com/fontlabcom/fontlab-fontport/blob/main/src/fontlab_fontport/host.py); [Font Info UI](https://github.com/fontlabcom/fontlab-fontlabapp/blob/main/src/fontlabapp/fontui/fontinfo.py).

That is a boundary found in the inspected source, not a promise about an installed package release. Typing a value, applying it, reading it back and finding it in a reopened source are separate checks. Finding it in an exported binary is another. A successful readback from the open model cannot replace the last two.

## Separate feature source from compiled layout

OpenType feature source uses **FEA**, a language different from Python. It describes layout rules and can also specify some font-table data. For example, `sub a by a.ss01;` is a substitution statement, not a Python expression. It refers to existing glyphs; it does not draw an alternate `a`. This statement is illustrative and has not been compiled for this chapter. [Adobe OpenType Feature File Specification](https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html).

Keep these stages separate:

| Stage | What has happened |
| --- | --- |
| Store source | Feature text is present in the editing model |
| Compile a candidate | A compiler has processed source and produced candidate layout data or diagnostics |
| Apply compiled layout | The open model has received the compiled result |
| Save source | A native project file has been written |
| Export a font | An output font has been produced using an export configuration |

The inspected feature editor's Apply path stores and reads back code, then reports that the code is **not compiled**. Its optional callback is a separate action. Text readback and checks on feature-block names do not prove valid FEA or working substitutions. [Feature editor source](https://github.com/fontlabcom/fontlab-fontlabapp/blob/main/src/fontlabapp/fontui/features.py); [native feature storage](https://github.com/fontlabcom/fontlab-fontport/blob/main/src/fontlab_fontport/native_features.py).

The inspected native implementation can also compile a candidate to validate edited text without applying its tables. Another operation applies compiled layout and calls that state `published`. In that source, the word means applied to the open font model; it does not mean uploaded or written to an exported binary. These are source findings, not instructions to call an installed native API.

FontLab's Features and Lookups workflows also require attention to which layout document is active. Displaying `a.ss01` directly proves that the glyph can be shown; it does not test whether ordinary `a` is substituted with the intended script, language and feature settings. [FontLab manual: The Features Panel](https://help.fontlab.com/fontlab/9/articles/the-features-panel/index.html).

## Inspect the artifact you intend to deliver

A native source preserves editing information that an exported font may not contain. Export configuration can affect outlines, names and generated layout. Reopening an export reconstructs supported data; it does not recover every detail of the original source. [FontLab manual: The Export Process](https://help.fontlab.com/fontlab/9/articles/the-export-process/index.html).

An adapter can have a narrower contract still. Fontport's inspected geometry-subset exporter deliberately writes selected geometry, limited metadata and a fixed Regular style. It omits source feature programs. Its later external TrueType compilation cannot recover those omitted programs. An export helper's name does not establish whole-font preservation. [Fontport export source](https://github.com/fontlabcom/fontlab-fontport/blob/main/src/fontlab_fontport/export.py).

Before a native editing recipe can be trusted, identify the installed build, source file, master or instance and intended output. Verify edits in a saved and reopened disposable source. Inspect naming records and layout tables in the actual exported file. Test ordinary text in the target application with the intended feature settings, including text that should remain unchanged. Check compiler errors and warnings, Undo/Redo and partial failures separately. The Python comparison above establishes none of those native results.
