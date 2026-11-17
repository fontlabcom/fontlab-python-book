---
this_file: src_docs/md/part3-shapes/043-coordinates.md
---

# 43. Coordinates

Wednesday. Mira has two glyphs side by side in a Glyph window, the `H` and the `O`, and she's zoomed in on their tops. The `O` pokes up a little above the `H`. She knows why. A round shape that stops at the very height of a flat one looks too short, so every type designer lets the rounds go a touch over. It's called overshoot.

"How much is it in Plum?" she asks. "And is it the same everywhere?"

She could click on the top node of the `O`, read its position, write it down, click on the `H`, and so on through the alphabet. That's fifty-two clicks for the capitals alone. You already know a better way. Every node carries an `x` and a `y`, and for two chapters you've only printed them. Today you'll do arithmetic with them.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`, with `node_counts` from the last chapter.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel.

## Step 1: Highest and lowest

Start with the `H`. Collect the `y` of every node in the Regular master, and ask for the smallest and the largest:

```python
import halfmoon
from fly import fl

font = fl.CurrentFont()
nodes = halfmoon.rich(font, font["H"]).nodes("Regular")
ys = [node.y for node in nodes]
print(min(ys), max(ys))
```

```text
0.0 688.0
```

The line that starts with `nodes` is the pattern from chapter 42: the plain glyph goes into the well-equipped box, and the box hands over the nodes of a layer you name. The line after it is a comprehension that keeps one number from each node. `min` and `max` you met in chapter 36. Given a list of numbers, they need no key.

So the `H` stands on the baseline, at 0, and reaches 688. Change `"H"` to `"O"` and run it again:

```text
-10.0 698.0
```

There's Mira's answer for one pair. The `O` goes 10 units over at the top and 10 under at the bottom. Its overshoot is 10.

Notice what kind of measuring this is. `y` counts up from the baseline, so a height is a `y`, and a depth is a negative one. You didn't have to subtract anything.

## Step 2: The box

Do the same for `x`, and you have four numbers:

```python
xs = [node.x for node in nodes]
print(min(xs), min(ys), max(xs), max(ys))
```

For the `H`:

```text
76.0 0.0 602.0 688.0
```

Left, bottom, right, top. Those four numbers describe the smallest upright rectangle that the glyph's outline fits inside. It's called the bounding box, and you'll meet it everywhere in font work.

Look at the first number, 76. In chapter 35 you asked the `H` for its left sidebearing and got 76. That's no coincidence. The left sidebearing is the distance from the left edge of the glyph's space, where `x` is 0, to the leftmost point of the outline. The right sidebearing is what's left over on the other side: the `H` is 672 wide, the outline ends at 602, and 672 − 602 is 70, the number chapter 35 gave you. So the sidebearings you've been reading since Part 2 are computed from the box and the width. There's nothing more to them.

A word of caution about what goes into the box. We used every node, handles too. A handle can stick out beyond the outline it controls, and then this box would be a little too big. In a carefully drawn font each curve has a node on the line at its highest, lowest, leftmost and rightmost point, and then the handles never stick out. Plum is drawn that way. I checked every glyph, and the box of all nodes and the box of on-line nodes are the same.

## Step 3: When there's nothing to measure

Put it in the module, so that any script can ask for a glyph's box:

```python
def box(font, glyph, master="Regular"):
    nodes = rich(font, glyph).nodes(master)
    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    return min(xs), min(ys), max(xs), max(ys)
```

Reload the module as in the last chapter and try it on a glyph that's built from others:

```python
print(halfmoon.box(font, font["eacute"]))
```

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File ".../site-packages/halfmoon.py", line 104, in box
    return min(xs), min(ys), max(xs), max(ys)
ValueError: min() arg is an empty sequence
```

Read it from the bottom, as chapter 3 taught you. `min` was given an empty list. The `é` has no nodes of its own, so `xs` is empty, and there's no smallest number among none. It's the same kind of trouble as dividing by zero yesterday: a question that has no answer when the count is zero.

What should `box` do with such a glyph? It can't invent four numbers. Zeros would be a lie, because a glyph with a box at 0, 0, 0, 0 is not the same as a glyph with no box. Python has a value for "there isn't one", and you've used it since chapter 6: `None`.

```python
def box(font, glyph, master="Regular"):
    nodes = rich(font, glyph).nodes(master)
    if not nodes:
        return None
    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    return min(xs), min(ys), max(xs), max(ys)
```

Now the function gives either a tuple of four numbers or `None`, and every caller has to be ready for both. Chapter 39 made the same bargain when a dialog could be cancelled. The caller checks before it unpacks:

```python
found = halfmoon.box(font, font["eacute"])
if found is None:
    print("no outline")
else:
    left, bottom, right, top = found
    print(top)
```

```text
no outline
```

## Step 4: What the font says

So the `H` is 688 tall. Is that what it's supposed to be?

A font keeps a few heights written down, apart from any glyph: the cap height, the x-height, how far ascenders rise and descenders drop. You see them in the Glyph window as horizontal lines across the drawing. They belong to a master, since a bold may be a little taller than a light. A script can read them:

```python
from fly.tr.proxy.fl.objects.font import pFont

metrics = pFont().fontMetrics()
print(metrics.getCapsHeight("Regular"))
print(metrics.getXHeight("Regular"))
print(metrics.getAscender("Regular"))
print(metrics.getDescender("Regular"))
```

```text
688
478
765
-235
```

`pFont()` is the well-equipped box for the font in front, the big brother of `pGlyph()`. Its `fontMetrics()` hands you a smaller box that holds only these heights, and each question takes a master's name. If one of the four calls complains, check its spelling against the TypeRig reference before you doubt the idea.

These questions have a side effect, which I read in TypeRig's source. Asking with a master's name makes that master the current one in FontLab, and it stays the current one afterwards. We ask about the Regular only, so if you were looking at the Bold, the Font window may show the Regular when the script has finished. Nothing in the font has changed. Switch back to the master you were working in.

The cap height is 688, and the `H` reaches 688. Good. The x-height is 478. Try the lowercase `x` with the first listing and you'll get a top of 478, and `o` gives 488: ten units over again.

Now you can say what overshoot is in numbers. It's the top of a glyph minus the height it's measured against:

```python
left, bottom, right, top = halfmoon.box(font, font["O"])
print(top - metrics.getCapsHeight("Regular"))
```

```text
10.0
```

## Step 5: All the capitals

Mira's second question was whether it's the same everywhere. Let's ask all twenty-six capitals how far above or below the cap height they end.

We need to walk the alphabet. A string is a row of characters, and `for` walks it one character at a time, as it did in chapter 7:

```python
for letter in "ABC":
    print(letter)
```

```text
A
B
C
```

For each capital we'll compute the difference. Then we want the letters grouped by that difference: all the ones at 0 together, all the ones at 10 together. In chapter 22 you counted things with a dictionary, where each key held a number that went up by one. Here each key will hold a list that grows by one name. The shape is the same:

```python
CAPITALS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

cap_height = metrics.getCapsHeight("Regular")
groups = {}
for letter in CAPITALS:
    found = halfmoon.box(font, font[letter])
    if found is None:
        print(letter, "has no outline")
    else:
        left, bottom, right, top = found
        over = top - cap_height
        if over not in groups:
            groups[over] = []
        groups[over].append(letter)

for over in sorted(groups):
    print(f"{over:>4.0f}  {' '.join(groups[over])}")
```

```text
  -4  E F T Z
   0  A H I J K L M N U V W X Y
  10  B C D G O P Q R S
```

Go through the new parts slowly. `if over not in groups:` asks whether this difference has been seen before. If it hasn't, the next line starts an empty list for it. Either way, the line after that adds the letter to the list for its difference. A dictionary whose values are lists is how you sort things into piles, and you'll use it more often than almost anything else in this book.

`sorted` from chapter 10 takes a dictionary too, and hands back its keys in order. And `' '.join(...)` is the glue from chapter 25: it makes one string out of a list of strings, with a space between each pair.

Now read the result as a designer. The bottom line is what Mira expected: nine round capitals, all 10 over. The middle line is the flat ones, at cap height. `U` is there because its top is two flat stems.

The top line nobody expected. `E`, `F`, `T` and `Z` stop 4 units short of the cap height. They're the four capitals whose top is a long horizontal bar.

Is that a mistake? The script can't say. It can only say that four letters differ from the rest, and that they have something in common. Some designers do lower a long flat top by a hair, because a wide bar at full height can look heavier than a stem end. It could also be an accident that got copied from the `E` to its relatives. Mira sends Oskar a message. The answer comes after lunch: "No idea. It was like that when I got it. Proof it before you touch it."

You'll see this again and again. A script finds what's different, and a person has to decide whether different is wrong.

## The whole script

`bounds.py` puts the pieces together and does the same for the lowercase against the x-height. `halfmoon.py` gains `box` from Step 3.

```python
# Groups letters by how far their tops end above or below a font height.
# Reads only.
import halfmoon
from fly import fl
from fly.tr.proxy.fl.objects.font import pFont

MASTER = "Regular"
CAPITALS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SMALL = "acemnorsuvwxz"


def groups_by_top(font, letters, height):
    groups = {}
    for letter in letters:
        glyph = font[letter]
        if glyph is None:
            print(f"  {letter} is not in the font")
        else:
            found = halfmoon.box(font, glyph, MASTER)
            if found is None:
                print(f"  {letter} has no outline")
            else:
                left, bottom, right, top = found
                over = top - height
                if over not in groups:
                    groups[over] = []
                groups[over].append(letter)
    return groups


def show(title, height, groups):
    print(f"{title}: {height}")
    for over in sorted(groups):
        print(f"{over:>6.0f}  {' '.join(groups[over])}")


def main():
    font = fl.CurrentFont()
    if font is None:
        print("Open a font first.")
        return

    metrics = pFont().fontMetrics()
    cap_height = metrics.getCapsHeight(MASTER)
    x_height = metrics.getXHeight(MASTER)

    print(f"{font.info.familyName}, {MASTER}")
    show("cap height", cap_height, groups_by_top(font, CAPITALS, cap_height))
    show("x-height", x_height, groups_by_top(font, SMALL, x_height))


main()
```

```text
GG Plum, Regular
cap height: 688
    -4  E F T Z
     0  A H I J K L M N U V W X Y
    10  B C D G O P Q R S
x-height: 478
    -4  z
     0  u v w x
     8  r
    10  a c e m n o s
```

The lowercase tells the same story as the capitals, with one extra. The `z` is 4 short, like its big sister. The flat-topped letters sit at the x-height. The round ones are 10 over, and `m` and `n` are among them because their arches are round on top. And the `r` is 8 over, alone. Mira adds it to her list for Oskar.

`SMALL` leaves out the letters with ascenders and the dotted ones on purpose. Their tops belong to a different height, and measuring them against the x-height would only make noise. Exercise 2 is about them.

In `groups_by_top` an `if` sits inside an `else` that sits inside another `else`, which is as deep as I like to go. Each `else` holds the rest of the work. Tomorrow you'll learn a word that flattens that staircase.

## What you learned

A node's `y` is a height above the baseline and its `x` is a distance from the glyph's left edge, so `min` and `max` over a layer's nodes give the bounding box, and the sidebearings follow from the box and the width. A function that may have nothing to return should return `None`, and its callers should check for it. The font's own heights can be read for each master and compared with what's drawn. A dictionary of lists sorts things into piles.

## Try it yourself

1. Do the bottoms. Change `groups_by_top` into a function that groups by the *bottom* of the box against a height of 0, and run it on the capitals. Leave `J` and `Q` aside; they have tails. One round capital goes deeper below the baseline than the others. Which one, and by how much?
2. Measure `b d f h k l` against the ascender height, `metrics.getAscender(MASTER)`. Do they reach it? What does that tell you about what the ascender line in this font is for?
3. Add the bounding box to `anatomy.py` from chapter 41: one line that says `box: 76 0 602 688` for the `H`, or `box: none` for a glyph without an outline.

## Next

Three `if`s nested like stairs is a sign that the loop wants a way to say "this one's no good, on to the next". Chapter 44 teaches that word, and uses it to hunt for contours that were never closed.
