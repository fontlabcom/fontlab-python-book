---
this_file: src_docs/md/19-know-where-automation-runs.md
---

# Know where the automation runs

A script started in a terminal can ask FontLab to execute Python inside the application. The terminal and FontLab still have separate interpreters, objects and lifetimes. Understanding that boundary helps you decide what a result actually proves.

This chapter describes source inspected on 13 November 2026. **No remote connection, authentication, cancellation or capture operation was tested for this chapter.** Its only executable example uses fictional records in external Python 3.11. Package installation and native compatibility remain unverified; independent review and semantic-map integration remain pending.

## Separate the four roles

These projects solve different parts of an automation task. The revisions below identify inspected source, not installed packages or a compatibility set.

| Project and source revision | Role |
| --- | --- |
| FontLab Remopy, `624a9d56` | External Python client for FontLab's native tools and Python execution |
| EchoPy, `957a8a3f` | Readable declarations and access to the host's native interfaces |
| Fly, `e5180aa1` | Short, lazy import aliases for other packages |
| GrabLab, `40bd2bd6` | Native application, widget and drawing captures |

The repository sources establish these roles: [Remopy](https://github.com/fontlabcom/fontlab-remopy/tree/624a9d56a99610fc7fe203520eaa90ec39cd6f20), [EchoPy](https://github.com/fontlabcom/fontlab-echopy/tree/957a8a3fd46a0b238208e7723947d6b4d49f3dcb), [Fly](https://github.com/fontlabcom/fontlab-fly/tree/e5180aa1669a994d2a559d06288f23f90e63f71e), [GrabLab](https://github.com/fontlabcom/fontlab-grablab/tree/40bd2bd62b21fa8cf0bf29d70666f8bc4c638f63). Source access may require repository permission. None of these links is an installation instruction.

EchoPy can expose declarations outside FontLab so that tools can inspect names and documentation. A declaration describes an interface; it does not supply the native implementation. Calls that need an unavailable host raise `NativeUnavailable`. Inside the host, the inspected implementation delegates to native objects, including attribute writes. A readable wrapper does not turn a live object into an independent Python copy. [EchoPy runtime source](https://github.com/fontlabcom/fontlab-echopy/blob/957a8a3fd46a0b238208e7723947d6b4d49f3dcb/src/fontlab_echopy/_runtime.py).

Fly loads an alias's target when needed. Its `fl` target is `echopy.fontlab`; `qt` targets `PythonQt`. Those names neither start a remote connection nor provide an external replacement for FontLab's PythonQt. Loading a target still runs that target's import behavior. Also distinguish an alias from a local variable: Remopy examples sometimes call their remote client `fl`, but that variable is not Fly's native alias. A name such as `client` makes the distinction clearer. [Fly alias source](https://github.com/fontlabcom/fontlab-fly/blob/e5180aa1669a994d2a559d06288f23f90e63f71e/src/fly/__init__.py).

## Follow a request across processes

A **process** is a running program with its own memory. Remopy's inspected connection uses Model Context Protocol, or **MCP**, to exchange requests and results. Its Python software development kit handles message framing and process communication. The native bridge connects that communication to FontLab.

```text title="Inspected request route; not a setup procedure"
External Python and Remopy
    → Python relay using the MCP SDK
    → native fontlab-mcp bridge process
    → FontLab's localhost server
    → native tool or embedded Python execution
```

Here **localhost** means the same computer. The relay communicates with the bridge through standard input and output streams. The native bridge then communicates with FontLab. A working connection establishes a route; it does not show that a particular script completed. Likewise, Remopy's macOS file-submission result explicitly leaves execution unverified. [Connection source](https://github.com/fontlabcom/fontlab-remopy/blob/624a9d56a99610fc7fe203520eaa90ec39cd6f20/src/fontlab_remopy/mcp/__init__.py); [submission result](https://github.com/fontlabcom/fontlab-remopy/blob/624a9d56a99610fc7fe203520eaa90ec39cd6f20/src/fontlab_remopy/discovery.py).

Remopy transports JSON-compatible values: ordinary data such as strings, numbers, lists and dictionaries with suitable keys and values. A native glyph wrapper cannot cross this boundary as the same live object. The inspected result code requires a valid result envelope with a matching **nonce**, a unique label for that execution. Missing or malformed result data produces a transport error rather than an invented empty result. Matching the nonce associates a response with a request; it does not establish that an operation happened exactly once. [Result encoding and decoding](https://github.com/fontlabcom/fontlab-remopy/blob/624a9d56a99610fc7fe203520eaa90ec39cd6f20/src/fontlab_remopy/results.py).

The native implementation inspected for this chapter checks a shared token during initialization and restricts its listener to localhost. The bridge and server perform that authentication handshake. No token was read for this chapter. Authentication establishes access to the connection; it does not choose the intended font, authorize a change to every open document or make submitted Python safe. These native-source observations have not been verified against a reader's installed build.

Enabling MCP is also an operation: Remopy's setup path changes a FontLab preference and submits a verification script. Do not treat setup as a passive connectivity check. The installed bridge, application build, allowed operations and intended documents need to be established before a real request. [Setup source](https://github.com/fontlabcom/fontlab-remopy/blob/624a9d56a99610fc7fe203520eaa90ec39cd6f20/src/fontlab_remopy/setup.py); [host preference operation](https://github.com/fontlabcom/fontlab-remopy/blob/624a9d56a99610fc7fe203520eaa90ec39cd6f20/src/fontlab_remopy/host.py).

## Keep an unknown outcome unknown

A **timeout** means the client stopped waiting. A **cancellation** means the caller requested that its operation stop. Neither observation alone proves that FontLab stopped executing the submitted work.

The inspected Remopy client marks a timed-out or cancelled connection as uncertain and refuses further calls until a fresh context opens. It does not automatically retry that call. Opening another connection restores a communication route; it does not roll back prior changes or prove the earlier operation finished. [Client source](https://github.com/fontlabcom/fontlab-remopy/blob/624a9d56a99610fc7fe203520eaa90ec39cd6f20/src/fontlab_remopy/client.py).

There is a separate lower-level limit. The inspected native server ignores MCP cancellation notifications. The inspected native bridge can reconnect and resend a request once after a failed socket write. This does not demonstrate that a duplicate operation occurred, but it prevents a claim of end-to-end exactly-once execution from Remopy's no-retry behavior alone. These are source findings, not cancellation or duplicate-execution experiments.

A reported Python exception is different from a missing result. Remopy preserves native failure details, including partial output, while a result transport failure can leave the execution outcome unknown. Even a reported exception does not prove that earlier statements made no changes. Keep the request identity, failure details and known state together, and investigate the original outcome before deciding what to do next. [Development and safety notes](https://github.com/fontlabcom/fontlab-remopy/blob/624a9d56a99610fc7fe203520eaa90ec39cd6f20/src_docs/md/development-and-safety.md).

## Decide what a capture may disclose

GrabLab uses FontLab and PythonQt inside the host. A captured window, a native drawing export and a structured widget record answer different questions. Its bundles can contain PNG, SVG, JSON and UI files, with metadata also embedded in image files. A screen SVG contains a raster image; it does not turn the desktop into editable vector geometry. A canvas PNG can be rendered from the paired SVG rather than captured separately from the visible editor. [Capture bundle documentation](https://github.com/fontlabcom/fontlab-grablab/blob/40bd2bd62b21fa8cf0bf29d70666f8bc4c638f63/src_docs/md/capture-bundles.md).

The inspected defaults permit whole-screen capture. Such an image can include unrelated windows and user data. Structured widget records can include titles and editable text; omitting password-field text does not remove every private value. Review the image, filenames, embedded metadata and accompanying files before sharing. A smaller chosen capture target still needs review. This chapter supplies no capture call. [Capture implementation](https://github.com/fontlabcom/fontlab-grablab/blob/40bd2bd62b21fa8cf0bf29d70666f8bc4c638f63/src/grablab/grab.py); [widget snapshot source](https://github.com/fontlabcom/fontlab-grablab/blob/40bd2bd62b21fa8cf0bf29d70666f8bc4c638f63/src/grablab/snapshot.py).

Capture also has state and file effects. GrabLab's constructor calls a configuration save. Capture helpers temporarily change selected rendering preferences and attempt to restore them in `finally`, the Python cleanup clause that runs when control leaves the protected block. That source structure does not prove restoration after process termination or every native failure. Capture writes output files; it should not be described as a passive read of font geometry.

## Read a fictional receipt

A **receipt** here is a record of what another operation reported. The following dictionaries are invented teaching data, not Remopy's result schema. The exercise runs in external Python 3.11 and imports no library. It makes no requests, reads no files and retries nothing.

`receipt_summary` accepts a nonempty expected request label and an ordinary dictionary or `None`. A completed fictional record needs the matching label, the Boolean `True` and a nonnegative integer count. A failure needs the Boolean `False` and a nonempty error string. Other cases remain unknown. These checks describe the record; they do not authenticate its sender or independently verify the count.

```python
def receipt_summary(expected_request: str, receipt: dict | None) -> str:
    unknown = f"{expected_request}: outcome unknown"
    if receipt is None or receipt.get("request") != expected_request:
        return unknown
    if receipt.get("ok") is False:
        error = receipt.get("error")
        if type(error) is str and error:
            return f"{expected_request}: reported failure; {error}"
        return unknown
    if receipt.get("ok") is not True:
        return unknown
    count = receipt.get("count")
    if type(count) is not int or count < 0:
        return unknown
    return f"{expected_request}: completed; count {count}"


receipts = [
    {"request": "sample-7", "ok": True, "count": 0},
    {"request": "sample-7", "ok": False, "error": "Fixture unavailable"},
    None,
]
for receipt in receipts:
    print(receipt_summary("sample-7", receipt))
```

The output is:

```text
sample-7: completed; count 0
sample-7: reported failure; Fixture unavailable
sample-7: outcome unknown
```

`dict.get` returns the stored value, or `None` here when a key is missing. The tests `is True` and `is False` require the actual Boolean objects; a string such as `"true"` is insufficient. `type(count) is int` also excludes Boolean values, which Python otherwise treats as a kind of integer. Zero passes because the test checks the count's type and range, not whether it is truthy. [Python dictionary methods](https://docs.python.org/3.11/library/stdtypes.html#dict.get); [Boolean values and numeric types](https://docs.python.org/3.11/library/stdtypes.html#numeric-types-int-float-complex).

The `or` condition stops evaluating when its first part is true, so a missing receipt never receives a `.get` call. The helper leaves its input unchanged. Changing the request label, removing the count or replacing `True` with `1` produces an unknown outcome. None of those records tells the program to repeat the original operation.

## Verify the route you intend to use

For a real workflow, record the loaded client and SDK versions, native bridge and FontLab build. Test connection, tool discovery, script execution and returned data as separate observations. Use an owned fixture and keep document identity, dirty state, UI effects and saved/reopened results distinct, as in [Chapter 17](17-test-the-promise.md).

Capture needs an additional check of the chosen target, operating-system permissions and every resulting data surface. Keep credentials out of source files, transcripts and shared artifacts. A successful fictional receipt test establishes only this small Python calculation; it establishes no native, authentication, cancellation or privacy guarantee.
