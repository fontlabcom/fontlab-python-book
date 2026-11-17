---
this_file: src_docs/md/part4-space/062-set-a-sidebearing.md
---

# 62. Set a sidebearing

Tuesday of week twelve. Yesterday's printout is still pinned over Mira's desk, and she has circled two numbers on it in pencil. The Bold `m` has 14 units of white on its right, where the `n` has 32. The Bold `i` has 46 on its left, where the other stems have 56.

"Give the `m` 32 on the right and the `i` 56 on the left," she says. "Those two first. Then we look again."

Two numbers to set. The first takes one line you already know. The second takes a line that looks the same and does the wrong thing, and the reason is worth the whole chapter: a right sidebearing and a left sidebearing are not changed the same way.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed. Keep the Font window in front, as in chapter 53.
- The helpers `box`, `ask` and `tell` from chapters 39 and 43, and `set_width` from chapter 49. The scripts below write them out again, so each one runs by itself.
- `sb_report.py` from chapter 61, to look at the result.

This chapter changes the font. Every change is one Undo step. I couldn't run it in FontLab 9, so the outputs are worked out from Plum's source file and from the code of the tools.

## Step 1: The right side is the width

Chapter 61 said it in passing: the right sidebearing is what's left of the width after the shape ends. So to get more white on the right you make the box wider, and nothing else has to happen.

Start with the numbers as they are:

```python
from fly import fl
from fly.pens import layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()
rich = pGlyph(font, font["m"])
print(rich.getLSB("Bold"), rich.getAdvance("Bold"), rich.getRSB("Bold"))
```

```text
56 788 14
```

Mira wants 32 where there's 14. That's 18 more, so the width goes from 788 to 806. Do the sum in the script, not in your head, since the script will have to do it for other glyphs later:

```python
want = 32
width = rich.getAdvance("Bold") + want - rich.getRSB("Bold")
print(width)
```

```text
806
```

Now set it. `set_width` from chapter 49 takes the rich glyph, the layer, the new width and a name for the Undo step. Here it is again, so this runs by itself:

```python
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting


def set_width(glyph, layer, width, title="Set width"):
    def change():
        layer.advanceWidth = width

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    history.commit(title, [layer], [glyph.fl], change, operation="geometry", facts=facts)


layer = layer_of(rich.fl, "Bold")
set_width(rich, layer, width, "Set right sidebearing")
print(rich.getLSB("Bold"), rich.getAdvance("Bold"), rich.getRSB("Bold"))
```

```text
56 806 32
```

The left sidebearing stayed at 56. The shape didn't move. Only the right edge of the box went 18 units further out.

That last `print` isn't decoration. Chapter 29 had you print before and after a change, and here it earns its place: you asked for a right sidebearing, you set a width, and the only proof that the one led to the other is to ask for the sidebearing again.

## Step 2: The mistake

Now the `i`. It has 46 on the left and should have 56. Ten more. The same recipe, then, with one thing to settle first. The `i` is borrowed by `ij`, which FontLab builds itself, and chapter 55 showed what follows: the change is refused with `Refused. i: base of auto ij.` unless `history.commit` hears `allow_bases=True`. So `set_width` gets a fifth parameter and passes it on:

```python
def set_width(glyph, layer, width, title="Set width", allow_bases=False):
    def change():
        layer.advanceWidth = width

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    history.commit(title, [layer], [glyph.fl], change, operation="geometry",
                   facts=facts, allow_bases=allow_bases)
```

The default is `False`, so every call you've written so far behaves as before. Save the font, as chapter 55 asked, and then:

```python
rich = pGlyph(font, font["i"])
layer = layer_of(rich.fl, "Bold")
print(rich.getLSB("Bold"), rich.getAdvance("Bold"), rich.getRSB("Bold"))

set_width(rich, layer, rich.getAdvance("Bold") + 10, "Set left sidebearing",
                   allow_bases=True)
print(rich.getLSB("Bold"), rich.getAdvance("Bold"), rich.getRSB("Bold"))
```

```text
46 222 24
46 232 34
```

No error. The width grew by 10, as told. But the left sidebearing is still 46, and the ten units of white turned up on the right, where nobody wanted them.

Think of the box again. Its left edge is at 0, always. You can't move that edge to the left to make room, because there is no "left of 0" for a box to start at. A wider box is wider on the right. The white on the left is the distance from 0 to the shape, and the only way to make it bigger is to move the shape.

Choose **Edit > Undo** once, and the `i` should be 222 wide again. That's what the one Undo step is for. I haven't seen it in FontLab 9.

## Step 3: Move the shape, then widen the box

So a left sidebearing needs two things done together. The shape moves right by 10. And the box gets 10 wider, or the right sidebearing would shrink from 24 to 14, since the shape has moved towards the right edge.

You know one way to move a shape: chapter 50 drew it again through a `TransformPen`. That would do for the outline, but an `i` isn't only an outline. It has anchors, and they must move with it, or every accent built on the `i` would sit 10 units to the left of the stem afterwards. The tools behind FontLab's own metrics panel have a function that does the whole job on a layer:

```python
import fly.ap.metrics.panel.model as metrics

metrics.shift_and_set(layer, 10, 232)
```

Don't run that line yet. `shift_and_set` takes a layer, the distance to move everything on it to the right, and the new width. It moves the outline, the components and the anchors, and then it sets the width. A distance of 0 is allowed, and then it only sets the width.

It doesn't make an Undo step by itself. For that it goes inside the pattern from chapter 29, a small function handed to `history.commit`:

```python
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting

def change():
    metrics.shift_and_set(layer, 10, 232)

package = scripting.current_package()
facts = history.scan_auto_facts(package)
history.commit("Set left sidebearing", [layer], [rich.fl], change, operation="geometry",
               facts=facts, allow_bases=True)
print(rich.getLSB("Bold"), rich.getAdvance("Bold"), rich.getRSB("Bold"))
```

```text
56 232 24
```

Left 56, right 24, as it was. One Undo step should take all of it back.

## Step 4: What moved and what stayed

Look at what else is on that layer. Chapter 54 showed how to read the anchors:

```python
import fly.ap.anchors.writer as anchors

print(anchors.anchor_points(layer))
```

```text
{'bottom': (141.0, 0.0), 'ogonek': (162.0, 0.0)}
```

Before the change they stood at 131 and 152. They went along with the stem, 10 units each, so a mark hung on the `bottom` peg still hangs under the same part of the letter.

Here's the full account for a change to the left sidebearing:

| Thing | What happens |
|---|---|
| The outline | moves right by the difference |
| Anchors on the layer | move with it |
| Components on the layer | move with it |
| The advance width | grows by the difference |
| The right sidebearing | stays |
| The other masters | stay; you changed one layer |

And for the right sidebearing: the width changes, and nothing else at all.

## Step 5: Who borrows this glyph?

There's one more thing that moved, and it isn't on the `i`'s layer. Chapter 52 ended with a warning: the outline of a base carries into every glyph that borrows it, while widths and shifts stay behind. You have moved the outline of the `i`. Who borrows the `i`?

```python
import fly.ap.components.writer as parts

for glyph in font.glyphs:
    found = parts.components(layer_of(pGlyph(font, glyph).fl, "Bold"))
    if "i" in [parts.base_of(part) for part in found]:
        print(glyph.name, [(parts.base_of(part), parts.offset(part)) for part in found])
```

```text
ij [('i', (0.0, 0.0)), ('j', (222.0, 0.0))]
```

One glyph, the Dutch `ij`. It's an `i` with no shift and a `j` shifted 222 to the right, which was the width of the `i` when FontLab built it. Now the `i` inside it stands 10 units further right. If the `j` stands where it stood, the two have come 10 units closer in a glyph that is still 460 wide, and nobody asked for that. If FontLab built the `ij` again when its base changed, the `j` may be at 232 and the width 470. I can't tell you which. Run the loop and read the line.

The `m` has no such trouble. Nothing in Plum borrows it. And for a right sidebearing the question doesn't come up in this form at all, since no outline moves. It comes up in another form: a glyph that borrows the `n`, like `ntilde`, keeps its own width, so widening the `n` leaves the `ntilde` as tight as before. Chapter 63 deals with that.

So the rule before any change to a left sidebearing: list the borrowers first, and look at each one afterward. The `ij` is an automatic glyph, so a script can't mend it, as chapter 56 found with the `î`. If it's still 460 wide, the cure is by hand, in the Glyph window. Mira writes "ij, Bold" on her list.

## The whole script

The script sets one or both sidebearings of one glyph in one master. `None` for a side means "leave it". It prints the plan, names the borrowers, asks, makes the change and prints the result.

```python
#FLM: Set Sidebearings
# Sets the left and right sidebearing of one glyph in one master.
# None for a side leaves it alone. One Undo step.
import fly.ap.components.writer as parts
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.metrics.panel.model as metrics
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box
from fly.pens import layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"
GLYPH = "i"
MASTER = "Bold"
LEFT = 56
RIGHT = None


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


def box(font, glyph, master="Regular"):
    nodes = pGlyph(font, glyph).nodes(master)
    if not nodes:
        return None
    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    return min(xs), min(ys), max(xs), max(ys)


def plan(rich, master, left, right):
    dx = 0
    width = rich.getAdvance(master)
    if left is not None:
        dx = left - rich.getLSB(master)
        width += dx
    if right is not None:
        width += right - rich.getRSB(master)
    return dx, width


def borrowers(font, name, master):
    found = []
    for glyph in font.glyphs:
        layer = layer_of(pGlyph(font, glyph).fl, master)
        if name in [parts.base_of(part) for part in parts.components(layer)]:
            found.append(glyph.name)
    return found


def numbers(rich, master):
    return f"left {rich.getLSB(master)}, width {rich.getAdvance(master)}, right {rich.getRSB(master)}"


def main():
    font = fl.CurrentFont()
    if font is None or font[GLYPH] is None:
        tell(f"Open a font that has a glyph named {GLYPH}.")
        return
    if box(font, font[GLYPH], MASTER) is None:
        tell(f"{GLYPH} has no outline in {MASTER}, so it has no sidebearings to set.")
        return
    rich = pGlyph(font, font[GLYPH])
    layer = layer_of(rich.fl, MASTER)
    dx, width = plan(rich, MASTER, LEFT, RIGHT)
    if dx == 0 and width == rich.getAdvance(MASTER):
        print(f"{GLYPH} {MASTER}: {numbers(rich, MASTER)}. Nothing to do.")
        return

    print(f"{GLYPH} {MASTER} now: {numbers(rich, MASTER)}")
    print(f"Plan: move the shape by {dx}, set the width to {width}.")
    users = borrowers(font, GLYPH, MASTER)
    if users and dx != 0:
        print(f"The shape also moves inside: {' '.join(users)}")
    elif users:
        print(f"Borrowed by: {' '.join(users)}")
    if not ask(f"Change {GLYPH} in {MASTER}?"):
        return

    def change():
        metrics.shift_and_set(layer, dx, width)

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    # The question above is the agreement that allow_bases stands for.
    history.commit("Set sidebearings", [layer], [rich.fl], change, operation="geometry",
                   facts=facts, allow_bases=True)
    print(f"{GLYPH} {MASTER} after: {numbers(rich, MASTER)}")


main()
```

Choose **Edit > Undo** until the `i` is back at 46 and 222, then run the script as it stands:

```text
i Bold now: left 46, width 222, right 24
Plan: move the shape by 10, set the width to 232.
The shape also moves inside: ij
i Bold after: left 56, width 232, right 24
```

Run it a second time and it has nothing to do:

```text
i Bold: left 56, width 232, right 24. Nothing to do.
```

A few things in it are worth a second look.

`plan` works out both numbers before anything is touched. The width starts as it is, grows by the move on the left, and grows again by whatever the right side needs. Either `if` can be skipped, so one function serves for the left side, the right side or both. It returns a pair, as `mark_shift` did in chapter 53.

`change` is written inside `main`, after the question. It's the function-in-a-function from chapter 49, and it sees `layer`, `dx` and `width` because it was written where those boxes live.

The guard with `box` keeps the script away from glyphs with no outline of their own. A `space` has a width and no shape, so "left sidebearing" means nothing for it. A glyph made only of components is a different case, and chapter 63 takes it up.

Mira runs the script for the `i` and, with three constants changed, for the `m`. Then she runs `sb_report.py` on `minimum` again:

```text
Bold       88   80   88   80   84   92   smallest 80, spread 12
```

Yesterday that line read 60, 80, 78, 80, 66, 92, with a spread of 32. The spread is now 12, a little under the 14 of the other two masters. She sets the word, looks, and says it's better and still not right. The whole Bold is tight, she thinks, not only uneven. That's a job for chapter 68. First there are the other glyphs with the `m`'s problem, and nobody has counted them yet.

## What you learned

The right sidebearing changes when the width changes, and nothing moves. The left sidebearing changes only when the shape moves, and the width has to change by the same amount to keep the right side as it was. `metrics.shift_and_set(layer, dx, width)` moves the outline, the components and the anchors of a layer and sets its width, and it belongs inside `history.commit`. A moved outline shows up in every glyph that borrows it, so list the borrowers before you move anything and print the numbers again afterwards.

## Try it yourself

1. Oskar once left a note that said "Give the H 60 on each side." Do it in the Bold: set `GLYPH = "H"`, `LEFT = 60` and `RIGHT = 60`. The Bold `H` starts at left 56, width 672, right 40. Work out the plan on paper before you run the script. You should get a move of 4 and a width of 696.
2. Set the right sidebearing of the Bold `n` to 40, with `LEFT = None`. Then print the three numbers of the Bold `ntilde`. Its width is still 523. In one sentence: why does the script not warn you about `ntilde`, and should it?
3. Set `GLYPH = "ij"` and run the script. It stops at the guard and says the glyph has no outline, since `ij` is two borrowed shapes. Now try the width alone, in the Scripting panel: `set_width(rich, layer, 470, allow_bases=True)` for the Bold layer of `ij`. By Fly's code that should stop with a refusal that begins `Refused: auto layer`. Why does `allow_bases=True` not help here? Chapter 55 has the answer.

## Next

The `d`, the `q` and the `g` begin with the same round stroke as the `o`, and Oskar's sheet says their left sides should match it. Chapter 63 copies sidebearings from one glyph to others, with a dictionary that says who follows whom.
