---
this_file: src_docs/md/part4-space/072-make-a-class.md
---

# 72. Make a class

Tuesday of week fourteen. Yesterday's report ended with three names: `ecaron`, built like the members of `R_eacute` and not among them, and `Uring` and `uring`, missing from the classes of the `U` and the `u`. Mira could open the Classes panel and drag the glyphs in. For one glyph in one class that's the right tool.

But it's three glyphs in three masters, and yesterday also turned up `Cacute` and `Ccaron`, which the report couldn't see. And the Polish edition is waiting for four letters with an ogonek that aren't drawn yet. Each time letters arrive, somebody has to remember the classes. So today's script holds the rule and applies it: every accented letter built on this base belongs in that class.

It's the first script of this part that changes the kerning.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The helpers `ask` and `tell` from chapter 39. The scripts below write them out again, so each one runs by itself.
- The accented letters of chapters 56 and 60. Without them the script finds nothing to add.
- A saved copy of the font from before today.

I couldn't run the code in FontLab 9. The way the classes are written is copied from one of Fly's own tools, which does the same job, and I haven't seen it work from a script of mine. Read the note before the listing.

## Step 1: A rule that catches too much

Which glyphs belong with the `e`? A first idea: the ones whose names start with `e`. Chapter 9 gave you `startswith`:

```python
from fly import fl

font = fl.CurrentFont()
print(sorted([glyph.name for glyph in font.glyphs if glyph.name.startswith("e")]))
```

```text
['e', 'eacute', 'ecaron', 'ecircumflex', 'edieresis', 'egrave', 'eight', 'ellipsis', 'emdash', 'endash', 'equal', 'exclam', 'exclamdown']
```

Your list may differ by a name or two, depending on which exercises you did. The trouble is the same: `eight`, `ellipsis`, two dashes, the equals sign and two exclamation marks. Put that list into a kerning class and an em dash after a `T` would be pulled in by 52 units, like an `é`.

That's today's mistake. A name is a label somebody chose, and a rule that reads labels finds whatever the labels happen to share. You could patch it: names that start with `e` and end with an accent's name. Then `eogonek` arrives, with its accent underneath, and the patch needs a patch.

Yesterday's rule read the glyph and not its label: a glyph belongs with the `e` when it's built from an `e` and an accent, as components. Take `base_letter` from yesterday, with the master as a third parameter this time, and build the list with it:

```python
def built_on(font, base, master):
    return sorted([glyph.name for glyph in font.glyphs if base_letter(font, glyph.name, master) == base])


print(built_on(font, "e", "Regular"))
print(built_on(font, "C", "Regular"))
print(built_on(font, "T", "Regular"))
```

```text
['eacute', 'ecaron', 'ecircumflex', 'edieresis', 'egrave']
['Cacute', 'Ccaron']
['Tcaron']
```

No figures, no dashes. The rule is a comprehension with a condition, as in chapter 37, and the condition is a question put to each glyph.

## Step 2: A new list, and the old one kept

The class has four members. The rule gives five names. The plan is the old members, in their old order, with the newcomers after them:

```python
old = ["eacute", "ecircumflex", "edieresis", "egrave"]
added = [name for name in built_on(font, "e", "Regular") if name not in old]
new = old + added
print(added)
print(new)
print(old)
```

```text
['ecaron']
['eacute', 'ecircumflex', 'edieresis', 'egrave', 'ecaron']
['eacute', 'ecircumflex', 'edieresis', 'egrave']
```

`+` between two lists makes a third list, with the items of the first and then the items of the second. Neither of the two is touched, and the last line shows it: `old` still has four names.

I'm making a point of that because `append` behaves differently. `old.append("ecaron")` would change `old` itself. Then there'd be no "before" left to compare with, and the script couldn't say what it's about to do. A script that changes a font should always be able to show the old state beside the new one.

Why keep the old order? Because FontLab keeps no separate "main glyph" for a class. By custom the first member stands for the whole class, in panels and in other people's scripts. Sort these lists and the first member stays first, by luck. A class led by `n` that also held `h` and `m` would come out of a sort with `h` in front.

## Step 3: A class that isn't there yet

`Tcaron` has no class to join. The `T` has fourteen pairs in each master, all written for the glyph `T` itself, and the `Ť` shares none of them. The cure is a class for the first place in a pair, with `T` and `Ť` in it. Call it `L_T`, after Plum's own habit.

For the plan, a class that doesn't exist is a class with no members. On Friday I warned you off `get` with a default, because there a missing key and a zero meant different things. Here they mean the same, and the default is the right tool:

```python
classes = scripting.kerning_classes(package, "Regular")
old, old_side = classes.get("L_T", ([], "left"))
print(old, old_side)
```

```text
[] left
```

The default has to have the shape of a real value: a tuple of a list and a word, so that it unpacks like one. A new class starts from the base letter itself, and then the rule adds the rest:

```python
start = old if old else ["T"]
```

An empty list counts as false, so `start` is the old members when there are any and `["T"]` when there are none.

## Step 4: The rules as data

Each class has a place in the pair and a base letter. That's a dictionary, and with yesterday's three classes for the `U` and the `u` it has six entries:

```python
RULES = {
    "R_eacute": ("right", "e"),
    "R_C": ("right", "C"),
    "L_T": ("left", "T"),
    "L_U": ("left", "U"),
    "R_U2": ("right", "U"),
    "R_uacute": ("right", "u"),
}
```

When the ogonek letters come, `eogonek` is built on `e` and the first rule picks it up. Whether it should be picked up is a fair question: its accent hangs below and never meets the bar of a `T`, so it might kern better with the plain `e`. The script prints its plan and asks before it writes. The script lists what the rule would add, and you read the list before it writes.

## How the writing works

The reading went through `scripting.kerning_classes`. For the writing there's no ready-made function, so the script does what Fly's own tool for building accented letters does when it adds its new glyphs to their classes.

The classes of one master live at `package.kerning(master).groups`. That object takes a class name in square brackets, like a dictionary, and you assign a tuple to it:

```python
package.kerning("Regular").groups["R_eacute"] = (new, "KernRight")
```

The list is the membership. The word is FontLab's own name for the place: `KernLeft` for first, `KernRight` for second, `KernBothSide` for either. Yesterday's `left` and `right` were Fly's shorter spellings of the same three. Assigning to a name that exists replaces the class, and assigning to a new name creates it.

That line alone would leave no step in the Edit menu. So it goes inside `history.commit`, as every change since chapter 62 has, with three differences. The operation is `"metadata"`, because no outline moves. Two lines at the start of the change tell the package and its kerning to note their state, so that Undo has something to go back to. And `retain` hands `commit` the three objects that hold kerning. I'm passing those on as I found them. If your FontLab refuses the commit, nothing has been written, and the Classes panel will do the job by hand.

## The whole script

```python
#FLM: Build Kerning Classes
# Adds accented letters to the kerning class their base letter stands for,
# in every master, and makes the class if the font has none.
import fly.ap.components.writer as parts
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
from fly import fl, qt
from fly.pens import layer_of
from fly.ap.ui.dialogs import run_standard_message_box
from fly.tr.proxy.fl.objects.glyph import pGlyph

TITLE = "Halfmoon"

MASTERS = ["Light", "Regular", "Bold"]
NATIVE = {"left": "KernLeft", "right": "KernRight"}
PLACE = {"left": "first", "right": "second"}
# class name: (place in the pair, base letter whose accented forms belong)
RULES = {
    "R_eacute": ("right", "e"),
    "R_C": ("right", "C"),
    "L_T": ("left", "T"),
    "L_U": ("left", "U"),
    "R_U2": ("right", "U"),
    "R_uacute": ("right", "u"),
}


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


def base_letter(font, name, master):
    rich = pGlyph(font, font[name])
    found = parts.components(layer_of(rich.fl, master))
    if len(found) < 2 or rich.contours(master):
        return None
    return parts.base_of(found[0])


def built_on(font, base, master):
    return sorted([glyph.name for glyph in font.glyphs if base_letter(font, glyph.name, master) == base])


def plan(font, package, master):
    classes = scripting.kerning_classes(package, master)
    rows = []
    for name, (side, base) in RULES.items():
        old, old_side = classes.get(name, ([], side))
        if old_side != side:
            print(f"{master} {name}: is a class for the {old_side}, not the {side}. Left alone.")
            continue
        start = old if old else [base]
        new = start + [found for found in built_on(font, base, master) if found not in start]
        if new != old:
            rows.append((master, name, side, old, new))
    return rows


def write(font, package, rows):
    layers = []
    owners = {}
    for master, name, side, old, new in rows:
        for glyph_name in new:
            if glyph_name not in old:
                rich = pGlyph(font, font[glyph_name])
                layers.append(layer_of(rich.fl, master))
                owners[glyph_name] = rich.fl
    container = package.kerningContainer()

    def change():
        package.checkInitHistoryState(0)
        container.checkInitHistoryState(0)
        for master, name, side, old, new in rows:
            package.kerning(master).groups[name] = (new, NATIVE[side])

    history.commit(
        "Build kerning classes",
        layers,
        list(owners.values()),
        change,
        operation="metadata",
        facts=history.scan_auto_facts(package),
        retain=[package, package.mastersContainer(), container],
    )


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    rows = []
    for master in MASTERS:
        rows = rows + plan(font, package, master)
    for master, name, side, old, new in rows:
        added = " ".join([glyph_name for glyph_name in new if glyph_name not in old])
        print(f"{master:<9}{name:<10}{PLACE[side]:<8}{len(old)} to {len(new)}   + {added}")
    print(f"{len(rows)} classes to write.")
    if not rows or not ask(f"Write {len(rows)} kerning classes?"):
        return
    write(font, package, rows)
    still = []
    for master in MASTERS:
        still = still + plan(font, package, master)
    print(f"Done. {len(still)} classes still to write.")


main()
```

Save it as `build_kern_classes.py`. On the practice font, with the letters of chapters 56 and 60 in it, the plan reads:

```text
Light    R_eacute  second  4 to 5   + ecaron
Light    R_C       second  2 to 4   + Cacute Ccaron
Light    L_T       first   0 to 2   + T Tcaron
Light    L_U       first   5 to 6   + Uring
Light    R_U2      second  5 to 6   + Uring
Light    R_uacute  second  4 to 5   + uring
Regular  R_eacute  second  4 to 5   + ecaron
Regular  R_C       second  2 to 4   + Cacute Ccaron
Regular  L_T       first   0 to 2   + T Tcaron
Regular  L_U       first   5 to 6   + Uring
Regular  R_U2      second  5 to 6   + Uring
Regular  R_uacute  second  4 to 5   + uring
Bold     R_eacute  second  4 to 5   + ecaron
Bold     R_C       second  2 to 4   + Cacute Ccaron
Bold     L_T       first   0 to 2   + T Tcaron
Bold     L_U       first   5 to 6   + Uring
Bold     R_U2      second  5 to 6   + Uring
Bold     R_uacute  second  4 to 5   + uring
18 classes to write.
```

Then it asks. Click Yes, and it should end with:

```text
Done. 0 classes still to write.
```

Notes on the listing.

`plan` works on one master and `main` adds the three plans together with `+`, the same joining of lists as in step 2. Classes are kept for each master, and a class that's in one master and missing from the next is trouble for every weight in between. So the script never writes to one master alone.

The `old_side != side` test guards against a rule that names an existing class for the wrong place. Writing `"R_eacute": ("left", "e")` by a slip would otherwise turn a second-place class into a first-place one, and every pair that names it would stop making sense.

`write` gathers the layers of the glyphs that join a class, and their glyphs, because `commit` wants to know what the change touches. `owners` is a dictionary so that a glyph that joins in three masters is listed once, as in chapter 65.

The last three lines of `main` plan again after writing. If the change went in, there's nothing left to plan. It's the same check as "0 layers still off" in chapter 68, and it's the only sign the script has that the font took the change.

## Did it work?

Don't take the script's word. Ask the font, with the tools of the last two days.

Run `list_kern_classes.py`. It should count 18 classes where it counted 17, show `L_T` under "First in a pair", and end with `0 left out:`.

Then run `pair_value.py` on `T ecaron`:

```text
T ecaron
  Light      -61   through a class
  Regular    -52   through a class
  Bold       -36   through a class
```

The same three numbers as `T eacute` yesterday morning. Nobody wrote a pair. The pair for `T` before `@R_eacute` was there all along, and the letter has joined the family it speaks for. `A Cacute` should now give −32, −13 and −32, from the one pair that names `@R_C`.

Mira sets `Těšín` again and the `ě` sits under the bar. Then she tries `Ťo`, with the script's `Tcaron o`, and gets "not kerned" three times.

That's as it should be, and it's worth a minute. `L_T` is a class with no pairs. All fourteen pairs of the `T` are still written for the glyph `T`, and a class without pairs changes nothing in the font. It's a name waiting to be used. Today's whole change, the new class included, should be one step in **Edit > Undo**. I haven't seen it in FontLab 9.

## What you learned

A rule that reads how a glyph is built is safer than one that reads its name. `old + added` makes a new list and leaves both of its parts alone, where `append` changes the list it's called on. The classes of a master are at `package.kerning(master).groups`, and assigning `(members, "KernLeft")` or `(members, "KernRight")` to a name replaces or creates a class. Write classes in every master at once, keep the first member first, and remember that a class does nothing until a pair names it.

## Try it yourself

1. Add a rule for a class `L_S`, first in a pair, on the base `S`. Run the script and read the plan before you click. Which glyphs does it propose? One of them wasn't built by you. Click No if you'd rather not keep it.
2. The plan prints eighteen lines for six classes, because the masters agree. Change the printing so that a class whose plan is the same in all three masters gets one line that starts with `all`. A dictionary from `(name, tuple(new))` to a list of masters will do it. Why `tuple(new)` and not `new`? Chapter 64 has the answer.
3. Add the rule `"R_aacute": ("left", "a")` by way of a deliberate slip, run the script, and read the line it prints. Then take the rule out again.

## Next

`L_T` needs pairs, and Mira's `TO` from Thursday has needed one for a week. Chapter 73 writes to the kerning list: adding a pair, changing one, and taking one away.
