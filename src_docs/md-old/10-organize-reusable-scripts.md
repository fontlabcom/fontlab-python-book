---
this_file: src_docs/md/10-organize-reusable-scripts.md
---

# Keep reusable code separate from its launcher

A report becomes easier to reuse when its formatting code accepts data and returns text. A separate **launcher** supplies the data and decides when to print the result. Another launcher can then use the same formatter without copying it.

This chapter builds that arrangement with two files and fictional glyph records. **The exercise runs in external Python 3.11, outside FontLab.** It imports no FontLab package and changes no font. Native installation and menu behavior remain unverified; this draft also awaits semantic-map integration and independent review.

## Know which Python runs the file

FontLab's embedded Python runs inside the application, with its native bindings and existing Qt application. A Python interpreter started from a terminal is a separate runtime. Installing a dependency for one does not establish that the other can find or use it. The inspected FontLab documentation targets embedded Python 3.11; its documentation-building environment is separate. [FontLab scripting guide: Install and connect](https://fontlabcom.github.io/fontlab-python-docs/guide/install.html).

For the exercise, use an available external Python 3.11 interpreter. The commands below assume its command is `python3.11`. Check that command's version before running the files; if it is unavailable, use the path to your external Python 3.11 interpreter. This chapter does not provision an interpreter or modify FontLab's Python environment.

## Make a two-file project

A Python **module** can be a `.py` file containing definitions and statements. An import makes its definitions available to another file. Keep this exercise in a new folder of your own, outside FontLab's Scripts and Extensions folders. [Python tutorial: Modules](https://docs.python.org/3.11/tutorial/modules.html).

Create this layout:

```text
report_demo/
    orchard_report.py
    run_report.py
```

Save the following helper as `orchard_report.py`. `glyph_lines` returns a complete list of report lines. It preserves the supplied record order and does not print, select glyphs or read a current font. The formatting expressions were introduced in the [selection-reporting chapter](09-report-selected-glyphs.md).

```python
# this_file: report_demo/orchard_report.py
"""Format fictional glyph records without accessing an application."""


def glyph_lines(records: list[dict]) -> list[str]:
    lines = [f"Supplied glyph records: {len(records)}"]
    for record in records:
        labels = [f"U+{value:04X}" for value in record["unicodes"]]
        assignments = " ".join(labels) if labels else "unencoded"
        lines.append(f"{record['name']} | {assignments}")
    return lines
```

The launcher uses `from orchard_report import glyph_lines` to make that function available under its name. The import names the module without the `.py` suffix. Its `main()` function supplies three fictional records and prints the returned lines.

The final `if __name__ == "__main__":` is a **main guard**. When external Python executes this file as the starting script, it sets `__name__` to `"__main__"` and the guard calls `main()`. When another script imports `run_report`, the name is `"run_report"`, so this call is skipped. The import still executes the file-level import and function definition. [Python reference: The main guard](https://docs.python.org/3.11/library/__main__.html#name-main).

Save this second file as `run_report.py` in the same folder:

```python
# this_file: report_demo/run_report.py
"""Print a report from owned sample data in external Python."""

from orchard_report import glyph_lines


def main() -> None:
    records = [
        {"name": "A", "unicodes": [0x0041]},
        {"name": "A.alt", "unicodes": []},
        {"name": "smile", "unicodes": [0x1F600]},
    ]
    for line in glyph_lines(records):
        print(line)


if __name__ == "__main__":
    main()
```

In a terminal with `report_demo` as its current directory, first check the interpreter, then run the launcher:

```sh
python3.11 --version
python3.11 run_report.py
```

The version command should report Python 3.11 with its patch version. The launcher should print:

```text
Supplied glyph records: 3
A | U+0041
A.alt | unencoded
smile | U+1F600
```

The count means supplied records, not distinct glyph identities or selected cells. Repeated records remain repeated. With an empty `records` list, the report contains only `Supplied glyph records: 0`. As in Chapter 9, an empty Unicode list means unencoded; a missing required key is an error. Building all lines before printing prevents a late missing key from leaving a partial report that looks complete.

## Understand imports before moving the files

For an ordinary `python3.11 run_report.py` invocation, Python places the script's directory on its module search path. That lets the launcher find `orchard_report.py` beside it. This exercise does not alter `sys.path`. Embedded hosts and interpreter options can use different search paths, so copying this layout into FontLab is a separate test. [Python reference: sys.path](https://docs.python.org/3.11/library/sys.html#sys.path).

If the launcher cannot find `orchard_report`, check the interpreter, filename and folder first. Keep the helper beside the launcher for this exercise. Do not respond by installing an unrelated package with a similar name. A project file named after another module can also hide the module you intended to import, so use distinctive names such as `orchard_report`.

Imports execute module-level statements when the module is first loaded. Later imports normally use the same module object from Python's cache. Saving an edited file does not by itself replace an already imported module. Each terminal run above starts a new interpreter process; this is not a claim that FontLab's Run button starts a new process or clears imports. [Python reference: The module cache](https://docs.python.org/3.11/reference/import.html#the-module-cache).

To test the main guard, run this command from the same folder:

```sh
python3.11 -c "import orchard_report; import run_report"
```

Here `-c` runs the quoted Python statements. The command should finish without printing a report. Both modules are loaded, but neither calls the formatter or launcher at import time. This result applies to these two files; a main guard does not prevent other imported modules from performing actions.

## Read the launcher and the code it calls

The inspected example repositories show several ways to separate an entry point from shared code. These are observations of source layouts, not proof that a particular released or installed package contains them.

| Source | Entry point and shared code |
| --- | --- |
| `fontlab-python-examples` | `Scripts/Models/Glyph Name Filter.py` imports `launch` from `fontlab_python_lessons`. The Lessons package contains the implementation and delays its native helper imports until `launch` is called. |
| `fontlab-python-scriptmix` | `Scripts/Font UI Lab/Detached Transform Preview.py` defines `main`, imports its Fly/App helpers inside that function and calls it under a main guard. |
| `fontlab-python-plugmix` | `Extensions/reporters/NodeIndexes.fontlabReporter/` contains `node_indexes.py` and a `plugin.json` manifest: data identifying the plugin and its entry point. App's plugin loader reads the manifest's `node_indexes:NodeIndexes` entry to locate the `NodeIndexes` class, the Python definition of this plugin. |

The Examples root project configures documentation tools; its Lessons subproject defines the runtime project named `fontlab-python-lessons`. Scriptmix is a menu collection, not an importable runtime package supplied by its root project. Its menus depend on shared packages. The repository name, name used for installation and name used in an import can therefore differ. [Examples repository](https://github.com/fontlabcom/fontlab-python-examples); [Scriptmix repository](https://github.com/fontlabcom/fontlab-python-scriptmix).

Read a script's opening documentation and the function it calls before choosing it as a model. Some examples change fonts, selection or application state. Even an import can act: the inspected `Scripts/Plugmix/Show Reporters.py` calls `show_reporters()` at file level. It is an action script, not a helper library to import for definitions.

## Keep menu files, packages and extensions distinct

The inspected Examples and Scriptmix instructions use the menu-file layout `Scripts/<Category>/<Tool>.py`, with one category level. Shared runtime packages live separately. Moving only a launcher does not supply its imported dependencies. When an existing FontLab script needs review in the Scripting panel, follow the [panel chapter's preservation and Run procedure](04-work-in-the-scripting-panel.md), including the check that only the intended code is present.

In the inspected current Plugmix source, an **extension bundle** groups a manifest and implementation files beneath a kind folder such as `Extensions/reporters/`. App's `plugins/bundles.py` validates it, imports the declared class and checks its identity. A reporter is registered for **callbacks**: functions the host calls when it needs the plugin to respond, rather than a report printed once by a launcher. Bundle discovery and import can execute Python code; neither is passive file inspection.

Plugmix also retains a separate compatibility package, `fontlab_plugmix`. Its Python package build includes that compatibility code, while the extension pack is built separately. Some documentation still describes the compatibility startup route. Identify which layout a source example belongs to before using its instructions; this chapter does not combine their startup or installation procedures.

Before installing a real tool, establish its intended interpreter, required helper packages, exact artifact or source revision, entry point and verified behavior. For native tools, successful import is only one check: menu placement, callbacks, window lifetime, selection preservation and any promised editing behavior need their own FontLab tests. No installer, startup hook or example from the inspected repositories was run for this chapter. Only the fictional two-file project was executed externally under Python 3.11.
