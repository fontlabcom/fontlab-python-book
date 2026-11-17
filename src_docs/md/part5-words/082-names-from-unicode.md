---
this_file: src_docs/md/part5-words/082-names-from-unicode.md
---

# 82. Names from Unicode

Tuesday of week sixteen. The Greek for the real Plum was drawn two years ago by a freelancer, in another program, and it came into Ines's file last night as three hundred glyphs called `glyph201`, `glyph202` and so on. The drawings are fine. Every glyph kept its Unicode value. Only the names were lost on the way.

"Three hundred," Ines says. "I am not typing three hundred names."

She doesn't have to. A glyph that knows its code point can be given a name by looking the code point up in a table, and a table is a dictionary.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The `tell` function from [chapter 39](../part2-a-toolbox/039-ask-the-user.md). The script below defines it again, so it runs by itself.
- `rename_suffix.py` from [chapter 31](../part2-a-toolbox/031-dry-run.md), to remind you of its shape. You'll build this chapter's script on it.

I couldn't run the code in FontLab 9. The outputs below were computed in plain Python from Plum's source file and from the name table in Fly's source. The renaming itself goes the way chapter 31's did, and I haven't seen either of them rename a glyph.

Your practice font has no Greek and no glyph called `glyph201`. Step 5 plants three such names so that the script has something to find.

## Step 1: A table by hand

You met the dictionary in chapter 21 with names on the left. The left side can be a number as well:

```python
NAMES = {0x5E: "asciicircum", 0x7C: "bar", 0x23: "numbersign"}

print(NAMES[0x5E])
print(NAMES)
```

```text
asciicircum
{94: 'asciicircum', 124: 'bar', 35: 'numbersign'}
```

`0x5E` is the sixteen-digit way of writing 94, as chapter 6 said, and Python stores the plain number whichever way you write it. Writing the keys in hex keeps them looking like the Unicode charts, where the circumflex sign sits at `U+005E`.

Ask the table for a code point it doesn't hold and you get an error you know from chapter 21:

```python
print(NAMES[0x3A9])
```

```text
KeyError: 937
```

`get` asks the same question politely and takes a second argument, the answer to give when the key is missing:

```python
print(NAMES.get(0x3A9))
print(NAMES.get(0x3A9, "?"))
```

```text
None
?
```

That second argument does most of the work in this chapter.

## Step 2: Borrow a bigger table

Three entries won't name a font. Somebody has typed the long table already, and it ships inside Fly:

```python
from fly.ap.glyphs.identity_tools.glyph_identity.unicode_from_names import AGL

print(len(AGL))
print(AGL["eacute"], AGL["A"])
```

```text
376
233 65
```

The import line is long because the table lives deep inside a tool that does the opposite job from ours: it finds a code point for a glyph that has a name. `AGL` stands for Adobe Glyph List, the published list most Latin glyph names come from. Fly's copy holds 376 of its names.

It runs the wrong way for us. Its keys are names and its values are code points, and you can only look a dictionary up by its keys. So turn it round. `items()` hands you each key with its value, and you file them the other way about:

```python
BY_CODE = {}
for name, code in AGL.items():
    BY_CODE[code] = name

print(len(BY_CODE))
print(BY_CODE[233])
```

```text
376
eacute
```

Look at the first number. A dictionary can't hold the same key twice, so if two names in `AGL` shared a code point, the second would overwrite the first and `BY_CODE` would come out shorter. It has 376 entries, the same as `AGL`. Nothing was lost. Chapter 63 showed what an overwritten key looks like. Compare the two lengths every time you turn a dictionary round.

The three-line loop has a one-line form, in the manner of chapter 37's comprehensions, with braces and a colon:

```python
BY_CODE = {code: name for name, code in AGL.items()}
```

Both build the same dictionary. The script below uses the short one.

## Step 3: When the table has no answer

The table has no Greek. `BY_CODE.get(0x3A9)` gives `None` for the capital omega, and it will for most of Ines's three hundred.

There is a rule for this case, and you saw its result in chapter 81: a glyph with no better name is called `uni` and its code point as four hex digits. Mira's first try:

```python
def name_for(code):
    return BY_CODE.get(code, f"uni{code:x}")

print(name_for(0x5E))
print(name_for(0x3A9))
```

```text
asciicircum
uni3a9
```

The first answer is right. The second looks right and isn't. `uni3a9` has three digits where the rule wants four, and small letters where it wants capitals. Chapter 81's `is_uni_name` says `False` to it. A program reading the exported font would take `uni3a9` for a word somebody made up, and wouldn't know the glyph is an omega.

The format from chapter 23 mends both faults. `04` pads to four digits with zeros and a capital `X` asks for capital letters:

```python
def name_for(code):
    return BY_CODE.get(code, f"uni{code:04X}")

print(name_for(0x3A9))
print(name_for(0x5E))
```

```text
uni03A9
asciicircum
```

`uni03A9` isn't pretty, and it is correct: every font tool reads it as "the glyph for U+03A9". Friendlier Greek names such as `Omega` need a bigger table than this one. Fly has none, and FontLab's own was out of my reach while I wrote this, so the script settles for names that are right.

## Step 4: Test the table on names you trust

Before a table renames three hundred glyphs, find out whether it agrees with the names the font already has. Every glyph in Plum that has a code point also has a name somebody chose with care. Ask the table about each and compare:

```python
from fly import fl
from fly.ap.glyphs.identity_tools.glyph_identity.unicode_from_names import AGL

BY_CODE = {code: name for name, code in AGL.items()}
font = fl.CurrentFont()

agree = 0
differ = 0
unknown = []
for glyph in font.glyphs:
    if glyph.unicode is None:
        continue
    listed = BY_CODE.get(glyph.unicode)
    if listed is None:
        unknown.append(glyph.name)
    elif listed == glyph.name:
        agree += 1
    else:
        differ += 1
        print(f"{glyph.name} is {listed} in the table")
print(f"{agree} agree, {differ} differ, {len(unknown)} not in the table")
print(unknown)
```

On Plum as it shipped this should print:

```text
196 agree, 0 differ, 8 not in the table
['Wacute', 'Wdieresis', 'Wgrave', 'Ygrave', 'wacute', 'wdieresis', 'wgrave', 'ygrave']
```

Your font has more glyphs than that by now, so your first and last numbers will be larger and your list longer. The middle number is the one to watch, and it should be 0. If it isn't, each line above the total names a glyph where your font and the table disagree, and a person has to decide which of them is right.

The eight are the Welsh letters. The table is partial, and for those eight `name_for` would answer `uni1E82` and its neighbors. That is worth knowing before you trust it with a font: where the table is silent, a good name can be replaced by a merely correct one. The script in this chapter only touches glyphs whose names are placeholders, so it can't do that harm.

## Step 5: Plant three, then name them

To have something to rename, take three glyphs nobody kerns and no feature mentions, and spoil their names. Put this in the Scripting panel and run it once:

```python
from fly import qt
import fly.ap.glyphs.names.model as names
from fly.ap.glyphs.identity_tools.glyph_identity.batch_rename import apply_renames

PLANT = [["numbersign", "glyph201"], ["asciicircum", "glyph202"], ["bar", "glyph203"]]
facts = names.scan()
print(apply_renames(None, qt.QtCore, facts.package_id, PLANT))
```

It should print the three pairs back. They're listed in the order the three glyphs have in the font, because the script below walks the font and will meet them in that order. One Undo step takes them away again if you change your mind.

Now the script needs to know a placeholder when it sees one. `glyph` followed by nothing but digits is a placeholder. `glyphs` isn't, and neither is `glyph12a`:

```python
PREFIX = "glyph"
DIGITS = "0123456789"

def is_placeholder(name):
    number = name.removeprefix(PREFIX)
    if number == name or number == "":
        return False
    return not [ch for ch in number if ch not in DIGITS]

for name in ["glyph201", "glyph", "glyphs", "glyph12a", "Glyph1"]:
    print(name, is_placeholder(name))
```

```text
glyph201 True
glyph False
glyphs False
glyph12a False
Glyph1 False
```

`removeprefix` is the twin of `removesuffix` from chapter 31. It cuts the given start off a string and returns the rest, and when the string doesn't start that way it returns the string unchanged. That gives the first test: if nothing was cut off, the name didn't begin with `glyph`. The last line is chapter 81's `strays`, written in place: collect every character that isn't a digit, and say `True` only if the list is empty.

The rest is chapter 31's shape: collect, plan, show, apply.

## The whole script

```python
#FLM: Fix Names
# Gives every glyph called glyph1, glyph2 and so on a name from its code point.
# Prints a plan first. With DRY_RUN = True it stops there.
# Afterward, by hand: fix the old names in Features and in kerning classes.
from fly import fl, qt
import fly.ap.glyphs.names.model as names
from fly.ap.glyphs.identity_tools.glyph_identity.batch_rename import (
    apply_renames,
    plan_renames,
)
from fly.ap.glyphs.identity_tools.glyph_identity.unicode_from_names import AGL
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


DRY_RUN = True
PREFIX = "glyph"
DIGITS = "0123456789"
BY_CODE = {code: name for name, code in AGL.items()}


def is_placeholder(name):
    number = name.removeprefix(PREFIX)
    if number == name or number == "":
        return False
    return not [ch for ch in number if ch not in DIGITS]


def name_for(code):
    return BY_CODE.get(code, f"uni{code:04X}")


def collect(font):
    pairs = []
    skipped = []
    for glyph in font.glyphs:
        if not is_placeholder(glyph.name):
            continue
        if glyph.unicode is None:
            skipped.append(glyph.name)
        else:
            pairs.append([glyph.name, name_for(glyph.unicode)])
    return pairs, skipped


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    pairs, skipped = collect(font)
    for name in skipped:
        print(f"{name:<12}has no code point, skipped")
    if not pairs:
        print("No placeholder names with a code point.")
        return

    facts = names.scan()
    plan = plan_renames(facts, pairs)
    problems = 0
    for old, new, status in plan:
        print(f"{old:<12}{new:<16}{status}")
        if status != "ok":
            problems += 1
    print(f"{len(plan)} to rename, {problems} with problems")

    if DRY_RUN:
        print("Dry run. Nothing changed. Set DRY_RUN = False to rename.")
    elif problems > 0:
        print("Nothing changed. Fix the problems first.")
    else:
        renamed = apply_renames(None, qt.QtCore, facts.package_id, pairs)
        print(len(renamed), "renamed")


main()
```

Save it as `fix_names.py`. With the three planted names in the font, it should print:

```text
glyph201    numbersign      ok
glyph202    asciicircum     ok
glyph203    bar             ok
3 to rename, 0 with problems
Dry run. Nothing changed. Set DRY_RUN = False to rename.
```

Read the plan. Three placeholders, three names you recognize, three times `ok`. Set `DRY_RUN = False`, run it again, and the last line should say `3 renamed`. Set the switch back to `True` before you close the file.

Notes on the listing.

`collect` returns two lists, the pairs to rename and the names it had to leave. A placeholder with no code point can't be looked up in any table. The script says so by name and goes on, and a person has to open that glyph and see what it is.

`plan_renames` is the judge here, as it was in chapter 31. It knows things `name_for` doesn't: whether the new name is already taken in the font, and whether two glyphs are about to be given the same name.

The comment about features and kerning classes came along from chapter 31, and it still holds. A rename changes the glyph's name and nothing that mentions it. The three glyphs you planted were chosen because nothing mentions them.

## Break it on purpose

Spoil the table. Under the `BY_CODE` line, add:

```python
BY_CODE[0x7C] = "numbersign"
```

Now the table claims that the bar and the number sign share a name. Plant the three names again if you've already mended them, leave `DRY_RUN = True`, and run:

```text
glyph201    numbersign      duplicate target
glyph202    asciicircum     ok
glyph203    numbersign      duplicate target
3 to rename, 2 with problems
Dry run. Nothing changed. Set DRY_RUN = False to rename.
```

Two glyphs can't have one name, and the plan says so for both, since it can't tell which of them you meant. With the switch off the script would stop at "Nothing changed. Fix the problems first." and rename none of the three, the good one in the middle included. That is deliberate. A half-done rename is harder to check than one that didn't happen.

Take the line out again.

## What the table can't tell you

A code point says which character a glyph stands for. It doesn't say which drawing it is. A small-cap omega and a swash omega carry no code point at all, so in Ines's import they arrive as placeholders the script reports and skips. Somebody who can see them has to name those, with the suffixes from chapter 81.

And a wrong code point gives a wrong name with full confidence. If the freelancer's file had the omega at the code point of the ohm sign, this script would name it for the ohm sign and print `ok`. Chapter 83 looks at that from the other side.

Ines runs the script on the real Plum. Two hundred and sixty-one glyphs get `uni` names in one Undo step. Thirty-nine are skipped, and she prints their list and takes it to her desk with a pencil.

## What you learned

A dictionary can be a lookup table with numbers for keys, and `get` with a second argument gives you a fallback for everything the table doesn't hold. Turning a dictionary round takes one line, and comparing the lengths before and after tells you whether anything was overwritten. Test a borrowed table against names you already trust before you let it rename anything. The format `{code:04X}` writes a code point the way a `uni` name needs it.

## Try it yourself

1. Add your own names on top of the borrowed table. Write `MINE = {0x1E82: "Wacute", 0x1E84: "Wdieresis"}` and make `name_for` ask `MINE` first, then `BY_CODE`, then fall back to the `uni` name. Run Step 4's test with it. How many are "not in the table" now?
2. Make the dry run say where each new name came from. Add a fourth column that reads `table` or `uni`. You can tell which it is without changing `name_for`: ask `BY_CODE` whether it has the code.
3. Code points above `U+FFFF` don't fit in four hex digits, and the rule for them is a single `u` followed by five or six digits, as in `u1F600`. Change `name_for` so that it writes those names for codes of 0x10000 and more. Test it in the Scripting panel on 0x1F600 and on 0x3A9 without touching a font.

## Next

Naming a glyph from its code point works when the code point is there and right. Chapter 83 goes the other way: it finds the glyphs that have a good name and no code point, or the wrong one, and proposes what it should be.
