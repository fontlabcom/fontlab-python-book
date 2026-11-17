---
this_file: src_docs/md/part1-first-words/005-a-font-is-a-list-of-glyphs.md
---

# 5. A font is a list of glyphs

Thursday. Ines stops at Mira's desk with a coffee in each hand.

"The publisher wants to know what's first and what's last in the font. Don't ask me why. Somebody there has a spreadsheet."

Mira opens `count.py`. Four lines. She ran them yesterday and they worked, and she still can't say what the third one does.

```python
from fly import fl

font = fl.CurrentFont()
print("This font has", len(font), "glyphs")
```

So today we take those four lines apart. By the end you'll have answered the publisher's question, and you'll have the one idea that the rest of this book stands on.

## What you need

- FontLab 9 with Fly installed, from [chapter 4](004-pack-the-toolbag.md).
- `Plum-practice` open, and your `count.py`.

## Step 1: Put a number in a box

Start a new script. Leave FontLab's words out of it for a minute and type this:

```python
glyph_count = 205
print(glyph_count)
```

Run it.

```text
205
```

Look at the second line. There are no quotes around `glyph_count`, so Python doesn't print the word. It prints what the word stands for.

Here's the picture I use. The first line takes the value `205`, puts it in a box, and sticks a label on the box that says `glyph_count`. From then on, whenever Python meets that label, it opens the box and uses what's inside.

The box with its label is called a **variable**. The `=` sign does the putting, and it works from right to left: the value on the right goes into the box named on the left. It doesn't mean "equals" the way it does in arithmetic. Read it as "becomes" and you won't go wrong.

You choose the label. A few rules come with that freedom. A label has no spaces, so people write an underscore where the space would go. It can't start with a digit. And capitals count, as they did in chapter 3: `glyph_count` and `Glyph_count` are two different boxes.

Now use the box for something.

```python
glyph_count = 205
masters = 3
print(glyph_count * masters)
```

```text
615
```

In chapter 2 you got that 615 by typing `205 * 3`. The answer hasn't changed. What's changed is that the script now says what the numbers are. Come back to it in a month and `glyph_count * masters` still makes sense. `205 * 3` won't.

## Step 2: Ask for a box that isn't there

Delete the first line, so the script is this:

```python
masters = 3
print(glyph_count * masters)
```

Run it.

```text
NameError: name 'glyph_count' is not defined
```

You met `NameError` in chapter 3, when Python didn't know `Print`. It's the same complaint here. Python went looking for a box labeled `glyph_count` and nobody had made one.

!!! tip "If it ran without an error"
    FontLab can remember boxes from the script you ran a minute ago. If you got 615 again, open the Scripting panel's menu, choose **Clear Python Context**, and run the script once more. It's a good habit when a script behaves as if it knows something it shouldn't.

The order matters. Python reads your script from the top, one line at a time, and a box exists only after the line that fills it has run. Put the line back.

One more thing a box can do: take a new value.

```python
glyph_count = 205
glyph_count = glyph_count + 4
print(glyph_count)
```

```text
209
```

The middle line looks like nonsense if you read `=` as "equals". Read it right to left. Python opens the box, finds 205, adds 4, and puts 209 back in the same box. The old value is gone.

## Step 3: Put a font in a box

Now go back to line 3 of `count.py`.

```python
font = fl.CurrentFont()
```

Right to left again. `fl.CurrentFont()` asks FontLab a question: which font is the person working on right now? FontLab hands back the font, and `=` puts it in a box labeled `font`.

So a box doesn't have to hold a number or a piece of text. It can hold a whole font. It's still a box with a label, and the next line can use the label.

Why bother with the box? Because without it you'd ask FontLab the same question on every line. You can call the box anything you like. `font` is what most people call it, and when I'm in a hurry I call it `f`. Stay with `font` for now, since it says what's inside.

The current font is the one in the Font window you clicked last. If you've got two fonts open, click the one you mean before you run the script.

## Step 4: Count without a font

Before we count the font, try `len` on something smaller. Start a new script:

```python
names = ["A", "B", "C"]
print(len(names))
```

```text
3
```

The square brackets make a **list**: several values in a row, separated by commas, kept in order. This one holds three pieces of text. `len` is short for length. Hand it a list and it tells you how many things are in it.

`len` is a function, like `print`. It has the same slot for you to push something through. The difference is what comes out. `print` writes to the Output panel. `len` hands a number back to your script, and what you do with that number is up to you. You can print it, put it in a box, or multiply it by three.

Not everything has a length. Try this:

```python
print(len(205))
```

```text
TypeError: object of type 'int' has no len()
```

`int` is Python's word for a whole number. A number isn't a row of things, so Python refuses to count it.

## Step 5: A font is a list of glyphs

Here's line 4 of `count.py` again, split in two so you can see the box:

```python
from fly import fl

font = fl.CurrentFont()
glyph_count = len(font)
print("This font has", glyph_count, "glyphs")
```

```text
This font has 205 glyphs
```

`len` worked on the font. That tells you something. A number has no length, but a font does, because to Python a font is a row of things kept in order. The things are glyphs.

That's the idea the title names. A font is a list of glyphs. Nearly every chore on Oskar's sheet comes down to going through that list and doing something with each glyph. Later you'll find lists inside the glyphs too. Once you can handle one list, you can handle them all.

Now for the publisher. Go back to the small list first, because it's easier to see what's going on.

```python
names = ["A", "B", "C"]
print(names[0])
print(names[2])
```

```text
A
C
```

Square brackets after a list mean "give me the one at this position". And Python starts counting at zero. The first thing in a list is at position 0, the second at position 1. I won't defend this. Every programmer trips over it for a week and then stops noticing.

It has one consequence you need today. A list of three things has positions 0, 1 and 2. There's no position 3.

```python
print(names[3])
```

```text
IndexError: list index out of range
```

**Index** is the word for the position number. The last thing in a list is always at the length minus one.

So, for the font:

```python
from fly import fl

font = fl.CurrentFont()
glyph_count = len(font)
first = font[0]
last = font[glyph_count - 1]
print("Glyphs:", glyph_count)
print("First:", first)
print("Last:", last)
```

Run it.

```text
Glyphs: 205
First: <fgGlyph '.notdef'>
Last: <fgGlyph 'tilde'>
```

Look at the top-left cell of the Font window, then scroll to the very last cell. The names match.

The odd wrapping, `<fgGlyph '...'>`, is what you get when you print a whole glyph. `first` isn't a piece of text. It's the glyph itself, with its drawing and its width and everything else, and all of that can't go on one line. So Python prints a short tag: the kind of thing it is, and its name. `fgGlyph` is the name FontLab's storage uses for a glyph. Tomorrow you'll reach inside and take out the name on its own.

Notice that I didn't type 204 for the last position. I wrote `glyph_count - 1` and let the script work it out. Tomorrow somebody adds a glyph to the font, and the script is still right.

Save it over `count.py`.

Mira copies the three lines into a message to Ines. Ines forwards them to the publisher without comment, which at Halfmoon counts as praise.

## Step 6: When there's no font

One last experiment. Save `Plum-practice` and close its window, along with any other font you have open, so that FontLab has no font at all. Run `count.py`.

```text
TypeError: object of type 'NoneType' has no len()
```

You saw this shape of message a few minutes ago, with `'int'` in it. This time the thing without a length is a `NoneType`.

Here's what happened. Line 3 asked FontLab for the current font. There wasn't one. FontLab didn't complain. It handed back a special value called `None`, which is Python's way of saying "nothing here". The box labeled `font` got `None` in it, and the script carried on. It was line 4 that fell over, when `len` tried to count nothing.

So the error is on line 4, and the cause is on line 3. That happens a lot, and it's worth remembering the pattern: when a message mentions `NoneType`, look back up the script for the place where you asked for something and didn't get it.

Open `Plum-practice` again. In chapter 19 you'll teach your scripts to check for `None` themselves and say something kinder.

## What you learned

A variable is a labeled box: `=` puts the value on the right into the box named on the left, and the label then stands for whatever's inside. A list keeps things in order, `len` counts them, and square brackets pick one by position, starting at zero. To Python, a font is a list of glyphs, so the same two tools tell you how many glyphs a font has and which one sits where.

## Try it yourself

1. Add two lines to `count.py` that print the second glyph in the font and the one before the last. Check both against the Font window.
2. Make a list of the names of five glyphs you'd put in a test word, and print its length, its first item and its last item. Use `len` for the last one, not a number you counted yourself.
3. In the `names` script, change `names[0]` to `names[1.5]` and run it. Read the message from the bottom. What does Python want between the brackets? Two words in the message are new; the first half is enough.

## Next

Chapter 6 opens up one glyph and asks it questions: its name, its Unicode value, its width.
