---
this_file: src_docs/md/23-name-the-batch-targets.md
---

# Name the targets before running the batch

“Apply this to the selected glyphs” leaves several questions unanswered. Which font supplied the selection? Which layers will change? Does the selection still contain the same glyphs when the operation starts? A batch repeats those assumptions along with the operation.

This chapter builds a proposal that answers the target questions before execution. **Its example uses fictional records in external Python 3.11; it invokes no action, reads no FontLab document and writes no files.** Source observations refer to the implementations inspected on 13 November 2026. Native execution, Undo and cancellation behavior were not tested for this chapter. The draft remains provisional pending independent review and semantic-map integration.

## Separate the view from the edit

The word *filter* can describe different operations:

| Kind | What to establish |
| --- | --- |
| Font-window filter | Which glyphs appear in the view; hiding a glyph does not delete it |
| Selection command | Which existing glyphs become targets; a visible empty cell is not necessarily an existing glyph |
| Live outline filter | Which construction derives geometry from editable inputs, and which references share those inputs |
| Plugin Filter | What its Apply implementation writes, and which selection it reads |
| External batch recipe | Which source files it opens and which output files it creates |

For example, the current Glyph Name Filter launcher distinguishes changing the displayed name prefix from selecting rows. Its existence does not turn every visible row into an editing target. The App plugin host, in contrast, can apply outline changes. Inspect the operation behind a label. [Glyph Name Filter source](https://github.com/fontlabcom/fontlab-python-examples/blob/341a665200ce9f1f911d2782b1fdfeb817d02925/Scripts/Models/Glyph%20Name%20Filter.py); [plugin Apply host](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/plugins/filters/host.py).

FontLab's Actions dialog separates glyph scope from layer scope. Its preview concerns current content, so it cannot establish every result in a larger batch. An open, nonempty action-set sidebar also changes the operation being requested: Run or OK executes that set. A saved set retains operations and parameters; it does not establish their suitability for another font. [FontLab Actions](https://help.fontlab.com/fontlab/9/articles/actions/index.html); [Action Sets](https://help.fontlab.com/fontlab/9/articles/action-sets/index.html).

Keep an operation description with the targets. For a geometric change, that might include its origin, coordinate units, parameter values and whether it should affect anchors or advances. This is a review record, not a guessed native parameter dictionary.

## Know which route interprets the request

Discovering an action and invoking it are separate operations. In the inspected App wrapper, `GlyphActions.items` obtains an action catalogue; `GlyphAction.__call__` sends a `run_actions` request. A catalogue entry supplies an identifier and label, not proof of installed compatibility or correct parameters for a particular font. [App action wrappers](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/core/host.py).

The local native bridge for the Model Context Protocol (MCP) distinguishes supplied glyph names from omitted names. Explicitly empty names refuse work instead of expanding to the selection. Omitted names consult selection, with a check against the requested font. The explicit-name loop does not remove duplicates. These are findings about that source path, not a universal contract for all scripts or the Actions dialog.

The bridge's `active`, `visible` and `masters` layer modes also require context. “Active” depends on application state. For ordinary actions, the inspected masters path restricts work to matching participating master layers relative to the active layer and excludes certain layers. The metrics helper uses a different expansion path. A named master and a broad mode are not interchangeable, and the same mode label does not prove identical targets across action kinds.

Order needs the same care. Starting at x = 10, scaling by 2 and then adding 5 gives 25. Adding 5 first and scaling afterward gives 30. The two operations and values are identical; their sequence changes the answer.

In the inspected native `toolRunActions` implementation, all action identifiers are checked first. Then `auto_space` and `auto_kern` run while ordinary actions are collected for later execution. **A mixed request can run its metrics actions before an ordinary action that appeared earlier in the submitted list.** A later failure can occur after an earlier metrics action has changed data. This source finding must not be replaced by an assumption that every entry runs in submitted order. It also does not redefine the dialog's action-set behavior.

The chapter therefore supplies no native action invocation. A future example needs the exact installed route, parameter contract and order verified on owned fixtures.

## Build a proposal from explicit records

The following original exercise knows one fictional font, `Orchard`, and a small layer inventory. Each requested target is a `(glyph name, layer name)` tuple. The inventory maps glyph names to dictionaries of layer states.

The exercise's policy is simple: only a layer marked `editable` becomes proposed work. Locked and automatic layers are listed with reasons. Unknown states are excluded. A missing glyph differs from an existing glyph without the requested layer. These are teaching rules, not a simulation of FontLab's layer eligibility rules.

```python
def propose(requests: list, inventory: dict) -> list:
    rows = []
    seen = set()
    for name, layer in requests:
        target = name, layer
        if target in seen:
            reason = "duplicate request"
        elif name not in inventory:
            reason = "missing glyph"
        elif layer not in inventory[name]:
            reason = "missing layer"
        else:
            state = inventory[name][layer]
            reasons = {"editable": "proposed", "locked": "locked", "automatic": "automatic"}
            reason = reasons.get(state, "unsupported state")
        seen.add(target)
        rows.append((name, layer, reason))
    return rows


inventory = {
    "A": {"Regular": "editable", "Bold": "editable", "Preview": "automatic"},
    "V": {"Regular": "locked"},
}
requests = [
    ("A", "Regular"),
    ("A", "Bold"),
    ("A", "Regular"),
    ("X", "Regular"),
    ("V", "Light"),
    ("V", "Regular"),
    ("A", "Preview"),
]
print("Fictional Orchard / target proposal only")
for name, layer, reason in propose(requests, inventory):
    print(f"{name} / {layer}: {reason}")
```

The output is:

```text
Fictional Orchard / target proposal only
A / Regular: proposed
A / Bold: proposed
A / Regular: duplicate request
X / Regular: missing glyph
V / Light: missing layer
V / Regular: locked
A / Preview: automatic
```

A **set** stores distinct values. Here, `seen` answers whether a target tuple has appeared before; it does not supply the output order. The loop reads the request list in order and appends one result for every request. Two layers of A remain two targets because their tuples differ. The repeated A/Regular remains visible as a duplicate instead of becoming a second proposed edit. [Python sets](https://docs.python.org/3.11/tutorial/datastructures.html#sets).

The `reasons.get(state, "unsupported state")` call looks up a dictionary entry and supplies the second argument when the key is absent. It prevents an unfamiliar state from silently becoming proposed work. The loop unpacks three values from each returned row; the `f` prefix inserts those values at the braces in the printed line. [Python dictionary get](https://docs.python.org/3.11/library/stdtypes.html#dict.get).

An empty request list produces an empty result. The helper never substitutes “all glyphs”. It leaves both inputs unchanged and creates no glyphs or layers. Its contract expects string names and states in the displayed container structure; it is not a parser for arbitrary input or a check of live FontLab objects.

“Proposed” means that the fictional record passed these rules. It does not mean the target was edited or even that a real action could edit it. Before adapting the idea to a document, retain its exact identity and the action description alongside the rows. A changed document, layer state or selection requires another check.

## Recheck what Apply will use

Opening a dialog does not necessarily freeze its targets. The inspected App filter host reads selection again when Apply runs. It also attempts to persist parameter preferences before applying the selection. A later refusal can therefore follow a preference change.

The filter planner deduplicates glyph IDs and plans for the package's current master. Before writing, it checks relevant source state again. Those checks narrow what it accepts, but the shared writer explicitly permits partial-write failures and supplies no enclosing rollback. Its changes can include coordinates or supported contour deletion. The word *Filter* does not establish that Apply is merely a preview. [Filter planner and application](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/plugins/filters/apply.py); [layer writer](https://github.com/fontlabcom/fontlab-fontlabapp/blob/8ee58adef7658fb1949d531c7c5315cdc5ddea6a/src/fontlabapp/masters/layers/writer.py).

Native actions can also traverse shared constructions and update dependent data. An explicit list of glyph names is useful scope evidence; it is not proof that every related object remains unchanged. Test the action's relevant dependencies as well as its named targets.

## Read a partial result honestly

Consider this fictional record after an attempted batch:

| Target | Recorded outcome | What is established |
| --- | --- | --- |
| A / Regular | Completed; coordinates compared | That particular comparison passed |
| A / Bold | Failed after write began | Some changes may remain |
| V / Regular | Not started | The record explicitly says execution did not start |
| X / Regular | No result received | The outcome is unknown |

**A missing result is not evidence that no work happened.** Do not automatically turn the last row into “not started” or retry it. Repeating a shift or scale can compound a change that already occurred. A completed comparison also says nothing by itself about saved data, exported fonts or other unchecked properties.

The inspected native bridge can report a contour-count error after ordinary actions have run. Its runner has no enclosing rollback transaction. History preparation and change notification are distinct operations; disabling an undo option does not turn a request into a simulation. A callback can stop the ordinary runner between glyphs, leaving earlier work done, but the inspected MCP invocation does not pass that callback. No universal Stop or Undo guarantee follows.

External files have a different boundary. Fontport's batch runner checks cancellation before each next file, not during that file's transformation or save. Earlier outputs remain, and a save failure may leave an artifact. Its progress callback runs after a write but before yielding the result: a callback failure can leave a written output without a delivered row. These observations come from source, not a new filesystem test. [Fontport batch implementation](https://github.com/fontlabcom/fontlab-fontport/blob/c0ece90c8b8eaa7a1c6e8787d06294d147e29498/src/fontlab_fontport/batch.py).

## Qualify execution as a separate step

A useful next experiment starts with one explicit action, one ordinary layer and a provenance-recorded disposable font copy. Record the runtime, document identity, selection, active master, dirty state and called history state before access. Compare the properties the action is meant to change, relevant dependencies and unaffected controls afterward. Equal contour counts cannot establish equal geometry, anchors, components, hints or spacing.

Broaden acceptance separately to missing targets, duplicates, locked or automatic layers and multiple masters. Establish actual Undo/Redo behavior and saved/reopened results before making those claims. External batches need separate path-ownership, partial-file and reopened-output checks. [Chapter 17](17-test-the-promise.md) explains these different kinds of evidence; [Chapter 21](21-make-the-report-reproducible.md) distinguishes a report from the artifacts it describes.
