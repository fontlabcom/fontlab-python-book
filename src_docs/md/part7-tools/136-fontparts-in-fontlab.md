---
this_file: src_docs/md/part7-tools/136-fontparts-in-fontlab.md
---

# 136. One script, several editors

It's Wednesday 6 January. Mira's friend Tove got her answer about stray points, and has written back with a request of her own. "That font summary you print before a release, with the counts. Could I have it? I'm in RoboFont, mind."

Every script you've written starts with `from fly import`. Tove's editor has no Fly. You could write her a second version, and from then on every change would have to be made twice.

Today you write the summary once, in a way that doesn't care which editor it's in, and give each editor a three-line script that hands it a font.

## What you need

`Plum-practice` open and Fly installed. Chapter 135 for the idea of an adapter, chapter 95 for a function that returns a dictionary, and chapter 33 for importing a module of your own.

I haven't run this chapter in FontLab 9, and I haven't run it in RoboFont. What I did is closer to the point of the chapter than either: I ran `plum_report.py` on a small seven-glyph test font through two different sets of fontParts objects, outside any editor. One was the reference set that the fontParts project ships. The other was Fontport's, the objects Fly's `fp` gives you, working on a font in memory. Both printed the same six lines, which are below. FontLab's side of the three-line launcher is unseen.

## Step 1: The agreement

In chapter 135 an adapter made FontLab answer to one other program's names. That works for one pair of programs at a time.

fontParts is a different kind of thing. It's a written list of names: a font has `info` and `kerning`, and you can loop over it to get glyphs; a glyph has `name`, `width`, `unicode`, and so on for a few hundred names. Nobody's editor is described by it. It's an agreement that several editors have each undertaken to answer to, whatever their own objects are called underneath. Programmers call such a list an interface. The wall socket is one: the kettle doesn't know which power station is behind it.

You've been on the other side of an interface already. In chapter 134, FontLab's part was to call `compute` with a snapshot and yours was to return marks. Neither side knew more about the other than that.

Fly's `fp`, Fontport, is FontLab's way of keeping its side of the fontParts agreement. It was in the toolbag in chapter 4.

## Step 2: A function that takes a font

The trick to writing for several editors is small. The part of your script that does the work must never go looking for the font. It's handed one:

```python
def glyph_count(font):
    return len(font)
```

There's no `fl.CurrentFont()` in it and no import at all. Whoever calls it has to bring a font, and the function will work with anything that answers to `len`. You've written functions like this since chapter 29. What's new is noticing that such a function has no idea where it is.

Getting the font is the one thing every editor does differently, so it goes in a separate, tiny script for each editor. For FontLab:

```python
from fly.fp.world import FontWorld

font = FontWorld().CurrentFont()
```

`FontWorld` is Fontport's front desk. Its `CurrentFont` gives the font in front, wearing fontParts names, or `None` when no font is open. Its glyphs are FontLab's own glyphs. Nothing is copied; a change made through these names would be a change to your font, which is why today's script only reads.

## Step 3: Use only what's on the list

Now the summary, with fontParts names:

```python
def summary(font):
    without = []
    for glyph in font:
        if glyph.unicode is None:
            without.append(glyph.name)
    return {"glyphs": len(font), "without": without}
```

Looping over the font gives glyphs. `glyph.unicode` is the glyph's character code as a number, or `None` when it has none. `len(glyph)` counts its contours and `glyph.components` lists its components, so a glyph with neither has nothing drawn in it. `font.kerning` behaves like a dictionary of pairs, so `len` of it counts them. `font.info.familyName` and `font.info.styleName` are the two halves of the font's name.

Some of these are spelled the way you know from Fly and some aren't. Don't guess from Fly. The agreement has its own documentation, and the rule for a portable script is that every name on a font or glyph comes from there.

## Step 4: Trust the order

Here is the mistake, and it's the one that makes two editors disagree about the same font. This version collects the glyphs with nothing drawn, in the order the loop meets them:

```python
def empty_names(font):
    empty = []
    for glyph in font:
        if len(glyph) == 0 and len(glyph.components) == 0:
            empty.append(glyph.name)
    return empty
```

On my test font, which has two empty glyphs, one set of fontParts objects printed:

```text
Nothing drawn     2  nbspace, space
```

and the other:

```text
Nothing drawn     2  space, nbspace
```

It's the same font and the same function. The agreement says that looping over a font gives you every glyph. It doesn't say in what order, and the two disagree. One follows the font's glyph order; the other follows the order of its own storage.

You would never have found this in FontLab alone. A script that runs in one place can lean on a hundred habits of that place without knowing it. The cure costs one word: return `sorted(empty)`. Whenever a portable script shows a list, it puts the list in an order of its own choosing.

## The whole script

There are three files today. The first does the work. Save it as `plum_report.py`, beside `halfmoon.py`:

```python
# A font report that uses only fontParts names, so it can run in any
# editor that speaks fontParts. It reads the font and changes nothing.


def summary(font):
    without = []
    empty = []
    widest = None
    for glyph in font:
        if glyph.unicode is None:
            without.append(glyph.name)
        if len(glyph) == 0 and len(glyph.components) == 0:
            empty.append(glyph.name)
        if widest is None or glyph.width > widest.width:
            widest = glyph
    return {
        "glyphs": len(font),
        "without": sorted(without),
        "empty": sorted(empty),
        "widest": widest,
        "pairs": len(font.kerning),
    }


def lines(font):
    facts = summary(font)
    out = [f"{font.info.familyName} {font.info.styleName}"]
    out.append(f"Glyphs            {facts['glyphs']}")
    out.append(f"No character      {len(facts['without'])}")
    out.append(f"Nothing drawn     {len(facts['empty'])}  {', '.join(facts['empty'])}")
    widest = facts["widest"]
    if widest is not None:
        out.append(f"Widest            {widest.name} at {widest.width:g}")
    out.append(f"Kerning pairs     {facts['pairs']}")
    return out


def report(font):
    if font is None:
        print("Open a font first.")
        return
    for line in lines(font):
        print(line)
```

It has no `#FLM` line and no import. It doesn't use `halfmoon`, because Tove doesn't have `halfmoon`. That's the price of a portable file: it can lean on Python and on the agreement, and on nothing of yours.

`summary` gathers the facts into a dictionary, as the functions of chapter 95 did. `lines` turns the facts into text. `report` prints, and deals with there being no font. Keeping them apart means the part that reads the font can be checked without printing anything, which chapter 139 will use.

`widest` starts as `None` and is replaced by any glyph wider than the one held so far. It's the glyph itself that's kept, so `lines` can ask it for both its name and its width.

The second file is FontLab's launcher. Save it as `plum_report_fontlab.py`:

```python
#FLM: Plum Report
from fly.fp.world import FontWorld

import plum_report

plum_report.report(FontWorld().CurrentFont())
```

The third is for Tove. Hers starts from the agreement's own front door, which her editor fills in:

```python
from fontParts.world import CurrentFont

import plum_report

plum_report.report(CurrentFont())
```

The two launchers differ in one import. Everything that could need fixing next month is in the file they share.

## Run it

On the seven-glyph test font, through both sets of objects:

```text
Plum Regular
Glyphs            7
No character      1
Nothing drawn     2  nbspace, space
Widest            m at 790
Kerning pairs     2
```

In FontLab, with `Plum-practice` in front, I expect the first number to be 274, the count chapter 114's check prints, "No character" to be 39, since that check finds 235 glyphs with one, and 105 kerning pairs, as chapter 109 left them. Which glyphs it finds with nothing drawn, and which is widest, you'll see before I do. If your first two numbers differ from chapter 114's, believe chapter 114 and tell me.

One thing to watch for. A fontParts font is one master. FontLab's Plum has three, and which of them `CurrentFont` hands over through Fontport, I haven't seen. The style name on the first line will tell you.

Mira sends Tove two files and a line: "Put them in the same folder. Run the short one."

## Break it on purpose

Add a line to `summary`, inside the loop:

```python
        if glyph.selected:
            print(glyph.name)
```

`selected` is on the agreement's list: a glyph can say whether it's selected. Run the report. Through Fontport, on the first glyph:

```text
UnsupportedCapability: RGlyph.<lambda>: No native primitive implements this FontParts operation
```

And through the reference objects, which have no window to select anything in:

```text
NotImplementedError: The RGlyph subclass does not implement this method.
```

A name being on the list means every editor knows what you're asking. It doesn't mean every editor can answer. Fontport's documents say plainly that selection is one of the things it doesn't carry, along with a few kinds of change it refuses because FontLab stores the thing differently, such as kerning values with a fraction. As in chapter 135, a refusal that names the missing piece is the honest behaviour.

So "portable" is a claim you test, editor by editor. The way to know that a report runs in two places is to run it in two places. Take the two lines out.

## What you learned

An interface is a list of names that several programs agree to answer to. A script becomes portable when the working part is a function that's handed its font, uses only names from the agreement, and leans on nothing of yours; fetching the font goes in a separate few lines for each editor. The agreement leaves things unsaid, such as the order of glyphs, so a portable script chooses its own order. And being on the list isn't the same as being supported, so you run the script in each place before you say it works there.

## Try it yourself

1. Add a line to the report for the narrowest glyph that has something drawn. Decide what to do when two glyphs tie, and make sure both editors would name the same one.
2. `glyph.leftMargin` is the left sidebearing, and `None` for a glyph with nothing drawn. Add a count of glyphs whose left and right margins are equal. Mind the `None`.
3. Write a third launcher that doesn't use the current font at all. It asks `FontWorld().AllFonts()` for every open font and prints a report for each, with a blank line between.

## Next

Friday's build still starts with somebody opening FontLab, finding the Scripts menu and clicking twice. Ines would like to type one line in a terminal window and go for coffee. Chapter 137 drives FontLab from outside, and finds out how long a job it will accept that way.
