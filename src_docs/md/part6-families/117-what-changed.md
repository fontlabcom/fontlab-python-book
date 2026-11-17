---
this_file: src_docs/md/part6-families/117-what-changed.md
---

# 117. What changed since last week?

Tuesday of week twenty-three. The production editor has two sets of files from Halfmoon now, version 1.001 from last Monday and version 1.002 from Thursday. She writes: "What changed between them? I need to know whether to reflow the sample pages."

Mira knows the answer from memory. Nothing changed but the number. She bumped the version because chapter 114's check found the 1.001 folders already in use.

She can't prove it. The note that `bump_version.py` writes says when each number was given, and says nothing of what was done to the font. And she has no copy of the font as it was last Monday. The exported files are there, but the file she works in has been saved over many times since.

So today has two results. One is a script that lists the differences between two open fonts. The other is a habit that makes sure there's a second font to open.

## What you need

- `Plum-practice.vfj` open in FontLab 9, with Fly installed, and `halfmoon.py`.
- A few minutes to make a copy of the file, in Step 1.

I couldn't run the code in FontLab 9. I ran the script in plain Python. The part that compares glyphs is Fly's own function, running for real on records I built from the shipped Plum. The part that reads two open fonts from FontLab is a stand-in.

## Step 1: Make a case whose answer you know

You don't have last Monday's font either. So build a comparison where you know what the script should say, the way chapter 42 tested a count on a glyph whose answer was known.

Save the font. In Finder or Explorer, copy `Plum-practice.vfj` and name the copy `Plum-practice-before.vfj`. Open the copy in FontLab too, so both are open. Then bring `Plum-practice` to the front and make three changes by hand, all in the Regular master:

1. Make `hyphen` 10 units wider.
2. Move the `top` anchor of `H` a few units to the right.
3. In the Kerning panel, change the pair `T` `ae` from −48 to −40.

Write the three down. That list is the answer sheet.

## Step 2: Ask Fly what differs

Fly has a tool for this, made for its own comparison window. It works in two moves. `capture` reads one master of one open font into a snapshot, a frozen record of every glyph's width, outline, anchors and components. `compare` takes two snapshots and returns the differences.

```python
import fly.ap.core.scripting as scripting
import fly.ap.fonts.revisions.model as revisions
from fly import fl

workspace = fl.flWorkspace.instance()
packages = [fl.flPackage(item) for item in workspace.packages()]
new = scripting.current_package()
old = [p for p in packages if scripting.font_id(p) != scripting.font_id(new)][0]

before = revisions.capture(workspace, scripting.font_id(old), "Regular")
after = revisions.capture(workspace, scripting.font_id(new), "Regular")
for difference in revisions.compare(before, after):
    print(difference.glyph, difference.fields)
```

The first two lines after the imports are chapter 99's: FontLab's list of open fonts, each turned into a package. `scripting.font_id` gives the number FontLab knows a font by. The font in front is the new one. The old one is whichever open font has a different number.

Each difference has four parts. `glyph` is a name. `fields` says which things differ, in Fly's words: `advance`, `geometry`, `anchors`, `components`, and a few more. `left` and `right` are the glyph's records from the two snapshots.

Mira ran this and got:

```text
H ('anchors',)
n ('raw_node_state',)
hyphen ('advance',)
```

Two of her three, in a tuple each. The kerning pair isn't there, and a glyph she never touched is.

## Step 3: The mistake

Start with `n`. Mira didn't change it. She had clicked one of its nodes that morning while looking at something else.

Fly's notes on `compare` say what that field is: the raw state of every node, and that includes whether the node is selected. A selected node in one font and not in the other counts as a difference. Fly keeps the field because its window lets a person switch it on and off. In a list for a client it's noise, and worse than noise. A client who reads "n changed" will ask what changed in the n.

A report of differences can be wrong in two directions. It can miss a change, and it can announce one that didn't happen. Each costs trust. So the script keeps a list of fields to pass over, and `raw_node_state` is on it:

```python
QUIET = ["raw_node_state"]
fields = [f for f in difference.fields if f not in QUIET]
```

Now the pair. `compare` didn't miss it. Snapshots don't hold kerning at all. Fly's notes say it compares named fields and nothing more, and kerning, Unicode values, features and Font Info aren't among them. A tool that compares some things should say which, so the script's last line will name the rest.

## Step 4: Kerning, by set arithmetic

Kerning you can compare yourself. `scripting.kerning_pairs(package, master)` has given you a dict of pairs since chapter 69, and the keys of two dicts can be compared as sets, with chapter 25's signs:

```python
was = scripting.kerning_pairs(old, "Regular")
now = scripting.kerning_pairs(new, "Regular")
print(len(set(was) - set(now)), "removed")
print(len(set(now) - set(was)), "added")
print(len(set(was) & set(now)), "in both")
```

```text
0 removed
0 added
105 in both
```

`set(was)` is the set of a dict's keys. Minus gives the pairs in one and not the other, and it matters which side is which. `&` gives the pairs in both, and those are the only ones whose values you can compare. Three questions, three lines. That's the whole of a dict difference, and it works for any two dicts with the same kind of keys: widths by glyph name, Unicode values by name, files by size.

## The whole script

```python
#FLM: Font Diff
# Lists what differs between two open fonts, master by master: glyphs,
# widths, shapes, anchors and kerning. Changes nothing in either font.
from pathlib import Path

import fly.ap.core.scripting as scripting
import fly.ap.fonts.revisions.model as revisions
import fly.ap.masters.inspect.model as masters_model
import halfmoon
from fly import fl

QUIET = ["raw_node_state"]
WORDS = {"state": "layer", "advance": "width", "geometry": "shape",
         "anchors": "anchors", "components": "parts",
         "glyph_order": "glyph order", "master_presence": "master"}


def other_fonts(current):
    workspace = fl.flWorkspace.instance()
    packages = [fl.flPackage(item) for item in workspace.packages()]
    mine = scripting.font_id(current)
    return [p for p in packages if scripting.font_id(p) != mine]


def glyph_lines(old, new, master):
    workspace = fl.flWorkspace.instance()
    before = revisions.capture(workspace, scripting.font_id(old), master)
    after = revisions.capture(workspace, scripting.font_id(new), master)
    lines = []
    for difference in revisions.compare(before, after):
        name = difference.glyph or "(whole font)"
        fields = [f for f in difference.fields if f not in QUIET]
        if not fields:
            continue
        if "glyph_presence" in fields:
            word = "added" if difference.left is None else "removed"
            lines.append(f"{name}: {word}")
        elif fields == ["advance"]:
            was = round(difference.left.advance)
            now = round(difference.right.advance)
            lines.append(f"{name}: width {was} to {now}")
        else:
            lines.append(f"{name}: " + ", ".join([WORDS.get(f, f) for f in fields]))
    return lines


def kern_lines(old, new, master):
    was = scripting.kerning_pairs(old, master)
    now = scripting.kerning_pairs(new, master)
    lines = []
    for pair in sorted(set(was) - set(now)):
        lines.append(f"{pair[0]} {pair[1]}: kern removed, was {round(was[pair])}")
    for pair in sorted(set(now) - set(was)):
        lines.append(f"{pair[0]} {pair[1]}: kern added, {round(now[pair])}")
    for pair in sorted(set(was) & set(now)):
        if was[pair] != now[pair]:
            lines.append(f"{pair[0]} {pair[1]}: kern {round(was[pair])} "
                         f"to {round(now[pair])}")
    return lines


def main():
    if fl.CurrentFont() is None:
        halfmoon.tell("Open a font first.")
        return
    new = scripting.current_package()
    others = other_fonts(new)
    if len(others) != 1:
        halfmoon.tell("Open two fonts, with the new one in front. "
                      f"{len(others) + 1} are open.")
        return
    old = others[0]
    print(f"Old: {Path(old.path).name}")
    print(f"New: {Path(new.path).name}")
    total = 0
    for master in masters_model.master_order(new):
        lines = glyph_lines(old, new, master) + kern_lines(old, new, master)
        total += len(lines)
        print(f"{master}: {len(lines)}")
        for line in lines:
            print(f"  {line}")
    print(f"{total} differences.")
    print("Not compared: Unicode values, features, Font Info.")


main()
```

Save it as `font_diff.py`. With `Plum-practice` in front, run it:

```text
Old: Plum-practice-before.vfj
New: Plum-practice.vfj
Light: 0
Regular: 3
  H: anchors
  hyphen: width 348 to 358
  T ae: kern -48 to -40
Bold: 0
3 differences.
Not compared: Unicode values, features, Font Info.
```

Hold it against your answer sheet: three changes made, three found, and nothing invented. The widths are from my stand-in and yours will be your own. The glyph lines come in the font's glyph order, so they may be arranged differently.

Notes on the listing.

The first two printed lines name the files. In a comparison the direction is half the meaning, and a report that doesn't say which font it called old can't be checked.

`difference.glyph or "(whole font)"` is chapter 91's `or` between values. A few differences belong to the font and not to a glyph, such as a changed glyph order, and for those Fly leaves the name empty.

When a glyph is in only one font, Fly puts `None` on the side that lacks it, so `difference.left is None` means the old font didn't have it.

For a width the script prints both numbers, read from the records in `left` and `right`. For shapes and anchors it prints only the word. The records hold every coordinate, and you could dig them out. For a client, "H: anchors" is the right length. The person who needs the coordinates has both fonts open and can look.

`WORDS` turns Fly's field names into the studio's words. `WORDS.get(f, f)` is chapter 22's `get` with a fallback: a field the dict doesn't know is printed under Fly's name, so a field Fly adds next year still shows up.

`capture` reads every glyph twice, to be sure the font didn't change under it, and the script calls it for two fonts in each of three masters. On a large family, expect a pause.

## The habit

Close `Plum-practice-before.vfj`. Undo your three changes in `Plum-practice`, or keep them if you like them.

The script works, and it couldn't answer the editor's question, because there was no old font to open. The cure costs one line. Whenever files leave the building, a copy of the font goes into the export folder beside them, with chapter 113's `shutil.copy`. Then every version a client holds has a font you can open. Chapter 119's build will do it without being asked.

For today, Mira writes the editor the truth. "Between 1.001 and 1.002, only the version number changed. I can't show you a comparison for that pair. From the next version on, I'll send a change list with every release."

## Break it on purpose

Open both fonts again, with the three changes in place, and this time bring `Plum-practice-before` to the front. Run:

```text
Old: Plum-practice.vfj
New: Plum-practice-before.vfj
Light: 0
Regular: 3
  H: anchors
  hyphen: width 358 to 348
  T ae: kern -40 to -48
Bold: 0
3 differences.
Not compared: Unicode values, features, Font Info.
```

Every number runs backward, and the count is the same. Nothing in the fonts tells the script which is older. It took your word, in the form of which window was in front. That's why the two file names are printed first.

Now open a third font, any font, and run:

```text
Open two fonts, with the new one in front. 3 are open.
```

With three open, "the other font" has no meaning, and the script says so and stops. It would have been simple to take the first of the others and carry on. Then the report would compare Plum with a stranger, find hundreds of differences, and look like a disaster.

## What you learned

Fly's `capture` and `compare` list which glyphs differ between one master of two open fonts and in which respect, and they leave kerning, Unicode values, features and Font Info alone. Two dicts are compared with three set expressions on their keys: minus one way, minus the other way, and `&` for the keys whose values can be compared. A difference report has to keep quiet about things that aren't changes, such as a selected node, and has to say which font it took as the old one. None of it works without an old font, so a copy of the source belongs with every export.

## Try it yourself

1. Print the report's lines to a file, `changes.txt`, in the newest export folder, using `halfmoon.latest_export` from chapter 116.
2. Add the master's count of unchanged kerning pairs to its heading line, so `Regular: 3` becomes `Regular: 3 (104 pairs the same)`.
3. Font Info isn't compared. Chapter 99's `sync_font_info.py` reads Font Info fields from every open font with `getattr`. Read the same fields from the two packages here and add lines such as `copyright: differs`.

## Next

Everything so far has asked FontLab about the font. The client doesn't have FontLab. They have an OTF file. Chapter 118 opens that file with fontTools, a package that reads fonts with no font editor involved, and asks it the same questions.
