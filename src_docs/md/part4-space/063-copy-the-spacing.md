---
this_file: src_docs/md/part4-space/063-copy-the-spacing.md
---

# 63. Copy the spacing

Wednesday of week twelve. Ines has Oskar's sheet out again. Seven of its eleven lines are crossed out, and the next one reads: *Make the left sidebearing of the d, q and g match the o.*

It's a sensible line. The `d`, the `q` and the `g` all begin with the same round stroke as the `o`. If the bowl is the same, the white in front of it should be the same. A designer sets the `o` with care and wants the others to follow it.

"Follow" is the word for this chapter. Yesterday you gave a glyph a number. Today you give it a model: this glyph takes its left side from that one. Written down for several glyphs, that's a dictionary, and the dictionary turns out to be the most useful part of the script.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and the Font window in front.
- `halfmoon.py` with `rich`, `ask` and `tell`.
- The font as chapter 62 left it. The exercises there are optional, and this chapter says where they'd show.

This chapter changes the font, in two Undo steps. I couldn't run it in FontLab 9. The numbers come from Plum's source file.

## Step 1: Look first

Before you copy anything, see how far apart the four glyphs are:

```python
import halfmoon
from fly import fl

font = fl.CurrentFont()
for master in ["Light", "Regular", "Bold"]:
    lefts = [halfmoon.rich(font, font[name]).getLSB(master) for name in ["o", "d", "q", "g"]]
    print(master, lefts)
```

```text
Light [50, 53, 53, 53]
Regular [38, 38, 38, 38]
Bold [30, 30, 30, 30]
```

In the Regular and the Bold, the job is done already. Somebody matched them by hand, and my guess is Oskar, before he wrote the line. In the Light, the three followers stand 3 units further in than the `o`.

Three units in a Light, on three glyphs. It's the smallest job on the sheet so far, and that's a good reason to do it with a script: the script will say "nothing to do" for six of the nine layers, and you'll believe it, where by hand you'd have opened all nine to check.

## Step 2: A dictionary that says who follows whom

Chapter 21 used a dictionary to look things up: a name goes in, a width comes out. The same thing can hold a rule. The key is the glyph that follows. The value is its model.

```python
LEFT_LIKE = {"d": "o", "q": "o", "g": "o"}

print(LEFT_LIKE["g"])
```

```text
o
```

Read `LEFT_LIKE["g"]` as a question: whose left side does the `g` take? The answer is `o`.

With that, the difference for one glyph in one master is two lookups and a subtraction:

```python
name = "d"
model = LEFT_LIKE[name]
dx = halfmoon.rich(font, font[model]).getLSB("Light") - halfmoon.rich(font, font[name]).getLSB("Light")
print(name, "follows", model, "and must move by", dx)
```

```text
d follows o and must move by -3
```

Minus 3: the shape goes 3 units to the left. Chapter 62 showed what goes with that. The width shrinks by 3 as well, so that the right side stays as it is.

## Step 3: The mistake

The first way that comes to mind is the way the sentence on Oskar's sheet runs. The `o` is the boss, so the `o` came first:

```python
LEFT_LIKE = {"o": "d", "o": "q", "o": "g"}
print(LEFT_LIKE)
print(len(LEFT_LIKE))
```

```text
{'o': 'g'}
1
```

Three pairs went in and one came out. Chapter 21's third exercise showed this: a dictionary holds each key once, and when the same key turns up again the later value takes its place, with no error. Here the key `o` turned up three times.

What makes it worse is that the script would have run. It would have found one rule, "the `o` follows the `g`", and moved the `o`, the one glyph that was supposed to stay put.

So the direction matters, and there's a way to remember it. Each follower has one model, but a model can have many followers. A dictionary allows a value to repeat and doesn't allow a key to repeat. The thing there's one of per entry goes on the left: the follower is the key.

## Step 4: A plan for every layer

Now walk through the font and collect what has to change. Each row of the plan holds the rich glyph, the master, the distance to move and the new width, the same two numbers as in chapter 62:

```python
rows = []
for glyph in font.glyphs:
    if glyph.name not in LEFT_LIKE:
        continue
    rich = halfmoon.rich(font, glyph)
    model = halfmoon.rich(font, font[LEFT_LIKE[glyph.name]])
    for master in ["Light", "Regular", "Bold"]:
        dx = model.getLSB(master) - rich.getLSB(master)
        if dx != 0:
            rows.append((rich, master, dx, rich.getAdvance(master) + dx))

for rich, master, dx, width in rows:
    print(rich.name, master, dx, width)
```

```text
d Light -3 520
g Light -3 520
q Light -3 520
```

`glyph.name not in LEFT_LIKE` asks whether the name is one of the dictionary's keys. For a dictionary, `in` looks at the keys only.

Three rows out of nine layers. The other six had a difference of 0 and were left out.

## Step 5: One Undo step for all of it

In chapter 62 every change was its own Undo step. For three layers that belong to one decision, one step is better: if Mira doesn't like the result, she undoes once.

`history.commit` has taken a list of layers and a list of glyphs all along. You've been handing it lists with one thing in each. Hand it longer lists, and do all the work inside the one small function:

```python
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.metrics.panel.model as metrics
from fly.pens import layer_of

layers = [layer_of(rich.fl, master) for rich, master, dx, width in rows]
owners = {}
for rich, master, dx, width in rows:
    owners[rich.name] = rich.fl


def change():
    for (rich, master, dx, width), layer in zip(rows, layers):
        metrics.shift_and_set(layer, dx, width)


package = scripting.current_package()
facts = history.scan_auto_facts(package)
history.commit("Copy left sidebearings", layers, list(owners.values()), change,
               operation="geometry", facts=facts, allow_bases=True)
```

`allow_bases=True` is there for the `g`. FontLab builds `gbreve` from it, so the `g` is a borrowed glyph, and chapter 55 explained what that keyword agrees to. Save the font before you run this.

Two things here are new.

`owners` is a dictionary used for its bad habit. The tool wants each glyph once, and a glyph with changes in two masters would turn up twice in the rows. Storing it under its name twice keeps one copy, which is the very thing that went wrong in step 3 and is wanted here. `owners.values()` gives the values without the keys, and `list` makes a list of them.

The `for` line inside `change` takes two things apart at once. `zip` pairs each row with its layer, so each turn of the loop gets a pair: a row, which is itself four things, and a layer. The parentheses around the four names say where the row ends. You saw the same shape in chapter 54 with `for family, (bx, by) in ...`.

Run the loop from step 1 again:

```text
Light [50, 50, 50, 50]
Regular [38, 38, 38, 38]
Bold [30, 30, 30, 30]
```

## Step 6: The ones who follow without being told

Chapter 62 ended with a loose thread. When a base glyph changes, the glyphs that borrow it get the new outline and keep their old width. The `g` has one borrower in Plum, `gbreve`, the Turkish `ğ`. Its `g` has now moved 3 units left with the Light `g`, and its box is still 523 wide where the `g` is 520.

Nobody would write `gbreve` into a dictionary by hand, along with seventy others. But the font already knows who follows whom here: an accented letter follows its first component. So this second map can be read out of the font. The rule I'll use has three parts. The glyph has no outline of its own and at least two components. The first component isn't shifted. And every other component is an accent, which means its glyph carries a loop anchor, one whose name starts with `_`, as chapter 54 showed.

The third part matters. Without it the rule would catch `ij`, which begins with an unshifted `i` and is rightly wider than an `i`. A `j` carries no loop, so `ij` is left alone.

In the script below that's the function `follow_rows`. It makes rows of the same shape as before, with a move of 0, since only the width has to follow.

There's a catch, and chapter 56 met it first. `gbreve` is a glyph FontLab builds itself, and no script of ours may write into it. So `follow_rows` hands back two things: the rows it can change, and the names of the automatic letters it had to leave. On the font as it stands now the first list is empty and the second holds one name, `gbreve`, whose Light is 523 wide over a `g` of 520. That's what Plum's file says. FontLab may have made it 520 by itself when the `g` changed, and then the second list is empty too. I haven't seen which.

If you did exercise 2 of chapter 62 and widened the Bold `n`, the first list isn't empty. `nacute` and `ncaron` are yours, built in chapters 53 and 60, and they get rows. `ntilde` came with Plum and is automatic, so it joins `gbreve`. That exercise asked whether the script should have warned you. This is the answer: better than a warning is a second pass that puts right what it may and names the rest.

One thing this pass doesn't do: it doesn't move the breve. The `g` under it went 3 units left, and so did the `top` peg on the `g`, from 262 to 259. The breve sat at a shift of 12 where 9 is now right. Chapter 57's builder would say `auto` for it and leave it. So `gbreve` goes on Mira's list beside the `î`: look at it, and see what FontLab did.

## The whole script

```python
#FLM: Copy Sidebearings
# Gives glyphs the left or right sidebearing of a model glyph,
# then makes accented letters as wide as their base letter.
import halfmoon
import fly.ap.anchors.writer as anchors
import fly.ap.components.writer as parts
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.metrics.panel.model as metrics
from fly import fl
from fly.pens import layer_of

MASTERS = ["Light", "Regular", "Bold"]
LEFT_LIKE = {"d": "o", "q": "o", "g": "o"}
RIGHT_LIKE = {}


def side_rows(font):
    rows = []
    for glyph in font.glyphs:
        name = glyph.name
        if name not in LEFT_LIKE and name not in RIGHT_LIKE:
            continue
        rich = halfmoon.rich(font, glyph)
        for master in MASTERS:
            dx = 0
            width = rich.getAdvance(master)
            if name in LEFT_LIKE:
                model = halfmoon.rich(font, font[LEFT_LIKE[name]])
                dx = model.getLSB(master) - rich.getLSB(master)
                width += dx
            if name in RIGHT_LIKE:
                model = halfmoon.rich(font, font[RIGHT_LIKE[name]])
                width += model.getRSB(master) - rich.getRSB(master)
            if dx != 0 or width != rich.getAdvance(master):
                rows.append((rich, master, dx, width))
    return rows


def is_accent(font, name, master):
    layer = layer_of(halfmoon.rich(font, font[name]).fl, master)
    return any([family.startswith("_") for family in anchors.anchor_points(layer)])


def follow_rows(font):
    rows = []
    left = []
    for glyph in font.glyphs:
        rich = halfmoon.rich(font, glyph)
        for master in MASTERS:
            layer = layer_of(rich.fl, master)
            found = parts.components(layer)
            if len(found) < 2 or rich.contours(master):
                continue
            if parts.offset(found[0]) != (0, 0):
                continue
            if not all([is_accent(font, parts.base_of(part), master) for part in found[1:]]):
                continue
            base = halfmoon.rich(font, font[parts.base_of(found[0])])
            if base.getAdvance(master) == rich.getAdvance(master):
                continue
            if layer.autoLayer:
                left.append(f"{rich.name} {master}")
            else:
                rows.append((rich, master, 0, base.getAdvance(master)))
    return rows, left


def show(rows):
    for rich, master, dx, width in rows:
        print(f"{rich.name:<10}{master:<9}move {dx}, width {rich.getAdvance(master)} to {width}")


def apply(rows, title):
    layers = [layer_of(rich.fl, master) for rich, master, dx, width in rows]
    owners = {}
    for rich, master, dx, width in rows:
        owners[rich.name] = rich.fl

    def change():
        for (rich, master, dx, width), layer in zip(rows, layers):
            metrics.shift_and_set(layer, dx, width)

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    history.commit(title, layers, list(owners.values()), change,
                   operation="geometry", facts=facts, allow_bases=True)


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    models = list(LEFT_LIKE.values()) + list(RIGHT_LIKE.values())
    missing = [name for name in models if font[name] is None]
    if missing:
        halfmoon.tell(f"No glyph named: {' '.join(missing)}")
        return

    rows = side_rows(font)
    show(rows)
    print(f"{len(rows)} layers to change.")
    if rows and halfmoon.ask(f"Copy sidebearings on {len(rows)} layers?"):
        apply(rows, "Copy sidebearings")

    rows, left = follow_rows(font)
    show(rows)
    print(f"{len(rows)} accented letters differ from their base in width.")
    if left:
        print(f"Automatic, left to FontLab: {', '.join(left)}")
    if rows and halfmoon.ask(f"Make {len(rows)} accented letters as wide as their base?"):
        apply(rows, "Follow base widths")


main()
```

Choose **Edit > Undo** to take back what you did in step 5, then run it and answer Yes:

```text
d         Light    move -3, width 523 to 520
g         Light    move -3, width 523 to 520
q         Light    move -3, width 523 to 520
3 layers to change.
0 accented letters differ from their base in width.
Automatic, left to FontLab: gbreve Light
```

Run it again and both counts are 0. The last line stays for as long as `gbreve` is 523 wide.

`main` uses the name `rows` twice, first for the side rows and then for the follower rows. That's allowed. The second assignment throws out the first list, which has done its work by then. The follower rows must be made after the first change and not before, since they compare with widths that the first change sets.

`if rows and halfmoon.ask(...)` leans on something chapter 35 used as `if not rows:`. An empty list counts as false. With no rows, Python doesn't go on to the second half, and nobody is asked a question about 0 layers.

The rows of the two passes have the same shape, four things each, so `show` and `apply` serve both. That wasn't luck. I gave the follower rows a move of 0 so that they'd fit.

Ines crosses out the line: eight of eleven. Mira looks at the sheet and then at the dictionary on the screen. "Three letters," she says. "It should be thirty. Half the alphabet follows the `n` or the `o`." She's right, and thirty entries typed one by one is a poor way to say something that simple.

## What you learned

A dictionary can hold a rule: the follower is the key, its model is the value, and many followers may share a model. Written the other way round, the entries overwrite each other with no error. `in` on a dictionary looks at the keys, and `.values()` gives the values. One `history.commit` can take many layers, with the work done in a loop inside the small function, and an accented letter's width follows its base.

## Try it yourself

1. The `b` and the `p` end with the round stroke the `o` ends with. Set `LEFT_LIKE = {}` and `RIGHT_LIKE = {"b": "o", "p": "o"}` and run the script. You should see four rows: Light widths from 523 to 520, Bold widths from 543 to 548. Before you answer Yes for the Bold, look at the Bold `o` itself: 30 on the left, 8 on the right. Is it a good model there? Say what copying from a bad model does.
2. Open `accents.txt` from chapter 56, add the line `ğ gbreve g breve`, and run the builder from chapter 57. It should say `auto` for `gbreve` and show shifts of 9, 22 and 22. Open the Light `gbreve` and read the breve's shift there. Did FontLab follow the `g`?
3. Add `"c": "o"` and `"e": "o"` to `LEFT_LIKE`. The Light `c` moves by -3 and the Light `e` by 2. Which accented letters does the second pass then bring into line, and which does it name as automatic? Only the ones you built yourself can get a row: `cacute`, `ccaron` and `ecaron`, if you made them in chapters 56 and 60.

## Next

Mira's thirty letters fall into a few families: those that start like an `n`, those that start like an `o`, those that end like one or the other. Chapter 64 writes the families down as a dictionary of lists and builds the follower map from them.
