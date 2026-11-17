---
this_file: src_docs/md/part5-words/086-sort-the-font.md
---

# 86. Put the font in order

Monday of week seventeen. Ines scrolls through her Plum in the Font window and stops. The three hundred Greek glyphs sit at the end in the order the import delivered them, and the import had no order. Further up, `AE` comes after `Atilde`, the two ligatures sit between `z` and the figures, and the accents trail in at the bottom behind the euro sign.

"Capitals, then small letters, then figures, then the rest," she says. "And alphabetical inside each."

That's two rules, one inside the other. In chapter 36 you sorted a table by one thing: width, or name. Today's sort has several parts to its key.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed. The font must be saved, because the script writes a text file next to it.
- The `tell` function from [chapter 39](../part2-a-toolbox/039-ask-the-user.md). The script below defines it again, so it runs by itself.

I couldn't run the code in FontLab 9. The sorting is plain Python, and I ran it on the glyph names and code points in Plum's source file. The numbers below are for Plum as it ships, 205 glyphs. Yours will be higher: by the small caps and alternates from Part 2, which have no code points, and by the letters Part 3 built, which have. Part 3's two stand-in accents land in odd places too, as the notes below say.

One limit, stated early. This chapter's script works out an order, prints it and saves it. It doesn't move a single glyph. I found no way to reorder a font from Python that I could vouch for, and Fly's own ordering tool says the same about itself. The end of the chapter shows what to do with the list.

## Step 1: What plain sorting does

Take the names in font order and sort them:

```python
from fly import fl

font = fl.CurrentFont()
names = [glyph.name for glyph in font.glyphs]
by_name = sorted(names)
print(" ".join(by_name[:8]))
print(" ".join(by_name[66:72]))
```

```text
.notdef A AE Aacute Abreve Acircumflex Adieresis Agrave
Ydieresis Ygrave Z a aacute abreve
```

Two things happen that Ines didn't ask for. `AE` jumps ahead of `Aacute`, and every capital comes before every small letter, so `Z` is followed by `a`.

Python compares strings one character at a time, by code point. Capital `E` is 69 and small `a` is 97, so `AE` beats `Aa`. You met the cure in chapter 36: sort on the name in lowercase.

```python
def lowered(name):
    return name.lower()

print(" ".join(sorted(names, key=lowered)[:10]))
```

```text
.notdef A a Aacute aacute Abreve abreve Acircumflex acircumflex acute
```

Now it's a dictionary, in the bookshop sense. Capitals and small letters are shuffled together, and the accent `acute` has wandered in among the letters because its name starts with `a`. Neither sort knows what a glyph is. Both look only at spelling.

## Step 2: A key with two parts

Tuples compare too, and the way they do it is the whole lesson of this chapter:

```python
print((1, "zeta") < (2, "alpha"))
print((1, "b") < (1, "a"))
```

```text
True
False
```

Python looks at the first items. If they differ, that settles it, and the rest is never read. Only when the first items are equal does it move on to the second. So a tuple key means "sort by this, and among equals by that". A league table works this way: points first, goal difference when points are level.

Try it on four small rows:

```python
rows = [("small", "b"), ("cap", "B"), ("small", "a"), ("cap", "A")]
print(sorted(rows))
```

```text
[('cap', 'A'), ('cap', 'B'), ('small', 'a'), ('small', 'b')]
```

Grouped, then ordered inside each group. `cap` came before `small` only because `c` comes before `s` in the alphabet, which is luck. The first part of the key should be a number that you choose.

## Step 3: The mistake

A first idea for the number: the code point. Capitals have low code points, small letters higher ones. Build the keys and sort:

```python
keys = [(65, "A"), (None, ".notdef"), (97, "a")]
print(sorted(keys))
```

```text
TypeError: '<' not supported between instances of 'NoneType' and 'int'
```

`.notdef` has no code point, so its `unicode` is `None`, and Python won't say whether `None` is less than 65. It's a fair refusal. Nothing is neither small nor large.

Every part of a sort key has to be comparable with the same part of every other key. A key function must never hand back `None` in one row and a number in the next. Your small caps have no code points either, so this would have hit `a.sc` as well.

And code points would have been a poor first part even without the error. `Aacute` is 193, far beyond `z` at 122. Sorting by code point puts the accented capitals after the whole basic alphabet.

## Step 4: What kind of glyph is it?

What Ines named were kinds: capitals, small letters, figures. Python knows the kind of every character in Unicode. The knowledge is in a module that comes with Python, `unicodedata`:

```python
import unicodedata

for char in "Aa5,+":
    print(char, unicodedata.category(char))
```

```text
A Lu
a Ll
5 Nd
, Po
+ Sm
```

Each answer is two letters. The first is the broad kind: `L` letter, `N` number, `P` punctuation, `S` symbol, `Z` separator. The second narrows it: `Lu` is an uppercase letter, `Ll` a lowercase one.

This works for `Aacute` and for a Greek alpha as well as for `A`. It's the standard's own classification, so you don't need a list of capitals.

Two small tables turn the codes into Ines's words, and a list gives the order she wants them in:

```python
KINDS = ["special", "capitals", "small letters", "other letters", "figures",
         "punctuation", "symbols", "spaces", "unknown"]
BY_CATEGORY = {"Lu": "capitals", "Ll": "small letters"}
BY_LETTER = {"L": "other letters", "N": "figures", "P": "punctuation",
             "S": "symbols", "Z": "spaces"}
```

The function looks in the exact table first and falls back to the broad one:

```python
def kind_of(name, codes):
    if name == ".notdef":
        return "special"
    base = name.split(".")[0]
    code = codes.get(name)
    if code is None:
        code = codes.get(base)
    if code is None:
        return "unknown"
    category = unicodedata.category(chr(code))
    if category in BY_CATEGORY:
        return BY_CATEGORY[category]
    return BY_LETTER.get(category[0], "unknown")
```

`codes` is a dictionary from glyph name to first code point, or `None`. A glyph without a code borrows its base's: `a.sc` splits at the dot into `a` and `sc`, and `a` is a small letter. So small caps and alternates sort next to the letters they belong to. A glyph with no code and no base to borrow from is `unknown`, and those go last where you can find them.

The function always returns one of the nine words. It never returns `None`. That's Step 3's rule kept.

## Step 5: The key and the suggested order

The first part of the key is the position of the kind in `KINDS`, a number you chose by ordering that list. The second is the name in lowercase. The third is the name as spelled:

```python
def order_key(name, codes):
    return (KINDS.index(kind_of(name, codes)), name.lower(), name)
```

```python
print(order_key("Aacute", codes))
print(order_key("five", codes))
```

```text
(1, 'aacute', 'Aacute')
(4, 'five', 'five')
```

The third part looks like a repeat. It's there for the day two names differ only in case inside one kind. Without it their keys would be equal and their order would depend on where they stood before. With it, the same font always gives the same list.

Run the whole script. It counts the kinds, then says how far the font is from the suggested order:

```text
   1  special
  67  capitals
  70  small letters
   1  other letters
  10  figures
  37  punctuation
  18  symbols
   1  spaces
136 of 205 glyphs would change place
   6  Agrave        AE
   7  Aring         Agrave
   8  Atilde        Aring
   9  AE            Atilde
  24  IJ            Iacute
Saved glyph-order.txt
```

The lines under the count are the first five places where the two orders part: position, the glyph there now, the glyph the suggested order puts there. `AE` moves up three places and pushes three glyphs down. 136 sounds dramatic. Most of those glyphs shift by a place or two because one neighbor moved.

One line in the count is odd: one "other letter" in a font of plain Latin. It's `circumflex`. The standard files that accent under modifier letters, while `acute`, `grave` and the others are symbols. So the suggested order puts `circumflex` between the small letters and the figures, away from its family. The classification is the standard's and it's consistent, but it isn't always what a type designer would choose. Exercise 2 mends this. In your font the stand-in `caron` from chapter 60 is a second "other letter" for the same reason, and `dotaccent` is one more symbol.

## The whole script

```python
#FLM: Sort Glyphs
# Proposes a glyph order: by kind, then by name. Prints how the font differs
# and saves the suggested order as glyph-order.txt. Does not reorder the font.
import unicodedata
from pathlib import Path

from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


KINDS = ["special", "capitals", "small letters", "other letters", "figures",
         "punctuation", "symbols", "spaces", "unknown"]
BY_CATEGORY = {"Lu": "capitals", "Ll": "small letters"}
BY_LETTER = {"L": "other letters", "N": "figures", "P": "punctuation",
             "S": "symbols", "Z": "spaces"}
FILE_NAME = "glyph-order.txt"
SHOW = 5


def kind_of(name, codes):
    if name == ".notdef":
        return "special"
    base = name.split(".")[0]
    code = codes.get(name)
    if code is None:
        code = codes.get(base)
    if code is None:
        return "unknown"
    category = unicodedata.category(chr(code))
    if category in BY_CATEGORY:
        return BY_CATEGORY[category]
    return BY_LETTER.get(category[0], "unknown")


def order_key(name, codes):
    return (KINDS.index(kind_of(name, codes)), name.lower(), name)


def propose(codes):
    def key(name):
        return order_key(name, codes)

    return sorted(codes, key=key)


def count_kinds(codes):
    counts = {}
    for name in codes:
        kind = kind_of(name, codes)
        counts[kind] = counts.get(kind, 0) + 1
    for kind in KINDS:
        if kind in counts:
            print(f"{counts[kind]:>4}  {kind}")


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    codes = {glyph.name: glyph.unicode for glyph in font.glyphs}
    now = list(codes)
    new = propose(codes)
    count_kinds(codes)

    moved = [(place, old, name)
             for place, (old, name) in enumerate(zip(now, new)) if old != name]
    print(f"{len(moved)} of {len(now)} glyphs would change place")
    for place, old, name in moved[:SHOW]:
        print(f"{place:>4}  {old:<14}{name}")

    order_file = Path(font.path).parent / FILE_NAME
    with open(order_file, "w", encoding="utf-8") as f:
        for name in new:
            f.write(name + "\n")
    print("Saved", FILE_NAME)


main()
```

Save it as `sort_glyphs.py`.

Notes on the listing.

`codes` does two jobs. It maps names to code points, and because a dictionary keeps the order things went in, `list(codes)` is the font's present order. `sorted(codes, ...)` sorts the names, since looping over a dictionary gives its keys.

`propose` defines `key` inside itself, as chapter 84's `main` defined `add`. `sorted` calls the key function with one argument, the item. `order_key` wants two. The inner function takes the one and supplies the other from the box it can see.

`zip(now, new)` pairs the two lists place by place, and `enumerate` numbers the pairs. You've used both before, most recently in chapter 78. The round brackets in `for place, (old, name)` unpack the pair inside the numbered item.

## Break it on purpose

Take `"unknown"` off the end of `KINDS` and run the script on a font that has a glyph with no code point and no base, such as a `glyph201` left over from chapter 82. If you have none, test the line by itself:

```python
KINDS.index("unknown")
```

```text
ValueError: 'unknown' is not in list
```

`index` raises an error when the item isn't there. That's the right behavior here. A kind missing from the order list is a mistake in the script, and a sort that quietly put such glyphs somewhere would hide it. Put the word back.

## Using the list

The file has one glyph name to a line, in the proposed order. What then?

FontLab can reorder a font by hand. Per the User Guide for FontLab 8, the Font window in its Index mode lets you drag glyphs into place, and **Font > Sort Glyphs** reorders the font by the rules it offers. I haven't checked that menu in FontLab 9, and I don't know of a rule there that matches Ines's two-part one. For a few misplaced glyphs, dragging with the list open beside you is quick. For three hundred, the list is what you hand to whoever builds the fonts, since export tools commonly accept a glyph order as a text file.

So the script's product is a decision written down. That has worth by itself: next month the same script will tell Ines in one line whether the font has drifted.

## What you learned

Tuples compare item by item, so a tuple key sorts by its first part and settles ties with the next. Every part of a key must be comparable across all rows, which rules out `None`. The order of a list can itself be data: `KINDS.index(...)` turns a word into a rank you chose. `unicodedata.category` tells you what kind of character a code point is, for every script in Unicode.

## Try it yourself

1. Ines changes her mind: figures before letters. Change one line and run again. How many glyphs would change place now?
2. Bring `circumflex` home. Add a dictionary `OVERRIDES = {"circumflex": "symbols"}` and have `kind_of` look there before anything else, with `.get`. The count should then read 19 symbols and no "other letters" line.
3. Add a part to the key so that inside each kind a base glyph is followed at once by its suffixed forms, and only then by the next base: `a`, `a.alt`, `a.sc`, `aacute`. Print the keys for those four names with and without your change. Hint: `name.split(".")[0].lower()` as the second part, and think about why `a.sc` sorts before `aacute` already but `A.sc` and `Aacute` might not agree.

## Next

Plum has features, and nobody at Halfmoon has read them since Oskar left. Chapter 87 opens the feature text and lists what's in it.
