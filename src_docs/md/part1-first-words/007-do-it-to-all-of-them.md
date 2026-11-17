---
this_file: src_docs/md/part1-first-words/007-do-it-to-all-of-them.md
---

# 7. Do it to all of them

Monday of the second week. Tomas has stopped asking for one glyph at a time.

*Can I have all of them? Name, Unicode, width. Whenever suits.*

Mira does the sum. `this_glyph.py` takes about ten seconds a glyph if she's quick with the mouse. Two hundred and five glyphs. Half an hour of clicking, and she'd lose her place twice.

She messages Oskar. The reply comes from what looks like a train.

*Don't click. Loop. Line 3 of my sheet has wanted doing for a year.*

Line 3 of the sheet says: *Make a table of every glyph and its width.*

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `this_glyph.py` from [chapter 6](006-ask-a-glyph-its-name.md).

## Step 1: Say it once, run it three times

Start with the small list from chapter 5. Type this, and when you get to the second line, press ++tab++ once before `print`:

```python
for name in ["A", "B", "C"]:
    print(name)
```

Run it.

```text
A
B
C
```

One `print` in the script, three lines in the Output panel.

Here's what Python did. It took the first thing in the list, `"A"`, and put it in a box labeled `name`. Then it ran the pushed-in line, which printed what's in the box. Then it went back up, put `"B"` in the same box, and ran the pushed-in line again. Then `"C"`. Then the list ran out, and Python stopped.

This is called a **loop**, and it's the reason scripting pays. You describe the job once. The computer does it for every item, in order, and doesn't lose its place.

Read the first line as a sentence: *for* each *name* *in* this list, do what follows. `for` and `in` are Python's words and you can't change them. `name` is a label, and labels are yours. The loop would work the same with `x` or `banana` there. Pick a word that says what one item is.

## Step 2: The colon and the push

Two small things on those two lines carry the whole meaning: the colon at the end of the first, and the space at the start of the second. Take each away in turn.

First the colon. Delete it and run.

```text
    for name in ["A", "B", "C"]
                               ^
SyntaxError: expected ':'
```

That's about as plain as Python gets. The little arrow points at the spot. The colon says "a block of lines belongs to this one, and here it comes". Put it back.

Now the push. Delete the space in front of `print` so both lines start at the left edge, and run.

```text
    print(name)
    ^^^^^
IndentationError: expected an indented block after 'for' statement on line 1
```

**Indentation** is the word for that space at the start of a line. In most writing it's a matter of taste. In Python it's grammar. The pushed-in lines are the ones the loop repeats. A line that isn't pushed in isn't in the loop, and a loop with nothing in it makes no sense, so Python stops.

The custom is four spaces. The Scripting panel puts them in for you when you press ++tab++, and after a line that ends in a colon it pushes the next line in on its own. To come back out, press ++backspace++ at the start of the line.

## Step 3: What's inside and what's outside

A loop can repeat more than one line. Everything pushed in by the same amount belongs to it.

```python
for name in ["A", "B", "C"]:
    print("Glyph:", name)
    print("Done")
```

```text
Glyph: A
Done
Glyph: B
Done
Glyph: C
Done
```

Three times "Done" is probably not what the writer meant. Pull the last line back to the left edge:

```python
for name in ["A", "B", "C"]:
    print("Glyph:", name)
print("Done")
```

```text
Glyph: A
Glyph: B
Glyph: C
Done
```

Same words, different script. The only thing that changed is four spaces. When a loop does something too often, or only once when you wanted it every time, look at the left edge of your lines before you look at anything else.

The spaces have to line up exactly, too. If one line in the block is pushed in by four and another by two, Python complains that the indentation "does not match", and it's right.

## Step 4: Every glyph in the font

Now the real list. In chapter 5 I said a font is a list of glyphs. A font object keeps that list in a drawer called `glyphs`.

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    print(glyph.name)
```

Run it and watch the Output panel.

```text
.notdef
A
Aacute
Abreve
Acircumflex
Adieresis
```

It goes on for 205 lines and ends with `grave`, `ring`, `tilde`. That's every glyph in Plum, in the order of the Font window, and it took less time than reading this sentence.

Go through the loop line the way you did in step 1. For each glyph in the font's list of glyphs: put it in a box labeled `glyph`, then run the pushed-in line. The first time around, `glyph` holds `.notdef`. The second time it holds `A`. Inside the loop you never say which glyph you mean. You say `glyph`, and the loop sees to it that the box holds the right one.

That's why the body of the loop can be the body of `this_glyph.py`, unchanged. Everything you learned to ask one glyph on Friday, you can now ask all of them.

Save this as `list_names.py`.

## Step 5: Tomas's table

Three questions, one line per glyph. Put the three answers into one `print`, separated by commas:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    print(glyph.name, glyph.unicode, glyph.width)
```

```text
.notdef None 500.0
A 65 596.0
Aacute 193 596.0
Abreve 258 596.0
Acircumflex 194 596.0
Adieresis 196 596.0
```

And so on to the end:

```text
grave 96 500.0
ring 730 500.0
tilde 732 500.0
```

There's the `None` for `.notdef` at the top, where you'd expect it from chapter 6.

Click in the Output panel, select everything, copy, and paste it into a message. Mira does. Tomas pastes it into his spreadsheet and writes back that the columns don't line up and the widths have a `.0` he doesn't want. He's right on both counts. Chapters 11 and 12 fix them, and then line 3 of Oskar's sheet gets crossed out properly. For now Tomas has his numbers.

## A list of your own

The loop doesn't care where its list comes from. The font's list has 205 glyphs in it. You can write a shorter one yourself.

Type designers have glyphs they look at before any others. For Latin it's often `H`, `O`, `n` and `o`: a straight capital, a round capital, a straight lowercase and a round lowercase. If those four sit well together, the rest of the alphabet has something to follow. Mira checks them every morning.

```python
from fly import fl

font = fl.CurrentFont()
for name in ["H", "O", "n", "o"]:
    glyph = font[name]
    print(name, glyph.width)
```

```text
H 672.0
O 708.0
n 523.0
o 520.0
```

This loop walks through four pieces of text, not through glyphs. So the first pushed-in line does what you did by hand in chapter 6: it uses the name to take the glyph out of the font. The second line prints. Two lines in the block, both run four times.

Notice the two kinds of square brackets, because they'll keep turning up together. The ones in the `for` line *make* a list. The ones in `font[name]` *pick from* a list. And `name` has no quotes in `font[name]`, because it's a box this time. The quotes are already inside it.

Change the four names to the glyphs you check first in your own work. If you mistype one, you'll get the `NoneType` message from chapter 6, and it'll arrive partway through the output, after the names that were spelled right. That tells you which name to look at: the one after the last line that printed.

## Step 6: Count as you go

One more thing a loop is good for. Suppose you want to know how many times it went around. Make a box before the loop, and add to it inside:

```python
from fly import fl

font = fl.CurrentFont()
count = 0
for glyph in font.glyphs:
    count = count + 1
print("Counted", count, "glyphs")
```

```text
Counted 205 glyphs
```

You know this move from chapter 5's `glyph_count = glyph_count + 4`: open the box, add one, put it back. Here it runs once per glyph. The last line sits at the left edge, so it runs once, after the loop has finished.

Yes, `len(font)` gives you 205 without the trouble. But this version can do something `len` can't. Tomorrow you'll add one line so that it counts only the glyphs you care about, and that's line 2 of Oskar's sheet.

Try the mistake that everybody makes once. Push the `print` line in by four spaces and run it. You get 205 lines, counting up from 1. Nothing's broken. The line moved inside the loop, so it runs every time around. Pull it back out.

??? info "Going deeper: the font itself as a list"
    You can count a font with `len(font)` and pick from it with `font[0]`, so you might expect `for glyph in font:` to work as well. It may; I haven't tried it. Use `font.glyphs` in a loop. It's the form the tools in the bag use themselves, and it says what you mean.

## What you learned

A `for` loop takes the things in a list one at a time, puts each in a box you name, and runs the indented lines below it once for each. The colon opens the block and the indentation marks what's in it, so four spaces decide whether a line runs 205 times or once. With `for glyph in font.glyphs:` every question you can ask one glyph becomes a question you can ask the whole font.

## Try it yourself

1. Change `list_names.py` so that each line shows the glyph's width first and its name second.
2. A piece of text is a row of characters, so a loop can walk through it. Run this, then put a glyph name from Plum in place of `"Plum"`:

    ```python
    for letter in "Plum":
        print(letter)
    ```

3. Before the loop in step 6, make a second box called `total` and set it to 0. Inside the loop, add each glyph's width to it. After the loop, print it. You've measured how wide a line would be if somebody typed every glyph in the font once. With the Regular master showing, `Plum-practice` gives 102107.0.

## Next

Chapter 8 teaches the loop to be choosy: do something for a glyph only if it passes a test.
