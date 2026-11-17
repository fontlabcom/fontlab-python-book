---
this_file: src_docs/md/part5-words/092-fractions-and-figures.md
---

# 92. Fractions and figures

Tuesday of week eighteen. The cookbook is full of quantities: 1/2 cup of sugar, 3/16 of an inch of pastry. The typesetter sets them with full-size figures and a slash, and asks whether Plum can do proper fractions, with a small figure up, a slanted bar and a small figure down.

Ines says the font needs three things for that. It needs small figures that sit high, called numerators. It needs small figures that sit on the baseline, called denominators. And it needs a `frac` feature that knows which is which. She'll draw the figures. The feature is Mira's.

Until now each feature you wrote did one thing to one glyph at a time. `frac` has to do two things in order, and the second depends on what stands before the glyph. Today you write three features, and one of them has two stages.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `Add Glyphs From List.py` from chapter 40 and `list_features.py` from chapter 87. The script below defines `tell` and `ask` from [chapter 39](../part2-a-toolbox/039-ask-the-user.md) again, so it runs by itself.
- The five features the font has after chapter 91.

I couldn't run the code in FontLab 9. I ran the name building and the text building in plain Python on Plum's glyph names. I also played the typesetting program by hand, with a few lines of Python that apply the rules as I understand them, to get the glyph sequences this chapter quotes. No real layout program has seen this feature. Treat the `frac` text as a careful draft until chapter 93 and a compile have looked at it.

## Step 1: The mistake

Twenty-one glyphs are missing: ten numerators, ten denominators and the bar. Mira types the names of the first set the fast way:

```python
names = [figure + ".numr" for figure in "0123456789"]
print(names)
```

```text
['0.numr', '1.numr', '2.numr', '3.numr', '4.numr', '5.numr', '6.numr', '7.numr', '8.numr', '9.numr']
```

Ten names, all wrong. A loop over a string gives characters, and the figure glyphs aren't named after their characters. The glyph for 0 is called `zero`. Chapter 81 said what a glyph name may start with, and a digit wasn't on the list.

Had she made glyphs from those names, nothing would have stopped her until a feature tried to pair `0.numr` with a glyph called `0`. The names of the figures are in the font, so ask the font. Chapter 91's `by_category` does it, with the category for decimal digits:

```python
import unicodedata

from fly import fl


def by_category(font, category):
    names = []
    for glyph in font.glyphs:
        code = glyph.unicode
        if code is not None and unicodedata.category(chr(code)) == category:
            names.append(glyph.name)
    return names


font = fl.CurrentFont()
figures = by_category(font, "Nd")
print(figures)
```

```text
['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
```

## Step 2: Twenty-one glyphs from a file

Build the full list of names and write it where chapter 40's script can find it:

```python
from pathlib import Path

needed = ["fraction"]
for suffix in [".numr", ".dnom"]:
    needed = needed + [name + suffix for name in figures]
print(len(needed), needed[:3], needed[-1])

path = Path(font.path).parent / "fraction-glyphs.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(needed) + "\n")
```

```text
21 ['fraction', 'zero.numr', 'one.numr'] nine.dnom
```

`fraction` is the standard name of the slanted bar, a character of its own at U+2044 and a different glyph from `slash`. The suffixes `.numr` and `.dnom` are the ones Fly's `suggested_tag` knows, which chapter 89 showed you how to ask.

Now run **Add Glyphs From List** from the Scripts menu, choose `fraction-glyphs.txt`, and say yes. You have 21 empty glyphs. Ines will fill them. A feature only needs the names.

## Step 3: The two simple features

`numr` turns every figure into its numerator, and `dnom` into its denominator. These are chapter 88's small caps under another name, and Fly's two functions build them. `suffix_pairs` takes the suffix without its period:

```python
import fly.ap.features.code as fea_code

names = [glyph.name for glyph in font.glyphs]
pairs = fea_code.suffix_pairs(names, "numr")
print(len(pairs), pairs[:2])
```

```text
10 [('eight', 'eight.numr'), ('five', 'five.numr')]
```

A typesetter who wants a superior-looking 2 on its own can switch on `numr` for that one character. These two features are also where `frac` gets its vocabulary.

## Step 4: What a fraction needs

Think about 3/16 as a row of glyphs: `three slash one six`. The result should be `three.numr fraction one.dnom six.dnom`.

No single rule of the kind you've written can do it. "Replace `one` by `one.numr`" and "replace `one` by `one.dnom`" can't both hold. Which one is right depends on the side of the bar the figure stands on. Feature code can say that, in two stages.

Stage one makes everything a numerator and turns the slash into the bar:

```text
three.numr fraction one.numr six.numr
```

Stage two walks along the row and changes a numerator into a denominator when the glyph before it is the bar or a denominator:

```text
three.numr fraction one.dnom six.numr
three.numr fraction one.dnom six.dnom
```

The `six` changes because the `one` before it has already changed. The rule feeds itself along the row, which is why one rule handles a denominator of any length.

A stage is called a lookup. A feature may hold several, and they run in the order they're written, each over the whole row before the next begins. The order matters here in the way it mattered for ligatures. Swap the two stages and the second finds no numerators to change, because the first hasn't made any yet.

## Step 5: Say it in feature code

Here's the text the script will produce. Three pieces of grammar are new:

```text
feature frac {
    @frac_plain = [zero one two three four five six seven eight nine];
    @frac_up = [zero.numr one.numr two.numr ... nine.numr];
    @frac_down = [zero.dnom one.dnom two.dnom ... nine.dnom];
    lookup frac_all_up {
        sub @frac_plain by @frac_up;
        sub slash by fraction;
    } frac_all_up;
    lookup frac_after_bar {
        sub [fraction @frac_down] @frac_up' by @frac_down;
    } frac_after_bar;
} frac;
```

I've shortened two lines with dots. The script writes them out in full.

The classes are defined inside the feature. Chapter 91's class sat in the prefix because any feature might want it. These three serve one feature and live with it.

`sub @frac_plain by @frac_up;` replaces a class by a class. It means ten rules at once: the first name by the first name, the second by the second. Both lists must have the same length and the same order. The script builds all three from one list of figures, so they can't drift apart.

`lookup name { ... } name;` wraps a stage and gives it a name.

The last rule has a mark, the `'` after `@frac_up`. The mark says which glyph is replaced. What stands before it is context: it must be there for the rule to fire, and it's left alone. Read it aloud as "after the bar or a denominator, a numerator becomes a denominator".

Building the text is string work. A small function writes a list of names in the feature language's brackets, which is the lesson of chapter 91's mistake put where it can't be forgotten:

```python
def group(names):
    return "[" + " ".join(names) + "]"


print(group(["zero", "one"]))
```

```text
[zero one]
```

## The whole script

```python
#FLM: Figure Features
# Writes or replaces numr, dnom and frac from the figure glyphs.
# Does not compile: do that in the Features panel afterward.
import unicodedata

from fly import fl, qt
import fly.ap.core.scripting as scripting
import fly.ap.features.code as fea_code
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


DRY_RUN = True


def by_category(font, category):
    names = []
    for glyph in font.glyphs:
        code = glyph.unicode
        if code is not None and unicodedata.category(chr(code)) == category:
            names.append(glyph.name)
    return names


def group(names):
    return "[" + " ".join(names) + "]"


def frac_text(figures):
    up = [name + ".numr" for name in figures]
    down = [name + ".dnom" for name in figures]
    lines = [
        "feature frac {",
        f"    @frac_plain = {group(figures)};",
        f"    @frac_up = {group(up)};",
        f"    @frac_down = {group(down)};",
        "    lookup frac_all_up {",
        "        sub @frac_plain by @frac_up;",
        "        sub slash by fraction;",
        "    } frac_all_up;",
        "    lookup frac_after_bar {",
        "        sub [fraction @frac_down] @frac_up' by @frac_down;",
        "    } frac_after_bar;",
        "} frac;",
    ]
    return "\n".join(lines)


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    names = [glyph.name for glyph in font.glyphs]
    figures = by_category(font, "Nd")
    needed = ["slash", "fraction"]
    for suffix in [".numr", ".dnom"]:
        needed = needed + [name + suffix for name in figures]
    missing = [name for name in needed if name not in names]
    if missing:
        print(f"{len(missing)} glyphs missing: {' '.join(missing)}")
        print("Nothing to write.")
        return

    made = []
    for tag in ["numr", "dnom"]:
        pairs = [pair for pair in fea_code.suffix_pairs(names, tag) if pair[0] in figures]
        made.append((tag, fea_code.feature_text(tag, pairs)))
    made.append(("frac", frac_text(figures)))
    for tag, text in made:
        print(f"{tag}: {len(text.splitlines())} lines")

    package = scripting.current_package()
    blocks = scripting.read_feature_blocks(package)
    new_tags = [tag for tag, text in made]
    kept = [(tag, code) for tag, code in blocks["features"] if tag not in new_tags]
    print(f"{len(kept)} features kept: {' '.join(tag for tag, code in kept)}")
    if DRY_RUN:
        print(made[2][1])
        print("Dry run. Nothing written.")
        return
    if not ask(f"Write {len(made)} features?"):
        return
    updated = {"prefix": blocks["prefix"], "features": kept + made}
    result = scripting.write_feature_blocks(
        package, blocks, updated,
        references=figures + needed, undo_name="Write figure features")
    print(result)
    print("Now compile in the Features panel.")


main()
```

Save it as `figure_features.py`. The dry run begins:

```text
numr: 12 lines
dnom: 12 lines
frac: 12 lines
5 features kept: liga cpsp smcp ss01 zero
feature frac {
    @frac_plain = [zero one two three four five six seven eight nine];
```

and goes on with the text you saw in step 5.

Notes on the listing.

The script refuses to write anything unless all 22 glyphs it will name are in the font. Delete `eight.dnom` and `nine.dnom` and it says `2 glyphs missing: eight.dnom nine.dnom` and stops. Chapter 88's script left out a pair that lacked a glyph and wrote the rest. That was right for small caps, where nine are better than none. A fraction feature with eight denominators would set 3/16 correctly and 3/18 wrongly, and the reader of the cookbook would be the one to find out. So this script stops and names the missing glyphs.

`if pair[0] in figures` keeps `numr` and `dnom` to the figures. If someone later draws `a.numr` for an ordinal, it won't slip into a feature that `frac` leans on.

`frac` comes last of the three, and all three come after the features you had. The order among different features matters less here than the order of the stages inside `frac`.

## Break it on purpose

After a real run, look at the result with `list_features.py`:

```text
frac  12 lines, 8 rules: 1 @frac_plain, 1 @frac_up, 1 @frac_down, 2 lookup, 3 replace
```

Eight rules, it says, and five of them aren't rules. Chapter 87 warned you that `rule_lines` was a filter made of four plain tests and would be wrong about feature text more complicated than Plum's. Now Plum has such text, and you wrote it. The lister counts a class definition as a rule whose first word is `@frac_plain`, and a `lookup` line as a rule whose first word is `lookup`.

It printed no error, and the three real rules are in the count. The number is wrong all the same, and anyone who reads "8 rules" in a report will believe it. A tool that reads text line by line stays honest only while the text stays as plain as the tool expects. Chapter 93 starts from this line.

## What the feature can't know

Stage one turns every figure in reach into a numerator. Switch `frac` on for a whole recipe and "2 cups" becomes a small raised 2 followed by "cups". For "1 1/2" the whole number goes up with the rest: `one.numr space one.numr fraction two.dnom`. So the typesetter applies `frac` to the fraction and nothing else, which is how this plain form of the feature is meant to be used. There are longer versions that look for the slash first and leave other figures alone. They need more context rules than a first fraction feature should carry.

You might expect figure sets here too. Plum has one set of figures, and chapter 66 found them tabular already, so there's nothing to switch between. In a font with `.tf` or `.onum` figures, chapter 89's table handles them.

## What you learned

A feature can hold several lookups, which run in order, each over the whole row of glyphs. A rule can replace a class by a class when both lists have the same length and order, and building them from one source list keeps them matched. A mark after a name says which glyph a rule replaces, and what stands before it is context. A loop over a string gives characters, and glyph names for figures have to come from the font.

## Try it yourself

1. The typesetter might type the real fraction bar, U+2044, in place of a slash. Does stage one need a rule for it? Give the `fraction` glyph its code point first (`fix_unicodes.py` from chapter 83 may propose it), then say which glyph the row already holds.
2. Write `shape(text)`, a function that plays the two stages on a list of glyph names: stage one with a comprehension, stage two with `range(1, len(row))` and a test on `row[i - 1]`. Try it on `["three", "slash", "one", "six"]`. Then swap the stages and see what comes out.
3. The cookbook also uses ½ as a single character in a few headings. Does the font have `onehalf`? If it does, would you add `sub one slash two by onehalf;` to `frac`, and in which stage?

## Next

The lister has now been wrong once in public, and none of the features you wrote since chapter 88 has been compiled by a script. Chapter 93 writes the checks that can be made without a compiler, and says where the Compile button comes in.
