---
this_file: src_docs/md/part2-a-toolbox/031-dry-run.md
---

# 31. Look before you leap

Friday morning. Mira opens the real Plum, the one that ships, and opens `rename_suffix.py` next to it. Sixty glyphs, one click. Her finger is over the Run button.

She doesn't press it. Yesterday's script prints its plan and carries the plan out in the same run. By the time she's read the first line of the plan, the sixtieth glyph is already renamed. There's Undo, and she trusts Undo more than she did on Wednesday morning. But "do it, then see whether it was right" is a poor way to treat a font that goes to a publisher on Monday.

What she wants is a rehearsal. The script should go through every motion except the last one, show her what it would have done, and stop. People who write scripts call that a dry run, after the fire brigade's drills with no water in the hose.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open and saved.
- `rename_suffix.py` from [chapter 30](030-rename-with-care.md).
- The four `.alt` glyphs from chapter 30. If you renamed them and didn't undo it, run exercise 2 of that chapter, or rename them back by hand.
- One more glyph: choose **Font > New Glyph…** and add `zero.alt`. You'll see why in Step 4.

## Step 1: A switch in a box

You've had `True` and `False` since chapter 8. They're what a question hands back: `name.endswith(".alt")` is one or the other, and `if` acts on it. Until now they've always come out of a question. But `True` and `False` are values like 20 and `"Plum"`. You can type one yourself and put it in a box:

```python
DRY_RUN = True

if DRY_RUN:
    print("Dry run. Nothing changed.")
else:
    print("This is where the renaming would happen.")
```

```text
Dry run. Nothing changed.
```

Change the first line to `DRY_RUN = False` and run it again:

```text
This is where the renaming would happen.
```

That's a switch. One box at the top of the script, holding yes or no, and an `if` further down that goes one way or the other. To change what the script does, you change one word at the top and touch nothing else.

`if DRY_RUN:` reads oddly the first time, since there's no `==` in it and no question. It doesn't need one. `if` wants a `True` or a `False`, and the box already holds one. You could write `if DRY_RUN == True:`, and it would work, but it says "if yes is yes".

`True` and `False` are spelled with a capital letter and no quotes. Both matter, and the next step shows why.

## Step 2: The switch that's stuck

Put quotes around the word, as if it were a string:

```python
DRY_RUN = "False"

if DRY_RUN:
    print("Dry run. Nothing changed.")
else:
    print("This is where the renaming would happen.")
```

```text
Dry run. Nothing changed.
```

You wrote False and got the dry run. There's no error message.

`"False"` in quotes isn't the value `False`. It's a string of five letters that happens to spell an English word. And when `if` is handed something that isn't `True` or `False`, it doesn't complain. It applies a rule of its own: empty things count as no, and everything else counts as yes. An empty string `""` counts as no. So do the number 0, an empty list and `None`. A string with five letters in it has something in it, so it counts as yes, whatever the letters say.

That rule is handy in places. `if pairs:` is a neat way to say "if the list has anything in it". But for a switch it means a typo can jam the switch in one position.

Notice which position, though. With the switch jammed, the script did the harmless thing. That isn't luck. It follows from a decision about names and defaults:

**Name the switch after the safe behavior, and ship it switched on.**

`DRY_RUN = True` is the safe state. Someone who opens the script cold and presses Run gets a rehearsal. To get a real rename they must do something deliberate: find the line, read it and type `False`. Had Mira called the switch `APPLY` and set it to `True`, the script would do damage by default, and a jammed switch would do damage too.

Take the quotes off again.

## Step 3: Plan always, apply sometimes

Now put the switch into the real script. The plan is printed whichever way the switch is set, because a plan costs nothing and you always want to see it. Only the last step sits behind the `if`:

```python
DRY_RUN = True

facts = names.scan()
plan = plan_renames(facts, pairs)

ok = 0
problems = 0
for old, new, status in plan:
    print(f"{old:<16}{new:<16}{status}")
    if status == "ok":
        ok += 1
    else:
        problems += 1
print(f"{ok} ok, {problems} with problems")

if DRY_RUN:
    print("Dry run. Nothing changed. Set DRY_RUN = False to rename.")
elif problems > 0:
    print("Nothing changed. Fix the problems first.")
else:
    renamed = apply_renames(None, qt.QtCore, facts.package_id, pairs)
    print(len(renamed), "renamed")
```

Everything above `DRY_RUN = True` is as it was in chapter 30: the imports, the two suffixes and the loop that builds `pairs`. Run it.

```text
a.alt           a.ss01          ok
ampersand.alt   ampersand.ss01  ok
g.alt           g.ss01          ok
y.alt           y.ss01          ok
zero.alt        zero.ss01       ok
5 ok, 0 with problems
Dry run. Nothing changed. Set DRY_RUN = False to rename.
```

Look at the Font window. The names are as they were, and the Edit menu has nothing new in it.

Two things were added besides the switch.

The first is the count. The loop that prints the plan also keeps two tallies, with the `+=` from chapter 22. On five rows you can see at a glance that every row says `ok`. On sixty you can't, and a single `exists in font` in row 37 would scroll past. The last line of the table says it in numbers.

The second is the middle branch, `elif problems > 0`. Yesterday I told you that the helper skips rows that aren't `ok` and renames the rest. That's a fair thing for a helper to do. For Mira's job it's the wrong policy. A font with 59 glyphs named `.ss01` and one still named `.alt` is worse than a font with none renamed, because it looks finished. So her script is stricter than the helper: all or nothing. If the plan has one problem in it, nothing is renamed, and she goes and finds out why.

Read the three branches as a ladder. Is this a rehearsal? Then stop. If not, are there problems? Then stop. Only when both answers are no does the script reach the line that changes the font.

## Step 4: Read the plan

A dry run only helps if you read what it prints. So read it. Five rows. Every one says `ok`.

And one of them is wrong.

`zero.alt` isn't a stylistic alternate. It's the zero with a slash through it, the one programmers like, and OpenType has a feature of its own for that, called `zero`. Oskar gave it the suffix `.alt` years ago because that was his suffix for everything. If it becomes `zero.ss01`, then turning on stylistic set 1 in the publisher's layout would slash every zero in the book along with changing the a's and g's.

This is what happened to Mira on the real font. The count at the bottom of her plan said `63 ok`, and she'd been told sixty. She didn't shrug. She went through the rows and found three that didn't belong: the slashed zero and two old ampersands that Ines wants in a different set.

The helper said `ok` to all 63, and it was right to. `ok` means the font will accept the rename. It doesn't mean the rename is a good idea. No helper can know which of Oskar's `.alt` glyphs belong in which set. You know that, or Ines does. The script checks what can be checked by machine, and the dry run is where you check the rest yourself.

Now tell the script. A set, from chapter 25, holds the names to leave alone:

```python
SKIP = {"zero.alt"}

pairs = []
for glyph in font.glyphs:
    if glyph.name.endswith(OLD_SUFFIX) and glyph.name not in SKIP:
        old = glyph.name
        new = old.replace(OLD_SUFFIX, NEW_SUFFIX)
        pairs.append([old, new])
```

```text
a.alt           a.ss01          ok
ampersand.alt   ampersand.ss01  ok
g.alt           g.ss01          ok
y.alt           y.ss01          ok
4 ok, 0 with problems
Dry run. Nothing changed. Set DRY_RUN = False to rename.
```

Four rows, and they're the right four. `not in` is the opposite of `in`. The `if` line now reads: "if the name ends in the old suffix and isn't one of the names to skip".

## Step 5: Tighten the replace

One more thing to fix while the switch is still on. The last exercise of chapter 30 asked what these give:

```python
print("a.alt.sc".replace(".alt", ".ss01"))
print("salt".replace("alt", "ss01"))
```

```text
a.ss01.sc
sss01
```

`replace` doesn't know about ends. It swaps the text wherever it finds it, and it swaps every occurrence. The `endswith` test picks glyphs whose names end in the suffix. Then `replace` is let loose on the whole name. Those two lines don't say the same thing. They agree for every name in Plum today. One day somebody will name a glyph so that they don't.

Python has a method that means exactly what you mean:

```python
print("a.alt".removesuffix(".alt") + ".ss01")
print("a.alt.sc".removesuffix(".alt"))
```

```text
a.ss01
a.alt.sc
```

`removesuffix` takes the text off the end and only off the end. If the string doesn't end that way, it hands the string back untouched. Then `+` glues the new suffix on. In the script:

```python
        new = old.removesuffix(OLD_SUFFIX) + NEW_SUFFIX
```

Run the dry run again. The same four rows come back, as they should. You've changed how the new name is made, not what it comes out as. Running the rehearsal after every edit, and seeing the same plan, is how you know an edit was harmless.

## Step 6: Throw the switch

The plan is right and you've read it twice. Change one word:

```python
DRY_RUN = False
```

```text
a.alt           a.ss01          ok
ampersand.alt   ampersand.ss01  ok
g.alt           g.ss01          ok
y.alt           y.ss01          ok
4 ok, 0 with problems
4 renamed
```

Then, before you do anything else, change the word back to `True` and save the script. That's the part people forget. A script left with its safety off will rename things for the next person who runs it out of curiosity. In a month, that next person is you.

Mira runs it on the real Plum. Sixty ok, none with problems, sixty renamed. She fixes the one line in the Features panel, exports, and sends the fonts that evening.

## The whole script

`rename_suffix.py`, second version:

```python
# Renames every glyph that ends in OLD_SUFFIX so that it ends in NEW_SUFFIX.
# Prints a plan first. With DRY_RUN = True it stops there.
# Afterward, by hand: fix the old names in Features and in kerning classes.
from fly import fl, qt
import fly.ap.glyphs.names.model as names
from fly.ap.glyphs.identity_tools.glyph_identity.batch_rename import (
    apply_renames,
    plan_renames,
)

DRY_RUN = True
OLD_SUFFIX = ".alt"
NEW_SUFFIX = ".ss01"
SKIP = {"zero.alt"}

font = fl.CurrentFont()

pairs = []
for glyph in font.glyphs:
    if glyph.name.endswith(OLD_SUFFIX) and glyph.name not in SKIP:
        old = glyph.name
        new = old.removesuffix(OLD_SUFFIX) + NEW_SUFFIX
        pairs.append([old, new])

facts = names.scan()
plan = plan_renames(facts, pairs)

ok = 0
problems = 0
for old, new, status in plan:
    print(f"{old:<16}{new:<16}{status}")
    if status == "ok":
        ok += 1
    else:
        problems += 1
print(f"{ok} ok, {problems} with problems")

if DRY_RUN:
    print("Dry run. Nothing changed. Set DRY_RUN = False to rename.")
elif problems > 0:
    print("Nothing changed. Fix the problems first.")
else:
    renamed = apply_renames(None, qt.QtCore, facts.package_id, pairs)
    print(len(renamed), "renamed")
```

The shape of this script matters more than its subject. It has four parts: collect what you mean to change, make a plan, show the plan, and apply it only if the switch allows and the plan is clean. You'll use this shape again: collect, plan, show, apply. A script that moves anchors can have it, and so can one that deletes kerning pairs.

## What you learned

`True` and `False` are values you can keep in a box, and a box like that works as a switch for an `if`. Name the switch after the safe behavior and leave it on, so that a careless run and a typo both end in a rehearsal. A dry run prints the plan and stops, and it only works if you read the plan: `ok` means the font will accept a change, not that the change is the one you wanted.

## Try it yourself

1. Add `g.alt` to `SKIP` and run the dry run. Then put a name in `SKIP` that isn't in the font at all, such as `q.alt`. Does the script mind? Should it? Add two lines that print a warning for any name in `SKIP` that the font doesn't have. Set subtraction from chapter 25 will do it.
2. Go back to `safe_edit.py` from chapter 29 and give it a `DRY_RUN` switch. In a dry run it should print the glyph name, the width now and the width it would become, and change nothing.
3. Make the plan say something a person can act on. When `problems` is more than 0, print only the rows that aren't `ok`, under a heading, after the full table. Test it by adding a glyph called `a.ss01` by hand before the dry run.

## Next

Ines keeps track of which glyphs are finished by painting their cells green. Chapter 32 teaches the script to read her colors, and to paint some of its own.
