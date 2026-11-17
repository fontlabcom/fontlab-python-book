---
this_file: src_docs/md/part3-shapes/052-components.md
---

# 52. Borrowed shapes

Tuesday. The art director's last note on the Bold was about the lowercase `a`: the bowl closes up at small sizes. Mira opened the counter a little this morning, eight units, and sent Ines a proof.

Ines calls back. "Good. The German edition is next. You did the ä as well? And the Swedish one with the ring?"

Mira hasn't touched them. She double-clicks `adieresis`, ready to do the same eight units again, and the bowl is already open. In `aring` too, and in `agrave`. She didn't change those glyphs, and they changed.

You know why, roughly. In chapter 41 you found that `eacute` has two elements and nothing drawn in it, and I said each element points at another glyph. Chapter 51 called that a second label. Today you'll open those pointers and read them: which glyph, and shifted by how much. Then you'll ask the whole font, and the first open line on Oskar's sheet gets crossed out: *List the glyphs that are built from other glyphs.*

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `rich`.
- Nothing in the font changes today. Every script in this chapter reads only.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. So were the names, shifts and counts.

## Step 1: Ask an element what it borrows

A layer keeps its elements in `layer.shapes`, as chapter 41 showed. Some of those are drawings and some are components. Fly has a small module that picks out the components and reads them:

```python
import fly.ap.components.writer as parts
import halfmoon
from fly import fl
from fly.pens import layer_of

font = fl.CurrentFont()
glyph = halfmoon.rich(font, font["adieresis"])
layer = layer_of(glyph.fl, "Regular")
for part in parts.components(layer):
    print(parts.base_of(part), parts.offset(part))
```

```text
a (0.0, 0.0)
dieresis (-12.0, 0.0)
```

The first line of the script gives a long module name a short one, `parts`, as you did with `history` in chapter 29. The module is called `writer` because most of what's in it changes components. Today you use only the three functions that read.

`parts.components(layer)` gives a list of the layer's components, in order. `parts.base_of(part)` gives the name of the glyph a component points at. FontLab calls that glyph the **base** of the component. `parts.offset(part)` gives the shift, as a pair of numbers: across and up.

So the `ä` in the Regular is two notes. One says "show `a` here, where it is". The other says "show `dieresis` here, 12 units to the left". There's no outline in the glyph. When Mira opened the bowl of `a`, there was nothing in `adieresis` to update. FontLab draws it from the `a` every time it shows it.

## Step 2: A pair of numbers

`parts.offset` gave `(-12.0, 0.0)`: two numbers in parentheses. You've had four numbers that way from `halfmoon.box`, and you took them apart with four names on the left of the `=`. A pair comes apart the same way:

```python
dx, dy = parts.offset(part)
print(round(dx), round(dy))
```

```text
-12 0
```

The `d` in `dx` is a habit from mathematics. It stands for "difference": how far across, compared with where the base glyph has its outline. The numbers are floats, so `round` tidies them for printing.

The shift belongs to a layer, as everything about an outline does. Ask all three masters:

```python
for master in ["Light", "Regular", "Bold"]:
    layer = layer_of(glyph.fl, master)
    for part in parts.components(layer):
        dx, dy = parts.offset(part)
        print(master, parts.base_of(part), round(dx), round(dy))
```

```text
Light a 0 0
Light dieresis -25 0
Regular a 0 0
Regular dieresis -12 0
Bold a 0 0
Bold dieresis -13 0
```

The two dots sit in a different place over each weight of `a`, because each `a` has a different shape. Whoever built the `ä` placed them three times.

## Step 3: Ask the whole font

Now the chore. Go through every glyph, and print the ones that have components:

```python
MASTER = "Regular"

for glyph in font.glyphs:
    layer = layer_of(halfmoon.rich(font, glyph).fl, MASTER)
    texts = []
    for part in parts.components(layer):
        dx, dy = parts.offset(part)
        texts.append(f"{parts.base_of(part)} {round(dx)} {round(dy)}")
    if texts:
        print(f"{glyph.name:<14}{', '.join(texts)}")
```

```text
Aacute        A 0 0, acute 88 210
Abreve        A 0 0, breve 48 210
Acircumflex   A 0 0, circumflex 48 210
Adieresis     A 0 0, dieresis 50 210
Agrave        A 0 0, grave 18 210
Aring         A 0 0, ring 48 210
...
```

I've cut the output after six lines. Yours has 85.

Look at the last number in each line: 210. The accents were drawn to sit over lowercase letters. Over a capital, each one is lifted by 210 units, which is the distance from the x-height to the cap height: 688 minus 478. The accents over lowercase letters have a 0 there. Somebody did that sum once and typed it 34 times. In chapter 54 you'll meet a way to let the glyphs carry that information themselves.

Farther down the list there are glyphs you may not have expected:

```text
colon         period 0 0, period 0 378
ellipsis      period 0 0, period 230 0, period 460 0
```

The colon is two periods, one of them 378 units up. The ellipsis is three, 230 apart. That's where chapter 49's step of 230 came from. I said then that a script could read it, and this is the script.

## Step 4: Turn the question around

Mira's question this morning ran the other way. She didn't ask "what is `adieresis` made of?" She asked, without knowing it, "which glyphs change when I change `a`?"

The list from step 3 has the answer in it, but you'd have to read 85 lines to find it. A dictionary can turn the list around: the key is a base glyph, and the value is a list of the glyphs that borrow it. That's new. Until now the values in your dictionaries were single things, a number or a name. A value can be a list, and then you fill it with `append`:

```python
users = {}
for glyph in font.glyphs:
    layer = layer_of(halfmoon.rich(font, glyph).fl, MASTER)
    for part in parts.components(layer):
        base = parts.base_of(part)
        users[base].append(glyph.name)
```

```text
Traceback (most recent call last):
  File "<string>", line 6, in <module>
KeyError: 'A'
```

The first glyph with a component is `Aacute`, and its first base is `A`. The script asks the dictionary for the list that belongs to `A`, to append to it. The dictionary is empty. There's no such list yet, and you can't append to a list that isn't there.

Chapter 22 had the same trouble when it counted, and solved it with `get`. For a list I'd rather spell it out: if the key is new, give it an empty list first.

```python
        if base not in users:
            users[base] = []
        if glyph.name not in users[base]:
            users[base].append(glyph.name)
```

The second `if` is there for glyphs such as the ellipsis, which borrows `period` three times and should be listed once. Now ask:

```python
print(users["a"])
print(users["period"])
```

```text
['aacute', 'abreve', 'acircumflex', 'adieresis', 'agrave', 'aring', 'atilde']
['colon', 'ellipsis', 'exclam', 'exclamdown', 'semicolon']
```

Seven glyphs follow the `a`. Mira's eight units went into all seven this morning, in the Bold, without a script.

The second line is worth a look too. Five glyphs borrow the period. Make the period heavier, and the colon, the semicolon, the ellipsis and both exclamation marks get heavier dots. That's a comfort when you want it and a surprise when you don't.

## Step 5: Borrowed and drawn in one glyph

The exclamation mark is on that list. Its dot is a period. Its stem is nobody's, so it's drawn in the glyph. Ask for both:

```python
glyph = halfmoon.rich(font, font["exclam"])
layer = layer_of(glyph.fl, MASTER)
print(len(parts.components(layer)), len(glyph.contours(MASTER)))
```

```text
1 1
```

It has one component and one contour of its own. Oskar's sheet has a word for such a glyph: it "mixes its own outlines with borrowed ones". Nothing is wrong with that in FontLab. Some other programs and some font formats don't take it, and I'd guess that's why Oskar wanted them found. Plum has two, `exclam` and `exclamdown`.

One more glyph stands out. The line for `questiondown` reads `question 416 688`. An upside-down question mark isn't a question mark shifted up and to the right. A component carries a whole transform, the kind you built in chapter 50, and this one turns the base around before it shifts it. The shift alone doesn't tell you that. The module has a test for it:

```python
print(parts.plain_move(part))
```

`plain_move` answers `True` when a component is only shifted, and `False` when it's also scaled, mirrored, slanted or turned. In Plum, `questiondown` is the only glyph where the answer is `False`.

## Step 6: What follows and what doesn't

Before you rely on components, know where the borrowing stops.

The outline follows. That's the whole idea. And it follows a long way: change the `period`, and five glyphs change.

The width doesn't follow. A component brings an outline, and the glyph that holds it keeps its own width. `adieresis` is 471 wide because somebody gave it that number, the same as `a`. If Mira had made the `a` eight units wider this morning, the seven accented glyphs would have kept 471, with an `a` inside that no longer fit. The script from step 4 tells you which glyphs to look at after such a change. That is untested in FontLab 9, so try it on a copy before you trust me. FontLab can also tie one glyph's width to another's, and Part 4 gets to that.

The shift doesn't follow either. The dots of the `ä` sit 13 units to the left in the Bold because of how the Bold `a` looked last year. Mira opened the bowl, and the dots stayed where they were. Eight units isn't much. She looks at all seven anyway.

## The whole script

Here is `list_components.py`. It prints the list, counts, and then turns the list around.

```python
# Lists every glyph that borrows outlines from other glyphs, with the shift
# of each component, and then the base glyphs that are borrowed most.
# Reads only.
import fly.ap.components.writer as parts
import halfmoon
from fly import fl
from fly.pens import layer_of

MASTER = "Regular"
TOP = 6


def describe(part):
    dx, dy = parts.offset(part)
    text = f"{parts.base_of(part)} {round(dx)} {round(dy)}"
    if not parts.plain_move(part):
        text = text + " turned"
    return text


def main():
    font = fl.CurrentFont()
    users = {}
    built = 0
    mixed = 0
    for glyph in font.glyphs:
        rich = halfmoon.rich(font, glyph)
        found = parts.components(layer_of(rich.fl, MASTER))
        if not found:
            continue
        kind = "built"
        if rich.contours(MASTER):
            kind = "mixed"
            mixed += 1
        built += 1
        texts = [describe(part) for part in found]
        print(f"{glyph.name:<14}{kind:<7}{', '.join(texts)}")
        for part in found:
            base = parts.base_of(part)
            if base not in users:
                users[base] = []
            if glyph.name not in users[base]:
                users[base].append(glyph.name)

    def how_many(base):
        return len(users[base])

    print()
    print(f"{built} glyphs borrow, {mixed} of them mixed. {len(users)} glyphs are borrowed.")
    for base in sorted(users, key=how_many, reverse=True)[:TOP]:
        print(f"{base:<12}{len(users[base]):>3}  {' '.join(users[base])}")


main()
```

The end of the output:

```text
exclam        mixed  period 24 4
exclamdown    mixed  period 24 378
questiondown  built  question 416 688 turned
...

85 glyphs borrow, 2 of them mixed. 40 glyphs are borrowed.
acute        14  Aacute Eacute Iacute Oacute Uacute Wacute Yacute aacute eacute iacute oacute uacute wacute yacute
circumflex   14  Acircumflex Ecircumflex Icircumflex Ocircumflex Ucircumflex Wcircumflex Ycircumflex acircumflex ecircumflex icircumflex ocircumflex ucircumflex wcircumflex ycircumflex
dieresis     14  Adieresis Edieresis Idieresis Odieresis Udieresis Wdieresis Ydieresis adieresis edieresis idieresis odieresis udieresis wdieresis ydieresis
grave        14  Agrave Egrave Igrave Ograve Ugrave Wgrave Ygrave agrave egrave igrave ograve ugrave wgrave ygrave
A             7  Aacute Abreve Acircumflex Adieresis Agrave Aring Atilde
a             7  aacute abreve acircumflex adieresis agrave aring atilde
```

`how_many` is a function inside a function, as `change` was in chapter 49. It sits inside `main` so that it can see `users`. Sorting a dictionary sorts its keys, and the key function says by what: the length of each key's list.

Of the 205 glyphs Plum came with, 85 have nothing or nearly nothing drawn in them. The four accents at the top of the table are borrowed 14 times each. Whoever redraws the acute redraws it in 14 letters at once.

None of the small caps is on the list, and neither is `leader`. You drew those with a pen, so they hold outlines of their own. And no base in Plum is itself built from components. A component can point at a glyph that has components, and fonts with long chains exist. Plum keeps it to one level.

Mira writes the list to a file, as in chapter 26, and pins it over her desk. Then she takes Oskar's sheet and crosses out *List the glyphs that are built from other glyphs.* The line below it, about the glyphs that mix, she leaves. She knows which two they are. She'd like to ask Oskar what color he had in mind.

## What you learned

A component is an element that shows another glyph's outline, and it knows two things: its base and its transform, which for most components is a plain shift. `parts.components(layer)` lists them, `parts.base_of` and `parts.offset` read them, and `parts.plain_move` says whether a shift is the whole story. A function can hand back a pair that you take apart with two names, and a dictionary can hold a list for each key, as long as you make the empty list before the first `append`. The outline of a base carries into every glyph that borrows it, while widths and shifts stay behind.

## Try it yourself

1. Change `MASTER` to `"Bold"` and run the script again. The counts stay the same and the shifts change. Find the acute over `e` in all three masters. How far does it travel from the Light to the Bold?
2. Do the line Mira left. Write `mark_mixed.py`: for every glyph that has components and contours of its own, set the mark as you did in chapter 14. Pick the color yourself. Run it, look at the Font window, and count the marked cells before you cross anything out.
3. From `users`, print every base that's borrowed by one glyph only. There are 16. For each, ask yourself whether borrowing saved anybody any work. Then look at `i` and `j`: each is borrowed once, by `ij`, while the accented `i` glyphs borrow `dotlessi`. Why can't `iacute` be built from `i`?

## Next

The publisher wants the cookbook in Czech and Polish, and Plum has no `ě` and no `ń`. Chapter 53 builds one accented letter from a base and an accent, with the shift worked out from numbers you can already read.
