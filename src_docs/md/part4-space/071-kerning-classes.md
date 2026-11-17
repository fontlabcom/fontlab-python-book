---
this_file: src_docs/md/part4-space/071-kerning-classes.md
---

# 71. Kerning classes

Monday of week fourteen. The publisher has sent a title from the Czech edition: `Těšín`, the name of a town. Mira sets it in the practice font, with the `ě` that chapter 60 built, and something is off at the very start. The `ě` stands away from the `T` as if it belonged to the next word.

She runs Friday's `pair_value.py` twice, once on `T eacute` and once on `T ecaron`:

```text
T eacute
  Light      -61   through a class
  Regular    -52   through a class
  Bold       -36   through a class
T ecaron
  Light        0   not kerned
  Regular      0   not kerned
  Bold         0   not kerned
```

The `é` is pulled in under the bar of the `T`. The `ě` isn't. They're the same letter with different hats. "Through a class" is all Friday's script could say, so today you open the classes and read who's in them.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The helper `tell` from chapter 39. The scripts below write it out again, so each one runs by itself.
- The `Uring` and `uring` from chapter 56 and the `ecaron` from chapter 60. If you skipped those chapters, the last part of today's report will be empty, and the rest holds.

Nothing is changed today. I couldn't run the code in FontLab 9. The classes and their members come from Plum's source file.

## Step 1: Read the classes

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
classes = scripting.kerning_classes(package, "Regular")
print(len(classes))
print(sorted(classes))
```

```text
17
['L_A', 'L_O', 'L_U', 'L_W', 'L_Y', 'R_A2', 'R_C', 'R_O2', 'R_U2', 'R_W2', 'R_Y2', 'R_aacute', 'R_eacute', 'R_oacute', 'R_uacute', 'R_wacute', 'R_yacute']
```

Seventeen classes, in a dictionary with their names as keys. `sorted` on a dictionary gives its keys in order, as it did with the pairs. The names carry no `@` here. The `@` is a mark the pair list puts in front, to tell a class from a glyph of the same name.

Like the pairs, the classes are kept for each master, which is why the call wants a master's name. In Plum the three masters hold the same seventeen. The first exercise checks that.

Now look at one:

```python
print(classes["L_A"])
```

```text
(['A', 'Aacute', 'Abreve', 'Acircumflex', 'Adieresis', 'Agrave', 'Aring', 'Atilde'], 'left')
```

Round brackets outside, square brackets inside. The value is a tuple of two things: a list of glyph names, and a word. The list is the membership. The word says in which place of a pair the class may stand.

## Step 2: A wrong answer with no complaint

Is `Aacute` in the class? You can see that it is. Ask Python:

```python
print("Aacute" in classes["L_A"])
```

```text
False
```

That's today's mistake. No error, and an answer that contradicts the line above it.

`in` asks whether something is one of the items of a collection. `classes["L_A"]` is the tuple, and the tuple has two items: a list and the word `'left'`. Is `"Aacute"` one of those two? No. It's inside the first of them, and `in` doesn't look inside. It compares with each item as a whole.

Take the tuple apart first, and ask the list:

```python
members, side = classes["L_A"]
print("Aacute" in members, side)
```

```text
True left
```

When a value is a tuple, unpack it into names as soon as you get it. `members` and `side` say what they are. `classes["L_A"][0]` would work too, and a month from now it would tell you nothing.

## Step 3: Which side is which

`'left'` is a word to be careful with. It doesn't mean the left side of the letter. It means the letter stands on the left in the pair, which is to say first. A class marked `left` gathers glyphs that look alike on their right-hand edge, the edge that meets the next letter. `L_A` holds the `A` and its accented forms because all eight end with the same diagonal.

A class marked `right` is for the second place in a pair, and its members look alike on their left-hand edge. There's a third word, `both`, for a class that may stand in either place. Plum has none of those.

To keep my own head straight, I'll say first and second from here on, and the script will too.

Walk through all seventeen. Each value is a tuple, so the loop can unpack it in parentheses, as chapter 69 did with the keys:

```python
for name, (members, side) in sorted(classes.items()):
    print(name, side, len(members))
```

```text
L_A left 8
L_O left 7
L_U left 5
L_W left 5
L_Y left 5
R_A2 right 8
R_C right 2
R_O2 right 7
R_U2 right 5
R_W2 right 5
R_Y2 right 5
R_aacute right 7
R_eacute right 4
R_oacute right 6
R_uacute right 4
R_wacute right 4
R_yacute right 4
```

Whoever made Plum named the classes for their side, `L_` and `R_`. That was a courtesy. Nothing in FontLab requires it, and you shouldn't rely on the name: the word in the tuple is what counts.

Five classes for the first place and twelve for the second. All five of the first kind are capitals with their accents. The lowercase letters have classes for the second place only, because that's where Plum's kerning needs them: after `T`, `V`, `W`, `Y` and the apostrophe, among others.

## Step 4: Turn it round

The dictionary answers "who's in this class?" Mira's question runs the other way: "which class is this glyph in?" Chapter 64 turned a dictionary of lists round with a loop inside a loop, and the same works here:

```python
def class_of(classes, wanted):
    found = {}
    for name, (members, side) in classes.items():
        if side in [wanted, "both"]:
            for glyph in members:
                found[glyph] = name
    return found


second = class_of(classes, "right")
print(second.get("eacute"), second.get("ecaron"), second.get("e"))
```

```text
R_eacute None None
```

`get` without a default, as on Friday, so that a glyph in no class shows as `None`.

There's the answer to this morning's puzzle. `eacute` is in `R_eacute`, and the pair `T` before `@R_eacute` covers it. `ecaron` is in no class. It didn't exist when the classes were made. Chapter 60 built it and never told the kerning.

The plain `e` is in no class either, and that one is on purpose. Friday showed why: after a `T`, the plain letter takes a tighter value than the accented ones, so it has a pair of its own and stays out of the family.

Two glyphs outside the class, then, one by design and one by oversight, and `None` for both. The dictionary can't tell them apart. For that you need to know something about the glyphs themselves.

## Step 5: Who ought to be in

Here's a rule that separates the two cases. The members of `R_eacute` are all built the same way: an `e` with an accent on top, as components. A glyph that's built on that base letter with an accent, and isn't a member, was probably forgotten. The plain `e` isn't built on anything, so the rule leaves it alone.

Chapter 52 read a glyph's components, and chapter 63 used them to find accented letters. The base is the first component:

```python
from fly.tr.proxy.fl.objects.glyph import pGlyph


def base_letter(font, name):
    rich = pGlyph(font, font[name])
    found = parts.components(layer_of(rich.fl, MASTER))
    if len(found) < 2 or rich.contours(MASTER):
        return None
    return parts.base_of(found[0])
```

A glyph with fewer than two components, or with a drawing of its own, has no base letter in this sense, and the function says `None`.

## The whole script

```python
#FLM: List Kerning Classes
# Prints the kerning classes of one master and the accented letters
# that were left out of the class their relatives are in.
import fly.ap.components.writer as parts
import fly.ap.core.scripting as scripting
from fly import fl, qt
from fly.pens import layer_of
from fly.ap.ui.dialogs import run_standard_message_box
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"

MASTER = "Regular"
PLACE = {"left": "first", "right": "second", "both": "either"}


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def base_letter(font, name):
    rich = pGlyph(font, font[name])
    found = parts.components(layer_of(rich.fl, MASTER))
    if len(found) < 2 or rich.contours(MASTER):
        return None
    return parts.base_of(found[0])


def show(classes, wanted):
    print(f"{PLACE[wanted].capitalize()} in a pair:")
    for name, (members, side) in sorted(classes.items()):
        if side == wanted:
            print(f"  {name:<10}{len(members):>2}  {' '.join(sorted(members))}")


def left_out(font, classes):
    bases = {}
    for glyph in font.glyphs:
        base = base_letter(font, glyph.name)
        if base is not None:
            bases[glyph.name] = base
    rows = []
    for name, (members, side) in sorted(classes.items()):
        family = set([bases[member] for member in members if member in bases])
        for glyph_name in sorted(bases):
            if bases[glyph_name] in family and glyph_name not in members:
                rows.append((glyph_name, name, PLACE[side]))
    return rows


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    classes = scripting.kerning_classes(package, MASTER)
    if not classes:
        print(f"No kerning classes in {MASTER}.")
        return

    print(f"{len(classes)} classes in {MASTER}.")
    for wanted in ["left", "right", "both"]:
        show(classes, wanted)
    rows = left_out(font, classes)
    print(f"{len(rows)} left out:")
    for glyph_name, name, place in rows:
        print(f"  {glyph_name:<12}is built like the members of {name} ({place})")


main()
```

Save it as `list_kern_classes.py`. On the practice font it prints:

```text
17 classes in Regular.
First in a pair:
  L_A        8  A Aacute Abreve Acircumflex Adieresis Agrave Aring Atilde
  L_O        7  O Oacute Ocircumflex Odieresis Ograve Oslash Otilde
  L_U        5  U Uacute Ucircumflex Udieresis Ugrave
  L_W        5  W Wacute Wcircumflex Wdieresis Wgrave
  L_Y        5  Y Yacute Ycircumflex Ydieresis Ygrave
Second in a pair:
  R_A2       8  A Aacute Abreve Acircumflex Adieresis Agrave Aring Atilde
  R_C        2  C Ccedilla
  R_O2       7  O Oacute Ocircumflex Odieresis Ograve Oslash Otilde
  R_U2       5  U Uacute Ucircumflex Udieresis Ugrave
  R_W2       5  W Wacute Wcircumflex Wdieresis Wgrave
  R_Y2       5  Y Yacute Ycircumflex Ydieresis Ygrave
  R_aacute   7  aacute abreve acircumflex adieresis agrave aring atilde
  R_eacute   4  eacute ecircumflex edieresis egrave
  R_oacute   6  oacute ocircumflex odieresis ograve oslash otilde
  R_uacute   4  uacute ucircumflex udieresis ugrave
  R_wacute   4  wacute wcircumflex wdieresis wgrave
  R_yacute   4  yacute ycircumflex ydieresis ygrave
Either in a pair:
0 left out:
```

Wait for the last line. I've printed what the shipped font gives, and yours should end differently if you built the letters of chapters 56 and 60:

```text
Either in a pair:
4 left out:
  Uring       is built like the members of L_U (first)
  Uring       is built like the members of R_U2 (second)
  ecaron      is built like the members of R_eacute (second)
  uring       is built like the members of R_uacute (second)
```

`Uring` is there twice because the capital `U` has a class for each place.

Notes on the listing.

`PLACE` is a small dictionary that translates FontLab's three words into mine. It's used twice, once for the headings and once for the last column, and if you'd rather keep left and right, it's one line to change.

`capitalize` is new. It gives back a text with its first letter made a capital, so `"first".capitalize()` is `First`. It saves writing the three headings out.

`left_out` first builds a dictionary, `bases`, from every accented composite to its base letter: `eacute` to `e`, `ecaron` to `e`, `Aring` to `A`. Then, for each class, it collects the base letters of the members into a set, the class's `family`. For `R_eacute` that set is `{"e"}`. Any composite whose base is in the family and whose name isn't among the members goes on the list.

The `[... if member in bases]` part skips members that aren't composites, such as the plain `A` in `L_A` and the `Oslash`, which is a drawing of its own. They belong to their class and say nothing about its family.

## Reading the report

Three things stand out.

**The capitals have the plain letter in the class, and the lowercase don't.** `R_A2` starts with `A`, and `R_aacute` has no `a`. A capital's accent sits above the cap height, clear of every neighbor, so `Á` kerns like `A`. A lowercase accent sits right where the bar of a `T` or the arm of a `V` wants to go. That's Friday's finding, written into the structure of the classes.

**Thirty glyphs are in two classes.** The `A` and its seven relatives are in `L_A` and in `R_A2`. That isn't a conflict. One class speaks for them when they come first and the other when they come second. What a glyph can't be is in two classes for the same place, because then FontLab would have two answers to one question.

**Three glyphs were left out, as far as this rule can see.** They are the `ecaron` of chapter 60 and the `Uring` and `uring` of chapter 56. The other letters from those chapters are built on `D`, `E`, `N`, `R`, `S`, `T`, `Z` and small letters that have no class in Plum, so there's nothing for them to be left out of. The rule has a blind spot, though. `R_C` holds `C` and `Ccedilla`, and in Plum the `Ç` is drawn in one piece. Neither member is a composite, so the class has no family the rule can read, and your `Cacute` and `Ccaron` pass unnoticed. They very likely belong there. A check that reads how glyphs are built can only find what was built that way.

Mira reads the `ecaron` line twice. "So I add `ecaron` to that list and `Těšín` is mended?"

Yes. One name added to one class, and every pair that has `@R_eacute` in it covers the new letter: after `T`, `V` and `P`, after the `W` and `Y` classes, after the apostrophe. That's six pairs in each master that nobody has to write. It's also a change to the font, and the first one this part makes to the kerning. It gets its own chapter, tomorrow.

## What you learned

A kerning class is a named list of glyphs that kern alike in one place of a pair. `scripting.kerning_classes(package, master)` gives them as a dictionary: the class name is the key, and the value is a tuple of the member list and a word, `left` for first in a pair, `right` for second, `both` for either. `in` looks at the items of a collection and not inside them, so unpack the tuple first, as `for name, (members, side) in classes.items():` does. A glyph made after the classes were set up belongs to none until somebody adds it.

## Try it yourself

1. Read the classes of the Light and the Bold into two more dictionaries and compare each with the Regular's using `==`. Two dictionaries are equal when they have the same keys with equal values. You should get `True` twice. What would it mean for an interpolated weight if one master's `R_eacute` had five members and another's four?
2. Use `class_of(classes, "left")` and `class_of(classes, "right")` to print, for one glyph name you type into the script, its class when first and its class when second. Try `Oslash`, `oslash`, `T` and `ecaron`.
3. `class_of` writes `found[glyph] = name` without looking. If a glyph were in two classes for the same place, the later one would win and you'd never know. Add a test that prints a warning when `glyph` is already in `found`. On Plum it stays silent. Why is this the mistake of chapter 63 again?

## Next

The report found three letters outside their families. Chapter 72 puts them in, and then turns the idea round: a script that proposes classes from the way the glyphs are built, the capital `C` and its relatives among them.
