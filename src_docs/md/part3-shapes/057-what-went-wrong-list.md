---
this_file: src_docs/md/part3-shapes/057-what-went-wrong-list.md
---

# 57. The what-went-wrong list

Tuesday. Yesterday's script read 34 recipes, had a line for 14 and said nothing about the other 20. Mira lost ten minutes over a missing `ę`.

This morning the recipe file grew. Slovak is no longer a rumor, so Mira added three lines for it, in a hurry, between two phone calls. Ines came by and asked for an `ĩ`, for a name in a book on Paraguay, and Mira added that as well. She suspects that at least one of the four new lines is wrong, and she'd like the script to tell her which.

Today's change is small. The script will stop treating a recipe it can't follow as nothing. Each one becomes an entry in a list, with the line number in the file and a sentence about what's wrong. The script finishes its work on the recipes that are sound, and then hands the list over.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, in the state chapter 56 left it. The outputs assume you didn't build `racute` and `Racute` in exercise 2 of that chapter. If you did, your row for `Racute` will say `fine`.
- `build_accents.py` and `accents.txt` from chapter 56.
- The Font window in front when you run the whole script.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The changes of the last four chapters were applied to that file by hand first.

Add Mira's new lines to the end of `accents.txt`, mistakes and all. Leave an empty line after the last line that's there, so that the line numbers match mine:

```text

# Slovak
Ŕ Racute R acute
ŕ racute rr acute
ľ lcaron l

# For Ines
ĩ itilde i tilde
```

## Step 1: What can go wrong with a recipe

Before you write the code, write the list of troubles. I count five.

1. The line doesn't have four words.
2. The base isn't in the font.
3. The accent isn't in the font.
4. Both are there, and the base has no peg that fits a loop of the accent.
5. The glyph is in the font already, and it isn't one base with one accent.

Yesterday's script crashed on the first, kept quiet on the next three, and would have crashed on the fifth if a recipe had hit it.

None of the five is a reason to stop. If line 47 is short, lines 1 to 46 are no worse for it. So the rule for today is: when one recipe is in trouble, write the trouble down and go on to the next. Then say everything at the end, in one place. Mira fixes her file once and runs the script again.

A script that stops at the first trouble would need 23 runs for 23 troubles.

## Step 2: Number the lines

To say "line 47", the reader function has to count lines as it goes. You could keep a counter in a box and add 1 on every turn. Python has a helper that does it for you:

```python
for number, word in enumerate(["ogonek", "caron", "dotaccent"], 1):
    print(number, word)
```

```text
1 ogonek
2 caron
3 dotaccent
```

`enumerate` wraps anything you can loop over and gives a pair on every turn: a count and the item. The `1` says where to start counting. Leave it out and the count starts at 0, which suits Python and doesn't suit a person who's looking at line numbers in a text editor.

In the reader, the count has to include the comment lines and the empty ones, because the editor counts those too. So `enumerate` goes around the file itself, and the test for lines to skip comes after:

```python
def read_recipes(path):
    recipes = []
    problems = []
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            words = line.split()
            if not words or words[0].startswith("#"):
                continue
            if len(words) != 4:
                problems.append((number, f"{len(words)} words where 4 are needed: {line.strip()}"))
                continue
            character, name, base, mark = words
            recipes.append((number, character, name, base, mark))
    return recipes, problems
```

Three things changed from yesterday.

The line is split first and tested afterwards. An empty line splits into an empty list, and `not words` is true for an empty list, as it is for an empty string.

The count of words is checked before the four names take them. That's the whole cure for yesterday's `ValueError`. The script looks before it unpacks.

And the function hands back two lists, the recipes and the problems, as a pair. A recipe now carries its line number in front, because trouble can turn up later, when the font is asked, and the script must still know which line to blame.

## Step 3: A problem is a thing you keep

A problem here is a tuple of two items: a number and a sentence. It's ordinary data. You can put it in a list, sort it, count it and print it, like a width or a name.

In `main`, every place where yesterday's script said `continue` and nothing else now leaves a note first:

```python
if base not in have:
    problems.append((number, f"{name}: no glyph named {base} for the base"))
    continue
```

Write the sentence for the person who'll read it. It names the glyph she wanted, the thing that's missing, and what role that thing played. "KeyError: 'rr'" would be true as well, and Mira would have to work out the rest.

For the fifth kind of trouble, `moves_for` gets a guard. It used to take the second component of every layer on trust. Now it counts them first and hands back `None` when a layer holds some other number than two:

```python
found = parts.components(layer)
if len(found) != 2:
    return None
```

So `moves_for` has three answers: `None` for "this glyph isn't what you think", an empty list for "fine", and a list with rows in it for "move these". The caller has to tell `None` from an empty list, and `not rows` can't, because it's true for both. Use `rows is None`.

## Step 4: Print them in order

The problems come from two places: the reader finds the short lines, and `main` finds the rest. Put together, they're out of order. `sorted` puts tuples in order by their first item, so a list of `(number, sentence)` comes out by line number without your saying how:

```python
print(sorted([(47, "short line"), (5, "no ogonek"), (46, "no rr")]))
```

```text
[(5, 'no ogonek'), (46, 'no rr'), (47, 'short line')]
```

That works as long as every entry has the same shape. Suppose that in one of the five places you type the sentence and forget the number:

```python
problems.append(f"{name}: {base} has no peg that fits {mark}")
```

```text
Traceback (most recent call last):
  ...
TypeError: '<' not supported between instances of 'str' and 'tuple'
```

To sort, Python asks of two entries which one is smaller. It can answer that for two tuples and for two strings. For a string and a tuple it has no answer, and says so. The message points at `sorted`, which is innocent. The fault is thirty lines up, where an entry of the wrong shape went into the list. When a list is filled in several places, check each place for the shape of what goes in.

You'll see that error only when a line in the file reaches that branch.

## Step 5: One more list, for the drawing table

Twenty of the problems will turn out to be the same three problems. Mira doesn't want to count carons by eye. A tally, as in chapter 22, turns the long list into a short one:

```python
to_draw = {}
...
to_draw[mark] = to_draw.get(mark, 0) + 1
```

It counts how many recipes are waiting for each missing accent. That's the order in which drawing them pays off.

## The whole script

Here is the new `build_accents.py`. The three functions that work out shifts and describe a new glyph are as they were.

```python
#FLM: Build Accented Letters
# Reads recipes from a text file: character, glyph name, base, accent.
# Builds the glyphs that are missing and moves accents that sit off their
# anchors. Every recipe it can't follow goes into a list, with its line
# number, and the list is printed at the end.
from pathlib import Path

import fly.ap.anchors.writer as anchors
import fly.ap.components.writer as parts
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.glyphs.creation as creation
import halfmoon
from fly import fl
from fly.pens import layer_of

MASTERS = ["Light", "Regular", "Bold"]


def read_recipes(path):
    recipes = []
    problems = []
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            words = line.split()
            if not words or words[0].startswith("#"):
                continue
            if len(words) != 4:
                problems.append((number, f"{len(words)} words where 4 are needed: {line.strip()}"))
                continue
            character, name, base, mark = words
            recipes.append((number, character, name, base, mark))
    return recipes, problems


def layer_for(font, name, master):
    return layer_of(halfmoon.rich(font, font[name]).fl, master)


def shift_for(font, base, mark, master):
    pegs = anchors.anchor_points(layer_for(font, base, master))
    loops = anchors.anchor_points(layer_for(font, mark, master))
    for loop in sorted(loops):
        family = loop[1:]
        if loop.startswith("_") and family in pegs:
            bx, by = pegs[family]
            mx, my = loops[loop]
            return round(bx - mx), round(by - my)
    return None


def shifts_for(font, base, mark):
    shifts = {}
    for master in MASTERS:
        shift = shift_for(font, base, mark, master)
        if shift is None:
            return None
        shifts[master] = shift
    return shifts


def new_glyph(font, character, name, base, mark, shifts):
    layers = []
    components = []
    for master in MASTERS:
        dx, dy = shifts[master]
        width = round(layer_for(font, base, master).advanceWidth)
        layers.append((master, width))
        components.append(creation.Part(master, base, 0, 0))
        components.append(creation.Part(master, mark, dx, dy))
    return creation.NewGlyph(
        name=name,
        layers=tuple(layers),
        unicodes=(ord(character),),
        components=tuple(components),
    )


def moves_for(font, name, shifts):
    rich = halfmoon.rich(font, font[name])
    rows = []
    for master in MASTERS:
        layer = layer_of(rich.fl, master)
        found = parts.components(layer)
        if len(found) != 2:
            return None
        accent = found[1]
        if parts.offset(accent) != shifts[master]:
            rows.append((rich.fl, layer, [(accent.id, shifts[master])]))
    return rows


def report(problems, to_draw):
    if not problems:
        print("Every recipe could be followed.")
        return
    print()
    print(f"{len(problems)} recipes need a look:")
    for number, text in sorted(problems):
        print(f"  line {number:>2}  {text}")
    if to_draw:
        def how_often(mark):
            return to_draw[mark]

        print()
        print("Accents to draw, and the recipes waiting for each:")
        for mark in sorted(to_draw, key=how_often, reverse=True):
            print(f"  {mark:<11}{to_draw[mark]:>3}")


def is_auto(font, name):
    rich = halfmoon.rich(font, font[name])
    return any([layer_of(rich.fl, master).autoLayer for master in MASTERS])


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    folder = Path(font.path).parent if font.path else ""
    path = halfmoon.choose_text_file("Choose a recipe file", folder)
    if path is None:
        return

    recipes, problems = read_recipes(path)
    print(f"{len(recipes)} recipes read.")
    have = {glyph.name for glyph in font.glyphs}
    specs = []
    work = []
    to_draw = {}
    moved = 0
    fine = 0
    auto = 0
    for number, character, name, base, mark in recipes:
        if base not in have:
            problems.append((number, f"{name}: no glyph named {base} for the base"))
            continue
        if mark not in have:
            problems.append((number, f"{name}: no glyph named {mark} for the accent"))
            to_draw[mark] = to_draw.get(mark, 0) + 1
            continue
        shifts = shifts_for(font, base, mark)
        if shifts is None:
            problems.append((number, f"{name}: {base} has no peg that fits {mark}"))
            continue
        if name not in have:
            specs.append(new_glyph(font, character, name, base, mark, shifts))
            state = "new"
        elif is_auto(font, name):
            auto += 1
            state = "auto"
        else:
            rows = moves_for(font, name, shifts)
            if rows is None:
                problems.append((number, f"{name}: is in the font, but not as one base and one accent"))
                continue
            if rows:
                work = work + rows
                moved += 1
                state = "move"
            else:
                fine += 1
                state = "fine"
        text = ", ".join([f"{shifts[m][0]} {shifts[m][1]}" for m in MASTERS])
        print(f"{name:<13}{state:<6}{base} + {mark}: {text}")
    print(f"{len(specs)} to build, {moved} to move, {fine} fine as they are, {auto} automatic.")
    report(problems, to_draw)

    if not specs and not work:
        return
    if not halfmoon.ask(f"Build {len(specs)} glyphs and move the accents in {moved}?"):
        return

    package = scripting.current_package()
    if work:
        facts = history.scan_auto_facts(package)
        parts.require_safe(work, facts)
        parts.apply_work(work, "Move accents to their anchors", facts, parts.MoveEditor())
    if specs:
        facts = history.scan_auto_facts(package)
        creation.create_glyphs(package, specs, "Build accented letters", facts)
    halfmoon.tell(f"Built {len(specs)} glyphs. Moved the accents in {moved}.")


main()
```

```text
37 recipes read.
Cacute       fine  C + acute: 88 210, 101 210, 111 210
cacute       fine  c + acute: -4 0, 5 0, 15 0
Nacute       fine  N + acute: 92 210, 119 210, 129 210
nacute       fine  n + acute: 40 0, 52 0, 62 0
Sacute       fine  S + acute: 18 210, 38 210, 48 210
sacute       fine  s + acute: -34 0, -25 0, 15 0
Zacute       fine  Z + acute: 33 210, 56 210, 66 210
zacute       fine  z + acute: -20 0, -12 0, 28 0
Uring        fine  U + ring: 57 210, 69 210, 69 210
uring        fine  u + ring: 0 0, 12 0, 12 0
iacute       auto  dotlessi + acute: -147 0, -139 0, -140 0
icircumflex  auto  dotlessi + circumflex: -153 0, -139 0, -124 0
idieresis    auto  dotlessi + dieresis: -153 0, -137 0, -123 0
igrave       auto  dotlessi + grave: -116 0, -117 0, -140 0
Racute       new   R + acute: 33 210, 52 210, 62 210
1 to build, 0 to move, 10 fine as they are, 4 automatic.

23 recipes need a look:
  line  5  Aogonek: no glyph named ogonek for the accent
  line  6  aogonek: no glyph named ogonek for the accent
  line  9  Eogonek: no glyph named ogonek for the accent
  line 10  eogonek: no glyph named ogonek for the accent
  line 17  Zdotaccent: no glyph named dotaccent for the accent
  line 18  zdotaccent: no glyph named dotaccent for the accent
  line 21  Ccaron: no glyph named caron for the accent
  line 22  ccaron: no glyph named caron for the accent
  line 23  Dcaron: no glyph named caron for the accent
  line 24  Ecaron: no glyph named caron for the accent
  line 25  ecaron: no glyph named caron for the accent
  line 26  Ncaron: no glyph named caron for the accent
  line 27  ncaron: no glyph named caron for the accent
  line 28  Rcaron: no glyph named caron for the accent
  line 29  rcaron: no glyph named caron for the accent
  line 30  Scaron: no glyph named caron for the accent
  line 31  scaron: no glyph named caron for the accent
  line 32  Tcaron: no glyph named caron for the accent
  line 35  Zcaron: no glyph named caron for the accent
  line 36  zcaron: no glyph named caron for the accent
  line 46  racute: no glyph named rr for the base
  line 47  3 words where 4 are needed: ľ lcaron l
  line 50  itilde: i has no peg that fits tilde

Accents to draw, and the recipes waiting for each:
  caron       14
  ogonek       4
  dotaccent    2
```

Add the totals up once by hand. The first line says 37 recipes, 15 rows follow, and 37 minus 15 is 22. The report says 23. The numbers disagree, and they should: the short line on line 47 never became a recipe, so the reader counted 37 sound lines and one problem. Thirty-eight lines were meant as recipes, 15 could be followed and 23 couldn't.

The problems are printed before the question is asked, so Mira can say no, fix her file and come back.

## Read the report

Twenty lines say the same thing in three flavors, and the short list at the bottom sums them up: draw a caron and 14 letters can be built, an ogonek gives 4, a dot accent gives 2. That's Mira's week, in order.

The last three lines are the ones she typed between phone calls.

Line 46 has `rr` for the base. Yesterday's script would have skipped it without a sound.

Line 47 has three words. She didn't forget the accent. She stopped, because `ľ` takes the apostrophe-like caron that Plum doesn't have, and she wasn't sure what to call it. The script can't know that, and reports what it sees.

Line 50 is the interesting one. Both glyphs exist, and the script says that `i` has no peg that fits `tilde`. Print the anchors of `i` and you get `bottom` and `ogonek`, nothing above. That's deliberate. An accent above an `i` replaces the dot, so the letter to build on is `dotlessi`, which is why the four recipes at the end of yesterday's list are written that way. An absent anchor stopped a wrong glyph from being built, and the report said why.

## What you learned

When one item in a batch is in trouble, record it as a tuple of a line number and a sentence, and carry on. `enumerate(things, 1)` counts while you loop, and the size of a list should be checked before you unpack it into names. `sorted` orders tuples by their first item, and fails with a `TypeError` when the entries don't share a shape. A function can have three answers, and then `is None` tells nothing-to-do from can't-be-done.

## Try it yourself

1. Fix the three lines. Correct `rr`. Put a `#` in front of the `ľ` line and write after it what's missing. Change the base in the `ĩ` line to `dotlessi`. Run the script. If you said yes to the `Racute` above, I get two glyphs to build, with shifts of -153, -139 and -124 for the `itilde`, and 20 recipes that need a look.
2. Add the recipe `Ø Oslash O acute`, which is nonsense, since the `Ø` is a drawn letter that Plum has. Which of the five troubles does the script report, and from which function does the answer come? Remove the line afterwards.
3. Mira wants to mail the list to Oskar. Add a step at the end of `report` that asks for a file with `halfmoon.choose_save_file` and writes the same lines into it, as chapter 26 wrote the glyph list. Keep the printing as well.

## Next

The recipes borrow shapes, and a borrowed shape can't drift away from its source. Some of Plum's look-alike glyphs were made the other way, as copied outlines, years ago. Chapter 58 puts two of them side by side and asks whether they are still the same drawing, node for node.
