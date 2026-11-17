---
this_file: src_docs/md/21-make-the-report-reproducible.md
---

# Make the report reproducible

A glyph report needs more than correct numbers. A reader must know which font and master supplied them, how missing values were represented and whether the file contains the same data that the script displayed. These choices determine what another person can reproduce.

This chapter uses source inspected on 13 November 2026 and current Python 3.11 documentation. **The exercise creates JSON and CSV text in memory; it writes no files and reads no FontLab document.** Native capture, filesystem failure handling and exported-font behavior were not tested for this chapter. The draft remains provisional pending independent review and semantic-map integration.

## Give each path a purpose

A **path** identifies a location. A relative path depends on the running process's current working directory; it does not automatically refer to the script's folder or the open font's folder. This chapter does not establish FontLab's working directory in any particular launch route.

Keep four locations distinct: the script's resources, the editable font source, the application's user-data folder and the chosen report destination. App's inspected `ApplicationPaths` obtains system locations through Qt and FontLab-specific locations through preferences. It exposes default user data, current user data and autosave paths separately. No single hardcoded directory represents them all. Reading a path also does not establish ownership of every file below it. [App path source](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/core/application/paths.py).

Python's `Path` joins path components, but joining is not filename validation: an absolute component can replace an earlier base. `is_relative_to` compares path structure without resolving the filesystem or treating `..` specially. `resolve` follows symbolic links; it does not grant permission to write. A **symbolic link** redirects a path to another location. An absolute output path can still pass through linked parent directories. [Python pathlib](https://docs.python.org/3.11/library/pathlib.html).

For an actual report writer, choose the destination deliberately and state what may be replaced. Avoid deriving an unrestricted filesystem path directly from a glyph name or other report text. The in-memory exercise below needs no destination.

## Read the writer's contract

The inspected projects use different file-writing rules:

| Writer | Source behavior |
| --- | --- |
| App Font Info Snapshot `export_new` | Requires an absolute path and opens a new UTF-8 text file with mode `x` |
| Scriptmix Glyph Table CSV `write_csv` | Uses `Path.write_text`, with UTF-8 BOM and explicit newline handling |
| App kerning-pair `export_csv` | Opens mode `w`, with UTF-8 and no BOM |

A **BOM**, or byte-order mark, is an encoding marker at the start of a file. These source choices affect bytes even when the visible text looks the same. The two CSV writers can replace existing file contents; a report being read-only with respect to the font does not make its output-file operation read-only. [Naming snapshot writer](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/fontui/teaching_writers/font_info_snapshot.py); [glyph CSV writer](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/2916208361336d88a93fc1c8407e4fb22aa12056/Scripts/Reports/Glyph%20Table%20CSV.py); [kerning CSV writer](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/studios/kerning_browser/pairs.py).

Python's mode `x` requests exclusive creation and fails if the destination already exists. Mode `w` truncates an existing file. Checking that a path does not exist before opening it does not reserve it. Exclusive creation also does not promise complete output after a later write failure, or control every parent directory. These distinctions explain the source; they are not an instruction to test a writer on a user's files. [Python open modes](https://docs.python.org/3.11/library/functions.html#open).

## Preserve the meaning of missing data

**JSON** represents named fields, arrays, numbers, text, Booleans and `null`. A report can include a schema version, font identity, master, units and the observations together. A **schema** states which fields and value types the report expects.

**CSV** represents rows and columns. Python's ordinary CSV reader returns strings. Its writer converts `None` to an empty field, which loses the distinction between missing data and an empty string unless the report supplies another convention. A separate status column can preserve that distinction. Use the CSV writer's quoting rules for commas, quotes and embedded newlines; manually joining fields with commas does not provide those rules. [Python CSV reference](https://docs.python.org/3.11/library/csv.html).

A real snapshot must also disclose its scope. App's inspected naming snapshot stores schema version 2, one master name and a fixed set of naming fields. It does not store a complete font. Its importer rejects duplicate JSON keys and reports UTF-8 BOM removal and carriage-return normalization. That can preserve the intended field values while changing the original byte representation. Those are this tool's conversion rules, not rules for every FontLab JSON file. [Snapshot schema and reader](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/fontui/teaching_writers/font_info_snapshot.py).

Capture ordinary numbers and strings with an explicit font, layer and selection scope. Native wrappers are not automatically detached report values, and reading them can prepare native data, as [Chapter 7](07-choose-the-drawing.md) explains. A serializer cannot settle that native-state question.

## Render one fictional report in two formats

The example runs in external Python 3.11 and imports only `csv`, `io` and `json`. `StringIO` is a text stream held in memory. The returned strings are not saved artifacts.

The input is an ordered list of dictionaries with exactly two fields: `label` is text; `width` is a finite number or `None`. The labels are invented observations, not a native glyph-naming rule. Zero is a recorded width; `None` means the width was not recorded. This small helper expects that input structure and leaves missing fields visible as errors.

`json.dumps` returns text. Here `ensure_ascii=False` keeps non-ASCII characters visible, `allow_nan=False` rejects non-finite numbers, and `sort_keys=True` orders object keys. It does not sort the observations. CSV uses fixed columns and a line-feed terminator. [Python JSON options](https://docs.python.org/3.11/library/json.html#json.dumps).

```python
import csv
import io
import json


def render_report(records: list[dict]) -> tuple[str, str]:
    report = {
        "schema": 1,
        "font": "Fictional Orchard",
        "master": "Regular",
        "units": "font units",
        "records": records,
    }
    json_text = json.dumps(
        report, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
    ) + "\n"
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["label", "width", "status"])
    for record in records:
        width = record["width"]
        if width is None:
            writer.writerow([record["label"], "", "missing"])
        else:
            writer.writerow([record["label"], width, "present"])
    return json_text, buffer.getvalue()


records = [
    {"label": "A, alternate", "width": 0},
    {"label": "é sample", "width": None},
]
json_text, csv_text = render_report(records)
print("JSON")
print(json_text, end="")
print("CSV")
print(csv_text, end="")
```

The output is:

```text
JSON
{
  "font": "Fictional Orchard",
  "master": "Regular",
  "records": [
    {
      "label": "A, alternate",
      "width": 0
    },
    {
      "label": "é sample",
      "width": null
    }
  ],
  "schema": 1,
  "units": "font units"
}
CSV
label,width,status
"A, alternate",0,present
é sample,,missing
```

The CSV writer quotes the comma-containing label so it stays one field. The `status` column distinguishes the missing width from zero. JSON retains the distinction directly as `null` versus `0`. The CSV table contains only observation columns; its font, master and units must travel with it separately. This example does not claim the table is a self-contained equivalent of the JSON document.

The assignment unpacks the returned pair into `json_text` and `csv_text`. `buffer.getvalue()` retrieves the accumulated CSV text. In the print calls, `end=""` suppresses an extra newline because each report already ends with one. Empty records still produce the JSON scope and an empty records array, plus the CSV header.

The helper reports on its input; it does not validate a font. A non-finite number raises `ValueError` during JSON encoding. A missing required record field raises `KeyError`. No partial file is created because there is no file operation.

## Decide which kind of equality matters

The same JSON values can be written with different spacing, key order or Unicode escapes. Parsing can recover equal data even when UTF-8 bytes differ. Conversely, matching hashes show a match to recorded bytes, not that the report captured the intended master or included every glyph. [Chapter 20](20-share-the-files-and-conditions.md) shows a byte-digest comparison.

For reproducible report bytes, record the input scope and order, schema, encoding, BOM policy, formatting and line endings. This exercise retains record order and makes formatting explicit. It does not define a universal canonical JSON format. A timestamp or machine-specific absolute path can vary between runs, so decide whether it belongs in the compared report or in separate provenance records.

For reproducible meaning, also establish what the fields measure. A report generated twice from a changing open font does not have identical input merely because the same script ran.

## Keep report files separate from font exports

The inspected GetGo TTF/OTF examples create a four-glyph geometry subset from one default master. Their source explicitly omits native hints, features, kerning, axes and other layers. The implementation reopens the binary through fontTools to check selected tables, mappings, metrics and outline properties. That readback is different from saving and reopening the editable source in FontLab. None of those export operations ran for this chapter. [Subset construction and verification](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/lessons/src/fontlab_python_lessons/getgo/_binary.py).

A JSON report, an exported subset and the editable font source therefore have different preservation limits. A `.ttf` suffix alone cannot prove a valid or complete font, just as a `.json` suffix cannot prove the report's schema or scope.

## Check every member of an output set

One report may have several files: data, metadata, images or a manifest listing them. The inspected GrabLab publisher links staged members into place one at a time. If an exception is caught, it removes the members it recorded as published. That code does not establish an all-or-nothing result after process termination. The first visible image is not proof that its accompanying JSON or UI file was delivered. [Bundle publisher](https://github.com/fontlabcom/fontlab-grablab/blob/40bd2bd62b21fa8cf0bf29d70666f8bc4c638f63/src/grablab/grab.py).

Python documents atomicity for a successful `os.replace` rename, which can replace an existing destination. That single operation does not make a series of file writes or renames atomic. It also differs from GrabLab's hard-link publication above. [Python os.replace](https://docs.python.org/3.11/library/os.html#os.replace).

Record the expected members, inspect the actual files and compare their recorded digests before describing an output set as complete. Then apply the separate checks its purpose requires: parse report data, inspect capture contents or reopen an exported font. Serialization tests establish the text transformation; they do not establish filesystem recovery, native preservation or a usable backup.
