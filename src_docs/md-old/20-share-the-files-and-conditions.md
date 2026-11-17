---
this_file: src_docs/md/20-share-the-files-and-conditions.md
---

# Share the files and the conditions

A script can work on your computer because a helper package, form or font fixture is already there. Sending only the visible menu file leaves the recipient with part of the program. A useful handoff identifies both the delivered files and the conditions under which they were tested.

This chapter examines source from the Examples, Scriptmix, Plugmix and FontLab App projects as inspected on 13 November 2026. **No package, installer or Extensions bundle was installed or run for this chapter.** The exercise compares fictional bytes in external Python 3.11. Native compatibility, independent review and semantic-map integration remain pending.

## Name the artifact you are sharing

An **artifact** is a concrete output you can deliver, such as an archive or a script file. A Python **distribution** is an installable project with package metadata. Its distribution name can differ from the module name used in an import. A **wheel** is one archive format for distributing a Python project.

The inspected repositories illustrate why these distinctions matter:

| Source | Deliverable described by its configuration |
| --- | --- |
| Examples root project | Documentation environment, with `tool.uv.package = false` |
| Examples `lessons/` subproject | `fontlab-python-lessons` distribution, containing the `fontlab_python_lessons` package |
| Scriptmix | Menu scripts and separate host dependency declarations; its root Python project builds documentation |
| Plugmix wheel | The retained `fontlab_plugmix` compatibility package |
| Plugmix Extensions pack | A separate ZIP containing bundles, its menu action and README |

These are source configurations, not a statement that corresponding releases are available. The inspected revisions are Examples `341a6652`, Scriptmix `29162083`, Plugmix `baffc66c` and App `8ee58ade`. Source links may require repository access. [Examples configuration](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/pyproject.toml); [Lessons configuration](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/lessons/pyproject.toml); [Scriptmix configuration](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/2916208361336d88a93fc1c8407e4fb22aa12056/pyproject.toml); [Plugmix packaging](https://github.com/fontlabcom/fontlab-python-plugmix/blob/baffc66c70f01c9a706e50776baf8f97b89e025e/pyproject.toml).

The Lessons wheel configuration includes package code and shared data: menu files, provenance records and documentation. Its form lesson also needs a packaged `.ui` resource. Placing menu files in a wheel's shared-data area does not establish that FontLab discovers them in its Scripts menu. The runtime package and the menu entry points have separate roles, as [Chapter 10](10-organize-reusable-scripts.md) explains. [Lessons package guide](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/lessons/README.md).

Plugmix's pack builder selects `Extensions/`, `Scripts/Plugmix` and the README. The compatibility wheel instead packages `src/fontlab_plugmix`. Inspecting the builder tells you what it intends to include; inspecting a produced artifact tells you what was actually delivered. Neither alone verifies its native startup or all required notices. [Pack builder](https://github.com/fontlabcom/fontlab-python-plugmix/blob/baffc66c70f01c9a706e50776baf8f97b89e025e/tools/build_pack.py).

## Keep runtime requirements attached to their scope

A documentation interpreter and FontLab's embedded interpreter do different jobs. The Examples root project declares Python `>=3.12` for its documentation environment. Lessons declares Python `>=3.11`, while its guide describes the FontLab host target as Python 3.11 with the host architecture and supplied PythonQt. The documentation floor does not require replacing FontLab's interpreter or adding another Qt binding.

Dependency requirements can also differ between consumers. The Examples root installer configuration names App and Fly minimums of `1.2.0`; the Lessons subproject records App `>=0.2.26.dev0` and Fly `>=0.2.1`. These are separate declarations at the inspected revision. Combining them into one generic installation command would hide which consumer needs what.

App's configuration resolves its Pens dependency from a sibling checkout for local development. That rule does not establish registry availability. An **extra** names optional dependencies of a particular distribution; a guide mentioning an extra is insufficient if the selected distribution does not declare it. For example, the inspected Scriptmix installation page names an App `fontedit` extra that is absent from the inspected App metadata. No replacement command is inferred here. [App metadata](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/pyproject.toml); [Scriptmix installation text](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/2916208361336d88a93fc1c8407e4fb22aa12056/src_docs/md/install.md).

Record the exact source or artifact used to resolve such discrepancies. A declared minimum, an import that succeeds and a tested native operation are three different pieces of evidence. Keep the application build, interpreter, architecture and dependency versions together in the test record.

## Treat a bundle as executable code

An App Extensions bundle contains a `plugin.json` manifest and Python source. Its folder, suffix and declared kind must agree. The manifest identifies an entry such as `module:Class`; loading that entry imports Python code. A manifest is a description, not a sandbox. [Extensions layout and trust boundary](https://github.com/fontlabcom/fontlab-python-plugmix/blob/baffc66c70f01c9a706e50776baf8f97b89e025e/Extensions/README.md).

The inspected App loader checks fields, entry paths and class identity. Its `min_app_version` refers to the **FontLab App distribution**, not FontLab's application version. If neither a supplied version nor installed App metadata provides a version, this source skips its version comparison. Passing that check cannot establish compatibility in an unknown environment. The tool host separately checks whether the native `registerPythonTool` capability exists. [Bundle loader](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/plugins/bundles.py); [native tool capability check](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/plugins/tools/host.py).

Loaded bundle modules remain cached during a session. Rescanning discovers bundles; it does not necessarily reload edited source. A successful rescan is therefore insufficient evidence that a change is running.

## Describe what installation and cleanup own

The inspected Scriptmix installer can place package links, copy menu files, install dependencies and record installed paths. It distinguishes edited script targets using recorded hashes and retains foreign bundle paths. Those checks are source mechanisms, not a guarantee that every partial failure leaves the environment unchanged. Do not run an installer merely to inspect its metadata. [Installer implementation](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/2916208361336d88a93fc1c8407e4fb22aa12056/install.vfpy).

App's startup helper adds or removes its marked block in `initScript.py`, preserving surrounding bytes and refusing malformed markers. That is a startup-file change. Plugmix's App and compatibility runtimes also share a preferences filename; their documentation calls for choosing one runtime per session and does not promise cross-runtime preference migration. Removing owned actions and panels can deliberately retain saved choices. Cleanup is not synonymous with deleting all settings, undoing font edits or restoring every earlier environment state. [Startup helper](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/plugins/startup.py); [runtime ownership](https://github.com/fontlabcom/fontlab-python-plugmix/blob/baffc66c70f01c9a706e50776baf8f97b89e025e/src_docs/md/installation.md#runtime-and-preference-ownership).

Keep font fixtures separate from code ownership. The Lessons GetGo data carries its own source hashes, attribution and license records. Its helper checks a fixture's bytes, copies it into temporary storage and identifies the opened copy by its path. The mutation branch requires a session with no other documents. These are inspected source boundaries; this chapter did not run them. The package explicitly leaves native acceptance pending. [Fixture records](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/lessons/src/fontlab_python_lessons/getgo/data/README.md); [owned-copy helper](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/lessons/src/fontlab_python_lessons/getgo/_shared.py); [lesson entry points](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/lessons/src/fontlab_python_lessons/getgo/__init__.py).

Sharing a script does not establish permission to include a user's font, proof text or screenshots. Document which data the recipient must supply and retain the notices belonging to any fixtures actually distributed. This chapter supplies no font files.

## Compare a fictional delivery

The exercise uses dictionaries of filenames and **bytes**, the data stored in a file. No file is opened or written. The `b` prefix creates a bytes literal; these examples contain ASCII text, and `\n` is a newline byte. The sample `.py` contents are data and are never executed.

A **digest** is a value calculated from bytes. Python's standard `hashlib.sha256` calculates a SHA-256 digest; `.hexdigest()` expresses it as hexadecimal text. Here each expected digest is recorded from fictional approved contents before comparing the supplied contents. The reference must itself be trustworthy: a digest supplied alongside altered data cannot authenticate the sender. [Python hashlib](https://docs.python.org/3.11/library/hashlib.html#usage).

This exercise runs in external Python 3.11 and imports only `hashlib`. `delivery_report` expects a dictionary of filename labels to recorded digest strings, and another dictionary of labels to bytes. It does not parse paths, open an archive, install code or check arbitrary input types.

```python
import hashlib


def delivery_report(expected: dict[str, str], supplied: dict[str, bytes]) -> list[str]:
    if not expected:
        return ["No required artifacts recorded; nothing verified"]
    lines = []
    for name, digest in expected.items():
        if name not in supplied:
            lines.append(f"{name}: missing")
        elif hashlib.sha256(supplied[name]).hexdigest() != digest:
            lines.append(f"{name}: differs from recorded digest")
        else:
            lines.append(f"{name}: matches recorded digest")
    for name in supplied:
        if name not in expected:
            lines.append(f"{name}: unexpected")
    return lines


approved = {
    "report.py": b"print('Fictional report')\n",
    "README.txt": b"Run in external Python 3.11.\n",
    "NOTICE.txt": b"Fictional exercise material.\n",
}
expected = {}
for name, content in approved.items():
    expected[name] = hashlib.sha256(content).hexdigest()

supplied = {
    "report.py": approved["report.py"],
    "README.txt": b"Run anywhere.\n",
    "draft.txt": b"Unreleased note.\n",
}
for line in delivery_report(expected, supplied):
    print(line)
```

The output is:

```text
report.py: matches recorded digest
README.txt: differs from recorded digest
NOTICE.txt: missing
draft.txt: unexpected
```

`dictionary.items()` supplies each key and value together; the loop unpacks them into the two names before `in`. Required items retain their recorded order. Unexpected labels follow in their supplied order. A missing required item differs from present but changed data. Even an empty byte string can have a matching digest; an empty requirements dictionary instead reports that nothing was verified.

Changing a newline changes the bytes under comparison. The helper neither repairs the delivery nor ignores the altered README. Its matching line says only that the digest matches the reference. It does not establish installation, safe behavior, licensing or native compatibility.

## Send the verification record too

A small handoff record can make the limits usable:

| Record | What the recipient can check |
| --- | --- |
| Source revision and artifact digest | Which exact source and delivered output were examined |
| Distribution, import and resource names | Whether the launcher has its package and supporting files |
| Host build, interpreter and architecture | Which runtime the result applies to |
| Dependency versions | Which combination was tested |
| Font, layer, selection and UI scope | Which data and state the operation reads or changes |
| Passed checks and pending checks | Whether evidence covers imports, callbacks, Undo/Redo or saved/reopened output |

A later package or FontLab build needs its own relevant checks; the previous result remains useful evidence for the earlier combination. [Chapter 17](17-test-the-promise.md) separates pure-Python checks from native acceptance. Delivering that distinction is part of delivering the script.
