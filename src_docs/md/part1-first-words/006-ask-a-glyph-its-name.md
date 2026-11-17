---
this_file: src_docs/md/part1-first-words/006-ask-a-glyph-its-name.md
---

# 6. Ask a glyph its name

Friday. The publisher's spreadsheet person has a name now, Tomas, and Tomas has a follow-up.

*Thanks for first and last. Could I also get the Unicode value and the width of the capital A? I'm testing my import.*

Mira could open the glyph and read both numbers off the screen. She knows that. She also knows Tomas will ask about another glyph on Monday, and another after that.

Yesterday's script printed a glyph as `<fgGlyph 'tilde'>`: a tag on a closed door. Today you open the door.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `count.py` from [chapter 5](005-a-font-is-a-list-of-glyphs.md), for reference.

## Step 1: Take one glyph out by name

Yesterday you picked glyphs by position: `font[0]`, `font[glyph_count - 1]`. That's fine for first and last. It's no use for the A, unless you want to count cells in the Font window.

A font lets you ask by name too. Start a new script:

```python
from fly import fl

font = fl.CurrentFont()
glyph = font["A"]
print(glyph)
```

Run it.

```text
<fgGlyph 'A'>
```

Same square brackets, but with a piece of text between them where the number was. The quotes matter. `font[A]` without them would send Python looking for a box labeled `A`, and you know which error that gives.

The glyph is now in a box labeled `glyph`. Printing the box gives you the tag again. So far, nothing new.

## Step 2: Open a drawer

Change the last line:

```python
from fly import fl

font = fl.CurrentFont()
glyph = font["A"]
print(glyph.name)
```

```text
A
```

No tag this time. You got the name, as plain text.

The new thing is the dot. Here's the picture, and we'll keep it for the rest of the book. A glyph is a wardrobe with labeled drawers. One drawer is labeled `name`, and the glyph's name is in it. Another is labeled `width`. The dot means "open this drawer": `glyph.name` is the `name` drawer of whatever is in the `glyph` box.

A thing with drawers is called an **object**. The font is an object. Each glyph is an object. A number like 205 is too plain to need drawers, but nearly everything FontLab hands you has them.

You've been writing dots since chapter 4. `fl.CurrentFont()` is a dot: `fl` is a wardrobe, and `CurrentFont` is one of its drawers.

Why does that one end in parentheses when `glyph.name` doesn't? Because the two drawers hold different kinds of thing. The `name` drawer holds a value, and you take it out. The `CurrentFont` drawer holds a function, and a function does nothing until you push something through its slot. Even when you have nothing to push, the empty parentheses are what make it go.

Leave them off and see what you get. Change the last line to this:

```python
print(fl.CurrentFont)
```

No error. Python prints a tag in angle brackets, like the one you got for a glyph. That's the function itself, sitting in its drawer, not doing its job. If one of your scripts ever prints a tag where you expected an answer, look for missing parentheses. Put the line back the way it was.

## Step 3: Answer Tomas

Two more drawers.

```python
from fly import fl

font = fl.CurrentFont()
glyph = font["A"]
print("Name:", glyph.name)
print("Unicode:", glyph.unicode)
print("Width:", glyph.width)
```

```text
Name: A
Unicode: 65
Width: 596.0
```

Both numbers need a word.

**Unicode: 65.** In chapter 1 we kept glyph and character apart. The glyph is the drawing. The character is the thing a person types. Unicode is the worldwide list that gives every character a number, and a font connects each glyph to the number of the character it draws. Capital A is number 65.

If you look at the glyph in FontLab, you'll see `0041` where the script says 65. They're the same number. FontLab writes it the way Unicode charts do, in a counting system with sixteen digits, and Python writes it the way you'd count on your fingers. Chapter 23 sorts this out. Until then, there's a function that translates:

```python
print(hex(65))
```

```text
0x41
```

Ignore the `0x` in front. That's Python's way of saying "sixteen-digit number coming up".

**Width: 596.0.** This is the glyph's **advance width**: how far the cursor moves when somebody types an A. It's the drawing plus the space on its left and right. The unit is the **font unit**. Plum is drawn on a grid 1,000 units tall, so an A that's 596 wide is a bit more than half as wide as the grid is tall.

Plum comes in three weights, and the A is 596 wide in Regular and Bold and 554 in Light. If you get 554, you're looking at the Light. Part 6 is about weights. Until then, stay on Regular.

The `.0` is Python telling you this number is allowed to have a fractional part, even though this one doesn't use it. Chapter 11 is about that.

Mira sends Tomas three lines. He replies with a thumbs-up and, as predicted, a second glyph.

## Step 4: Change one word, ask again

Tomas wants the `n` now. Change one line:

```python
glyph = font["n"]
```

```text
Name: n
Unicode: 110
Width: 523.0
```

One word changed, three correct answers. Try `space`. Try `tilde`.

Then try the very first glyph, the one called `.notdef`:

```text
Name: .notdef
Unicode: None
Width: 500.0
```

There's `None` again, the "nothing here" value from yesterday. It isn't an error this time. `.notdef` is the glyph a font shows when somebody types a character the font doesn't have. No character belongs to it, so its `unicode` drawer is empty, and Python says so.

Now put two glyphs side by side. Mira does this by eye a hundred times a day: is the `n` wider than the `o`, and by how much? With two boxes the script can say.

```python
from fly import fl

font = fl.CurrentFont()
n_width = font["n"].width
o_width = font["o"].width
print("n:", n_width)
print("o:", o_width)
print("Difference:", n_width - o_width)
```

```text
n: 523.0
o: 520.0
Difference: 3.0
```

Look at `font["n"].width`. That's two steps on one line, read from left to right: take the `n` out of the font, then open its `width` drawer. You don't have to put the glyph in a box of its own first. When you only want one thing from it, you can reach straight through.

Three units. Mira would have guessed more. The round `o` looks narrower than the `n` on screen, and in Plum it nearly isn't. That's the kind of thing a script is good for: it doesn't replace your eye, but it tells you when your eye is guessing.

Some glyphs draw more than one character. For those there's a second drawer, `unicodes` with an s, which holds a list.

```python
glyph = font["A"]
print(glyph.unicodes)
```

For the A that prints `[65]`: a list with one thing in it. You know lists from yesterday.

## Step 5: Ask for a glyph that isn't there

Tomas's third request is the small-cap A. Glyph names for small caps usually end in `.sc`, so:

```python
from fly import fl

font = fl.CurrentFont()
glyph = font["a.sc"]
print("Name:", glyph.name)
```

Run it.

```text
AttributeError: 'NoneType' object has no attribute 'name'
```

That's the last line of the message. From here on I'll often show only that line, because it's the one to read first. **Attribute** is Python's word for a drawer. So: something called `NoneType` has no drawer called `name`.

You saw `NoneType` yesterday, and the rule from yesterday holds. Look back up the script for the place where you asked for something and didn't get it. It's the line above. Plum has no small caps yet. You asked the font for `a.sc`, there was no such glyph, and the font handed back `None`. Then the last line tried to open a drawer on nothing.

This is the error you'll meet more than any other in this book. You'll get it from a typo in a glyph name. You'll get it from a wrong capital, because `font["a"]` and `font["A"]` are two different glyphs. Whenever you see `'NoneType' object has no attribute`, the fault is almost never in the line Python points at. Something a little earlier came back empty.

Put `"A"` back.

## Step 6: The glyph in front of you

Typing a name into the script is one way to choose a glyph. Here's another. In the Font window, double-click the `o` so that it opens in the Glyph window. Then run this:

```python
from fly import fl

glyph = fl.CurrentGlyph()
print("Name:", glyph.name)
print("Unicode:", glyph.unicode)
print("Width:", glyph.width)
```

```text
Name: o
Unicode: 111
Width: 520.0
```

`fl.CurrentGlyph()` is the cousin of `fl.CurrentFont()`. It asks FontLab which glyph you're working on and hands it back. There's no name in the script at all now. Go to another glyph, run the script, and it reports on that one.

Save this as `this_glyph.py`. It's the first script in this book that you can use without editing it: go to a glyph, run, read.

If you run it with no glyph open, you'll get the `NoneType` message from step 5, for the same reason.

??? info "Going deeper: two kinds of glyph object"
    The glyph you get from `fl.CurrentGlyph()` or `font["A"]` is the one FontLab's storage keeps. It's called `fgGlyph`, and it's good for reading names, Unicode values and widths. FontLab has a second, richer glyph object for work on layers and outlines. The friendly tools in the bag hand you that one when a chore needs it, starting in chapter 8.

## What you learned

An object is a wardrobe with labeled drawers, and a dot opens a drawer: `glyph.name`, `glyph.unicode`, `glyph.width`. You can take a glyph out of a font by name with `font["A"]`, or ask FontLab for the one you're working on with `fl.CurrentGlyph()`. When either comes back as `None`, the next dot fails with `'NoneType' object has no attribute`, and the cause sits a line or two above.

## Try it yourself

1. Use `this_glyph.py` to find the widest of these in Regular: `m`, `w`, `M`, `W`. Write the four widths down. You'll check them against a script in chapter 12.
2. Add a line to `this_glyph.py` that prints the Unicode value the way FontLab shows it, using `hex`. Test it on `A` and on `space`.
3. Change `font["A"]` to `font["a"]` in the script from step 3 and run it. Then try `font["Å"]`. One of these works and one doesn't. Find the name Plum uses for that glyph by looking at its cell in the Font window.

## Next

Chapter 7 stops asking one glyph at a time and puts the same three questions to all 205.
