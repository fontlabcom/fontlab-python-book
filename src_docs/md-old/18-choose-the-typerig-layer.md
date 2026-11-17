---
this_file: src_docs/md/18-choose-the-typerig-layer.md
---

# Choose the TypeRig layer before copying an example

A TypeRig example can calculate a point in ordinary Python, wrap a live FontLab node or open a panel. Those actions have different requirements. The shared project name does not make them interchangeable.

TypeRig is Vassil Kateliev's framework for font design and engineering. It adds geometry, host wrappers and tools around the application's own interfaces. It is separate from FontLab's built-in `fontlab`, `fontgate` and `PythonQt` modules. The earlier plain-Python exercises do not require it. [TypeRig source](https://github.com/kateliev/TypeRig/tree/02118fdcce9263b272d1f0533680f46d57c498ef).

This chapter maps inspected source and uses a fictional requirements inventory. **No TypeRig package installation, native proxy operation or GUI behavior was tested for this chapter.** The draft remains provisional pending independent review and semantic-map integration.

## Keep the source generation visible

The local checkout inspected for this chapter was at commit `960d25f`. On 13 November 2026, a remote check found upstream `master` at `02118fdc`, twelve commits later. Both were inspected; the source links in this chapter pin the latter revision. Neither commit identifies whatever package may already be installed in a reader's environment.

The newer README adds consequential limits: FontLab 8 is the main target; FontLab 9 has not been tested systematically; some recent panels have seen little use; and some tools do not record Undo correctly. It names Element → Flip as a case that remains flipped after Undo. These are the author's reported limits, not a native result reproduced here. [TypeRig status at the inspected revision](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/README.md#status).

Older references can still explain the design. The repository's proxy reference describes FontLab 6 objects, for example. Read its terminology alongside the current implementation; do not turn a historical host name into a present compatibility guarantee. [Proxy reference](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Docs/Proxy/Documents/Proxy-API-Doc.md).

## Locate the work in the architecture

An import path tells you which part of the package a name comes from. It does not establish that importing or using that part is passive.

| Area | Role in the inspected source |
| --- | --- |
| `typerig.core.objects` | Python geometry and containers, such as points, contours and layers |
| `typerig.core.func` and `core.algo` | Calculation helpers and algorithms |
| `typerig.core.fileio` | File-format readers and writers, with format-specific dependencies |
| `typerig.proxy.fl` | FontLab object wrappers, actions and GUI helpers |
| `typerig.proxy.gs3` | Glyphs-facing wrappers and tools |
| `Scripts/` | Host scripts, including panel and manager entry points |

Much of the geometry core can work without an editor. That does not mean every core module has no dependencies: the inspected README distinguishes geometry from consumers of fontTools, including direct requirements in UFO and designspace file I/O. The `gs3` branch imports `GlyphsApp`; its presence is not evidence that those imports work in FontLab. [Architecture](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/README.md#architecture); [Glyphs proxy source](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Lib/typerig/proxy/gs3/objects/glyph.py).

TypeRig, Fontport, Glyport and FontLab App provide different interfaces. TypeRig's inspected package metadata directly requires fontTools; it does not declare those three packages as a mandatory chain. A familiar word such as glyph or layer does not make objects from different libraries interchangeable. [Package metadata](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/pyproject.toml).

## Distinguish owned coordinates from a live wrapper

Compare these two names as source-reading examples:

- `typerig.core.objects.point.Point` stores Python coordinates. Its addition operation creates another Point. Other operations can still change a core object; it is not necessarily immutable.
- `typerig.proxy.fl.objects.node.pNode` retains a supplied native `flNode`. Its `x` and `y` setters assign directly to that wrapped node.

Changing a live wrapper's coordinate is therefore different from calculating a new independent point. There is no separate “apply this preview” step implied by those setters. These are source observations; no assignment to a native node is prescribed here. [Point source](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Lib/typerig/core/objects/point.py); [pNode source](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Lib/typerig/proxy/fl/objects/node.py).

The inspected `pGlyph` combines FontGate and FontLab interfaces through members such as `.fg`, `.fl` and `.parent`. Its no-argument constructor obtains the current font and glyph. That branch does not explicitly guard an absent current font or glyph. A convenient constructor should not be assumed to handle every empty-window state safely. Nor does a returned Python list detach the native nodes it contains. [pGlyph source](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Lib/typerig/proxy/fl/objects/glyph.py).

The same file's `update()` notifies contours of changes. Its `updateObject()` also refreshes master layers, requests a history notification and calls `UpdateAll()`. Those calls show what the wrapper requests. They do not prove complete Undo, atomic edits or saved-file persistence. [Chapter 17](17-test-the-promise.md) explains how to test those separate promises.

## Separate the library from a launcher

The inspected wheel configuration packages `Lib/typerig`; the source-distribution list also excludes `Scripts/`. A library installation therefore does not itself deploy the panel scripts. The package also declares a separate `tr-kern` console entry point. Its subcommands dispatch different operations; a console tool is not automatically read-only. [Packaging configuration](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/pyproject.toml); [console entry point](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Lib/typerig/core/actions/kern_cli.py).

The panel script imports FontLab and PythonQt, initializes workspace/UI resources and constructs its panel at module scope. Its panel package imports sibling modules. Importing an entry script to “see whether it works” can therefore start UI activity. [Panel entry point](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Scripts/TypeRig%20GUI/typerig-panel.py); [panel module loading](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Scripts/TypeRig%20GUI/Panel/__init__.py).

Legacy installers are operations too. The inspected `install.py` writes a `.pth` link to a library checkout when run. The native installer offers linking and copying; its copy routine can remove an existing destination tree. These files are not harmless diagnostics, and their presence does not establish a verified installation procedure for the current host. [Link installer source](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/install.py); [native installer source](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/install.vfpy).

## Compare a fictional requirements inventory

The following exercise imports no package and runs in external Python 3.11. Its names and requirements are invented examples, not a TypeRig support matrix. The `available` list records what someone has written down; the program does not discover installed packages or query FontLab.

For each example, `requirement_report` lists requirements absent from that inventory. If the requirements are `None` or an empty list, it reports missing information instead of declaring readiness. Even when every label is present, compatibility remains untested. The inputs must have the shown keys and string labels; this small helper does not validate arbitrary records.

```python
def requirement_report(examples: list[dict], available: list[str]) -> list[str]:
    lines = []
    for example in examples:
        name = example["name"]
        required = example["requires"]
        if not required:
            lines.append(f"{name}: requirements not recorded")
            continue
        missing = []
        for requirement in required:
            if requirement not in available:
                missing.append(requirement)
        if missing:
            labels = ", ".join(missing)
            lines.append(f"{name}: missing from inventory: {labels}")
        else:
            lines.append(f"{name}: listed requirements present; compatibility untested")
    return lines


examples = [
    {"name": "Coordinate sketch", "requires": ["external Python"]},
    {"name": "Host inspection", "requires": ["FontLab", "PythonQt"]},
    {"name": "Unreviewed tool", "requires": None},
]
available = ["external Python"]

for line in requirement_report(examples, available):
    print(line)
```

The output is:

```text
Coordinate sketch: listed requirements present; compatibility untested
Host inspection: missing from inventory: FontLab, PythonQt
Unreviewed tool: requirements not recorded
```

Here `continue` moves to the next example after reporting missing information. `", ".join(missing)` combines the missing labels with commas and spaces, as introduced in [Chapter 9](09-report-selected-glyphs.md). The helper preserves input order and does not change the records. Label matching is exact: `FontLab` and `fontlab` are different strings. Neither a label match nor this report authorizes importing or running the named tool.

## Record which version you actually have

On 13 November 2026, the PyPI metadata endpoint reported TypeRig **3.0.0**, with Python `>=3.10` and `fonttools>=4`. That establishes a registry metadata observation. No release artifact was downloaded, installed or tested for this chapter. [TypeRig registry metadata](https://pypi.org/pypi/typerig/json).

Module-local version strings, distribution versions and source commits are different identifiers. In the inspected source, the core and FontLab proxy have their own version strings; the root package's apparent version assignment is inside a historical text block. Do not assume `typerig.__version__` identifies the installed distribution. [Root module](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/Lib/typerig/__init__.py).

Even license metadata differs between the observed registry release and newer source. Check the license and notices belonging to the exact version you use; do not combine metadata from one release with code from another. [Pinned source license](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/LICENSE); [pinned source notices](https://github.com/kateliev/TypeRig/blob/02118fdcce9263b272d1f0533680f46d57c498ef/NOTICE).

Before relying on a native TypeRig operation, identify its loaded source, host build and interpreter, then test the specific operation on an owned fixture. Verify object lifetime, target layer, UI behavior, Undo/Redo and saved/reopened results as appropriate. A passing standalone Point test or an installed library cannot establish those host results.
