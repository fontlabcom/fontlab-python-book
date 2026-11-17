---
this_file: src_docs/md/part3-shapes/044-open-contours.md
---

# 44. Open contours

Thursday. Ines tells a story at the coffee machine. Some years ago Halfmoon delivered a font in which the comma, in one weight, had a contour that wasn't closed. On screen at the studio it looked fine. In the exported font it was gone, and nobody noticed until a cookbook came back from the printer with every list of ingredients run together.

A contour is supposed to come back to where it started. One that doesn't is called open. It's a line with two loose ends and nothing inside it to fill with black. Open contours get into fonts in ordinary ways: a sketch you forgot to finish, a guideline drawn with the wrong tool, two nodes that look joined and aren't.

"Can a script find them?" Mira asks. She already knows what I'll say. In chapter 41 you printed `contour.closed` and it said `True` twice. Today you'll look for the ones that say `False`, in every glyph and every master, and on the way you'll learn two small words that make loops easier to read.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `box` from yesterday, and `anatomy.py` from chapter 41.
- The seven small-cap glyphs you added in chapter 40. They're still empty.

Plum's source file has no open contours. So in Step 1 you'll plant one. The outputs below were computed from Plum's source file, not copied from FontLab's Output panel.

## Step 1: Plant one

Open the empty `d.sc` in a Glyph window, with the Regular master showing. Take the Pen tool and click three times, anywhere, to make three corners of a triangle. Don't click on the first point again to close it. Press ++esc++ to put the pen down. You have a line with two bends, which is a contour that's open.

Run `anatomy.py` on it:

```text
d.sc, layer Regular
  elements: 1
  contour 1: open, 3 nodes
  total: 1 contours, 3 nodes
```

If yours says `closed`, the pen closed the shape for you. Undo and try again, or draw the three points and stop after the third.

Now there's one open contour in a font of 220 glyphs, in one master of three. Let's go and find it as if we didn't know where it was.

## Step 2: On to the next

First, a helper for the module. For two chapters we've asked for a layer's nodes. Today we need its contours, since `closed` belongs to a contour and not to a node:

```python
def contours_of(font, glyph, master="Regular"):
    return rich(font, glyph).contours(master)
```

Now walk the font. Most glyphs will have nothing for us: the ones built from other glyphs and the empty ones have no contours at all. Yesterday we handled cases like that with an `if` and an `else`, and the real work ended up three levels deep, like a staircase. Here's another way to write it:

```python
for glyph in font.glyphs:
    contours = halfmoon.contours_of(font, glyph)
    if not contours:
        continue
    print(glyph.name, len(contours))
```

`continue` means: I'm done with this one, go on to the next. When Python meets it, it skips whatever is left in the body of the loop for this round and goes straight back to the `for` line to pick up the next glyph. So the `print` only happens for glyphs that got past the `if`.

You've seen the same move before. In chapter 19, `main()` began with a guard: if there's no font, say so and `return`. The guard turned away the hopeless case at the door, and the rest of the function didn't have to be indented under an `else`. `continue` is that guard for one round of a loop. `return` leaves the whole function. `continue` leaves only this round.

The two get mixed up, and Python will tell you when you do. Suppose you write the guard at the top of `main()` with the wrong word:

```python
def main():
    font = fl.CurrentFont()
    if font is None:
        continue
```

```text
  File "<string>", line 4
SyntaxError: 'continue' not properly in loop
```

There's no loop there to continue. It's a `SyntaxError`, so Python found it while reading the script, before running a single line.

## Step 3: Is any of them open?

For each glyph that has contours, we want to know whether at least one of them is open. You can already write that, with a switch like `DRY_RUN` from chapter 31, only this one is flipped by the loop:

```python
contours = halfmoon.contours_of(font, font["d.sc"])
has_open = False
for contour in contours:
    if not contour.closed:
        has_open = True
print(has_open)
```

```text
True
```

The switch starts at `False`, and the first open contour flips it. Nothing ever flips it back. After the loop it tells you whether there was one.

Once it's flipped, the rest of the contours don't matter. On a glyph with fifty contours you could stop looking after the first open one. There's a word for that too:

```python
for contour in contours:
    if not contour.closed:
        has_open = True
        break
```

`break` leaves the loop altogether. The loop is over, and Python carries on with the line after it. So there are three ways out, each a size bigger than the last. `continue` ends this round, `break` ends the loop, and `return` ends the function.

This pattern, a switch and a loop and a `break`, is so common that Python has it built in:

```python
has_open = any([not contour.closed for contour in contours])
```

Read it aloud: is any of these true? The comprehension makes a list with one `True` or `False` for each contour, and `any` answers `True` if at least one item is true. That's the five-line loop in one line, and it says what it means.

`any` has a sibling, `all`, which answers `True` only if every item is true:

```python
all_closed = all([contour.closed for contour in contours])
```

For a glyph with contours, `all_closed` is the opposite of `has_open`, and you can use whichever reads better.

But try both on a glyph with no contours:

```python
print(any([]), all([]))
```

```text
False True
```

`any` of nothing is `False`, which sounds right: there's no open contour in an empty glyph. `all` of nothing is `True`, and that one can fool you. "Are all the contours closed?" Yes, says Python, all none of them. It's sound logic. If you fire everyone on the team who was late, and nobody was late, you've done it. But a report that says "220 glyphs have all contours closed", when 99 of them have no contours, is saying less than it seems to. When you use `all`, think about what it does with an empty list, and whether you should have turned the empty cases away first. That's what the `continue` in Step 2 was for.

## Step 4: Every master

The cookbook comma was open in one weight. A check that looks only at Regular would have missed it. So for each glyph we have to look at three layers, and that's a loop inside a loop again:

```python
MASTERS = ["Light", "Regular", "Bold"]

for glyph in font.glyphs:
    for master in MASTERS:
        contours = halfmoon.contours_of(font, glyph, master)
        if any([not contour.closed for contour in contours]):
            print(glyph.name, master)
```

```text
d.sc Regular
```

There it is. Think of the clock from chapter 41: the glyph is the hour hand, the master is the minute hand, and the script looks at 660 layers to find one.

The list of masters is typed in as a constant, as it was in chapter 40, and it's right for Plum only. Asking the font for its masters is still to come.

Here `continue` would add nothing, because `any` of an empty list is `False` and the `if` takes care of the empty layers on its own. Use `continue` when it saves you a level of indentation or a wrong answer, and leave it out when it doesn't.

One more thing would help Mira when she goes to fix what the script finds: how many open contours a layer has, and how big they are. A stray open contour with two or three nodes is usually a slip of the pen. One with thirty is a real shape that somebody forgot to close, and it needs care. So let's collect the open ones, with a filter:

```python
loose = [contour for contour in contours if not contour.closed]
```

If `loose` is empty, the layer is fine. If it isn't, its length is the count, and each contour in it can be asked for its nodes.

## The whole script

Here is `find_open.py`. `halfmoon.py` gains `contours_of` from Step 2.

```python
# Lists every open contour in the font, in every master.
# Reads only.
import halfmoon
from fly import fl

MASTERS = ["Light", "Regular", "Bold"]


def main():
    font = fl.CurrentFont()
    if font is None:
        print("Open a font first.")
        return

    found = 0
    for glyph in font.glyphs:
        for master in MASTERS:
            contours = halfmoon.contours_of(font, glyph, master)
            loose = [contour for contour in contours if not contour.closed]
            if not loose:
                continue
            found = found + 1
            sizes = [str(len(contour.nodes())) for contour in loose]
            print(f"{glyph.name:<12}{master:<9}open: {len(loose)}  nodes: {' '.join(sizes)}")

    if found == 0:
        print("No open contours.")
    else:
        print(f"{found} layers with open contours.")


main()
```

```text
d.sc        Regular  open: 1  nodes: 3
1 layers with open contours.
```

Look at how the inner loop reads now. It gets the contours, keeps the open ones, and if there are none it moves on. What comes after the `continue` is the part that only happens for the rare bad layer, and it isn't indented any deeper than the rest. A reader can see at a glance which lines are the normal path and which are the exception.

The `sizes` line uses `' '.join` from yesterday, and `join` insists on strings, so each count goes through `str` first, the cure chapter 3 gave for gluing text to a number.

"1 layers" is bad grammar. You know enough to fix it, and exercise 1 asks you to.

Mira runs it. One line. She opens `d.sc`, deletes the three-point sketch, runs it again, and gets `No open contours.` Delete your sketch too, and run the script once more to see the same line. Later chapters count layers, and their counts assume that no sketch is left behind. Then she saves the script in the `Halfmoon` folder with a `#FLM: Find Open Contours` line at the top, the way chapter 18 showed, because this is one she'll want before every delivery.

Ines reads the output over her shoulder. "That would have saved us a cookbook," she says.

## What you learned

`continue` ends one round of a loop and goes on to the next, `break` ends the loop, and `return` ends the function. `any` asks whether at least one item in a list is true and `all` asks whether every one is, and `all` of an empty list is `True`, so turn the empty cases away before you trust it. A check that matters has to look at every master, which means a loop inside a loop. An open contour has `closed` equal to `False`.

## Try it yourself

1. Fix the grammar: make the last line say `1 layer with open contours.` or `2 layers with open contours.` as needed. The `a if test else b` form from chapter 37 fits in one line.
2. Plant a second open contour, in the Bold master of `e.sc`, with two points only. Run the script. Delete both points when you're done. Then change it so that it prints the word `stray` at the end of the line when every open contour in the layer has fewer than four nodes. Which of `any` and `all` do you need?
3. Rewrite `groups_by_top` in yesterday's `bounds.py` with `continue`, so that nothing in the loop is indented more than two levels. Run it and make sure the output hasn't changed. Which version would you rather read in six months?

## Next

A closed contour still has a property you can't see by looking at the black shape: the way round it runs. Chapter 45 finds out why the hole in the `o` is a hole, and what happens when it isn't.
