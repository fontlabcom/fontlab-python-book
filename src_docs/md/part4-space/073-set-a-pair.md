---
this_file: src_docs/md/part4-space/073-set-a-pair.md
---

# 73. Set a pair

Wednesday of week fourteen. Two things have waited for this chapter.

The first is the `TO` of `TOAST`. Chapter 69 found that Plum never kerned it, and since yesterday there's a class, `L_T`, with no pairs to its name.

The second is new. Mira sets `AVOCADO` in the Bold and the `A` and the `V` have run into each other. Chapter 68 gave the Bold `A` 42 more units on its right, and it didn't help enough. Run `pair_value.py` on `A V`:

```text
A V
  Light      -69   through a class
  Regular    -55   through a class
  Bold       -69   through a class
```

The Bold has the Light's number, to the unit. Somebody copied the Light's kerning into the Bold years ago and never went through it. In the Regular the tips of the two letters end up 34 units into each other, which is what a diagonal next to a diagonal wants. In the Bold, the space between them is −2 before any kerning, and the pair takes away 69 more. Mira tries values in the Kerning panel until the Bold pair looks like the Regular one, and settles on −27.

She could leave it at that, with the number typed in the panel. Today you write it from a script, because by Friday there'll be many such numbers.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The helpers `ask` and `tell` from chapter 39. The scripts below write them out again, so each one runs by itself.
- The class `L_T` from chapter 72. Step 3 shows what happens without it.
- `pair_value.py` from chapter 70, to check the result.

I couldn't run the code in FontLab 9. The values that come back are worked out from Plum's source file, and the two refusals in step 3 are copied from the source of the function that makes them.

## Step 1: The shape of an order

The function that writes kerning is `write_kerning`, in Fly's kerning toolkit. It takes the package, a set of edits, and a name for the Undo step:

```python
import fly.ap.core.scripting as scripting
import fly.ap.kerning.batch as kerning_batch

package = scripting.current_package()
edits = {"Bold": {("A", "V"): -27}}
kerning_batch.write_kerning(package, edits, "Set kerning pairs")
```

Look at `edits` before you run anything. It's a dictionary with one key, a master's name. The value under that key is another dictionary, and that inner one has the shape you know from chapter 69: a pair as the key, a number as the value.

A dictionary inside a dictionary is new, and it reads the way it's written. `edits["Bold"]` is the inner dictionary, the orders for one master. `edits["Bold"][("A", "V")]` is one number. The outer level says where, and the inner level says what.

The whole batch goes in as one piece. `write_kerning` checks every order in it before it changes anything, makes all the changes as one Undo step, and gives back `True` if the font changed and `False` if every pair already had its value.

Now run it, and check with `pair_value.py`, this time on `A V Aacute V`:

```text
A V
  Light      -69   through a class
  Regular    -55   through a class
  Bold       -27   its own pair
Aacute V
  Light      -69   through a class
  Regular    -55   through a class
  Bold       -69   through a class
```

## Step 2: The pair that was too narrow

That's today's mistake, and the report shows it in two places.

"Its own pair", says the Bold line for `A V`. The script didn't change the pair that was there. It wrote a second one beside it, for the glyph `A` alone, and chapter 70 told you what happens then: a pair for the glyph wins over a pair for its class. So `AV` is mended.

`ÁV` isn't. Nor are `ÄV`, `ÅV` and the other four. They still go through the class pair, and the class pair still says −69. I asked for `("A", "V")` because that's what I saw on the page. The font keeps this kerning as `("@L_A", "V")`.

The mended `A` now hides the fault. Anyone who checks `AV` will see a good pair and move on. Before you write a pair, ask where the value comes from at present, and write to that place. Friday's script tells you: "through a class" means the order must name the class.

So the repair has two parts: take the narrow pair out again, and change the right one. An order with `None` for its value removes a pair:

```python
edits = {"Bold": {("A", "V"): None, ("@L_A", "V"): -27}}
kerning_batch.write_kerning(package, edits, "Set kerning pairs")
```

`None` and 0 are different orders. A pair with the value 0 is still a pair, and for a glyph it still overrides the class, with nothing. `None` means the pair is gone and the class speaks again.

Check once more, and both `A V` and `Aacute V` should read −27 in the Bold, through a class.

## Step 3: Two refusals

`write_kerning` won't write everything you hand it. Try a value with a half in it:

```python
edits = {"Bold": {("@L_A", "V"): -27.5}}
kerning_batch.write_kerning(package, edits, "Set kerning pairs")
```

The last line of the traceback should begin:

```text
ValueError: Kerning on Bold: @L_A V = -27.5 is not a whole number
```

and go on to say that no changes were applied. Kerning in this toolkit is whole units. If a value comes out of a sum, `round` it first, as chapter 68 did.

Then try a class the font doesn't have. If you skipped chapter 72, this is what the pair for `TO` gets you:

```text
ValueError: Unknown or wrong-side kerning class: L_T on Light
```

The same line appears when the class exists and stands in the wrong place, for instance `("@R_O2", "T")`: `R_O2` is a class for the second place, and the order puts it first. A glyph name the font doesn't have is refused as well, with `Unknown glyph`.

Both refusals come before anything is written. That's the use of handing over the batch in one piece: one bad order among many, and the font stays as it was.

## Step 4: Before and after

A script that changes many pairs should show a line for each first, with the old value beside the new. The old value is whatever chapter 69's dictionary has under the same key, or `None`:

```python
def text(value):
    return "none" if value is None else f"{value:.0f}"


pairs = scripting.kerning_pairs(package, "Bold")
old = pairs.get(("@L_A", "V"))
print(text(old), "to", text(-27))
```

```text
-69 to -27
```

`text` turns a value into something printable, with the word `none` for a pair that isn't there. It's needed twice in every line, for the old value and for the new, since a removal has `None` on the new side.

An order whose old and new values are equal isn't an order, and the plan leaves it out. That makes the script safe to run twice.

## The whole script

```python
#FLM: Set Pairs
# Adds, changes or removes the kerning pairs listed in EDITS,
# in one Undo step, after showing old and new values.
import fly.ap.core.scripting as scripting
import fly.ap.kerning.batch as kerning_batch
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"

MASTERS = ["Light", "Regular", "Bold"]
# master: {(first, second): value}. A class has @ in front. None removes a pair.
EDITS = {
    "Light": {("@L_T", "@R_O2"): -30},
    "Regular": {("@L_T", "@R_O2"): -20},
    "Bold": {("@L_T", "@R_O2"): -20, ("@L_A", "V"): -27},
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


def text(value):
    return "none" if value is None else f"{value:.0f}"


def plan(package):
    rows = []
    for master in MASTERS:
        pairs = scripting.kerning_pairs(package, master)
        for (first, second), new in EDITS.get(master, {}).items():
            old = pairs.get((first, second))
            if old != new:
                rows.append((master, first, second, old, new))
    return rows


def main():
    if fl.CurrentFont() is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    rows = plan(package)
    for master, first, second, old, new in rows:
        print(f"{master:<9}{first:<8}{second:<8}{text(old):>6} to {text(new):>5}")
    print(f"{len(rows)} pairs to write.")
    if not rows or not ask(f"Write {len(rows)} kerning pairs?"):
        return

    edits = {}
    for master, first, second, old, new in rows:
        if master not in edits:
            edits[master] = {}
        edits[master][(first, second)] = new
    try:
        kerning_batch.write_kerning(package, edits, "Set kerning pairs")
    except ValueError as problem:
        print(f"Refused, nothing written: {problem}")
        return
    print(f"Done. {len(plan(package))} pairs still to write.")


main()
```

Save it as `set_pair.py`. With step 2's repair already made, it prints:

```text
Light    @L_T    @R_O2     none to   -30
Regular  @L_T    @R_O2     none to   -20
Bold     @L_T    @R_O2     none to   -20
3 pairs to write.
```

The order for `@L_A V` is in `EDITS` and not in the plan, because the font already has −27 there. If you undid step 2, you'd see four lines, the fourth reading `-69 to   -27`.

Click Yes:

```text
Done. 0 pairs still to write.
```

Notes on the listing.

`EDITS.get(master, {})` is `get` with a default that fits: a master with no orders is a master with an empty set of orders, and the loop over an empty dictionary does nothing. It lets you leave a master out of `EDITS` altogether.

The plan compares `old != new` with a float on one side and a whole number on the other. Python counts `-27.0` and `-27` as equal, so a pair that already has its value drops out. `None` is equal only to `None`, so "no pair, and none wanted" drops out too.

The middle of `main` builds the dictionary of dictionaries from the rows. `if master not in edits:` makes the inner dictionary the first time a master turns up, which is the pattern chapter 64 used for a dictionary of lists. Sending only the rows of the plan, and not `EDITS` as it stands, means the font is asked to change what the reader was shown and nothing else.

The `try` and `except ValueError` are from chapter 19. `as problem` gives the error a name, so the next line can print its text. A refusal here is a message for the person at the desk, not a crash, so the script prints the reason in one line and stops.

## The value for TO

Where do −30, −20 and −20 come from? From looking. The space between `T` and `O` before kerning is 70 units in the Light, 34 in the Regular and 36 in the Bold. Mira set `HOTOH` and took space out until the `O` after the `T` sat as it does after the `H`. A script can carry a number into three masters and sixty glyphs. It can't tell you what the number should be.

The pair is written from class to class. `@L_T` holds `T` and `Ť`, and `@R_O2` holds `O` and its six relatives, so one line in each master covers fourteen combinations. Check two of them with `pair_value.py`, on `T O Tcaron Odieresis`. Both should say "through a class", with the same three values.

The `T`'s fourteen older pairs are still written for the glyph `T`, and `Ť` has no share in them. Moving them to the class is the second exercise.

## What you learned

`kerning_batch.write_kerning(package, edits, name)` takes a dictionary of dictionaries: a master's name, then pairs with their values. A number adds or changes a pair, and `None` removes it, which is different from setting it to 0. Find out where a value comes from before you change it: if it comes through a class, the order must name the class. Values are whole numbers, a class must exist and stand in the right place, and one bad order stops the whole batch before anything is written.

## Try it yourself

1. The Regular has a pair `("questiondown", "exclamdown")` with the value 11, the Bold has it at 28, and the Light doesn't have it. A pair in one master only is a hazard for every weight in between. Decide whether to give it to all three or to none, and write the order. Check with `pair_value.py`, then undo: later chapters count the pairs as they are.
2. Move the pair `T` before `o` to the class: for each master, remove `("T", "o")` and add `("@L_T", "o")` with the value the old pair had. Chapter 70 printed the three values. Write the six orders, read the plan, and run it. Then check `T o` and `Tcaron o`, and undo when you've seen them.
3. Put `("@L_A", "V"): -27.5` into `EDITS` beside a good order and run the script. Which line does it print, and how many pairs were written?

## Next

One pair is mended. How many others in the Bold are as deep as `AV` was, and which pairs carry the most weight in this font? Chapter 74 sorts the kerning list by the size of each value, whichever way it points, and sets the pairs against the space they act on.
