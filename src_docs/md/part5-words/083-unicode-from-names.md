---
this_file: src_docs/md/part5-words/083-unicode-from-names.md
---

# 83. Unicode from names

Wednesday of week sixteen. Yesterday's script named 261 Greek glyphs from their code points. This morning Ines finds the opposite trouble in the same file. A dozen glyphs carry good names, `numbersign` among them, and type nothing: somewhere in the import their code points fell off. One more has the code point of its neighbor.

A glyph with no code point can't be typed. The keyboard sends a number, the font looks the number up, and a glyph nobody listed under that number stays in the drawer.

Yesterday the number was trusted and the name was made from it. Today the name is trusted and the number is made from it. It's the same table, read from the other side.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed. Chapter 82's three planted names should be mended, so that the font has `asciicircum`, `bar` and `numbersign` again.
- The `tell` function from [chapter 39](../part2-a-toolbox/039-ask-the-user.md). The script below defines it again, so it runs by itself.
- The Font window in front, and no Glyph window or glyph tab open. Fly refuses to write code points while a glyph is open for editing.

I couldn't run the code in FontLab 9. The plans and counts below were computed in plain Python from Plum's source file and from Fly's own planning code. I haven't seen the write happen, and I haven't seen what Fly says when a glyph tab is open.

Your practice font has no glyph that lost its code point. Step 4 spoils three.

## Step 1: The number inside a name

Some names carry their code point in plain sight. `uni03A9` is the Greek capital omega, `U+03A9`. Getting the number out is a slice and a conversion:

```python
def code_from_uni(name):
    return int(name[3:])

print(code_from_uni("uni0041"))
```

```text
41
```

It ran, it printed a number, and the number is wrong. `U+0041` is the capital A, and A is number 65. What you got is 41, which is the closing parenthesis. `int` read `0041` as an everyday number and threw away the zeros.

Try a name with a letter among its digits and Python complains:

```python
print(code_from_uni("uni00C1"))
```

```text
ValueError: invalid literal for int() with base 10: '00C1'
```

"Base 10" is the giveaway. Chapter 23 warned about this trap: a hex number with no letters in it looks like an everyday number and isn't one. The error for `00C1` is the kind one. The silence for `0041` would have put a parenthesis on the A key.

Tell `int` which way of counting the text uses:

```python
def code_from_uni(name):
    return int(name[3:], 16)

print(code_from_uni("uni0041"))
print(code_from_uni("uni00C1"))
```

```text
65
193
```

## Step 2: The table, the right way round

Most names don't carry a number. `eacute` doesn't. For those you need the table from chapter 82, and this time you need it the way it was made, with names on the left:

```python
from fly.ap.glyphs.identity_tools.glyph_identity.unicode_from_names import AGL

print(AGL["eacute"])
print("eacute" in AGL)
print("a.sc" in AGL)
```

```text
233
True
False
```

Yesterday you turned this dictionary round to get `BY_CODE`. Looking up by name needs no turning. A dictionary answers one kind of question fast: "what stands next to this key?" If you want to ask from the other side, you build a second dictionary. Mira keeps both, and she names each after its left side.

## Step 3: Let Fly read the name

Between `uni` names and the table there's a third kind. `Wacute` isn't in the table, as chapter 82 found. Yet its name says what it is: a `W` with an acute. Fly has a function that tries all three routes in order. Run it on a handful of names:

```python
from fly.ap.glyphs.identity_tools.glyph_identity.unicode_from_names import code_for_name

for name in ["uni03A9", "eacute", "Wacute", "a.sc", "f_i", "uni03a9"]:
    code, source = code_for_name(name)
    print(f"{name:<10}{code}  {source!r}")
```

```text
uni03A9   937  'uni'
eacute    233  'AGL'
Wacute    7810  'derived'
a.sc      None  ''
f_i       None  ''
uni03a9   None  ''
```

The function hands back two things, and `code, source = ...` puts them in two boxes, as `plan` did in chapter 62. The second says how the first was found: from a `uni` name, from the table, or derived from a letter and an accent word.

Three names got `None`, and each for a reason.

`a.sc` has a suffix. A small-cap `a` is a second drawing of a letter that already has its code point on the plain `a`. It gets none of its own, and a feature brings it in, which chapter 88 writes.

`f_i` is a ligature, two letters in one glyph. It gets none either.

`uni03a9` has a lowercase `a` in its hex digits. Chapter 81's `is_uni_name` turned such names down, and Fly does too.

So "no code point" isn't always a fault. The fault is a name that implies a code point which the glyph doesn't have.

## Step 4: Spoil three glyphs

Take the same three glyphs as yesterday. Two lose their code point and `bar` gets the one that belongs to `asciicircum`. Put this in the Scripting panel and run it once, with the Font window in front:

```python
import fly.ap.glyphs.names.model as names

PLANT = {"asciicircum": [], "numbersign": [], "bar": [0x5E]}

facts = names.scan()


def spoil():
    for name, codes in PLANT.items():
        facts.entries[name].record.unicodes = codes


names.commit("Spoil three code points", [facts.entries[name] for name in PLANT],
             spoil, operation="unicode", facts=facts, window=facts.package_id)
```

This is the write itself, with nothing wrapped round it. A glyph's code points are a list, `unicodes`, because a glyph may have more than one, which is chapter 84's subject. An empty list means none. The assignment sits inside a function, and `names.commit` runs that function as one Undo step, the same arrangement as `history.commit` in chapter 29. `window=` asks Fly to check the Font window rule before anything is written.

You won't write this by hand again in this chapter. Fly has a planner and a writer for the job, and they're built like the rename pair from chapter 31.

## Step 5: The plan

`plan_unicodes` takes the facts, a list of names and a switch. It returns one row for every name that implies a code point: the name, the codes the glyph has now, the code the name implies, the source and a status.

```python
from fly.ap.glyphs.identity_tools.glyph_identity.unicode_from_names import plan_unicodes

facts = names.scan()
plan = plan_unicodes(facts, list(facts.entries), False)
for name, current, code, source, status in plan:
    if status != "same":
        print(f"{name:<14}{current}  {code}  {status}")
```

```text
numbersign    []  35  assign
asciicircum   []  94  used by bar
bar           [94]  124  encoded differently
```

`list(facts.entries)` is every glyph name in font order: looping over a dictionary gives its keys, and `list` collects them.

Four statuses can turn up. `same` means the glyph already has the code its name implies, and on Plum that's nearly all of them. `assign` means the glyph has none and the code is free. `used by bar` means another glyph holds that code, and Fly won't give one code point to two glyphs. `encoded differently` means the glyph has a code, it isn't the implied one, and the switch says not to replace.

The switch is the third argument. `False` fills gaps only. `True` also replaces a code that disagrees with the name.

## Step 6: Apply, and apply again

The whole script is below. Run it as it stands and you get the plan with codes written the Unicode way:

```text
numbersign    none      U+0023  AGL      assign
asciicircum   none      U+005E  AGL      used by bar
bar           U+005E    U+007C  AGL      encoded differently
232 already right, 1 to assign, 2 stuck, 16 with names that imply nothing
Dry run. Nothing changed. Set DRY_RUN = False to assign.
```

These counts are for the practice font as the book has left it: Plum's 205 glyphs, the fifteen suffixed glyphs from Part 2 and the thirty-one glyphs Part 3 built, 251 in all. The sixteen names that imply nothing are `.notdef` and the fifteen with a suffix. If you skipped a chapter or did an exercise that added glyphs, your first and last numbers differ and the three rows don't.

Two rows are stuck and they're stuck on each other. `bar` sits on the circumflex's code, so `asciicircum` can't have it. With `OVERWRITE = False` the script won't move `bar`.

Mira reads the two rows, agrees that `bar` is the one in the wrong, and sets `OVERWRITE = True` and `DRY_RUN = False`:

```text
numbersign    none      U+0023  AGL      assign
asciicircum   none      U+005E  AGL      used by bar
bar           U+005E    U+007C  AGL      assign
232 already right, 2 to assign, 1 stuck, 16 with names that imply nothing
2 assigned
```

One row is still stuck. The plan is made before anything changes, and when it was made `bar` still held `U+005E`. Now it doesn't. Run the script a second time:

```text
asciicircum   none      U+005E  AGL      assign
234 already right, 1 to assign, 0 stuck, 16 with names that imply nothing
1 assigned
```

A third run prints one line, which begins `235 already right, 0 to assign, 0 stuck`, and that line is how you know you're done. A script you can run until it has nothing left to say is a comfortable script to own.

Then set both switches back.

## The whole script

```python
#FLM: Fix Unicodes
# Finds glyphs whose name implies a code point they don't have.
# Prints a plan. With DRY_RUN = True it stops there.
# OVERWRITE = True also replaces a code point that disagrees with the name.
from fly import fl, qt
import fly.ap.glyphs.names.model as names
from fly.ap.glyphs.identity_tools.glyph_identity.unicode_from_names import (
    apply_unicodes,
    plan_unicodes,
)
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


DRY_RUN = True
OVERWRITE = False


def show_codes(codes):
    if not codes:
        return "none"
    return " ".join(f"U+{code:04X}" for code in codes)


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    facts = names.scan()
    everyone = list(facts.entries)
    plan = plan_unicodes(facts, everyone, OVERWRITE)

    same = 0
    stuck = 0
    todo = []
    for name, current, code, source, status in plan:
        if status == "same":
            same += 1
            continue
        print(f"{name:<14}{show_codes(current):<10}U+{code:04X}  {source:<9}{status}")
        if status == "assign":
            todo.append(name)
        else:
            stuck += 1
    silent = len(everyone) - len(plan)
    print(f"{same} already right, {len(todo)} to assign, {stuck} stuck, "
          f"{silent} with names that imply nothing")

    if DRY_RUN:
        print("Dry run. Nothing changed. Set DRY_RUN = False to assign.")
    elif todo:
        changed = apply_unicodes(None, qt.QtCore, facts.package_id, todo, OVERWRITE)
        print(len(changed), "assigned")


main()
```

Save it as `fix_unicodes.py`.

Notes on the listing.

Chapter 31's script refused to rename anything while one row had a problem. This one assigns the clean rows and leaves the stuck ones, because a stuck row here often comes loose once its neighbor is mended, as you saw. `apply_unicodes` makes its own plan again before it writes and touches only rows that say `assign`, so a font that changed since the printout can't be written from stale news.

`continue` skips the rest of the loop body for this row and goes on to the next. You met it in chapter 44.

`silent` is a subtraction. The plan holds only names that imply something, so whatever is missing from it implied nothing.

The two strings in the last `print` stand side by side with nothing between them. Python joins neighbors like that into one string, which is a way to keep a long line inside the page.

## Break it on purpose

Fly's table has a few surprises, and one of them matters to Ines today:

```python
print(code_for_name("Delta"))
```

```text
(8710, 'AGL')
```

8710 is `U+2206`, the increment sign from mathematics. The Greek capital delta is `U+0394`. The old name list that this table comes from gave the name `Delta` to the maths sign, long before anyone drew Greek for it. A Greek glyph called `Delta` with `U+0394` would show up in the plan as `encoded differently`, and with `OVERWRITE = True` the script would move it to the maths sign and report success.

That's the reason `OVERWRITE` is off unless somebody has read the rows. It's also the reason yesterday's script called Greek glyphs `uni0394` and didn't guess.

## Which side do you trust?

Chapter 82 trusts the number and writes the name. This chapter trusts the name and writes the number. Run both on one glyph and the second undoes nothing: it agrees with whatever the first left. Run either on a glyph where both sides are wrong and you get a wrong answer with a tidy status.

So decide for each batch which side is good. Ines's Greek import had good numbers and junk names. The dozen glyphs from this morning had good names and no numbers. No script can make that decision for her, though a dry run puts the rows in front of her.

## What you learned

A lookup table answers from its left side, so a question asked from the other side needs a second table or the first one turned round. `int(text, 16)` reads hex, and leaving out the 16 gives either an error or a silently wrong number. A function can return a value and a note on where the value came from, and a status word on every row lets a script act on the clean rows and leave the rest. A plan describes the font before the write, so a second run can find work that the first run made possible.

## Try it yourself

1. Write `show_char(code)` that returns the character for a code point with `chr` from chapter 23, and add it as a last column to the plan rows. Which of the three planted rows shows a character you can't tell from its neighbor at a glance?
2. Count the sources. Loop over the whole plan, not only the rows that changed, and build a dictionary from source to count with `.get(source, 0) + 1`. On Plum as it ships you should see 196 from the table and 8 derived. Which eight? Chapter 82 printed their count for another reason.
3. Spoil the font differently: give `numbersign` the code `0x7C` and leave `bar` alone. Before you run the dry run, write down what status each of the two glyphs will get with `OVERWRITE = False`, and then with `True`. Run both and compare. Undo the spoiling afterward.

## Next

Some glyphs are meant to have two code points: one drawing that serves the space and the no-break space. Chapter 84 finds the glyphs that carry more than one, and gives a second code point to two that should.
