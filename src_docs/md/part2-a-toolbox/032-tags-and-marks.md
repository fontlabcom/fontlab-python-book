---
this_file: src_docs/md/part2-a-toolbox/032-tags-and-marks.md
---

# 32. Tags and marks

Monday of the sixth week. Ines has a system, and she's had it for longer than Mira has worked here. A green cell is a glyph she's approved. Yellow means "I've looked, and it needs work". Red means not drawn yet. Nobody ever wrote the system down. It lives in Ines's head and in the Font window.

This morning the publisher asks how far along the small caps are, and Ines asks Mira, and Mira looks at a Font window full of colored cells and starts counting greens with her finger on the screen.

You marked cells red in [chapter 14](../part1-first-words/014-mark-them-red.md). Today you go the other way: the script reads the colors that are already there and says what they mean. Then it meets the limit of colors, and you find out what FontLab offers in their place.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open and saved.
- A font with some colors in it. Your practice copy has whatever earlier chapters left behind, so start from a known state. Run this once:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

RED = 1
YELLOW = 61
GREEN = 121

paint = {}
for name in ["A", "B", "C", "D", "E", "H", "O", "n", "o"]:
    paint[name] = GREEN

font = fl.CurrentFont()
for glyph in font.glyphs:
    pGlyph(font, glyph).mark = paint.get(glyph.name, 0)
```

Nothing in it is new. It builds a dictionary from glyph name to color number, then walks the font and gives every glyph its color from the dictionary, or 0 for "no mark" when the name isn't there. That's `get` with a fallback, from chapter 22. The Font window should now show nine green cells and nothing else in color.

Now add the rest. Put these lines under the green loop, above `font = fl.CurrentFont()`, and run it again:

```python
for name in ["a", "g", "s"]:
    paint[name] = YELLOW
for name in ["a.sc", "b.sc", "c.sc"]:
    paint[name] = RED
paint["Q"] = 200
```

Nine green cells, three yellow, three red and one `Q` in a color that isn't one of your three.

That `Q` is there to cause trouble. Somebody was trying out colors one afternoon and never cleared it. Real fonts are full of such leftovers.

As chapter 14 warned, marks set by a script leave no step in **Edit > Undo**. That's why you saved first.

## Step 1: Names for numbers

Look at the top of that listing:

```python
RED = 1
YELLOW = 61
GREEN = 121
```

You've been writing boxes in capitals since chapter 17, and `AMOUNT`, `DRY_RUN` and `OLD_SUFFIX` joined them last week. It's time to say what the custom is for.

A box whose value is set once at the top and never changed afterward is called a **constant**. Python doesn't enforce that. You could write `GREEN = 5` on line 40 and nobody would stop you. The capitals are an agreement between people: this is a fixed fact of the script, look for it at the top, don't assign to it anywhere else.

Constants buy you two things. The first is reading. `rich.mark = 121` tells you nothing, and `rich.mark = GREEN` tells you what's going on. The second is changing. If Ines decides that approved glyphs should be a bluer green, there's one line to edit, and every place that says `GREEN` follows.

A number that sits bare in the middle of a script, with no name, has a nickname among programmers: a magic number. It works, and nobody remembers why it's 121. Give it a name.

## Step 2: A legend

Ines's system is a mapping: this color means that. You know what holds a mapping. A map has a legend in its corner that says what the colors stand for, and this dictionary does the same job:

```python
LEGEND = {
    0: "untouched",
    RED: "not drawn",
    YELLOW: "needs work",
    GREEN: "done",
}
```

The keys are the constants, so the dictionary reads like the sentence in Ines's head. It's in capitals for the same reason they are: it's set once and never changed. And for the first time, her system is written down somewhere.

Now ask it about one glyph. Click the `A` cell and run:

```python
rich = pGlyph()
print(rich.name, rich.mark, LEGEND[rich.mark])
```

```text
A 121 done
```

## Step 3: The color nobody planned

Now the whole font. Walk the glyphs, look up each mark in the legend, and print what you find:

```python
for glyph in font.glyphs:
    rich = pGlyph(font, glyph)
    print(glyph.name, LEGEND[rich.mark])
```

It prints for a while and then stops:

```text
Otilde untouched
OE untouched
P untouched
KeyError: 200
```

You know `KeyError` from chapter 21. The script asked the legend for a key it doesn't have. The last line printed was `P`, so the glyph that broke it is the next one: the odd-colored `Q`, with a mark of 200 that isn't in anybody's system.

The legend describes what Ines intended. The font holds what people did, and a script that reads other people's work has to expect values outside the plan. `get` gives the legend a fallback, and while you're at it, count and don't print 213 lines:

```python
tally = {}
for glyph in font.glyphs:
    rich = pGlyph(font, glyph)
    status = LEGEND.get(rich.mark, "unknown color")
    tally[status] = tally.get(status, 0) + 1

for status in LEGEND.values():
    print(f"{status:<14}{tally.get(status, 0):>4}")
print(f"{'unknown color':<14}{tally.get('unknown color', 0):>4}")
```

```text
untouched      197
not drawn        3
needs work       3
done             9
unknown color    1
```

Your first number depends on how many practice glyphs you've added along the way. Mine has 213 glyphs in all.

That's the counting pattern from chapter 22, used twice: once to build the tally and once, with a fallback of 0, to print a line for a status that no glyph has. `LEGEND.values()` is new. `items()` gave you keys and values in pairs. `values()` gives the values alone, in the order you wrote them. So the report comes out in the legend's order, which is the order Ines thinks in.

One honest caution. I've set these marks from a script, with exact numbers. When a person picks a color from FontLab's own menu, I can't tell you which number is stored for "green". It may be 121 and it may be a neighbor. So before you trust a legend on a font that people have colored by hand, print the marks that are really in it:

```python
seen = set()
for glyph in font.glyphs:
    seen.add(pGlyph(font, glyph).mark)
print(sorted(seen))
```

```text
[0, 1, 61, 121, 200]
```

Then write the legend from what you see.

## Step 4: One color isn't enough

Mira reports: nine done, three need work, three not drawn. Ines nods and then says the thing that breaks the system. "The `a` is drawn and I like it. It needs kerning. And the `g` needs work *and* Tomas found it in a proof."

A cell has one color. `a` can be green or yellow. It can't be "drawn, approved, not yet kerned", and it certainly can't carry two facts at once. Studios work around this with more colors, until there's an orange that means "approved except for the kerning" and nobody but Ines remembers it.

FontLab has a second way to label a glyph: tags. A tag is a word you stick on a glyph. A glyph can carry several tags, and they don't show as a color. Put two on `a`:

```python
font = fl.CurrentFont()
rich = pGlyph(font, font["a"])
rich.tag("drawn")
rich.tag("needs-kerning")
print(rich.getTags())
```

```text
['drawn', 'needs-kerning']
```

`tag` sticks one word on the glyph. `getTags()` hands back the glyph's tags as a list of strings. I've written `needs-kerning` with a hyphen and no space. I don't know how FontLab treats a space inside a tag, so I keep clear of the question.

This is how the two compare:

| | Mark | Tag |
|---|---|---|
| What it is | one number, shown as a color | a word |
| How many on a glyph | one | as many as you like |
| Where you see it | at a glance, in the cell | when you search or filter for it |
| Good for | one status that people scan by eye | several facts that scripts and searches use |

Neither replaces the other. Ines isn't going to give up her colors, and she shouldn't. Colors are for eyes. Tags are for questions.

## Step 5: Ask by tag

A tag is useful when you can ask for it. `getTags()` gives a list, and `in` asks a list whether it holds something, as it has since chapter 10:

```python
print("Needs kerning:")
for glyph in font.glyphs:
    if "needs-kerning" in pGlyph(font, glyph).getTags():
        print(" ", glyph.name)
```

```text
Needs kerning:
  a
```

Now do it for the whole of Ines's system: read each glyph's color, look up the word in the legend and stick that word on as a tag. First, the words need to be fit for tags, so the legend gets hyphens: `"not-drawn"`, `"needs-work"`.

There's one trap here, and it's the lesson of chapter 30 over again. A script should be safe to run twice. If the script tags `a` with `needs-work` today and you run it again tomorrow, does `a` get the tag a second time? I don't know what FontLab does with a repeated tag, and I'd sooner not find out on a real font. So ask first:

```python
        if status not in rich.getTags():
            rich.tag(status)
```

Then the script doesn't depend on the answer.

## The whole script

Save this as `status_marks.py`. It has last week's switch at the top. With `DRY_RUN = True` it reports and changes nothing:

```python
# Reads Ines's mark colors and reports how many glyphs have each status.
# With DRY_RUN = False it also tags each marked glyph with its status word.
# Marks and tags set by a script leave no Undo step: save the font first.
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

DRY_RUN = True

RED = 1
YELLOW = 61
GREEN = 121
LEGEND = {
    0: "untouched",
    RED: "not-drawn",
    YELLOW: "needs-work",
    GREEN: "done",
}
UNKNOWN = "unknown-color"

font = fl.CurrentFont()

tally = {}
tagged = 0
for glyph in font.glyphs:
    rich = pGlyph(font, glyph)
    status = LEGEND.get(rich.mark, UNKNOWN)
    tally[status] = tally.get(status, 0) + 1
    if status == UNKNOWN:
        print("Unknown color", rich.mark, "on", glyph.name)
    elif rich.mark != 0 and not DRY_RUN:
        if status not in rich.getTags():
            rich.tag(status)
            tagged += 1

for status in LEGEND.values():
    print(f"{status:<14}{tally.get(status, 0):>4}")
print(f"{UNKNOWN:<14}{tally.get(UNKNOWN, 0):>4}")

if DRY_RUN:
    print("Dry run. No tags added.")
else:
    print(tagged, "glyphs tagged")
```

```text
Unknown color 200 on Q
untouched      197
not-drawn        3
needs-work       3
done             9
unknown-color    1
Dry run. No tags added.
```

The script names the glyph with the unknown color. A count of 1 tells Mira there's a problem. `on Q` tells her where to click.

Untouched glyphs get no tag, because of the `rich.mark != 0` test. A tag that says "nobody has looked at this" on 197 glyphs is noise.

And `UNKNOWN` is a constant too, though it's used in only four places. The word appears in the lookup, in a comparison and in two print lines. Typed four times by hand, it would sooner or later be `unknown-colour` in one of them, and the comparison would quietly never match.

Set `DRY_RUN = False`, run it, and the last line reads `15 glyphs tagged`. Run it again and it reads `0 glyphs tagged`, because every glyph already has its word. Then set the switch back.

Ines looks at the report and says she didn't know the `Q` had a color at all. Then she asks the question that's been coming all month: could the Friday report include this?

## What you learned

A constant is a box you set once at the top of a script and write in capitals, so that numbers get names and there's one place to change them. A small dictionary can serve as a legend that turns a stored value into a word, and `get` with a fallback keeps it from breaking on values nobody planned. A mark is one color on a glyph, for eyes. Tags are words, as many as you need, for scripts and searches.

## Try it yourself

1. Add a fifth status to Ines's system: blue, number 241, meaning "waiting for the publisher". Which lines of `status_marks.py` do you have to change? If the answer is more than two, look again.
2. Write a script that prints the names of all glyphs tagged `done`, on one line, with spaces between them. `join` is from chapter 25. Then make it answer Ines's real question: which glyphs are tagged `done` and also tagged `needs-kerning`?
3. The tags describe the colors on the day you ran the script. On Tuesday Ines repaints `g` from yellow to green. What does `g` carry after you run `status_marks.py` again? Describe in words what the script would have to do to keep tags and colors in step. You don't have to write it. Taking a tag off needs a call this chapter hasn't shown.

## Next

`pGlyph(font, glyph)`, the legend and the tally loop are now in several of Mira's scripts, pasted from one to the next. Chapter 33 puts them in one file that all her scripts can share.
