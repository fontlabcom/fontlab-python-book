---
this_file: src_docs/md/part1-first-words/011-numbers-with-units.md
---

# 11. Numbers with units

Friday morning. Tomas, the publisher's spreadsheet person, is on the phone. He's laying out a sample page and wants to know how much room a line of Plum takes.

"How wide is the n?"

Mira has the answer in the Output panel. "Five hundred and twenty-three."

"Five hundred and twenty-three what? Millimeters? Points?"

She looks at the number. `523.0`. It has a decimal point and a zero that nobody asked for, and no unit at all.

"I'll call you back," says Mira.

Two things are wrong with that number, and this chapter fixes both. The `.0` is about how Python keeps numbers. The missing unit is about how a font keeps sizes. After today a width means something you can say on the phone.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- Nothing saved from earlier chapters. You'll use `font["n"]` from [chapter 6](006-ask-a-glyph-its-name.md) and the loop over a string from the exercises of [chapter 7](007-do-it-to-all-of-them.md).

## Step 1: Two kinds of number

Start without the font. Type this and run it:

```python
print(523)
print(523.0)
print(7 / 2)
print(8 / 2)
print(3 * 4)
```

```text
523
523.0
3.5
4.0
12
```

Python keeps two kinds of number. A whole number, written without a decimal point, is called an integer, or `int` for short. A number with a decimal point is called a float. `523` is an int. `523.0` is a float. They're worth the same, and Python still treats them as two kinds of thing, the way a designer treats a 12 pt rule and a 12 pt gap as two kinds of thing.

The last three lines show the arithmetic signs you haven't met. You know `+` and `-`. The star `*` multiplies, because the keyboard has no multiplication cross. The slash `/` divides.

Look at `8 / 2`. The answer is 4, and Python prints `4.0`. Division always hands back a float, even when it comes out even, because most divisions don't. Multiplying two ints gives an int. One float anywhere in a sum is enough to put a decimal point on the result.

That's where Mira's `.0` comes from. FontLab keeps every width as a float, so that a width of 523.5 would be possible. Plum's widths are all whole, and Python shows the decimal point anyway to tell you which kind of number it is holding.

One rule about order, the same one you learned at school:

```python
print(2 + 3 * 4)
print((2 + 3) * 4)
```

```text
14
20
```

Multiplying and dividing happen before adding and subtracting. Parentheses go first of all. When you're not sure, add parentheses. They cost nothing and they show the reader what you meant.

## Step 2: Ask the font for its unit

Now Tomas's question. 523 what?

A font has no millimeters in it. A typeface can be printed at 9 pt or painted two meters high, and the drawing is the same drawing. So a font measures everything on a grid of its own. The grid divides the height of the type size, which typographers call the em, into a fixed number of steps. Every width, every point of every outline, every sidebearing is counted in those steps. They're called font units.

How many steps make one em is the font's decision. Ask it:

```python
from fly import fl

font = fl.CurrentFont()
print(font.info.unitsPerEm)
```

```text
1000
```

Two dots again, like `glyph.name.endswith` in chapter 9. `font.info` opens a drawer of the font that holds the facts about the font as a whole: its names, its measurements. Inside that drawer, `unitsPerEm` is the number of units in one em. You'll hear it called UPM. You can see the same number in FontLab under **File > Font Info**.

Plum's em has 1000 units. So the answer for Tomas is: the *n* is 523 units wide, and there are 1000 units to the em. Put the other way, the *n* takes 523 thousandths of the type size, a little more than half.

That's the reason the widths in a font look like they do. A width of 523 isn't large or small. It's a share.

## Step 3: Turn units into points

Tomas sets his sample in 12 pt. At 12 pt, the em is 12 points high, and those 12 points are divided into 1000 units. To get from units to points, divide by the UPM and multiply by the size:

```python
from fly import fl

font = fl.CurrentFont()
upm = font.info.unitsPerEm
print(font["n"].width / upm * 12)
```

```text
6.276
```

The *n* is 6.276 points wide at 12 pt. Python worked from left to right: 523.0 divided by 1000 is 0.523, and 0.523 times 12 is 6.276.

Before you go on, break it. Suppose you'd typed the UPM in by hand, and out of habit put quotes around it:

```python
from fly import fl

font = fl.CurrentFont()
upm = "1000"
print(font["n"].width / upm * 12)
```

```text
Traceback (most recent call last):
  File "<string>", line 5, in <module>
TypeError: unsupported operand type(s) for /: 'float' and 'str'
```

Read the last line. `TypeError` you met in [chapter 3](003-break-it-on-purpose.md): the wrong kind of thing. An operand is one of the two things on either side of a sign. So the letter says: I can't divide a float by a string. Inside the quotes, `"1000"` is four characters behind a fence, and you can't do sums with characters. Take the quotes away, or better, go back to asking the font. Then the script is still right when you open a font with 2048 units to the em.

Now try the capital *A*. Change `"n"` to `"A"`:

```text
7.151999999999999
```

Do it on paper and you get 7.152. Python is off by a hair in the fifteenth decimal place. Nothing is broken. A float is kept in a fixed amount of room, and some decimal fractions don't fit exactly, the way one third doesn't fit into any number of decimal places. The float holds the nearest value it can.

For a type designer, an error that small doesn't matter. What matters is that you don't hand Tomas a number with fifteen decimals.

## Step 4: Tidy the number

Python has two words for tidying a number. Try them next to each other:

```python
print(int(6.276))
print(int(6.9))
print(round(6.276))
print(round(6.9))
```

```text
6
6
6
7
```

`int` cuts the decimals off. It doesn't care what they were: 6.9 becomes 6. `round` goes to the nearest whole number: 6.9 becomes 7. Both hand back an int, without a decimal point.

`round` has a second slot. Pass a second number and it keeps that many decimals:

```python
print(round(6.276, 1))
print(round(6.276, 2))
print(round(7.151999999999999, 2))
```

```text
6.3
6.28
7.15
```

Two things go through the slot, with a comma between them: the number, and how many decimals to keep. The untidy 7.151999999999999 comes out as 7.15.

Which of the two do you use? When the number is whole already and only looks like a float, use `int`. It says "this is a count of units, show it as one". When the number has real decimals, use `round`, and decide how many decimals the reader needs. For a size in points, one is plenty.

Neither word changes the number you gave it. `round` hands back a new, tidy number. A number you keep in a box stays as exact as it was. So calculate with the exact number and round at the last moment, when you print.

## Step 5: Print widths without the .0

Here are four glyphs from chapter 7's table, with the widths tidied:

```python
from fly import fl

font = fl.CurrentFont()
for name in ["H", "O", "n", "o"]:
    glyph = font[name]
    print(name, int(glyph.width))
```

```text
H 672
O 708
n 523
o 520
```

No `.0`. The widths in the font are still floats. You changed how they're shown, and nothing else.

You may wonder whether the two kinds of number get in each other's way when you compare them. They don't:

```python
print(523.0 == 523)
```

```text
True
```

That's why `glyph.width == 708` worked in [chapter 8](008-only-the-ones-i-want.md), with a float on the left and an int on the right. Python compares what the numbers are worth.

## Step 6: Measure a word

Mira calls Tomas back with a better answer than he asked for. A script that takes a word and a size, and says how wide the word sets:

```python
from fly import fl

font = fl.CurrentFont()
upm = font.info.unitsPerEm

word = "Plum"
size = 12

total = 0
for letter in word:
    total = total + font[letter].width

print(word, "is", int(total), "units wide")
print("At", size, "pt that is", round(total / upm * size, 1), "pt")
```

```text
Plum is 2025 units wide
At 12 pt that is 24.3 pt
```

Save it as `widths.py` in your `scripting-book` folder.

Read it in three parts. At the top it asks the font for its UPM and puts the two things you might change, `word` and `size`, into boxes with plain names. In the middle is a loop. A string is a row of characters, so `for letter in word:` hands you `P`, then `l`, then `u`, then `m`. Each time around, the loop looks up the glyph with that name and adds its width to `total`. That's the counter from chapter 7, except that it grows by a width each time and not by 1. At the bottom are the two tidying words: `int` for the units, which are whole, and `round` with one decimal for the points.

Check it by hand once. *P* is 492, *l* is 222, *u* is 523 and *m* is 788. That makes 2025. Divided by 1000 and multiplied by 12, it's 24.3.

Change `size` to 72 and run it again:

```text
Plum is 2025 units wide
At 72 pt that is 145.8 pt
```

The units didn't change. They never do. Only the last line depends on the size.

The script has two limits, and you should know them. It adds up widths and nothing else. When FontLab sets the word, it also applies kerning, the small corrections between particular pairs of letters, so the real line can be a little shorter or longer. Kerning is the subject of Part 4. And `font[letter]` only works when the glyph's name is the letter itself. That's true for `P` and `m`. It isn't true for a space, whose glyph is called `space`, or for a comma. Put a space in `word` and you get the `AttributeError` about `'NoneType'` from chapter 6. Part 2 shows how to get from any character to its glyph.

"Twenty-four point three points, at twelve," says Mira. "Before kerning."

"Before what?" says Tomas.

??? info "Going deeper: why round(2.5) is 2"
    Try `print(round(2.5))` and `print(round(3.5))`. You get `2` and `4`. When a number sits exactly halfway, Python rounds to the nearest even number, not always upward as you learned at school. Over many numbers, that keeps the rounding errors from piling up in one direction. It only affects exact halves, and it won't change a width report. But it explains a result that would otherwise look like a bug.

## What you learned

Python has whole numbers and floats, division always gives a float, and FontLab keeps widths as floats, which is where the `.0` comes from. `int` cuts the decimals off and `round` goes to the nearest value, with an optional second number for how many decimals to keep. A width is counted in font units, and `font.info.unitsPerEm` says how many units make one em, so a width divided by the UPM and multiplied by the type size gives a real measurement.

## Try it yourself

1. Change `word` in `widths.py` to `"Mira"` and `size` back to 12. You should get 1852 units and 22.2 pt.
2. How many times wider is the *m* than the *n*? Divide one width by the other and round the answer to two decimals.
3. Print `font["emdash"].width / upm`. What does the result tell you about how the em dash got its name?

## Next

Chapter 12 builds the table Tomas asked for on Monday: every glyph and its width, with the names lined up on the left and the numbers lined up on the right.
