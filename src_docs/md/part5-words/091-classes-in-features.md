---
this_file: src_docs/md/part5-words/091-classes-in-features.md
---

# 91. Classes in features

Monday of week eighteen. The Istanbul publisher sends a cover proof. The title is set in Plum's capitals with capital spacing turned on, and one word looks wrong: in İSTANBUL the first letter sits closer to the S than any other letter sits to its neighbor.

Mira knows where to look. Chapter 87 found a class called `@cpsp` in the features prefix, with 63 capitals in it, and the `cpsp` feature gives a little room to every glyph in that class. Sixty-three was the number of capitals Plum had when somebody typed the list. The font has more now.

A class in feature code is a list of glyph names with a name of its own. Nothing ties it to the font. Glyphs can be added, renamed and deleted, and the list stays as it was typed. Today you read the list, compare it with the font and write it again.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `tell` and `ask`, and `list_features.py` from chapter 87.
- The accented capitals you built in Part 3. If you built fewer than I did, your counts will be smaller than mine.

I couldn't run the code in FontLab 9. I ran the reading, the comparing and the text building in plain Python on Plum's own prefix and glyph names, plus the fifteen capitals from Part 3. The write is the one from chapter 88, and I haven't seen it work.

## Step 1: Keep the names this time

Chapter 87 cut a class line apart to count its members. Today you keep them. The function takes one line of the prefix and answers with a name and a list, or with `None` if the line doesn't define a class:

```python
def class_line(line):
    code = line.split("#")[0].strip()
    if not code.startswith("@") or "=" not in code:
        return None
    name = code.split("=")[0].strip()
    members = code.split("[")[1].split("]")[0].split()
    return name, members


print(class_line("@cpsp = [A B C];  # capitals"))
print(class_line("languagesystem DFLT dflt;"))
```

```text
('@cpsp', ['A', 'B', 'C'])
None
```

The first line of the function drops a comment, as `rule_lines` did. The three splits in a row are chapter 87's. A function with two kinds of answer, a pair or `None`, is the shape `recipe` almost had on Friday. The caller has to ask which one came back before using it.

Now the real prefix:

```python
from fly import fl
import fly.ap.core.scripting as scripting

font = fl.CurrentFont()
package = scripting.current_package()
blocks = scripting.read_feature_blocks(package)
for line in blocks["prefix"].splitlines():
    found = class_line(line)
    if found is not None:
        name, members = found
        print(name, len(members), members[:3], members[-2:])
```

```text
@cpsp 63 ['A', 'B', 'C'] ['Ydieresis', 'Ygrave']
```

One class, 63 names, from `A` to `Ygrave`.

## Step 2: Is every member still in the font?

This is the check chapter 87 said was coming. A class that names a glyph the font no longer has should stop the features from compiling. I haven't seen the message FontLab gives, but it would arrive at export time, on a Friday.

```python
known = {glyph.name for glyph in font.glyphs}
gone = [name for name in members if name not in known]
print(len(gone), gone)
```

```text
0 []
```

Nothing is missing. All 63 are in the font. That was the worry, and it turns out to be unfounded. The proof on the desk is still wrong, though.

## Step 3: Ask it the other way round

"Is every member in the font?" has a twin: "is every glyph that belongs in the class a member?" The first question needs only the two lists. The second needs a rule that says what belongs.

For capital spacing the rule is simple to state: every capital letter. Chapter 86 showed how Python knows a capital. `unicodedata.category` gives `Lu`, letter uppercase, for each one:

```python
import unicodedata


def by_category(font, category):
    names = []
    for glyph in font.glyphs:
        code = glyph.unicode
        if code is not None and unicodedata.category(chr(code)) == category:
            names.append(glyph.name)
    return names


capitals = by_category(font, "Lu")
missing = [name for name in capitals if name not in members]
print(len(capitals), len(missing))
print(" ".join(missing))
```

```text
82 19
Abreve Gbreve Idotaccent Scedilla Cacute Nacute Sacute Zacute Uring Racute Zdotaccent Ccaron Dcaron Ecaron Ncaron Rcaron Scaron Tcaron Zcaron
```

There it is: `Idotaccent`, the İ of İSTANBUL. Nineteen capitals get no capital spacing. Fifteen are the ones you built in Part 3, and they come in the order you built them, because `by_category` walks the font and new glyphs sit at its end. The first four were in Plum when it came to you, which means the class was already out of date before anyone at Halfmoon touched the font. Three of those four are Turkish.

So the first check found nothing and the second found nineteen. A list can be wrong in two directions, and a check that covers one of them says nothing about the other.

## Step 4: The mistake

Write the class line again with all 82 names. Mira's first try glues the pieces together the quick way:

```python
members = ["A", "B", "C"]
line = "@cpsp = " + str(members) + ";"
print(line)
```

```text
@cpsp = ['A', 'B', 'C'];
```

Python is content. `str` of a list is how Python writes a list: quotes around each item, commas between. Feature code writes a list its own way, with spaces and nothing else. A compiler would stop at the first quote.

You can see this one because you printed the line before writing it into the font. With 82 names on one long line you might not look closely, so look at a short one first. The cure is `join`, as in chapter 88:

```python
line = "@cpsp = [" + " ".join(members) + "];"
print(line)
```

```text
@cpsp = [A B C];
```

Whenever a program writes text for another program to read, the other program's grammar decides, and `str` knows only Python's.

## Step 5: Keep the old order, add at the end

The new list could be the 82 capitals in font order. But someone chose the order of the old list, the alphabet first and the accented letters after, and a person comparing the old line with the new one will want to see what changed. So keep the old members in their order and put the new ones behind them:

```python
def rebuilt(members, known, should):
    kept = [name for name in members if name in known]
    added = [name for name in should if name not in members]
    return kept + added
```

`kept` drops a member only when the font has lost the glyph. `added` holds whatever the rule asks for and the list lacks. A name a person once put in by hand stays in, whether the rule knows it or not.

The line then goes back where it was. The prefix is 37 lines of text, one of which you change. That's Friday's loop again, which copies every item and replaces one on the way through:

```python
lines = []
for line in blocks["prefix"].splitlines():
    found = class_line(line)
    if found is not None and found[0] == "@cpsp":
        line = "@cpsp = [" + " ".join(fresh) + "];"
    lines.append(line)
prefix = "\n".join(lines)
```

Every other line, comments included, passes through untouched.

## The whole script

```python
#FLM: Feature Classes
# Checks the classes in the features prefix against the font
# and rebuilds the ones named in WANTED.
# Does not compile: do that in the Features panel afterward.
import unicodedata

import halfmoon
from fly import fl
import fly.ap.core.scripting as scripting

WANTED = {"@cpsp": "Lu"}
DRY_RUN = True


def class_line(line):
    code = line.split("#")[0].strip()
    if not code.startswith("@") or "=" not in code:
        return None
    name = code.split("=")[0].strip()
    members = code.split("[")[1].split("]")[0].split()
    return name, members


def by_category(font, category):
    names = []
    for glyph in font.glyphs:
        code = glyph.unicode
        if code is not None and unicodedata.category(chr(code)) == category:
            names.append(glyph.name)
    return names


def rebuilt(members, known, should):
    kept = [name for name in members if name in known]
    added = [name for name in should if name not in members]
    return kept + added


def new_prefix(prefix, font):
    known = {glyph.name for glyph in font.glyphs}
    lines = []
    used = []
    changed = 0
    for line in prefix.splitlines():
        found = class_line(line)
        if found is not None:
            name, members = found
            gone = [member for member in members if member not in known]
            print(f"{name}: {len(members)} glyphs, {len(gone)} not in the font")
            if name in WANTED:
                should = by_category(font, WANTED[name])
                fresh = rebuilt(members, known, should)
                extra = [member for member in fresh if member not in members]
                print(f"  rebuilt: {len(fresh)} glyphs, added {' '.join(extra) or 'none'}")
                if fresh != members:
                    line = name + " = [" + " ".join(fresh) + "];"
                    used = used + fresh
                    changed += 1
        lines.append(line)
    return "\n".join(lines), used, changed


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    blocks = scripting.read_feature_blocks(package)
    prefix, used, changed = new_prefix(blocks["prefix"], font)
    print(f"{changed} class lines to rewrite.")
    if changed == 0:
        return
    if DRY_RUN:
        print("Dry run. Nothing written.")
        return
    if not halfmoon.ask(f"Rewrite {changed} class lines in the prefix?"):
        return
    updated = {"prefix": prefix, "features": list(blocks["features"])}
    result = scripting.write_feature_blocks(
        package, blocks, updated,
        references=used, undo_name="Rebuild feature classes")
    print(result)
    print("Now compile in the Features panel.")


main()
```

Save it as `feature_classes.py`. The dry run:

```text
@cpsp: 63 glyphs, 0 not in the font
  rebuilt: 82 glyphs, added Abreve Gbreve Idotaccent Scedilla Cacute Nacute Sacute Zacute Uring Racute Zdotaccent Ccaron Dcaron Ecaron Ncaron Rcaron Scaron Tcaron Zcaron
1 class lines to rewrite.
Dry run. Nothing written.
```

After a real run, `list_features.py` should say `class @cpsp: 82 glyphs`. Run the script a second time and it reports `0 class lines to rewrite.` and stops, because the list it would build is the list that's there.

Notes on the listing.

`WANTED` maps a class name to a Unicode category. It's a small table with one row, built for more.

`' '.join(extra) or 'none'` uses `or` between two values. An empty string counts as false, so when nothing was added the `or` hands over its second value. Use it for a default in a printed line, and write an `if` for anything more important.

`new_prefix` returns three things, and `main` unpacks three. The function reports every class it meets, including classes that aren't in `WANTED`. The first check, for members the font has lost, costs nothing and applies to any class.

The `cpsp` feature itself isn't touched. It says `pos @cpsp <5 0 10 0>;`, and it will find the longer list under the same name.

## Break it on purpose

Change the table to `{"@cpsp": "Ll"}`, as if you'd mistyped the category, and do the dry run:

```text
@cpsp: 63 glyphs, 0 not in the font
  rebuilt: 147 glyphs, added a aacute abreve acircumflex adieresis agrave aring …
```

I've cut the line short. It goes on for eighty-four names, Plum's seventy lowercase letters and the fourteen from Part 3. The script kept the 63 capitals, since it never removes a name a person put in, and added every lowercase letter. Nothing in the code could tell it that capital spacing on lowercase letters is nonsense. What stops you is the dry run and the number in it: 147 where you expected about 80. Put `"Lu"` back.

## What the rule can't know

Unicode's idea of a capital and the designer's may differ. Your ten small caps have no code points, so `by_category` never sees them, and for capital spacing that's correct. For a class of "everything as tall as a capital" it would be wrong, and you'd add a second source of names: a suffix, say, as in chapter 89.

A feature class isn't a kerning class. Chapter 71's kerning classes say which glyphs kern alike on one side, and each glyph may be in one class per side. A feature class is a list and nothing more. A glyph may be in ten of them. FontLab keeps the two kinds in the same place inside the font, as far as I can tell from the source, and I haven't seen how its Classes panel shows a class that the prefix text defines. This script reads and writes the prefix text only, because that's the route with an Undo step behind it.

## What you learned

A feature class is a named list of glyph names in the feature text, and it doesn't follow the font when glyphs come and go. A list can be wrong by holding what it shouldn't or by lacking what it should, and each direction needs its own check. Text written for another program has to follow that program's grammar, so build it with `join` and never with `str` of a list. When you rebuild a list a person made, keep their order and add to the end, so the change can be read.

## Try it yourself

1. Add a count of names that appear twice in a class. Test it on `class_line("@x = [A B A];")`. Chapter 22's tally will do it.
2. The figures get no class in Plum. Extend the script so that a class in `WANTED` that the prefix lacks is added as a new line at the end of the prefix: `"@figures": "Nd"`. Print the line in the dry run. You should get ten names.
3. Before the `ask`, print the old line and the new line of each rewritten class, one under the other, cut to 70 characters with a slice. Which end of the line would you rather see?

## Next

Plum has one set of figures. The typesetter's recipes want fractions from them, for the half cups and the sixteenths of an inch. Chapter 92 writes the figure features.
