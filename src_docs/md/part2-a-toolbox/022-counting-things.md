---
this_file: src_docs/md/part2-a-toolbox/022-counting-things.md
---

# 22. Counting things

Tuesday. The publisher prints price lists, and the proofreader has a question that sounds small.

*Do Plum's figures line up in columns? If the 1 is narrower than the 8, our tables wobble.*

Mira knows what she's being asked. Figures that all share one width are called **tabular figures**, because they stack up cleanly in a table. To answer, she could open ten glyphs and read ten numbers.

Ines, reading over her shoulder, makes it bigger. "While you're in there. How many different widths does that font have, anyway?"

Nobody at Halfmoon knows. It's the kind of question you don't ask when the only way to answer it is by hand.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `lookup.py` from [chapter 21](021-a-dictionary-of-glyphs.md), for the dictionary moves.

## Step 1: A tally sheet

Think about how you'd count the cars on your street by color, with a pencil. You write a color the first time you see it and put one stroke next to it. Every time that color comes by again, you add a stroke. You don't know before you start which colors will turn up.

A dictionary can be that sheet. The key is the thing you're counting. The value is the number of strokes.

Try it on a short list first, with no font. This counts glyph names by their first letter:

```python
names = ["A", "Aacute", "B", "a", "adieresis", "b", "a.sc"]

tally = {}
for name in names:
    first = name[0]
    tally[first] = tally[first] + 1
print(tally)
```

`name[0]` is the first character of the name, the same square brackets you used on lists and on text in Part 1. The line after it is the pencil stroke: open the drawer for this letter, add one, put it back. Run it.

```text
KeyError: 'A'
```

You met `KeyError` yesterday. Python is right again. The first name is `A`. The script tries to open the drawer `"A"` to add one to it, and the sheet is still blank. You can't add a stroke next to a color you haven't written down.

## Step 2: Ask politely with get

What you want to say is: "give me the count for this letter, and if there isn't one yet, call it zero." A dictionary has a tool for exactly that sentence. It's called `get`.

```python
tally = {"A": 2}
print(tally.get("A", 0))
print(tally.get("B", 0))
```

```text
2
0
```

`get` sits in a drawer of the dictionary, so there's a dot in front of it, and it's a function, so it has a slot. Two things go through the slot: the key you're asking about, and the answer you want if the key isn't there. For `"A"` the dictionary has a value, and you get it. For `"B"` it has nothing, and you get your zero. No error either way.

Square brackets are the strict way to ask, and `get` is the polite way. Use the strict way when a missing key means something has gone wrong, as it did with Mira's typo yesterday. Use the polite way when a missing key is normal, and on a tally sheet it's normal every time something turns up for the first time.

Put `get` into the tally:

```python
names = ["A", "Aacute", "B", "a", "adieresis", "b", "a.sc"]

tally = {}
for name in names:
    first = name[0]
    tally[first] = tally.get(first, 0) + 1
print(tally)
```

```text
{'A': 2, 'B': 1, 'a': 3, 'b': 1}
```

Seven names, four different first letters. Go through it for `"A"`. The first time, `get` answers 0, the script adds 1, and the pair `"A": 1` goes on the sheet. The second time, `get` answers 1, and the pair becomes `"A": 2`. You'll write that one line many times. Capital `A` and small `a` are counted apart, as they should be.

While we're counting, here's a shorter way to write something you've typed since chapter 7. `count = count + 1` has a short form, `count += 1`. It means the same thing: take what's in the box, add 1, put it back.

```python
count = 0
count += 1
count += 1
print(count)
```

```text
2
```

It works with any number on the right, so `total += 20` adds 20. From here on the book uses the short form for a plain counter. The tally line keeps its long form, because `get` has to supply the 0 for a key that's new.

## Step 3: Tally the font

Now the real question. The thing to count is the width, so the width is the key.

One decision first. The three small caps from chapter 8 are empty, and `.notdef` isn't a character anybody types. I'd leave those four out, so that the count is about glyphs a reader of the price list can meet. They have one thing in common: no Unicode value. You know how to test for that.

```python
from fly import fl

font = fl.CurrentFont()
tally = {}
for glyph in font.glyphs:
    if glyph.unicode is not None:
        width = int(glyph.width)
        tally[width] = tally.get(width, 0) + 1

print(len(tally), "different widths")
```

```text
84 different widths
```

There's Ines's answer. Plum has 204 glyphs with a Unicode value, and between them they use 84 different widths.

Is that a lot? It's about what you'd expect from a text face. Each letter gets the width its shape needs, and an `m` needs more than an `i`. But it isn't 204 either, so many glyphs share a width with others. The interesting part is which ones.

Notice that the keys are numbers this time. I said yesterday that numbers can be keys, and here they are. `tally[596]` doesn't mean position 596. It means "the count filed under the width 596".

## Step 4: Read the sheet, pair by pair

Print `tally` and you get one long line with 84 pairs between curly braces. It's all there and it's hard to read. You want one pair per line.

Yesterday's loop over a dictionary gave you the keys. There's a second way that gives you the key and the value together:

```python
for width, count in tally.items():
    print(width, count)
```

```text
596 8
852 1
517 1
621 2
665 1
485 5
```

And 78 more lines. `items` hands the loop one pair at a time, and the loop puts the two halves in two boxes. That's why there are two labels between `for` and `in`, with a comma. The first box gets the key and the second gets the value. I've called them `width` and `count` because that's what they are on this sheet. On another sheet you'd pick other words.

The first line says eight glyphs are 596 wide. That's the `A` and its seven accented versions, which you saw at the top of Tomas's table. An accent doesn't change how much room a letter takes, so the whole group shares the width of its base letter.

## Check that the strokes add up

Before you trust a tally, add it up. If you counted cars for an hour and a hundred went by, the strokes on your sheet should come to a hundred. If they come to ninety, you missed some. If they come to a hundred and ten, you counted some twice.

Here the strokes should come to the number of glyphs that have a Unicode value. Add this under the loop from step 3:

```python
total = 0
for width, count in tally.items():
    total = total + count
print(total, "glyphs counted")
```

```text
204 glyphs counted
```

Your font has 208 glyphs. Take away `.notdef` and the three empty small caps, and 204 is what should be left. It is, so the sheet and the font agree.

It takes four lines, and it catches a wrong tally before anyone else sees it. A script that counts will always give you a number, and a wrong number looks as tidy as a right one. Whenever you can think of a second way to arrive at a figure, spend the four lines. The day the two don't match, you've found a mistake before Ines did.

## Step 5: Only the busy widths

Eighty-four lines is still a lot to look at, and half of them say `1`. Put a test inside the loop, and tidy the line with an f-string:

```python
for width, count in tally.items():
    if count >= 8:
        print(f"{width}: {count} glyphs")
```

```text
596: 8 glyphs
708: 8 glyphs
523: 9 glyphs
471: 8 glyphs
490: 14 glyphs
500: 10 glyphs
```

Six widths do a lot of the work. One of them stands out: fourteen glyphs at 490. Ten of those could be the figures. If they are, what are the other four?

The tally knows how many. It doesn't know who, because you only asked it to count. For that, go back to the font with the number in your hand.

## Step 6: Who is 490 wide?

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if int(glyph.width) == 490:
        print(glyph.name)
```

```text
zero
one
two
three
four
five
six
seven
eight
nine
numbersign
dollar
yen
Euro
```

All ten figures, at one width. Plum's figures are tabular, and the price lists won't wobble.

The other four are the number sign, the dollar, the yen and the euro. Whoever drew Plum gave the currency signs the same width as the figures, so that a column of prices lines up from the sign to the last digit. Nobody at Halfmoon had noticed that. It was sitting in the font, and a count found it.

Mira writes back: *Yes. All ten figures are 490 units wide, and so are $, ¥, € and #.* Then she changes 490 to 708 and runs it again, for fun, and gets the `O` family and the `Q`.

One note. `who_is.py` doesn't test for a Unicode value, so it looks at every glyph, the empty small caps from chapter 8 included. If your new glyphs show up in one of its lists, that's why.

Put the script from step 3 together with the loop from step 5 and save it as `width_tally.py`. Keep the script from this step as `who_is.py`. The number on its `if` line is the part you change.

??? info "Going deeper: sorting the sheet by count"
    The lines in step 5 come out in the order the widths first turned up in the font, so 490 isn't at the top even though it's the biggest group. `sorted` on a dictionary sorts the keys, which here would sort by width. Sorting by the count takes one more idea, and chapter 36 has it.

## What you learned

A dictionary makes a tally sheet: the thing you count is the key and the count is the value. `d.get(key, 0)` asks for a value and takes 0 when the key is new, so `d[key] = d.get(key, 0) + 1` adds one stroke without tripping over the first one. `for key, value in d.items():` goes through the pairs. A count tells you how many, and a second pass over the font tells you which.

## Try it yourself

1. Change the script from step 3 so that it tallies by the first letter of the glyph name, as in step 2, and take the Unicode test out so that every glyph counts. How many glyph names in your font start with a small `a`? Count the cells in the Font window to check.
2. In `width_tally.py`, change the test to `count == 1` and print only the count of such widths, not the widths themselves. You'll need a counter from chapter 7 inside the loop.
3. Run `who_is.py` for 523 and for 500. One of the two groups has an odd member that doesn't share a shape with the rest. Which glyph is it, and can you think why the designer gave it that width?

## Next

Chapter 23 looks hard at the number you've been using to tell real characters from the rest: the Unicode value.
