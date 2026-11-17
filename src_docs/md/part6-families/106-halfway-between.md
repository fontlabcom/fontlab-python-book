---
this_file: src_docs/md/part6-families/106-halfway-between.md
---

# 106. Halfway between

Monday of week twenty-one. The art director's note from last Monday is still pinned over Mira's desk: "The Regular is a little light for the ingredient lists, and the Bold is too heavy for them. Could there be something in between?"

"A Medium", Mira says. "Halfway between Regular and Bold. FontLab can do that, I've seen Oskar do it."

It can, and chapter 110 will ask it to. But first I'd like you to do it yourself, with a pencil's worth of arithmetic, on the plainest glyph in the font. When a weight comes out wrong three weeks from now, you'll want to know what sum was done, and it's a small one.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- Chapter 102's result: every glyph you compare has the same skeleton in all three masters.

I couldn't run the code in FontLab 9. The sums are plain Python and I ran those. The glyph's coordinates come from Plum's source file.

## Step 1: One number

Plum's hyphen is a rectangle, as chapter 50 found. In the Regular its bottom edge is at y 246. In the Bold it's at 228. Where is it halfway?

You don't need a computer for that: 237. Say how you got it, though. You took the distance from one to the other, which is 228 minus 246, or −18. You took half of it, −9. You added that to where you started.

```python
def lerp(a, b, t):
    return a + (b - a) * t

print(lerp(246, 228, 0.5))
```

```text
237.0
```

That's the whole of interpolation. `a` is where you start, `b` is where you'd end, and `t` says how much of the way you go: 0 for none of it, 1 for all of it, 0.5 for half. The name `lerp` is what programmers call it, short for "linear interpolation", and you'll meet it in other people's code.

Try the ends, to be sure the function does what the sentence says:

```python
print(lerp(246, 228, 0), lerp(246, 228, 1))
```

```text
246 228
```

## Step 2: The mistake

Now the Medium. In Plum the weights have numbers: Light is 300, Regular is 400, Bold is 700. Chapter 101 printed them. A Medium is 500 by long custom. So:

```python
print(lerp(246, 228, 500))
```

```text
-8754
```

The bottom of the hyphen is nearly nine thousand units below the baseline. Nothing stopped the sum. `lerp` did what it was told: it went 500 times the distance from Regular to Bold.

The 500 is a place on the weight scale. `t` is a share of the way from one master to the other. They're different kinds of number, and the function can't tell, since both are numbers.

## Step 3: From a weight to a share

How much of the way from 400 to 700 is 500? It's 100 along a road of 300. A third.

```python
def share(value, low, high):
    return (value - low) / (high - low)

print(share(500, 400, 700))
```

```text
0.3333333333333333
```

`share` is `lerp` run backward. `lerp` takes a share and gives a place. `share` takes a place and gives the share. Put one inside the other:

```python
t = share(500, 400, 700)
print(lerp(246, 228, t), lerp(294, 312, t))
```

```text
240.0 300.0
```

The Medium's hyphen runs from 240 to 300, so it's 60 thick. The Regular's is 48 and the Bold's is 84.

And here's what the arithmetic tells Mira that her eye hadn't. She said "halfway", and 500 is a third of the way. Halfway between 400 and 700 is 550, and its hyphen would be 66 thick. Whether the chapter titles want 60 or 66 is hers to judge. But she now knows that the word and the number meant two different fonts.

## Step 4: A whole outline

A glyph is a lot of numbers, and each one gets the same sum with the same `t`. Fly reads a layer's outline as a list of contours, each a list of `(x, y, on)` tuples, the form chapter 103 used:

```python
import fly.ap.core.scripting as scripting
import fly.ap.masters.interpolation.model as interpolation
from fly.pens import layer_of

package = scripting.current_package()
glyph = package.findName("hyphen")
regular = interpolation.outline(layer_of(glyph, "Regular"))
bold = interpolation.outline(layer_of(glyph, "Bold"))
print(regular)
print(bold)
```

```text
[[(56.0, 246.0, True), (292.0, 246.0, True), (292.0, 294.0, True), (56.0, 294.0, True)]]
[[(56.0, 228.0, True), (292.0, 228.0, True), (292.0, 312.0, True), (56.0, 312.0, True)]]
```

One contour, four nodes, in both. Node 1 of the Regular goes with node 1 of the Bold, node 2 with node 2. That's `zip`, twice: once to pair the contours, once to pair the nodes inside each pair.

```python
def between(first, second, t):
    result = []
    for one, other in zip(first, second):
        contour = []
        for (x1, y1, on), (x2, y2, also_on) in zip(one, other):
            contour.append((round(lerp(x1, x2, t)), round(lerp(y1, y2, t)), on))
        result.append(contour)
    return result
```

Now you can see why chapters 102 and 103 mattered. `zip` pairs by position and asks no questions. If the Bold had five nodes, `zip` would stop at four and the fifth would vanish. If the Bold's contour started at another corner, each node would travel toward the wrong partner, and the rectangle would fold on its way. The sum is innocent. The pairing is where glyphs go wrong.

So the script asks before it pairs. `interpolation.problem(a, b)` gives `None` when two outlines can be paired, and a sentence when they can't.

Handles get the same treatment as nodes. A handle is a pair of numbers, and it moves a third of the way toward its partner like everything else. That's why a curve between two masters stays a curve.

## The whole script

```python
#FLM: Lerp
# Works out one glyph between two masters, by hand. Changes nothing.
import fly.ap.core.scripting as scripting
import fly.ap.masters.interpolation.model as interpolation
from fly import fl, qt
from fly.pens import layer_of
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


# Chapter 39's tell, written out again so this script runs by itself.
def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


GLYPH = "hyphen"
LOW = "Regular"
HIGH = "Bold"
WEIGHT = 500


def lerp(a, b, t):
    return a + (b - a) * t


def share(value, low, high):
    return (value - low) / (high - low)


def weight_of(package, master):
    axis = package.axes[0]
    return float(package.location(master)[axis.shortName])


def between(first, second, t):
    result = []
    for one, other in zip(first, second):
        contour = []
        for (x1, y1, on), (x2, y2, also_on) in zip(one, other):
            contour.append((round(lerp(x1, x2, t)), round(lerp(y1, y2, t)), on))
        result.append(contour)
    return result


def main():
    if fl.CurrentFont() is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    glyph = package.findName(GLYPH)
    if glyph is None:
        tell(f"There is no glyph named {GLYPH}.")
        return
    low_layer = layer_of(glyph, LOW)
    high_layer = layer_of(glyph, HIGH)
    low = interpolation.outline(low_layer)
    high = interpolation.outline(high_layer)
    reason = interpolation.problem(low, high)
    if reason:
        print(f"{GLYPH}: {LOW} and {HIGH} don't match, {reason}")
        return
    t = share(WEIGHT, weight_of(package, LOW), weight_of(package, HIGH))
    print(f"{GLYPH} at {WEIGHT}: t is {t:.3f}, from {LOW} to {HIGH}")
    for number, contour in enumerate(between(low, high, t), 1):
        for x, y, on in contour:
            kind = "node" if on else "handle"
            print(f"  contour {number}: {x:>5} {y:>5}  {kind}")
    width = round(lerp(low_layer.advanceWidth, high_layer.advanceWidth, t))
    print(f"  width {width}")


main()
```

Save it as `lerp.py` and run it:

```text
hyphen at 500: t is 0.333, from Regular to Bold
  contour 1:    56   240  node
  contour 1:   292   240  node
  contour 1:   292   300  node
  contour 1:    56   300  node
  width 348
```

Notes on the listing.

`weight_of` asks the font where a master sits on its first axis. Plum has one axis, so the first is the only one. I read this route in Fly's own code, which uses it to put the masters in order. I haven't seen the numbers come back in FontLab 9, and if yours aren't 400 and 700, the first line of output will show it.

The width is one more number, and it gets the same `lerp`. Kerning does too, and anchors. A master is a long list of numbers, and the font between two masters is the same sum done on every one of them.

`between` rounds, because a font's coordinates are whole units. The sum itself gives 240.0 here, since a third of 18 is 6. With other numbers it gives a long tail, and what the rounding does to two nodes that should stay level is a thing to look at in a proof.

`LOW` and `HIGH` are two masters, and Plum has three. Which two? The pair on either side of the weight you want. 500 lies between 400 and 700, so it's Regular and Bold. A 350 lies between 300 and 400, so it would be Light and Regular. The Light has no say in the Medium at all. A family with three masters is two roads that meet at the Regular, and each weight is on one of them. The script trusts you to pick the right pair, and the Break it section shows what the wrong pair does.

It also explains a thing you may have wondered about in chapter 104. The figures were 490 wide in the Regular and in the Bold, and 456 in the Light. On the road from Regular to Bold a figure's width doesn't move, whatever `t` is. On the other road it does.

The script changes nothing. It prints what an in-between glyph would be. Drawing it into the font is chapter 110's work.

## Break it on purpose

The scale has room below the Light. A Thin is 100 by custom. Set `LOW = "Light"`, `HIGH = "Regular"` and `WEIGHT = 100`, and run:

```text
hyphen at 100: t is -2.000, from Light to Regular
  contour 1:    56   276  node
  contour 1:   292   276  node
  contour 1:   292   264  node
  contour 1:    56   264  node
  width 348
```

Read the y values. The first two nodes were the bottom edge and they're at 276. The last two were the top and they're at 264. The bottom is above the top. The hyphen has turned inside out.

`t` is −2: go twice the distance, the other way. From Regular to Light the bar loses 20 units of thickness, 48 down to 28. Go that far twice more and it loses another 40, which is 12 more than it had.

Nothing raised an error, and the outline still has four nodes in the right order, so chapter 102's check would pass it. Going beyond the masters is called extrapolation, and the sum allows it without complaint. A share between 0 and 1 stays between drawings somebody made. Outside that range you get a guess, and on thin strokes the guess goes wrong fast.

Put the three constants back.

## What you learned

Interpolation is one sum, `a + (b - a) * t`, done on every coordinate, width and kerning value with the same `t`. A weight like 500 has to be turned into a share of the way between two masters before it can be used, and "halfway" and "Medium" turned out to be different shares. The sum pairs numbers by position, so it's only as good as the matching skeletons of chapters 102 and 103. A share below 0 or above 1 still gives an answer, and nothing warns you when the answer is a glyph turned inside out.

## Try it yourself

1. Fly has its own blend: `interpolation.blend(low, high, t)`. In `main`, print its result next to yours. It doesn't round. For the hyphen at 500 the two should agree but for the `.0`. Then try `WEIGHT = 475`. The sum gives 241.5 and 298.5, and `round` sends both halves to the even neighbor, 242 and 298. How thick is the bar before the rounding, and after?
2. Set `GLYPH = "period"`. The dot has curves, so the output has handles. Check one handle with a calculator: read its position in the Regular and in the Bold from two runs with `WEIGHT = 400` and `WEIGHT = 700`, and go a third of the way.
3. Set `LOW = "Light"`, `HIGH = "Bold"` and `WEIGHT = 400`. That asks for a Regular made from the two outer masters. The sum gives a hyphen from 249 to 291, 42 thick. The Regular that was drawn is 48 thick. What does that tell you about why Plum has a third master at all?

## Next

Chapter 107 reads what the font itself knows about its weight scale: the axis, where each master sits on it, and the list of weights it has been told to produce.
