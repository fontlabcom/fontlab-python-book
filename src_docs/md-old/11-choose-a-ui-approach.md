---
this_file: src_docs/md/11-choose-a-ui-approach.md
---

# Choose the host before choosing the UI

A button can call the report function you already wrote. The extra work is deciding who owns that button, when its callback runs and how the window closes.

This chapter compares UI approaches found in the inspected FontLab sources. Its only executable example prepares text in ordinary Python 3.11. **No native UI behavior was tested for this chapter.** The draft remains provisional pending independent review and semantic-map integration.

## Separate the control from the work

A **user interface**, or UI, presents information and accepts input. A **control** is an element such as a button or text field. A **callback** is a function invoked in response to an event, such as a button click. An **event loop** dispatches events while an application runs.

Keep the useful work in an ordinary function, as in the [reusable-script chapter](10-organize-reusable-scripts.md). A future callback could read a text field, pass that text to the function, then show its result. Each of those UI operations still needs the correct binding and host.

A **binding** exposes a framework's objects to Python. PythonQt and PySide expose Qt through different bindings. An **adapter** translates a supported part of one interface to another; sharing a class name does not establish identical arguments, results or ownership.

## Identify the runtime

Qt's external PySide6 tutorial creates a `QApplication` and calls `app.exec()` to run its own event loop. That is the structure of a standalone application. [Qt for Python: First QtWidgets application](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/widgets.html).

The inspected FontLab UI guide instead targets embedded PythonQt and FontLab's existing Qt application. It explicitly excludes creating another `QApplication`, starting an application-wide event loop or loading PySide/PyQt binaries inside FontLab. Its examples and source describe a host contract; they do not establish the configuration or behavior of your installed build. [FontLab scripting guide: UI](https://fontlabcom.github.io/fontlab-python-docs/guide/ui.html).

Use these distinctions when reading an example:

| Approach | What the inspected sources describe | What remains separate |
| --- | --- | --- |
| Embedded PythonQt | Access to the Qt objects supplied by FontLab; App helpers organize native panels and their cleanup. | Actual constructors, callbacks and window lifetime in the installed host. |
| `pythonqtside` | Native namespace routing and specific adaptations for PySide2-style code. | Full PySide2 compatibility; PySide6/Qt6 support is outside its stated scope. |
| Glyport's Vanilla adapter | Supported Vanilla-style controls implemented with Qt, under an owned session. | The original Cocoa library, complete Vanilla coverage and arbitrary Cocoa/Qt mixing. |
| External PySide6 | A separate application with its own Qt runtime and event loop. | Embedded PythonQt behavior and access to FontLab's native objects. |

The relevant FontLab documentation describes a FontLab 9, Python 3.11 and Qt 5 target. This chapter has not queried the installed application. An external test with PySide6 cannot establish which Qt version or binding is present inside FontLab.

## Treat compatibility as a set of specific behaviors

In the inspected `pythonqtside` source, a namespace lookup such as `QtWidgets.QWidget` returns the routed native class. The separate `compat.pyside_method` and `compat.pyside_construct` helpers adapt selected calls. The `run_app` route executes supported source through an adaptation context and requires the host's existing application. These names identify source routes here; they are not instructions to launch an unverified tool.

This distinction matters for property access. A value exposed as `widget.width` in the captured PythonQt interface may appear as `widget.width()` in a PySide example. A matching class name or changed import line does not resolve that difference. The inspected compatibility guide also treats keyword arguments, signal arguments, result tuples and object lifetime separately. [FontLab UI guide](https://fontlabcom.github.io/fontlab-python-docs/guide/ui.html); [Pythonqtside source and compatibility guide](https://github.com/fontlabcom/pythonqtside).

Source details can be narrower than a summary page. For example, the inspected file-picker adapter rejects a `selectedFilter` keyword, while the general package page describes dropping it. A chooser also introduces settings and lifetime behavior beyond displaying a label. This chapter uses neither interpretation as a runnable chooser recipe; consult the matching implementation and verify the exact installed contract before using it.

## Distinguish the two Vanilla implementations

RoboTools Vanilla is a Python wrapper around Cocoa. Glyport's Vanilla-style UI is a separate compatibility implementation using Qt. A familiar control name does not make their underlying objects interchangeable. [RoboTools Vanilla](https://github.com/robotools/vanilla).

The inspected Glyport source places `VanillaSession` in `fontlab_glyport.ui.session`. Its constructor creates the supported UI namespaces and tracks their windows. The older App module, `fontlabapp.core.legacy.vanilla`, is retained only to report the move: asking it for `VanillaSession` raises an import error. This is a source-location finding, not a verified installed-package migration procedure.

The adapter supports an explicit set of controls and options. In its inspected implementation, `getNSView()` returns the underlying Qt widget as a compatibility handle; its name does not promise a Cocoa `NSView`. Callback and programmatic-setter behavior also have documented exceptions. Use the matching compatibility guide for the particular control rather than assuming every upstream Vanilla example is supported. [Glyport source](https://github.com/fontlabcom/fontlab-glyport); [Vanilla's original control documentation](https://vanilla.robotools.dev/en/latest/).

## Prepare preview text without opening a window

Suppose a future tool has a text field for glyph names and a Preview button. First define what its preview should say. This exercise treats each whitespace-separated item as a supplied name; it does not validate names or look them up in a font.

`text.split()` with no separator splits at whitespace, including repeated spaces, tabs and newlines. `names[:PREVIEW_LIMIT]` is a **slice** containing up to the first three items. `"\n".join(lines)` places a newline between the prepared lines. The constant `PREVIEW_LIMIT` names this exercise's display limit. [Python reference: String splitting](https://docs.python.org/3.11/library/stdtypes.html#str.split) and [sequence slicing](https://docs.python.org/3.11/library/stdtypes.html#common-sequence-operations).

```python
PREVIEW_LIMIT = 3


def preview_text(text: str) -> str:
    names = text.split()
    if not names:
        return "Enter at least one glyph name."
    lines = [f"Supplied names: {len(names)}"]
    for name in names[:PREVIEW_LIMIT]:
        lines.append(name)
    if len(names) > PREVIEW_LIMIT:
        lines.append(f"Not shown: {len(names) - PREVIEW_LIMIT}")
    return "\n".join(lines)


sample_text = " A  A.alt\nspace smile "
print(preview_text(sample_text))
```

Expected output:

```text
Supplied names: 4
A
A.alt
space
Not shown: 1
```

The function returns a complete string; the final `print` displays it. Try an empty string, then three names, then repeated names. Empty or whitespace-only input returns `Enter at least one glyph name.` Three names need no `Not shown` line. Repetitions remain repetitions: the total counts supplied names, not distinct glyph identities.

The code imports no UI library. Calling it directly tests its text preparation, including the empty-input result. It does not test a button, signal, window or event loop. A real UI integration would need to establish how the text is read, which arguments reach its callback and where the returned string is displayed.

## Keep the owner until cleanup is complete

A **modeless window** returns control while it remains available for interaction. Its callbacks can run later, so the code needs an **owner** that retains the window and knows which connections and resources to release.

The inspected `VanillaSession` source retains its windows, attempts cleanup on `close()` and closes when its associated `with` block ends. A short `with` block that opens a window and immediately ends therefore does not express a lasting modeless session. The inspected Pythonqtside handle also records cleanup errors and retained objects. A call named `close` is not sufficient evidence that every resource has been released.

The FontLab UI guide describes disconnecting owned callbacks before widget deletion and making window Close, Escape and replacement reach the intended cleanup path. A Qt parent alone does not establish signal cleanup. These are source-defined responsibilities awaiting verification on the actual UI surface. [FontLab UI guide: Owned dialog lifetime](https://fontlabcom.github.io/fontlab-python-docs/guide/ui.html#keep-an-owned-dialog-alive-until-cleanup).

Plugmix adds another owner: its plugin host. The inspected compatibility palette facade creates controls under host-supplied content, records button connections and routes commands through a host-provided function. That facade is neither a general Vanilla replacement nor a standalone application. Keep the extension and compatibility routes distinguished in [Chapter 10](10-organize-reusable-scripts.md).

Before promoting a native UI example, verify its installed interpreter and package identities, native object origins, callback arguments, repeated opening, Close, Escape, replacement and delayed cleanup. For a plugin, verify registration and removal separately. The plain-Python preview above establishes none of those results; it gives the future callback a tested piece of work to call.
