---
this_file: src_docs/md/part6-families/103-fix-the-start-point.md
---

# 103. Where the contour starts

Wednesday of week twenty. Yesterday's check came back clean, and Oskar isn't satisfied.

"Draw me a square," he says, and Mira draws one on the back of the proof. "Number the corners from the bottom left, going round. Now draw a fatter square next to it and number that one from the top right." She does. "Join the ones, join the twos."

The four lines cross in the middle. A shape halfway between the two squares, made by joining node 1 to node 1 and node 2 to node 2, isn't a square. It's a knot. Both squares have four nodes on one contour, and yesterday's script would call them a match.

A contour is a ring, and a ring has no beginning. A list has one. So FontLab picks one node of the ring to be number 0, and that choice is the start point. For masters to mix, the choice has to fall on the same corner in every master. Today's script finds the contours where it doesn't and turns the ring until it does.

## What you need

- `Plum-practice` open in FontLab 9 with the Regular showing, and Fly installed.

I couldn't run the code in FontLab 9. I computed the outputs in plain Python from the outlines in Plum's source file, for the 205 glyphs Plum came with, and I moved the start points in a stand-in, not in FontLab.

## Step 1: Turn a ring

Forget the font for a minute. Here is a ring of six letters:

```python
ring = list("abcdef")
turned = ring[2:] + ring[:2]
print(turned)
```

```text
['c', 'd', 'e', 'f', 'a', 'b']
```

`ring[2:]` is the slice from position 2 to the end and `ring[:2]` is the slice before position 2. Chapter 10 took slices of a list of widths, and these are the same slices. Glue the two together the other way round and the ring has turned: what was at position 2 is now at 0. Nothing was added or lost, and every letter still has the same neighbours.

That's what a new start point does to a contour. The outline on screen doesn't move. Only the numbering does.

## Step 2: Arithmetic that goes round

After the turn, where is `e`? It was at position 4, the ring turned by 2, so it's at 2. Where is `a`? It was at 0, and 0 minus 2 is −2, which isn't a position you'd want to say out loud. It's at 4.

Python has an operator for arithmetic that goes round. `%` gives the remainder of a division:

```python
print(7 % 6, 6 % 6, (0 - 2) % 6)
```

```text
1 0 4
```

Seven steps round a ring of six land on position 1. Six steps land where you began. Two steps back from 0 land on 4. A clock does this with twelve, and you've done it all your life.

So when a ring of `count` nodes turns to start at `start`, the node that was at `old` moves to `(old - start) % count`.

Now turn the question round, because the script needs it the other way. Some node sits at position `here`. You want it at position `there`. Which `start` does that?

```python
def new_start(here, there, count):
    return (here - there) % count
```

## Step 3: The mistake

Mira's first version had the subtraction the other way round, `(there - here) % count`. It looks as reasonable as the right one. So test it on the ring before it touches a font. Put `e`, which is at 4, at position 1:

```python
start = (1 - 4) % 6
turned = ring[start:] + ring[:start]
print(start, turned, turned.index("e"))
```

```text
3 ['d', 'e', 'f', 'a', 'b', 'c'] 1
```

The last number comes from `index`, which chapter 86 used to ask a list where a value sits. That one happens to work. Try to put `e` at position 0, with the wrong formula and then with the right one:

```python
for start in [(0 - 4) % 6, (4 - 0) % 6]:
    turned = ring[start:] + ring[:start]
    print(start, turned.index("e"))
```

```text
2 2
4 0
```

The wrong formula leaves `e` at 2. It passed the first test by luck: on a ring of six, a turn of three is the same in both directions. One test that passes isn't a proof, and a test with a number that sits in the middle of the ring is a poor test. `index`, by the way, gives the position of the first thing in a list that equals what you ask for.

A wrong sign in a font would have turned every faulty contour further from where it should be, and the report would still have said "1 contour moved".

## Step 4: Which node should be the same?

The script needs a node it can recognise in every master. Positions differ between masters, so "the node at 255, −10" is no use. Fly's choice is the lowest node on the outline, and the leftmost of them if there are several:

```python
import fly.ap.contours.writer as outline
import fly.ap.core.scripting as scripting
import fly.ap.fontui.outline_order as order
import fly.ap.masters.inspect.model as masters_model

package = scripting.current_package()
layer = package.findName("e").findLayer("Regular")
contour = masters_model.own_contours(layer)[0]
points = outline.node_points(contour)
print(len(points), order.bottom_left(points), points[12])
```

```text
23 12 (255.0, -10.0, True)
```

`own_contours` gives the contours drawn in this layer, without those borrowed from other glyphs. `node_points` gives each node as a tuple of x, y and whether it's on the outline. `bottom_left` gives the position, in that list, of the lowest node. In the Regular `e` it's number 12 of 23, the bottom of the bowl.

If the Bold's lowest node is also number 12, the two rings start at the same corner. If it's number 6, the Bold's ring was turned, and `new_start(6, 12, 23)` says where it has to start to put things right.

## The whole script

```python
#FLM: Start Points
# Finds contours that start at a different node than in the master
# you're looking at, and moves the start to match.
from fly import fl, qt
import fly.ap.contours.writer as outline
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.fontui.outline_order as order
import fly.ap.masters.inspect.model as masters_model
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


# Chapter 39's tell, written out again so this script runs by itself.
def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


DRY_RUN = True
SKIP = ["Oslash"]


def new_start(here, there, count):
    return (here - there) % count


def plan(glyph, trusted, master):
    steps = []
    model = masters_model.own_contours(glyph.findLayer(trusted))
    contours = masters_model.own_contours(glyph.findLayer(master))
    for number, (good, contour) in enumerate(zip(model, contours), 1):
        points = outline.node_points(contour)
        there = order.bottom_left(outline.node_points(good))
        here = order.bottom_left(points)
        if here is None or here == there or not contour.closed:
            continue
        start = new_start(here, there, len(points))
        if not points[start][2]:
            print(f"{glyph.name} {master} contour {number}: by hand, node {start} is a handle")
            continue
        steps.append((number, contour, start))
    return steps


def main():
    package = scripting.current_package()
    if package is None:
        tell("Open a font first.")
        return
    trusted = package.master
    others = [m for m in masters_model.master_order(package) if m != trusted]
    moves = []
    for font_glyph in fl.CurrentFont().glyphs:
        if font_glyph.name in SKIP:
            continue
        glyph = package.findName(font_glyph.name)
        signatures, ok, problems = masters_model.check_glyph(glyph, [trusted] + others)
        if not ok or signatures[trusted] is None:
            continue
        for master in others:
            layer = glyph.findLayer(master)
            for number, contour, start in plan(glyph, trusted, master):
                print(f"{glyph.name} {master} contour {number}: start at node {start}")
                moves.append((glyph, layer, contour, start))
    print(f"{len(moves)} contours start somewhere else than in {trusted}.")
    if DRY_RUN:
        print("Dry run. Nothing was changed.")
        return
    if not moves:
        return

    def change():
        for glyph, layer, contour, start in moves:
            if contour.setStartPoint(start) is False:
                raise RuntimeError(f"FontLab refused the start node in {glyph.name}.")

    glyphs = []
    layers = []
    for glyph, layer, contour, start in moves:
        if glyph not in glyphs:
            glyphs.append(glyph)
        if layer not in layers:
            layers.append(layer)
    facts = history.scan_auto_facts(package)
    history.commit("Match start points", layers, glyphs, change,
                   operation="geometry", facts=facts, allow_bases=True)

main()
```

Save it as `start_points.py`. On Plum as it came, with the Regular showing:

```text
0 contours start somewhere else than in Regular.
Dry run. Nothing was changed.
```

Notes on the listing.

The master you're looking at is the one the script trusts. The others are brought into line with it. Look at the right master before you run.

Glyphs that failed yesterday's check are passed over, and so are the automatic ones. Moving a start point in a contour whose masters have different node counts would repair nothing.

A start point has to be a node on the outline. If the arithmetic lands on a handle, the lowest node isn't the same node in both masters after all, and the script says `by hand` and leaves it.

The change itself is `contour.setStartPoint(start)`. The loop only collects the moves, as chapter 68 collected its rows, and one `change` makes them all, so a run is one Undo step however many contours it turns. The call answers `False` when FontLab won't do it, and the script turns that into an error, which takes every move of the run back with it. `glyphs` and `layers` are built with `not in` because one glyph can have a move in two masters, and each belongs in the list once.

Run it with the Font window in front. Fly refuses a change to many glyphs from a Glyph window, with a message that begins `Switch to the Font window first`, because Undo there only reaches the glyphs that window shows.

The commit carries `allow_bases=True`. Without it Fly refuses any glyph that other glyphs are built from automatically, with a message that begins `Refused.` and says `base of auto`, and the `e` is such a glyph: `eacute` and three more borrow it. The refusal has a reason. When a base changes, FontLab rebuilds the glyphs that borrow it, and Fly's own notes say Undo may not put their anchors back as they were. A turned start point doesn't change the outline, so the rebuilt glyphs should look as before. I haven't watched it happen. Save the font before a real run, and afterward look at one borrower of each glyph the script names.

`SKIP` has one name in it. Empty the list and run, and you get:

```text
Oslash Bold contour 1: start at node 20
```

Nothing is wrong with the `Oslash`. Its slash pokes out below the bowl at the left, and at the bottom the bowl itself dips under the baseline. In the Regular the bowl is lower by a few units, in the Bold the tip of the slash is. The lowest node is a different node, the script takes that for a turned ring, and its cure would cause the twist it was written to prevent. "The lowest node" is a guess about which node is which, and it was right for 170 of Plum's 171 contours. Read the dry run, look at each glyph it names, and put the false alarms in `SKIP`.

## Break it on purpose

Go to the Bold of `e`, select a node on the outline a few nodes away from the start, and choose **Contour > Set Start Point**. I believe that's where the command is. If it isn't, right-click the node. Switch back to the Regular, bring the Font window to the front, and run:

```text
e Bold contour 1: start at node 17
1 contours start somewhere else than in Regular.
Dry run. Nothing was changed.
```

Your node number depends on the node you picked. Set `DRY_RUN = False`, run, set it back to `True`, and run once more. The second run should print 0. That second run is the test: the script found its own repair in order.

## What the script doesn't do

It doesn't look at the order of the contours. If the Light keeps the bowl of the `e` first and the Bold keeps the bar first, and both have as many nodes, nothing here notices. I found no call that reorders contours and is known to work, so that repair stays in the Glyph window.

It doesn't look at direction either. Chapter 45 measured that for one master. A contour that runs clockwise in one master and the other way in the next twists as surely as a turned ring.

## What you learned

A contour is a ring stored as a list, the start point is the node at position 0, and masters mix properly only when that node is the same corner in each. A ring turns by gluing two slices together in the other order, and `%` does the arithmetic of positions that go round. A formula should be tested on a small made-up ring with more than one case, since one passing test can be luck. The lowest node is a useful guess at "the same node" and it is sometimes wrong, so the script proposes and you read before you let it write.

## Try it yourself

1. A contour has 23 nodes and should start at the node now at 20. Where will the node now at 3 end up? Work it out, then check with a list made by `list(range(23))`.
2. Write `turned_back(ring, start)` that undoes a turn. Test it on the ring of letters.
3. Change the script so that it trusts the master named in a constant at the top, and not the one on screen. Which is safer, and for whom?

## Next

Chapter 104 puts the widths of every glyph in every master into one table, a dictionary whose values are dictionaries.
