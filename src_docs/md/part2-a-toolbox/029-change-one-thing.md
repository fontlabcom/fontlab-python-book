---
this_file: src_docs/md/part2-a-toolbox/029-change-one-thing.md
---

# 29. Change one thing, and take it back

Wednesday. Ines has the first proofs from the publisher on her desk, and she's drawn a pencil line under one paragraph. *The word space is tight. Try twenty units more.*

Mira could do it by hand in ten seconds. Click `space`, type 250 where it says 230. But there are three masters, and next week Ines will say "try ten less", and the week after that it'll be the figures. This is a job for a script.

It's also a job she's been putting off. In four weeks, her scripts have counted, listed, looked up and written files. They've painted a mark on a cell. Not one of them has changed a shape or a width. Today's script will reach into real work and move something.

So before she lets a script do that, she wants an answer to one question. If it goes wrong, can she take it back?

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open. The practice copy, not the real font. That's what a practice copy is for.
- The Font window in front, with the `space` cell clicked so that `space` is the current glyph.
- The Regular master showing. If you aren't sure, look at the Layers & Masters panel.

Save the font before you start. A script that changes things should always begin from a saved font, the way a haircut should begin with a photo of what you had before.

## Step 1: Look before you touch

From chapter 5 on, you've met the font through `fl.CurrentFont()`. That's the plain view: names, numbers, widths. To change a glyph properly you need the richer view of it, the one that knows about masters and about the Edit menu. You met it briefly in chapter 8, when you asked a glyph whether it was empty. It's called `pGlyph`, and the book keeps it in a box named `rich`, for the rich view:

```python
from fly.tr.proxy.fl.objects.glyph import pGlyph

rich = pGlyph()
print(rich.name, rich.getAdvance())
```

```text
space 230
```

The import line is long, and it's a magic line. It says: inside Fly, in the part called `tr`, down four drawers, there's a thing named `pGlyph`. Copy it. You'll type it often enough in Part 3 that it'll stop looking strange.

`pGlyph()` with an empty slot means "the glyph I'm on right now". That's why you clicked `space` first. `getAdvance()` asks for the advance width, which is the full name of what you've been calling the width: how far the pen advances before the next glyph starts.

You've changed nothing yet. Good scripts that edit things open with a line like this one. If it had printed `A 596`, you'd know you had the wrong cell clicked, and you'd know it before anything moved.

## Step 2: A function you hand to someone else

Here's the idea the whole chapter rests on, and it has nothing to do with fonts. Type this plain Python:

```python
def say_hello():
    print("Hello")

def twice(job):
    job()
    job()

twice(say_hello)
```

```text
Hello
Hello
```

Read `twice` slowly. It takes one thing, which it calls `job`. Then it writes `job()` two times. Parentheses after a name mean "run this", as they have since chapter 2. So `twice` expects to be handed something it can run.

And look at the last line: `twice(say_hello)`. No parentheses after `say_hello`. You aren't running the function there. You're handing it over, the way you'd hand someone a recipe card. `twice` takes the card and cooks from it, twice, when it chooses to.

A function is a thing you can put in a box, like a number or a string. Print it and Python shows you the box's contents:

```python
print(say_hello)
```

```text
<function say_hello at 0x104f92480>
```

Your number at the end will differ. The point is that there's something there, and that it isn't the word Hello.

Now make the mistake. Add the parentheses:

```python
twice(say_hello())
```

```text
Hello
TypeError: 'NoneType' object is not callable
```

One Hello, then a complaint. Follow what happened. Python works from the inside out, so it ran `say_hello()` first. That printed Hello. `say_hello` has no `return` line, and you know from chapter 24 that a function with nothing to return hands back `None`. So `twice` was given `None`, tried to run it, and couldn't. "Not callable" means "you put parentheses after something that isn't a function."

Keep the two apart. `say_hello()` is the dish, cooked now. `say_hello` is the recipe card. When a function asks you for a job to do later, hand over the card.

## Step 3: Why anyone would want that

Why would a function want your recipe and not the dish? Because it wants to do something before your steps and something after them.

That's the situation with Undo. When you move a node by hand, FontLab remembers the glyph as it was, a snapshot, lets you make the move, and adds a line to its history. **Edit > Undo** puts the snapshot back. A script that changes a width directly skips both ends. No snapshot is taken and no line is written, so as far as I can tell from Fly's source there's nothing for Undo to undo.

Fly has a helper that does the two ends for you. You hand it your change as a function. It takes the snapshot, runs your function, and writes the line. The helper is called `commit`.

To commit, in plain English, is to stop saying "maybe" and make it official. A pencil sketch isn't committed. Ink is. In scripting, to commit a change is to hand it over as one sealed package: all of it happens, and it goes on the record under one name. You'll meet the word again if you ever use Git, where it means much the same.

## Step 4: Commit the change

Here's the script. Type it under your Step 1 lines and read it before you run it:

```python
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
from fly.tr.proxy.fl.objects.glyph import pGlyph

rich = pGlyph()
layer = rich.activeLayer()
print("Before:", rich.name, rich.getAdvance())

def widen():
    layer.advanceWidth += 20

package = scripting.current_package()
facts = history.scan_auto_facts(package)
history.commit("Widen", [layer], [rich.fl], widen, operation="geometry", facts=facts)

print("After:", rich.name, rich.getAdvance())
```

```text
Before: space 230
After: space 250
```

That's a lot of new lines at once, so take them in three groups.

**The thing to change.** `rich.activeLayer()` gives you the layer of this glyph that's showing now. A glyph in Plum is three drawings stacked up, one for each master, and the width lives on each drawing separately. With Regular showing, `layer` is the Regular drawing of `space`.

**The change itself.** `widen` is your recipe card, and it's one line long. `layer.advanceWidth += 20` is the `+=` from chapter 22: take what's in the drawer, add 20, put it back. Defining `widen` changes nothing. It's a card in a box until somebody runs it.

**The hand-over.** The `commit` line has six things in its slot. Here's what each is for.

- `"Widen"` is the title, the words that'll show in the Edit menu.
- `[layer]` is the list of layers your function will change. The helper needs it to take the right snapshot.
- `[rich.fl]` is the list of glyphs those layers belong to. The `.fl` is a part I'm not opening yet: it's the glyph in the form FontLab's history wants.
- `widen` is the recipe card. No parentheses.
- `operation="geometry"` says what kind of change this is. A width counts as geometry, along with outlines.
- `facts=facts` hands over what the line above collected. That line, with `package = scripting.current_package()` before it, is a magic line. `package` is Fly's word for the open font file as FontLab's history knows it. `scan_auto_facts` looks through the font for glyphs that FontLab builds automatically, because changing those by script is asking for trouble, and `commit` will refuse to.

The two lists look fussy for one glyph. They're lists because the next script will change sixty.

## Step 5: Take it back

Now the part Mira asked for. Open the **Edit** menu. The first item should read **Undo Widen**: your title, in FontLab's own menu, next to the things you've done by hand. Choose it, or press ++cmd+z++ on a Mac and ++ctrl+z++ on Windows. Then check:

```python
print(rich.getAdvance())
```

```text
230
```

Back where it was. And **Edit > Redo** puts the 250 back again.

One line in the menu is the point. Suppose `widen` had changed sixty glyphs in a loop. It would still be one line, and one Undo would take all sixty back. Without the helper you'd have sixty changes and nothing to undo them with.

Two limits, so you don't lean on Undo harder than it can bear. Undo lasts only while the font is open. Close the font and the history goes with it, which is why you saved first. And Undo covers the font, not the files your script wrote. Nothing will un-write last Friday's report.

## Step 6: When the helper says no

Leave something out on purpose. Delete `operation="geometry", ` from the commit line and run:

```text
TypeError: commit() missing 1 required keyword-only argument: 'operation'
```

"Keyword-only" means the helper insists you write the name and the equals sign, `operation=...`, and won't accept the value on its own. That's deliberate. A line that changes your font should say in words what it's doing.

Put it back, but misspell the kind:

```python
history.commit("Widen", [layer], [rich.fl], widen, operation="width", facts=facts)
```

```text
ValueError: Unknown operation 'width'; use one of ['geometry', 'metadata', 'rename', 'unicode'].
```

That's a helpful letter of complaint. It tells you the four words it knows. You'll use `"rename"` in the next chapter.

In both cases, check the width afterward. It's still 230 or 250, whichever it was. The helper checks everything it can before it takes the snapshot, and if it doesn't like what it sees, it stops without touching the font. A refusal starts with the word `Refused` and names the glyph and the reason. If you ever see `has auto layers` in one, you've pointed the script at a glyph that FontLab builds for you, and the answer is to leave that glyph alone.

There's one more refusal you may meet. If you run the script from a Glyph window on glyphs that the window isn't showing, the helper tells you to `Switch to the Font window first`. Do as it says. It knows about a case where FontLab would undo only part of the change.

## The whole script

Save this as `safe_edit.py`. The amount has a box of its own at the top, in capitals, because next week it'll be a different number:

```python
# Widens the current glyph on the current master by AMOUNT units.
# One step in Edit > Undo.
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
from fly.tr.proxy.fl.objects.glyph import pGlyph

AMOUNT = 20

rich = pGlyph()
layer = rich.activeLayer()
print("Before:", rich.name, rich.getAdvance())

def widen():
    layer.advanceWidth += AMOUNT

package = scripting.current_package()
facts = history.scan_auto_facts(package)
history.commit("Widen", [layer], [rich.fl], widen, operation="geometry", facts=facts)

print("After:", rich.name, rich.getAdvance())
```

Mira runs it on Regular, switches to Bold and runs it again, then Light. Bold goes from 230 to 250. Light goes from 234 to 254, which tells her something she hadn't noticed: the Light space was already a little wider. She prints a paragraph and puts it on Ines's desk next to the proof. Ines looks at both for a while and says, "Fifteen."

Mira changes one number at the top, presses Undo three times, and runs it again.

## What you learned

A function is a thing you can hand to another function, and you hand it over by name, without parentheses. Fly's `history.commit` takes your change as such a function, and runs it so that the whole change is one named step in **Edit > Undo**. It refuses before it touches anything if what you asked for looks unsafe. Print the value before and after, work on a saved font, and remember that Undo can't reach files on disk.

## Try it yourself

1. Change the title from `"Widen"` to `"Widen space by 20"` and run the script. What does the Edit menu show? Then set `AMOUNT = -20`. Is "Widen" still an honest title? Build the title from `AMOUNT` with an f-string so that it can't lie.
2. Write a `narrow` function next to `widen` that subtracts `AMOUNT`. Commit `widen`, then commit `narrow`. How many Undo steps are there now, and in what order do they come back?
3. Add a third line to `twice` from Step 2 so that it becomes `three_times`, and hand it a function of your own that prints the name of the current glyph. Then hand it `print`. What happens, and why is that not an error?

## Next

About sixty glyphs in the real Plum carry the old suffix `.alt`, and the publisher's files want `.ss01`. In chapter 30, a script renames them.
