---
this_file: src_docs/md/part3-shapes/058-compare-two-glyphs.md
---

# 58. Compare two glyphs

Wednesday. Mira is drawing a caron, and while she draws she talks.

"The nine is the six turned upside down. The `u` is the `n` turned upside down. The closing bracket is the opening one in a mirror. That's how I made them, seven years ago. Since then I've nudged things. I don't know which pairs are still pairs."

The accented letters of the last few days can't have this trouble. A component borrows a shape, so when the `n` changes, the `ń` changes with it. But a nine made by copying the six and turning the copy is a drawing of its own from that moment. Move a node in the six and the nine stays as it was.

So today's question is whether two glyphs are the same drawing. You'll need a way to compare two lists of points, and you'll find out that "the same" needs a number attached to it.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` as chapter 49 left it.

Nothing in this chapter changes the font. The outputs below were computed from Plum's source file, not copied from FontLab's Output panel.

## Step 1: A glyph as a list of points

For comparing, a glyph is its points and nothing else. Make each node into a pair of numbers:

```python
import halfmoon
from fly import fl

font = fl.CurrentFont()


def points_of(font, name, master):
    nodes = halfmoon.rich(font, font[name]).nodes(master)
    return [(node.x, node.y) for node in nodes]


six = points_of(font, "six", "Regular")
nine = points_of(font, "nine", "Regular")
print(len(six), len(nine))
```

```text
31 31
```

The list holds every node, the ones on the outline and the handles alike. Both glyphs have 31, which is a good start. If the counts differed, we could stop here and say no.

## Step 2: When are two lists equal?

Python compares lists with `==`, the same sign it uses for numbers:

```python
print([1, 2, 3] == [1, 2, 3])
print([1, 2, 3] == [3, 2, 1])
```

```text
True
False
```

Two lists are equal when they have the same items in the same order. The same items in another order make a different list. Tuples work the same way, and so do lists of tuples: Python goes through both, pair by pair, and says `False` at the first pair that doesn't match.

```python
print(six == nine)
```

```text
False
```

One more thing about `==` before we go on. FontLab hands out coordinates as numbers with a decimal point, such as `250.0`, and you'll often type whole numbers. That makes no difference to a comparison:

```python
print([(1.0, 2)] == [(1, 2.0)])
```

```text
True
```

Python compares the values, and 1.0 is the same value as 1. What does make a difference is a coordinate of 250.4 against 250: those are two numbers, however alike the glyphs look on screen. Keep that in mind for step 4.

Nobody expected `True` for the six and the nine. One is upside down, and they sit in different places between their sidebearings. Before the lists can be compared, both glyphs have to be brought to the same place, and one of them has to be turned.

## Step 3: Bring both home

The six runs from x 45 to 450, the nine from 40 to 445. Measure every point from the bottom left corner of its own box and that difference is gone:

```python
def at_home(points, how):
    xs = [x for x, y in points]
    ys = [y for x, y in points]
    left, bottom, right, top = min(xs), min(ys), max(xs), max(ys)
    if how == "turn":
        return [(right - x, top - y) for x, y in points]
    if how == "flip":
        return [(right - x, y - bottom) for x, y in points]
    return [(x - left, y - bottom) for x, y in points]
```

The last line is the plain case. A point at the left edge gets x 0, a point at the bottom gets y 0.

The `"turn"` line measures from the opposite corner: how far left of the right edge, how far below the top. Hold a page upside down and that's what happens to every point on it. The `"flip"` line measures x from the right edge and leaves the heights alone, which is what a mirror does.

Any other word, such as `"keep"`, falls through both `if`s to the plain case.

```python
first = at_home(six, "keep")
second = at_home(nine, "turn")
print(first == second)
```

```text
False
```

Still `False`, and for a dull reason. A contour is a loop, and a loop can start anywhere. The six starts at the bottom of its bowl. The turned nine has the same points and starts somewhere else. The order in the list is an accident of where the designer clicked first.

Take the accident away by sorting both lists:

```python
print(sorted(first)[:3])
print(sorted(second)[:3])
print(sorted(first) == sorted(second))
```

```text
[(0.0, 84.0), (0.0, 260.0), (0.0, 506.0)]
[(0.0, 84.0), (0.0, 260.0), (0.0, 506.0)]
True
```

The nine is still the six, to the last handle. Try `"n"` and `"u"` and you get `True` again.

## Step 4: Nearly the same

Now the braces:

```python
left = sorted(at_home(points_of(font, "braceleft", "Regular"), "keep"))
right = sorted(at_home(points_of(font, "braceright", "Regular"), "turn"))
print(left == right)
```

```text
False
```

`False` is all `==` can say. It doesn't say whether the braces are two different drawings or one drawing with a node a hair out of place, and those call for different things from Mira. We need a distance.

For two points, take the larger of the two differences, across and up:

```python
def gap(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))
```

Then walk the two sorted lists side by side with `zip`, from chapter 35, and keep the largest gap:

```python
print(max([gap(p, q) for p, q in zip(left, right)]))
```

```text
714.0
```

Seven hundred units. That says the braces have nothing to do with each other, and one look at the Font window says otherwise. The mistake is in the method.

Print the pairs that differ:

```python
print([(p, q) for p, q in zip(left, right) if p != q])
```

```text
[((105.0, 785.0), (107.0, 71.0)), ((107.0, 71.0), (107.0, 785.0)), ((109.0, 439.0), (110.0, 439.0)), ((112.0, 710.0), (113.0, 146.0)), ((113.0, 146.0), (113.0, 422.0)), ((113.0, 422.0), (113.0, 710.0))]
```

Look at the first pair. The point at (105, 785) in one brace has a partner at (107, 785) in the other: two units apart. But sorting goes by x first. With x 105 the point comes before (107, 71) in its own list. In the other list its partner has x 107 and comes after. From there the two lists are out of step, and `zip` pairs each point with a stranger.

Sorting was fine for asking "exactly equal?". It breaks down for "how close?", because a small difference changes the order.

So don't rely on order at all. For each point, look through all the points of the other glyph and take the smallest gap. That's the distance to its nearest neighbor. The largest of those, over the whole glyph, tells how far apart the two drawings are:

```python
def farthest(points, others):
    return max([min([gap(p, q) for q in others]) for p in points])


print(farthest(left, right))
```

```text
2.0
```

Read it from the inside. `[gap(p, q) for q in others]` is the list of gaps from one point `p` to every point of the other glyph, and `min` picks the nearest. The outer list does that for every `p`, and `max` picks the point that's worst off.

Two units. The braces are one drawing, and somebody has touched one of them since. It's only the Regular, too: in the Light and the Bold the answer is 0.

This looks at 31 times 31 pairs, close to a thousand. Python doesn't mind.

## Step 5: Say how close is close enough

Now "the same" needs a number. I'll use three verdicts. A gap of 0 is `same`. Up to 3 units is `close`, which means: one drawing, with a nudge that Mira should look at. More than 3 is `differ`.

The 3 is a tolerance, and it's a judgment. I picked it because a nudge of a unit or two is what a slipped hand does, and nobody redraws a letter by three units on purpose. It goes at the top of the script as a constant, where Mira can change it.

## Step 6: Keep the pairs apart from the code

Which glyphs belong together, and whether a pair is turned or mirrored, is knowledge about Plum. It isn't Python. So it goes into a list at the top, one tuple of three words for each pair:

```python
PAIRS = [
    ("six", "nine", "turn"),
    ("parenleft", "parenright", "flip"),
]
```

The loop takes a tuple apart into three names, the way chapter 35 took rows apart:

```python
for first, second, how in PAIRS:
    print(first, second, how)
```

```text
six nine turn
parenleft parenright flip
```

Mira can add a pair without reading a line of the code below it. She can also get a name wrong, as she did yesterday, so the script checks that both glyphs exist before it measures, and says so when one doesn't. A pair that can't be measured for another reason, because one glyph is built from components and has no nodes of its own, or because the two have different numbers of points, gets `None` for a distance and its own verdict. The lesson of chapter 57 holds here too: one bad row shouldn't stop the other nine.

## The whole script

```python
#FLM: Compare Glyph Pairs
# Tells whether pairs of glyphs are still the same drawing, turned upside
# down or mirrored. Changes nothing.
import halfmoon
from fly import fl

MASTERS = ["Light", "Regular", "Bold"]
TOLERANCE = 3
PAIRS = [
    ("six", "nine", "turn"),
    ("n", "u", "turn"),
    ("b", "q", "turn"),
    ("d", "p", "turn"),
    ("parenleft", "parenright", "flip"),
    ("bracketleft", "bracketright", "flip"),
    ("braceleft", "braceright", "turn"),
    ("less", "greater", "flip"),
    ("slash", "backslash", "flip"),
    ("quoteleft", "quoteright", "turn"),
]


def points_of(font, name, master):
    nodes = halfmoon.rich(font, font[name]).nodes(master)
    return [(node.x, node.y) for node in nodes]


def at_home(points, how):
    xs = [x for x, y in points]
    ys = [y for x, y in points]
    left, bottom, right, top = min(xs), min(ys), max(xs), max(ys)
    if how == "turn":
        return [(right - x, top - y) for x, y in points]
    if how == "flip":
        return [(right - x, y - bottom) for x, y in points]
    return [(x - left, y - bottom) for x, y in points]


def gap(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def farthest(points, others):
    return max([min([gap(p, q) for q in others]) for p in points])


def apart(font, first, second, how, master):
    a = points_of(font, first, master)
    b = points_of(font, second, master)
    if not a or len(a) != len(b):
        return None
    a = at_home(a, "keep")
    b = at_home(b, how)
    return round(max(farthest(a, b), farthest(b, a)))


def verdict(gaps):
    if None in gaps:
        return "not comparable"
    worst = max(gaps)
    if worst == 0:
        return "same"
    if worst <= TOLERANCE:
        return "close"
    return "differ"


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    have = {glyph.name for glyph in font.glyphs}
    print(f"{'':<27}{'how':<6}{'L':>4}{'R':>4}{'B':>4}")
    for first, second, how in PAIRS:
        if first not in have or second not in have:
            print(f"{first:<13}{second:<14}one of them is missing")
            continue
        gaps = [apart(font, first, second, how, master) for master in MASTERS]
        numbers = "".join([f"{str(g):>4}" if g is None else f"{g:>4}" for g in gaps])
        print(f"{first:<13}{second:<14}{how:<6}{numbers}  {verdict(gaps)}")


main()
```

```text
                           how      L   R   B
six          nine          turn     0   0   0  same
n            u             turn     0   0   0  same
b            q             turn    56  52  48  differ
d            p             turn    56  52  48  differ
parenleft    parenright    flip     0   0   0  same
bracketleft  bracketright  flip     0   0   0  same
braceleft    braceright    turn     0   2   0  close
less         greater       flip     2   3   3  close
slash        backslash     flip     0   1   0  close
quoteleft    quoteright    turn     0   0   0  same
```

`apart` measures both ways, from the first glyph to the second and back, and keeps the larger number. One way alone could be fooled: if every point of the first has a neighbor in the second, the second might still have a point far from everything. `apart` also gives `None` when a glyph has no nodes of its own or when the counts differ, and `verdict` turns that into words.

## Read the report

Five pairs are what Mira thought they were.

Two differ by about 50 units in every master, and she laughs when she sees them. The `q` was never a `b` turned over. The descender is shorter than the ascender, by design, and the gap is that difference. The script reports a difference. Only a person can say that it's meant.

Three are close. In the Regular, one brace has three nodes off by a unit or two, and the backslash is a unit away from the mirrored slash. Those are slips. Mira writes them on her list.

The `less` and `greater` row is odd. It's off in all three masters, by 2, 3 and 3 units. A slip doesn't repeat itself three times. Exercise 1 looks into it.

A report like this doesn't fix anything, and it shouldn't. Which of two braces is the right one isn't something the script knows.

## What you learned

Two lists are equal when they hold the same items in the same order, and sorting takes away an order that doesn't matter. `==` answers yes or no, and for "how far off?" you need a distance and a tolerance. Sorting and pairing with `zip` fails when values are nearly equal, and a nearest-neighbor search with `min` inside `max` doesn't depend on order. A tolerance is a judgment, and it belongs in a constant with a name.

## Try it yourself

1. In `PAIRS`, change `"flip"` to `"turn"` for `less` and `greater`. I get 0, 0, 0. So the `greater` was made by turning the `less` upside down, and the `less` isn't quite the same above and below its middle. Which of the two findings would you report to Mira, and what would you ask her?
2. Add `("comma", "quoteright", "keep")` to the list. I get 20, 20 and 10. Is that a slip or a decision? Look at both glyphs in FontLab before you answer.
3. Set `TOLERANCE` to 0 and then to 60, and run the script each time. Which verdicts change? What would a tolerance of 60 hide?

## Next

Mira's list has grown since chapter 49: a dot outside its glyph, nudged braces, two accents to look at. Chapter 59 goes through the whole font for the small faults that collect in seven years, and writes them into one report.
