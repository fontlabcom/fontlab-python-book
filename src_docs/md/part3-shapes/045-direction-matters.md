---
this_file: src_docs/md/part3-shapes/045-direction-matters.md
---

# 45. Direction matters

Friday of the eighth week. Mira asks a question that sounds childish and isn't: "How does the `o` know it has a hole?"

Think about what the font holds. It holds two closed lines, a big oval and a small oval. Nothing in either says "I'm the outside" or "I'm the hole". If you filled both with black, you'd get a black disc with a blacker disc in the middle, which is to say a blob. Yet the `o` prints with white in its center, every time, on every machine.

The answer is a property of a contour that you can't see in the finished letter. A contour runs in a direction. Its nodes come in an order, as you saw in chapter 41 when the list went from the bottom of the oval to the right, the top and the left. That order goes round the shape one way or the other. Today you'll read it, break it on purpose, and write a check for the kind of damage that your eyes won't catch.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `box` and `contours_of` from the last two chapters. You'll write them out again here.
- The `o` open in a Glyph window, Regular master.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The directions quoted for Plum were worked out the same way. The drawer that reports direction, `clockwise`, is taken from FontLab's list of names.

## Step 1: Which way round

Ask the two contours of the `o`:

```python
from fly.tr.proxy.fl.objects.glyph import pGlyph

glyph = pGlyph()
for contour in glyph.contours():
    print(len(contour.nodes()), contour.clockwise)
```

```text
12 False
12 True
```

The outer oval doesn't run clockwise, so it runs the other way, which is called counter-clockwise. The inner oval runs clockwise. They go in opposite directions.

You can check the first with the node list from chapter 41. The outer contour went from the bottom, at 260, −10, to the right side, at 482, 239, then to the top and then to the left. Trace that with a finger on the `o`: bottom, right, top, left. Your finger moves against the clock.

`clockwise` is a drawer and not an action, so it takes no parentheses. If you add them out of habit from the last few chapters, you'll get the opposite of the complaint in chapter 41:

```python
print(contour.clockwise())
```

```text
TypeError: 'bool' object is not callable
```

`contour.clockwise` is already the answer, `True` or `False`. Python calls those two values `bool`. Putting parentheses after an answer asks Python to run it as if it were a function, and "not callable" means it can't be run. So now you know both halves. A method without parentheses gives you `'method'` trouble, and a value with parentheses gives you `not callable`.

## Step 2: Why opposite makes a hole

Here's the rule the machine uses to decide what's black. Imagine walking across the letter in a straight line from far outside, keeping a number in your head that starts at zero. Each time you cross a contour that runs one way, add one. Each time you cross a contour that runs the other way, take one away. Wherever your number isn't zero, the page is black.

Walk across the `o`. You cross the outer oval: the number becomes 1, and you're in black. You cross the inner oval, which runs the other way: back to 0, and you're in white. You cross the inner oval again on your way out of the middle, and the number is 1 again. Then you cross the outer oval and return to 0.

So a hole isn't a kind of contour. It's what happens when a contour sits inside another and runs against it.

Now you can guess what goes wrong. If the inner oval ran the same way as the outer one, the number in the middle would be 2, not 0, and the middle would be black.

## Step 3: Break it

Try it. In the Glyph window, click on the inner oval of the `o` to select that contour alone. Then find the command that reverses a contour. In my copy it's in the **Contour** menu and it's called **Reverse Contour**. Look at the letter in the preview: the hole should have filled in.

Run the listing from Step 1 again and you should get `False` twice.

Press ++cmd+z++ on a Mac, or ++ctrl+z++ on Windows, to put it back.

That damage shows at once, because the letter looks wrong. Now do the other experiment. Select the whole `o`, both contours, and reverse them together. Look at the preview.

Nothing should have changed. The hole is still a hole, because the two contours still run against each other. Run the listing: `True`, then `False`. Both have flipped.

So is that a problem at all? It is, and it's the worse kind, because you can't see it. The rule about adding and taking away doesn't care which direction is which. But fonts follow a convention on top of the rule. In the kind of outlines Plum has, the outside of a shape runs counter-clockwise and the holes run clockwise. Other software relies on that. Tools that make a letter bolder, remove overlaps or add an outline work out which side of a line is "inside" from its direction, and a glyph that runs backwards can come out thinner where it should be bolder, or lose its counters. Some of the tools that turn your font into the files you deliver are sensitive to it too.

How does a whole glyph end up backwards? Usually by flipping. Mirror a `b` to start a `d`, and every contour in it reverses, because a mirror turns clockwise into counter-clockwise. The letter looks perfect and runs the wrong way.

Leave your `o` reversed for now. We'll use it to test the script.

## Step 4: Which one is the outside?

To check a glyph, a script has to know which contour is the outside one, and nothing in the contour says so. But there's a simple test that's right nearly always: the outside is the biggest. The contour whose bounding box covers the most ground is an outer contour, and it should run counter-clockwise.

In chapter 43, `box` worked out the box of all the nodes in a layer. Now we need the box of the nodes in one contour. It's the same arithmetic on a different list, so split the function in two. Define this pair in this script, in place of the old `box`:

```python
from fly.tr.proxy.fl.objects.glyph import pGlyph


def box_of(nodes):
    if not nodes:
        return None
    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    return min(xs), min(ys), max(xs), max(ys)


def box(font, glyph, master="Regular"):
    return box_of(pGlyph(font, glyph).nodes(master))
```

`box` still does what it did, and every call to it still works. All of its arithmetic has moved into `box_of`, which will take any list of nodes. This is how your code should grow. When you need half of a function somewhere else, cut that half out and give it a name, and let the old function call it. Don't copy the lines.

Add one more, for the ground a contour covers:

```python
def box_area(contour):
    left, bottom, right, top = box_of(contour.nodes())
    return (right - left) * (top - bottom)
```

A width times a height. Try it on the `o`:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph


def contours_of(font, glyph, master="Regular"):
    return pGlyph(font, glyph).contours(master)


font = fl.CurrentFont()
contours = contours_of(font, font["o"])
for contour in contours:
    print(box_area(contour))
```

```text
221112.0
96624.0
```

The outer oval's box is 444 by 498, and the inner one's is 264 by 366. Now pick the biggest, with `max` and a key as in chapter 36:

```python
outer = max(contours, key=box_area)
print(outer.clockwise)
```

```text
True
```

`max` hands back the contour itself, the one for which `box_area` gave the largest number. And since you left your `o` reversed, its outside runs clockwise. That's the check, in two lines.

Notice `key=box_area`, with no parentheses. It's the "function is a value" idea, put to work this time: you're handing `max` the function, for it to call on each contour.

## The whole script

Here is `check_direction.py`. It writes out `contours_of`, `box_of` and `box_area` at the top, so it runs by itself. It doesn't need `box`.

```python
# Reports layers whose largest contour runs clockwise.
# Reads only.
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

MASTERS = ["Light", "Regular", "Bold"]


def contours_of(font, glyph, master="Regular"):
    return pGlyph(font, glyph).contours(master)


def box_of(nodes):
    if not nodes:
        return None
    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    return min(xs), min(ys), max(xs), max(ys)


def box_area(contour):
    left, bottom, right, top = box_of(contour.nodes())
    return (right - left) * (top - bottom)


def main():
    font = fl.CurrentFont()
    if font is None:
        print("Open a font first.")
        return

    checked = 0
    wrong = 0
    for glyph in font.glyphs:
        for master in MASTERS:
            contours = contours_of(font, glyph, master)
            if not contours:
                continue
            checked = checked + 1
            outer = max(contours, key=box_area)
            if outer.clockwise:
                wrong = wrong + 1
                print(f"{glyph.name:<12}{master:<9}outside runs clockwise")

    print(f"{checked} layers checked, {wrong} wrong.")


main()
```

With the `o` still reversed in Regular:

```text
o           Regular  outside runs clockwise
363 layers checked, 1 wrong.
```

Go back to the `o` and undo the reversal, or reverse both contours again. Run the script once more:

```text
363 layers checked, 0 wrong.
```

Plum has 121 drawn glyphs in each of three masters, 363 layers, and in every one of them the largest contour runs counter-clockwise. I worked that out from the source file too, and it's what you'd hope for from a font that's been through a foundry's hands.

Here `continue` earns its place. `max` of an empty list fails with the same `ValueError` that `min` gave you in chapter 43, so the empty layers have to be turned away before the `max` line, and `continue` does that.

Be clear about what this script doesn't do. It looks at one contour in each layer, the biggest. It will catch a glyph that's backwards as a whole, which is the damage you can't see. It won't catch a single hole that runs the wrong way inside a good glyph, as in your first experiment. To find that, a script would have to work out which contours lie inside which, and that's real geometry, more than a box can tell you. An `i` has two contours and neither is a hole. A percent sign has five, and two are holes. I don't mind the gap much, because a filled-in hole is the one you'll see in any proof. And FontLab has its own command that sets every direction in a glyph by the proper geometry. Look in the **Contour** menu for it. Use your script to find the glyphs that need it.

Mira saves the script in the `Halfmoon` folder with `#FLM: Check Direction`. That's two delivery checks this week. She takes the sheet of chores, reads down the seven lines that are left, and finds that neither check is on it. Oskar never ran them.

## What you learned

A contour runs clockwise or counter-clockwise, and `contour.clockwise` tells you which. What's black is decided by counting crossings, so a hole is a contour that runs against the one around it, and a glyph reversed as a whole still looks right while breaking the convention that other tools depend on. The largest contour in a layer is an outside one and should run counter-clockwise in a font like Plum. When you need part of a function elsewhere, split it and let the old one call the new one.

## Try it yourself

1. Add the direction to `anatomy.py`: each contour line should end with `clockwise` or `counter-clockwise`. Run it on `i`, `B` and `percent`, and say for each contour whether it's an outside or a hole.
2. Open `b` and `d` side by side. Select everything in a copy of the `b` (make a new glyph called `b.test` and paste into it), flip it horizontally with FontLab's own tools, and run `check_direction.py`. Did the flip reverse it? Delete `b.test` when you're done.
3. `check_direction.py` and `find_open.py` have the same skeleton: two loops, a helper, a counter, a last line. Write a third script on that skeleton, `find_tiny.py`, that reports contours whose `box_area` is under 100. On Plum it should find none. Plant a tiny triangle in `f.sc` and find it. Delete the triangle when you're done.

## Next

Enough reading. You've spent five chapters looking at outlines that someone else drew. In chapter 46 the script picks up a pen and draws a rectangle of its own.
