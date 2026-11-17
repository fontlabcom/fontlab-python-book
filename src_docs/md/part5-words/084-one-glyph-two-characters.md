---
this_file: src_docs/md/part5-words/084-one-glyph-two-characters.md
---

# 84. One glyph, two characters

Thursday of week sixteen. Tobias sends a screenshot of a web page set in Plum. One line reads "page 12" and the gap between the word and the number is wider than every other gap on the page, and a different gray.

Ines knows the cause before she opens the file. The author typed a no-break space there, so that "page" and "12" never part at a line end. A no-break space is a character of its own, `U+00A0`. Plum has no glyph for it, so the browser borrowed a space from another font.

Plum doesn't need a new drawing. The no-break space should look like the space, to the unit. What the font needs is a second number on the glyph it already has.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and the three code points from chapter 83 mended.
- `halfmoon.py` with `tell`.
- The Font window in front and no glyph open for editing, as in chapter 83.

I couldn't run the code in FontLab 9. The list behavior in Steps 1 to 3 is plain Python and I ran it. The report and plan were computed from Plum's source file. I haven't seen FontLab accept a list of two code points from a script: Fly's own tools shorten such lists and never lengthen them, so the write in this chapter is one step past what I could read in source. Keep the dry run on until you've looked at the plan, and check the glyph afterward.

## Step 1: A list in a drawer

In chapter 83 you wrote `record.unicodes = []` and I said the code points of a glyph are a list. Look at one:

```python
from fly import fl

font = fl.CurrentFont()
space = font["space"]
print(space.unicodes)
print(space.unicode)
print(len(space.unicodes))
```

```text
[32]
32
1
```

A glyph is a wardrobe with drawers, as it has been since chapter 6. Most drawers hold one thing: a name, a width. This drawer holds a list, and a list can hold none, one or several. `unicode` without the `s` is a shortcut to the first item, or `None` when the list is empty.

Every glyph in Plum has one code point, except `.notdef`, which has none. So every list you can print today is one item long. You're about to make two that are longer.

## Step 2: Two names for one list

Before you touch a glyph, try the idea on a plain list. This needs no font:

```python
codes = [32]
longer = codes
longer.append(160)
print(longer)
print(codes)
```

```text
[32, 160]
[32, 160]
```

You appended to `longer` and `codes` grew too. Nothing went wrong inside Python. `longer = codes` doesn't copy a list. It ties a second label to the same box. There's one list here with two names, and whatever you do through one name you see through the other.

With numbers and strings you never noticed, because you can't change a number in place. `append` changes a list in place, and so the sharing shows.

Now make a new list on purpose:

```python
codes = [32]
longer = codes + [160]
print(longer)
print(codes)
```

```text
[32, 160]
[32]
```

`+` between two lists builds a third and leaves both alone. Now you have the old list and the new one, and you can compare them, print them side by side or throw the new one away.

That second form is the one to use on a glyph. Fly's own code always builds a new list and assigns it to the drawer in one statement, and I follow it. What `space.unicodes.append(160)` does to the font, I can't tell you. It may change the glyph behind Undo's back and it may change nothing at all, and neither is what you want.

## Step 3: Order counts

Put the new code in front and see what the shortcut says:

```python
codes = [32]
wrong = [160] + codes
print(wrong)
print(wrong[0])
```

```text
[160, 32]
160
```

The first item is the glyph's main code point. It's what `unicode` returns and what chapter 82's `name_for` reads. With 160 in front, `fix_names.py` would look at your `space`, find `nbspace` in the table and offer to rename it. Every script in this book that asks a glyph for its one code point would get the newcomer.

So the old code stays first and the extra goes on the end.

## Step 4: Who has what

A report first. Two questions: which glyphs have more than one code point, and is any code point on two glyphs? The first is a loop with `len`. The second needs the table turned round again, from code to names, and this time the right side is a list because the whole point is to catch a code with two owners:

```python
def owners(all_codes):
    found = {}
    for name, codes in all_codes.items():
        for code in codes:
            if code not in found:
                found[code] = []
            found[code].append(name)
    return found
```

It's the dictionary of lists from chapter 64, with a loop inside a loop because each glyph may bring several codes. In chapter 82 you turned a table round with one line and checked the lengths to see whether anything had been overwritten. Here nothing can be overwritten: a second owner joins the list.

`all_codes` is a plain dictionary, name to list of code points, read from the font once at the top of the script:

```python
all_codes = {glyph.name: list(glyph.unicodes) for glyph in font.glyphs}
```

`list(...)` makes a copy of each glyph's list. After Step 2 you know why: the script should hold its own lists and not labels tied to the font's.

## Step 5: The plan

What should be added goes in a dictionary at the top:

```python
WANTED = {"space": 0xA0, "hyphen": 0xAD}
```

`U+00AD` is the soft hyphen, the character a writer puts inside a long word to say "you may break here". Fonts give it the hyphen's drawing.

Each wanted pair gets a status, the way chapter 83's rows did. The glyph may be missing. It may have the code already. Another glyph may hold the code. Otherwise the code can be added:

```python
def plan_extras(all_codes, wanted):
    taken = owners(all_codes)
    rows = []
    for name, code in wanted.items():
        if name not in all_codes:
            rows.append((name, code, "no such glyph"))
        elif code in all_codes[name]:
            rows.append((name, code, "has it"))
        elif code in taken:
            rows.append((name, code, f"used by {taken[code][0]}"))
        else:
            rows.append((name, code, "add"))
    return rows
```

The order of the tests matters. "Has it" is asked before "used by", because a glyph that already has the code is itself in the owners list and would be reported as its own rival.

Run the whole script as a dry run:

```text
More than one code point:
  0 found
One code point on two glyphs:
  0 found
space       U+0020          U+00A0  add
hyphen      U+002D          U+00AD  add
Dry run. Nothing changed. Set DRY_RUN = False to add.
```

Set `DRY_RUN = False` and run again. It ends with `2 added`. Set it back and run a third time:

```text
More than one code point:
  hyphen      U+002D U+00AD
  space       U+0020 U+00A0
  2 found
One code point on two glyphs:
  0 found
space       U+0020 U+00A0   U+00A0  has it
hyphen      U+002D U+00AD   U+00AD  has it
Dry run. Nothing changed. Set DRY_RUN = False to add.
```

`hyphen` comes first in the report because it comes first in the font. The plan follows `WANTED`.

Then look with your own eyes. Select `space` in the Font window and open the Glyph panel: the Unicode field should show both code points. If it shows one, the write didn't take, and I'd like to hear about it.

## The whole script

```python
#FLM: Double Encoded
# Reports glyphs with more than one code point and code points on two glyphs.
# Then adds the extra code points in WANTED, each as a second code point.
import halfmoon
from fly import fl
import fly.ap.glyphs.names.model as names

DRY_RUN = True
WANTED = {"space": 0xA0, "hyphen": 0xAD}


def show_codes(codes):
    if not codes:
        return "none"
    return " ".join(f"U+{code:04X}" for code in codes)


def owners(all_codes):
    found = {}
    for name, codes in all_codes.items():
        for code in codes:
            if code not in found:
                found[code] = []
            found[code].append(name)
    return found


def plan_extras(all_codes, wanted):
    taken = owners(all_codes)
    rows = []
    for name, code in wanted.items():
        if name not in all_codes:
            rows.append((name, code, "no such glyph"))
        elif code in all_codes[name]:
            rows.append((name, code, "has it"))
        elif code in taken:
            rows.append((name, code, f"used by {taken[code][0]}"))
        else:
            rows.append((name, code, "add"))
    return rows


def report(all_codes):
    print("More than one code point:")
    count = 0
    for name, codes in all_codes.items():
        if len(codes) > 1:
            print(f"  {name:<12}{show_codes(codes)}")
            count += 1
    print(f"  {count} found")
    print("One code point on two glyphs:")
    count = 0
    for code, glyph_names in owners(all_codes).items():
        if len(glyph_names) > 1:
            print(f"  U+{code:04X}  {' '.join(glyph_names)}")
            count += 1
    print(f"  {count} found")


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    all_codes = {glyph.name: list(glyph.unicodes) for glyph in font.glyphs}
    report(all_codes)

    rows = plan_extras(all_codes, WANTED)
    todo = {}
    for name, code, status in rows:
        print(f"{name:<12}{show_codes(all_codes.get(name, [])):<16}U+{code:04X}  {status}")
        if status == "add":
            todo[name] = all_codes[name] + [code]

    if DRY_RUN:
        print("Dry run. Nothing changed. Set DRY_RUN = False to add.")
        return
    if not todo:
        return

    facts = names.scan()
    allowed, refused = names.editable(facts, list(todo), "unicode")
    for name, reason in refused.items():
        print(f"{name}: left alone, {reason}")

    def add():
        for name in allowed:
            facts.entries[name].record.unicodes = todo[name]

    names.commit("Add extra code points", [facts.entries[name] for name in allowed],
                 add, operation="unicode", facts=facts, window=facts.package_id)
    print(len(allowed), "added")


main()
```

Save it as `double_encoded.py`.

Notes on the listing.

`todo` maps each name to the complete new list, built with `+` in the loop that prints the plan. By the time `add` runs there's nothing left to work out: it puts each finished list in its drawer.

`names.editable` sorts the names into those Fly will let you change and those it won't, with a reason for each refusal. Chapter 83's `apply_unicodes` did this for you out of sight. Here you call the write yourself, so you ask yourself.

`def add()` sits inside `main`. A function defined inside another can see the outer one's boxes, `facts`, `todo` and `allowed`, with no need to pass them. It's the arrangement from chapter 49, where `commit` wants a function it can call with no arguments.

`glyph_names` in `report` is called that and not `names`, because `names` is already the label on Fly's module at the top of the file. Reuse the label inside the function and the module is out of reach there.

## Break it on purpose

Step 5 gave `space` and `hyphen` their second codes, so first take that back: choose **Edit > Undo** once, and check that the step it names is "Add extra code points". Now give the no-break space to the wrong glyph. In the Glyph panel, select `period` and type `002E,00A0` into the Unicode field. Then run the dry run:

```text
More than one code point:
  period      U+002E U+00A0
  1 found
One code point on two glyphs:
  0 found
space       U+0020          U+00A0  used by period
hyphen      U+002D          U+00AD  add
Dry run. Nothing changed. Set DRY_RUN = False to add.
```

The script won't give `U+00A0` to `space` while `period` holds it. It also won't take it off `period`: taking a code away is a decision, and this script only adds. Clear it by hand in the Glyph panel, or undo, and the plan says `add` again. Then set `DRY_RUN = False`, run the script once more so that `space` and `hyphen` have their second codes back, and set the switch to `True`. Later chapters count on those two codes.

Had the script added it anyway, the second report would have had its first line: one code point, two glyphs. Which of the two a program shows when you type that character isn't something I'd want to guess.

## How this sits with chapter 83

Run `fix_unicodes.py` after this chapter. It should still say everything is right. Its test for `same` asks whether the code a name implies is somewhere in the glyph's list, and `space` still has 32. The second code point is nobody's business but yours.

Run `fix_names.py` and it's content too, as long as the old code is first. That's Step 3 again.

## What you learned

An object's drawer can hold a list, and a list has a length and an order that both mean something. Giving a list a second name doesn't copy it, so build a new list with `+` when you want to keep the old one. A script that changes a font should compute the complete new value first and assign it in one statement inside an Undo step. A dictionary of lists catches the case a plain dictionary hides: two owners for one key.

## Try it yourself

1. Add a third pair to `WANTED` that gives `U+2010`, the typographer's hyphen, to `hyphen`. A dictionary can't hold two entries for `"hyphen"`. Change `WANTED` so each name maps to a list of codes, and change `plan_extras` and the `todo` loop to match. What does the report print for `hyphen` afterward?
2. Write `remove_code(codes, code)` that returns a new list without one code, using a comprehension from chapter 37. Check on a plain list that the one you passed in is unchanged. Then say what should happen if the code to remove is the first one, and make the function refuse that case by returning the list untouched.
3. `len(codes) != len(set(codes))` is true when a list holds the same item twice. Chapter 25 introduced sets. Try it on `[32, 160, 160]`. FontLab is said to drop such repeats when a list is assigned, so a font should never show one. Add the test to `report` anyway and see that it finds nothing.

## Next

"Does it do Turkish?" asks the client, and nobody in the room is sure. Chapter 85 keeps the characters each language needs in a file and holds the font against it.
