---
this_file: src_docs/md/part1-first-words/012-the-width-report.md
---

# 12. The width report

Friday, after lunch. Tomas has been patient since Monday. He asked for every glyph and its width, and what he got was this:

```text
.notdef None 500.0
A 65 596.0
Aacute 193 596.0
Abreve 258 596.0
Acircumflex 194 596.0
Adieresis 196 596.0
```

Two hundred lines of it. The numbers start wherever the name happens to stop, so the eye can't run down them. Every one has a `.0` on the end. He pasted it into his spreadsheet and wrote back one line: *Can the numbers be in a column?*

Mira knows how to lose the `.0` since this morning. The column is the last thing missing. It's also line 3 on Oskar's sheet: "Make a table of every glyph and its width." Today she crosses it out.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open, with 208 glyphs.
- What you learned about floats in [chapter 11](011-numbers-with-units.md). No saved script is needed.

## Step 1: Put a value inside a sentence

So far, when you wanted words and values on one line, you gave `print` several things with commas between them. Here's another way. Type this and run it:

```python
name = "A"
width = 596
print(f"{name} is {width} units wide")
```

```text
A is 596 units wide
```

Look at the string. It has an `f` in front of the opening quote, touching it, and it has two pairs of curly braces inside. That's called an f-string. The `f` stands for "formatted".

You know that quotes are a fence, and that Python doesn't read what's behind a fence. The curly braces are gates in that fence. Wherever Python finds a pair of them in an f-string, it reads what's between them as Python, works out the value and puts the value into the sentence at that spot. Everything outside the braces stays as you typed it.

The `f` is what opens the gates. Take it away and run the line again:

```python
print("{name} is {width} units wide")
```

```text
{name} is {width} units wide
```

No error. Without the `f`, it's an ordinary string, the braces are ordinary characters, and Python prints them. When you see curly braces in your output, look for the missing `f`.

Between the braces you can put more than a name. Anything that has a value will do:

```python
print(f"{name} with 4 more units is {width + 4}")
print(f"The name has {len(name)} character")
```

```text
A with 4 more units is 600
The name has 1 character
```

## Step 2: Say how the number should look

Now use a real width, which is a float:

```python
from fly import fl

font = fl.CurrentFont()
name = "A"
width = font["A"].width
print(f"{name} is {width} units wide")
```

```text
A is 596.0 units wide
```

The `.0` is back. This morning you'd have wrapped the width in `int`. An f-string has its own way. Inside the braces, after the value, you can put a colon and then a short note that says how to show it:

```python
print(f"{name} is {width:.0f} units wide")
```

```text
A is 596 units wide
```

Read `:.0f` in three pieces. The colon separates the value from the note. `.0` says "no decimals". The `f` at the end says "this is a float, show it as an ordinary decimal number". That last `f` has nothing to do with the `f` in front of the quote. It's an unlucky coincidence of letters.

Change the digit and you get that many decimals. Here's this morning's calculation, the *A* at 12 pt:

```python
print(f"{width / 1000 * 12:.1f} pt")
print(f"{width / 1000 * 12:.2f} pt")
```

```text
7.2 pt
7.15 pt
```

The untidy `7.151999999999999` never shows. The note rounds for you, the way `round` did. And as with `round`, the value in the box doesn't change. Only what's printed does.

## Step 3: Give each value a column

The same note can say how much room a value gets. Run this:

```python
name = "A"
width = 596
print(f"{name:<14}|")
print(f"{width:>6}|")
```

```text
A             |
   596|
```

The upright bars are there so you can see where each piece ends.

`:<14` says: give this value 14 characters of room and push it to the left. The name `A` takes one character, and Python fills the other thirteen with spaces. `:>6` says: six characters of room, pushed to the right. The number takes three, and three spaces go in front.

The arrow points to the side where the value goes. `<` points left, `>` points right. Names read best pushed left, the way a list of words does. Numbers read best pushed right, so that ones sit under ones and hundreds under hundreds. That's what Tomas means by a column.

You can combine room and decimals in one note. Room first, then the decimals:

```python
width = 596.0
print(f"{width:>6.0f}|")
```

```text
   596|
```

Six characters wide, pushed right, no decimals, a float.

Now make the mistake that everybody makes once. Give the name the note that was meant for the number:

```python
name = "A"
print(f"{name:>6.0f}")
```

```text
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ValueError: Unknown format code 'f' for object of type 'str'
```

Read the letter from the bottom. `ValueError` is new: the kind of thing was acceptable, the particular value wasn't. Here the complaint is about the note. A "format code" is the letter at its end, and `f` means float. Python is telling you that `name` holds a `str`, a string, and a string has no decimals to show. Take the `.0f` off the name's note and it runs. When you see this message, check which note you gave to which value.

## Step 4: Line up six glyphs

Put the two notes on one line and try them on the six glyphs from Tomas's ragged sample:

```python
from fly import fl

font = fl.CurrentFont()
for name in ["H", "O", "n", "o", "emdash", "quotesingle"]:
    glyph = font[name]
    print(f"{glyph.name:<8}{glyph.width:>6.0f}")
```

```text
H          672
O          708
n          523
o          520
emdash    1000
quotesingle   190
```

Nearly. Five rows line up and the sixth doesn't. The name `quotesingle` has eleven characters, and you gave the names eight characters of room. Python doesn't cut a value to make it fit. When the value is longer than its room, it takes what it needs and pushes everything after it to the right.

So the name column has to be at least as wide as the longest name in the font. In Plum, the longest names have 14 characters: `guillemotright` and `guilsinglright`. Give the names 16, which leaves two spaces of air:

```python
    print(f"{glyph.name:<16}{glyph.width:>6.0f}")
```

```text
H                  672
O                  708
n                  523
o                  520
emdash            1000
quotesingle        190
```

Run your eye down the numbers. The 1000 sticks out to the left by one digit, and the 190 shows at once as the smallest. A column lets you see things that a ragged list hides.

## Step 5: The whole font, with a header

Now all the glyphs, with a line on top that says what the columns are:

```python
from fly import fl

font = fl.CurrentFont()

print(f"{'Glyph':<16}{'Width':>6}")
print("-" * 22)
for glyph in font.glyphs:
    print(f"{glyph.name:<16}{glyph.width:>6.0f}")
print(f"{len(font)} glyphs")
```

Here's the top of the output:

```text
Glyph            Width
----------------------
.notdef            500
A                  596
Aacute             596
Abreve             596
Acircumflex        596
Adieresis          596
Agrave             596
Aring              596
```

It goes on for 208 rows and ends with the line `208 glyphs`.

Save it as `width_report.py` in your `scripting-book` folder.

Three details are new. In the header line, the values between the braces are strings typed on the spot: `'Glyph'` and `'Width'`. They're in single quotes because the f-string around them is already using double quotes, and Python needs to tell the inner fence from the outer one. The header gets the same notes as the rows, `<16` and `>6`, so the words sit exactly above their columns.

The second line uses the star on a string. You learned this morning that `*` multiplies numbers. A string times a number repeats the string: `"-" * 22` is 22 hyphens. Why 22? The two columns are 16 and 6 characters wide.

And the last line counts with `len(font)` from chapter 4, inside braces.

The table is in font order: `.notdef`, then the capitals with their accents. If Tomas would like it by name, you know how from [chapter 10](010-keep-a-list.md). Collect the names in a list, sort the list, then loop over the sorted names and look each glyph up with `font[name]`. That's exercise 2.

## Step 6: Send it

The table is in the Output panel. Click in the Output panel, select everything, copy, and paste it into a mail to Tomas.

One warning goes with it. The columns are made of spaces. They line up only in a typeface where every character has the same width, as in the Output panel. Pasted into a mail that's set in a proportional typeface, a typeface like Plum, the numbers wander again. A type designer doesn't need this explained. Tell Tomas to view it in a fixed-width typeface, or to split the lines at the spaces when he imports them. Writing a real spreadsheet file, one that opens with each value in its own cell, is the subject of chapter 28.

Mira sends it. The answer takes four minutes.

*That's it. Thank you. Can I have this for the Bold as well?*

That one has to wait. The script reads one set of widths, and asking for another weight comes in a later chapter. But the table she has sent took one run. A week ago it would have been an afternoon of clicking and typing.

Then she takes Oskar's sheet and draws a line through number 3. Three of eleven.

??? info "Going deeper: a column for a value that might be missing"
    You might want a third column with the Unicode number: `{glyph.unicode:>6}`. It stops at the first row with `TypeError: unsupported format string passed to NoneType.__format__`. The `.notdef` glyph has no Unicode value, so `glyph.unicode` is `None`, and `None` doesn't know what to do with a note about room. You need a way to say "if there's a number, show it, otherwise show something else". That's `else`, and it's in the next chapter.

## What you learned

An f-string is a string with an `f` in front, in which every pair of curly braces is replaced by the value of what's inside. After a colon, a note says how to show the value: `.0f` for a float without decimals, `<16` for sixteen characters of room pushed left, `>6` for six pushed right. Give every row the same notes, with the name column wider than the longest name, and the output is a table.

## Try it yourself

1. Add a third column to `width_report.py` that shows each width in points at 12 pt, with one decimal, in eight characters of room. The row for `H` should end in `8.1`. Give the header a third word.
2. Print the table sorted by name. Collect the names in a list first, then loop over `sorted(names)`.
3. Print the table only for glyphs wider than 800. You should get 11 rows, from `AE` at 852 to `at` at 848.

## Next

Chapter 13 joins tests together. "Wider than 700" is one question and "an uppercase letter" is another, and the proofreader wants the glyphs that answer yes to both.
