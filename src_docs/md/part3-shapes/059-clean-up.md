---
this_file: src_docs/md/part3-shapes/059-clean-up.md
---

# 59. Clean up

Thursday. The caron is drawn, the ogonek is half drawn, and Mira wants a day off from accents.

"Before we build sixty letters on top of this font," she says, "I'd like to know what's lying around in it."

A font that has been worked on for seven years collects small faults. A node gets dropped on top of another node. A segment three units long is left behind where two shapes were joined. None of it shows at text size. Some of it shows when the font is exported, as a kink, or as a complaint from a program further down the line.

Today's script looks for three such faults and writes them into one list. To find them you'll compare each node with its neighbor, and you'll put more than one condition into a loop. The order of the conditions turns out to matter.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `contours_of` from chapter 44. The scripts below write it out again.

The script reads the font. One step at the end marks glyphs, and it asks first. The outputs below were computed from Plum's source file, not copied from FontLab's Output panel.

## Step 1: Every node and the one before it

Chapter 42 walked along a contour node by node. A fault of the kind we're after isn't in a node. It's between two nodes, so the loop needs two at a time: each node and the one before it.

A `for node in nodes` loop gives you one. To reach the neighbor, loop over positions instead. `range(len(nodes))` counts 0, 1, 2 and so on up to the last position:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph


def contours_of(font, glyph, master="Regular"):
    return pGlyph(font, glyph).contours(master)


font = fl.CurrentFont()
contour = contours_of(font, font["Q"], "Regular")[0]
nodes = contour.nodes()
for i in range(len(nodes)):
    before = nodes[i - 1]
    here = nodes[i]
    print(i, before.x, before.y, "to", here.x, here.y)
```

```text
0 576.0 -157.0 to 440.0 6.0
1 440.0 6.0 to 440.0 6.0
2 440.0 6.0 to 578.0 43.0
...
```

I've cut the output after three lines. There are 16.

Look at the first line. When `i` is 0, `i - 1` is -1, and `nodes[-1]` is the last item of a list, as chapter 10 showed. That's what a closed contour needs. The node before the first is the last one, because the outline is a loop. No special case, and no `if`.

And look at the second line: 440, 6 to 440, 6. Two nodes sit on one spot.

## Step 2: Three questions about a pair

How far apart are two nodes? Use the measure from yesterday, the larger of the two differences:

```python
def reach(a, b):
    return max(abs(a.x - b.x), abs(a.y - b.y))
```

Now the questions. If the reach is 0, the nodes are stacked. If it's small, 3 units or less, and both nodes are on the outline, there's a segment too short to be meant. Otherwise the pair is fine.

My first try:

```python
SHORT = 3

for i in range(len(nodes)):
    a = nodes[i - 1]
    b = nodes[i]
    if reach(a, b) == 0:
        print("two nodes on one spot", a.x, a.y)
    if reach(a, b) <= SHORT and a.isOn() and b.isOn():
        print("short segment", a.x, a.y)
```

```text
two nodes on one spot 440.0 6.0
short segment 440.0 6.0
```

One fault, two lines. Zero is less than 3, so the stacked pair passes the second test as well. The two `if`s don't know about each other. Python asks each one in turn.

A report that says everything twice looks twice as bad as the font is, and Mira would have to work out which lines are echoes. The cure is `elif`:

```python
    if reach(a, b) == 0:
        print("two nodes on one spot", a.x, a.y)
    elif reach(a, b) <= SHORT and a.isOn() and b.isOn():
        print("short segment", a.x, a.y)
```

```text
two nodes on one spot 440.0 6.0
```

With `elif`, Python asks the second question only when the answer to the first was no. The two tests now form a ladder, and a pair stops at the first rung that fits. So put the narrowest test at the top. Turn these two around and the stacked nodes would be reported as a short segment, which is true and less useful.

The second test has three parts joined by `and`. All three must hold. The two `isOn()` calls are there because a segment runs between two nodes on the outline. A handle that sits close to its node is a different thing, a tight curve, and often it's drawn that way on purpose.

## Step 3: Open contours don't wrap

The trick with `nodes[-1]` treats every contour as a loop. An open contour isn't one. Its last node and its first aren't joined, and they may well lie close together: that's what an outline looks like when someone forgot to close it. The pair at position 0 mustn't be tested there.

```python
if i == 0 and not contour.closed:
    continue
```

Read it aloud: "if this is the first position and the contour is not closed, skip." `not` turns a yes into a no. `and` wants both sides.

Plum has no open contours, unless the one you planted in chapter 44 is still there, so this line does nothing today. It's there for the font that has some. A check that's right only for the font on your desk will be wrong for the next one.

## Step 4: A check that cries wolf

I had a fourth check in mind. In chapter 49, the third dot of the Bold ellipsis sat outside the glyph's width. So why not list every glyph whose outline reaches left of 0 or right of its advance width?

```python
edges = box(font, glyph, master)
if edges is not None and (edges[0] < 0 or edges[2] > width):
    print(glyph.name)
```

The parentheses matter. Without them, Python would read `edges is not None and edges[0] < 0` as one group and `edges[2] > width` as another, because `and` binds tighter than `or`, and a glyph with no box would crash on `edges[2]`.

In the Regular the check names 10 glyphs: `J`, `K`, `T`, `Y`, `f`, `j`, `backslash`, `comma`, `slash` and `dieresis`. In the Bold it names 44.

Mira looks at the list for a few seconds. "The `f` hangs over on purpose. So does the `j`, and the `J`. The `T` and the `Y` have their arms out by design. That's how letters fit together."

The numbers also tell a story of their own: 6 in the Light, 10 in the Regular, 44 in the Bold. The heavier the letter, the less room it has inside its width, and the more of it leans out. That's a property of bold type.

The test is correct and the list is useless. Forty-four names, nearly all of them fine, and somewhere among them perhaps one real fault that nobody will find, because nobody reads a list like that twice. I took the check out. A check earns its place when most of what it reports needs doing. If you can't tell a fault from a decision with a test, leave it to the eye.

## Step 5: Mixed glyphs

One line on Oskar's sheet has waited since chapter 1: "Mark every glyph that mixes its own outlines with borrowed ones." Chapter 52 found them by reading a list. Here's the test, with the components module from that chapter:

```python
if contours and parts.components(layer):
    ...
```

A list is true when it has something in it. So this reads: "if there are contours and there are components".

## The whole script

Each finding is a tuple of glyph name, master and a sentence, kept in a list as in chapter 57.

```python
#FLM: Tidy Report
# Looks for stacked nodes, short segments and glyphs that mix their
# own outlines with components. Prints a list. Marks the glyphs if asked.
import fly.ap.components.writer as parts
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box
from fly.pens import layer_of
from fly.tr.proxy.fl.objects.glyph import pGlyph

MASTERS = ["Light", "Regular", "Bold"]
SHORT = 3
VIOLET = 270
TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


def contours_of(font, glyph, master="Regular"):
    return pGlyph(font, glyph).contours(master)


def reach(a, b):
    return max(abs(a.x - b.x), abs(a.y - b.y))


def pair_faults(contour):
    faults = []
    nodes = contour.nodes()
    for i in range(len(nodes)):
        if i == 0 and not contour.closed:
            continue
        a = nodes[i - 1]
        b = nodes[i]
        far = reach(a, b)
        if far == 0:
            faults.append(f"two nodes on one spot, {a.x:.0f} {a.y:.0f}")
        elif far <= SHORT and a.isOn() and b.isOn():
            faults.append(f"segment of {far:.0f} units at {a.x:.0f} {a.y:.0f}")
    return faults


def glyph_faults(font, glyph, master):
    found = []
    contours = contours_of(font, glyph, master)
    layer = layer_of(fl.flGlyph(glyph, font), master)
    if contours and parts.components(layer):
        found.append("own outline and a component")
    for number, contour in enumerate(contours, 1):
        for text in pair_faults(contour):
            found.append(f"contour {number}: {text}")
    return found


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    findings = []
    for glyph in font.glyphs:
        for master in MASTERS:
            for text in glyph_faults(font, glyph, master):
                findings.append((glyph.name, master, text))

    for name, master, text in findings:
        print(f"{name:<12}{master:<9}{text}")
    names = []
    for name, master, text in findings:
        if name not in names:
            names.append(name)
    print(f"{len(findings)} findings in {len(names)} glyphs.")

    if not names:
        return
    if not ask(f"Mark these {len(names)} glyphs violet?"):
        return
    for name in names:
        pGlyph(font, font[name]).mark = VIOLET


main()
```

```text
Q           Light    contour 1: segment of 3 units at 394 -6
Q           Regular  contour 1: two nodes on one spot, 440 6
Q           Bold     contour 1: two nodes on one spot, 495 13
exclam      Light    own outline and a component
exclam      Regular  own outline and a component
exclam      Bold     own outline and a component
exclamdown  Light    own outline and a component
exclamdown  Regular  own outline and a component
exclamdown  Bold     own outline and a component
9 findings in 3 glyphs.
```

Three functions, each a level deeper: `main` walks glyphs and masters, `glyph_faults` walks the contours of one layer, `pair_faults` walks the nodes of one contour. Each hands a list back to the one above. Written as one piece, this would be a loop in a loop in a loop in a loop, with the tests at the bottom of the stairs.

Two small things in `main` are worth a look.

`enumerate(contours, 1)` from chapter 57 numbers the contours, so that a finding can say "contour 2". People count from 1, and the Glyph window won't show Mira a contour number at all, so the position that's printed after it matters more: she can click there.

The loop that fills `names` collects each glyph name once, in the order of the font. `if name not in names` asks the list whether it already has the name, and only a new name gets in. A set would drop the repeats too, as chapter 25 did, but a set forgets the order, and here the order is the one in the Font window.

The marking is the only change the script makes, and it comes after a question. As chapter 14 said, don't count on **Edit > Undo** for marks. Violet is a color Halfmoon hasn't used for anything yet.

## Read the report

Nine findings sounds like a lot, and it's three things. That's usual. Faults come in families: one slip of the hand shows up in every master, and one old habit shows up in every glyph it touched. Read a report for its families before you count its lines.

The `Q` has one stray node. It's the same node in all three masters, at the spot where the tail meets the bowl. In the Regular and the Bold it lies on top of its neighbor. In the Light it has drifted 3 units away. Had the script looked for stacked nodes only, the Light would have come out clean, and somebody would have removed the node from two masters and left it in the third. Then the three masters would no longer have the same number of nodes, and FontLab couldn't blend between them. Mira removes the node by hand, in all three masters, in the Glyph window. It takes her a minute.

That's why this script reports and doesn't repair. Deleting a node takes one line. Knowing that it must go from every master at once, and checking that the curve keeps its shape, is the work, and for one node the hand is faster and safer.

The `exclam` and the `exclamdown` are the two mixed glyphs. They're marked now. Mira crosses out the line on Oskar's sheet. Six of the eleven lines are done.

## What you learned

`range(len(things))` loops over positions, and `things[i - 1]` reaches the neighbor. At position 0 it wraps around to the last item, which suits a closed loop and has to be guarded for an open one. Two `if`s are two separate questions, `if` and `elif` are one ladder with the narrowest test on top, and `and` binds tighter than `or`, so use parentheses when you mix them. A check that reports mostly decisions and few faults does harm, because it teaches people to stop reading.

## Try it yourself

1. Set `SHORT` to 10 and run the report without marking. Do you get more findings? Open one in the Glyph window and decide whether it's a fault.
2. Swap the `if` and the `elif` test in `pair_faults`, so that the short-segment test comes first. What does the report say about the `Q` now, and what has been lost?
3. Add a count by kind at the end, with a dictionary as in chapter 22: how many findings are stacked nodes, how many short segments, how many mixed glyphs? You can tell the kind from a word in the sentence, with `in`.

## Next

The font is tidy, the caron and the ogonek are drawn, and the recipe file is waiting. Chapter 60 puts the pieces of this part into one script and builds the Czech and Polish letters in an afternoon.
