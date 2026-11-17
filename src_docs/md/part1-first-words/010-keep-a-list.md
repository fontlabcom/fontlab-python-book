---
this_file: src_docs/md/part1-first-words/010-keep-a-list.md
---

# 10. Keep a list

Thursday. Mira has run the "wider than 800" loop from Tuesday four times this morning, and each time she's done the same thing afterwards: scrolled up in the Output panel, read the names and counted them on her fingers.

The publisher's proofreader wants the wide glyphs on one proof page. Ines wants them in alphabetical order, because that's how the proofreader's checklist is sorted. And Mira wants to know which three come first, so she can start drawing the proof while the rest waits.

Three wishes, and the loop can't grant any of them. It prints a name and forgets it. By the time it reaches the em dash, it no longer knows it ever saw the *AE*.

She writes to Oskar: *How do I make it remember?*

*Give it somewhere to put things,* he answers. *An empty list. Then append.*

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open, with 208 glyphs.
- The "wider than 800" loop from [chapter 8](008-only-the-ones-i-want.md). You'll type it again in step 2.

## Step 1: Start empty, then add

In [chapter 5](005-a-font-is-a-list-of-glyphs.md) you made a list by typing everything that was in it: `names = ["A", "B", "C"]`. Today you start with nothing in it and add things one at a time. Type this and run it:

```python
wide = []
print(wide)
print(len(wide))
```

```text
[]
0
```

Two square brackets with nothing between them: an empty list. It's a real list. It has a length, and the length is zero. Think of an empty row with room at the end.

Now add to it:

```python
wide = []
wide.append("AE")
wide.append("M")
print(wide)
print(len(wide))
```

```text
['AE', 'M']
2
```

`append` is a drawer that every list has, the way every string has `endswith`. You pass one thing through the slot and the list puts it at the end of the row. Run `append` twice and the list holds two things, in the order you added them.

There's a difference from everything you've asked an object so far. `endswith` answers a question and leaves the string alone. `append` changes the list. After the line has run, the list is longer than before. You don't write `wide = ...` in front of it. The list in the box changes where it sits.

## Step 2: Let the loop fill the list

Here's Tuesday's loop with one line changed. Where it said `print`, it now says `append`:

```python
from fly import fl

font = fl.CurrentFont()
wide = []
for glyph in font.glyphs:
    if glyph.width > 800:
        wide.append(glyph.name)

print(wide)
print(len(wide), "wide glyphs")
```

```text
['AE', 'M', 'OE', 'W', 'Wacute', 'Wcircumflex', 'Wdieresis', 'Wgrave', 'oe', 'emdash', 'at']
11 wide glyphs
```

The loop runs in silence now. It visits all 208 glyphs, and each time one passes the test, its name goes onto the row. When the loop has finished, the row holds eleven names, and the two lines at the left edge look at it.

Mira doesn't have to count on her fingers any more. `len(wide)` does it. You also don't need the counter from chapter 7 here, the box that went `count = count + 1`. A list knows how long it is.

The order of three lines matters. `wide = []` comes before the loop, so the row exists before anything goes onto it. The `append` is inside the `if`, so only the wide glyphs go in. The `print` lines are outside the loop, so they run once at the end.

Take the first of them away and see. Delete the line `wide = []` and run the script:

```text
Traceback (most recent call last):
  File "<string>", line 6, in <module>
NameError: name 'wide' is not defined
```

Read it from the bottom. You know `NameError` from [chapter 3](003-break-it-on-purpose.md): Python met a name it had never heard. You asked it to append to `wide`, and there's no box with that label. Python won't guess that you wanted a list. Put the line back.

If you saw no error, that's the Scripting panel remembering the `wide` from your last run. Choose **Clear Python Context** from the panel's menu and run again. You met that trick in chapter 5.

There's a quieter way to get this wrong. Put `wide = []` inside the loop, indented under the `for` line, and run it. No error. The output is `[]` and `0 wide glyphs`, or one name if the last glyph in the font happens to be wide. The loop makes a fresh, empty row every time around and throws the old one away. When a list comes out empty and you expected it full, look at where it was born.

## Step 3: Pick from the list

The names are in a list of your own now, so everything you learned about lists in chapter 5 works on them. Add these lines at the bottom of the script:

```python
print(wide[0])
print(wide[10])
```

```text
AE
at
```

Number 0 is the first name. The list has eleven names, counted from zero, so the last is number 10. You could work that out each time as `len(wide) - 1`, the way you found the last glyph of the font in chapter 5. There's a shortcut:

```python
print(wide[-1])
print(wide[-2])
```

```text
at
emdash
```

A negative number counts from the end. `-1` is the last one, `-2` the one before it. It works on any list, however long, and you don't have to know the length.

## Step 4: Take a slice

Mira's third wish was the first three names. You could print `wide[0]`, `wide[1]` and `wide[2]`. Or you can ask for a stretch of the list in one go:

```python
print(wide[0:3])
```

```text
['AE', 'M', 'OE']
```

That's called a slice. Inside the brackets there are two numbers with a colon between them: where to start, and where to stop. The start is included and the stop isn't. So `0:3` gives numbers 0, 1 and 2. Three things, which is also 3 minus 0. That's the reason for the odd rule: the count is always the second number minus the first.

A slice is a new list. The square brackets in the output tell you so. The original stays as it was, all eleven names.

You can leave either number out. Python fills in "from the start" or "to the end":

```python
print(wide[:3])
print(wide[8:])
print(wide[-3:])
```

```text
['AE', 'M', 'OE']
['oe', 'emdash', 'at']
['oe', 'emdash', 'at']
```

`[:3]` reads "the first three". `[8:]` reads "from number 8 to the end". `[-3:]` reads "the last three", and you'll use that one most: it works without knowing that the list has eleven things in it.

Slices are forgiving. `wide[5]` on a list of three gives you an `IndexError`, as you saw in chapter 5. `wide[:50]` on a list of eleven gives you all eleven and no complaint. A slice hands over what's there.

## Step 5: Sort it

Now Ines's wish. The names came out in the order the loop met them, which is the order of the glyphs in the font. That order was chosen by whoever built the font: capitals, then lowercase, then figures and punctuation, with the accents near the end. It's a sensible order for drawing. It isn't the alphabet.

```python
print(sorted(wide))
```

```text
['AE', 'M', 'OE', 'W', 'Wacute', 'Wcircumflex', 'Wdieresis', 'Wgrave', 'at', 'emdash', 'oe']
```

`sorted` takes a list through its slot and hands back a new list in order. It's a word that stands by itself, like `len` and `print`, not a drawer after a dot.

Compare the two outputs. The first eight names didn't move. The last three did: `oe`, `emdash`, `at` became `at`, `emdash`, `oe`. And look where they ended up. After *Wgrave*. In your alphabet, *at* comes long before *M*.

Python's alphabet isn't yours. It puts every capital letter before every lowercase letter. All of A to Z first, then all of a to z. That's because it compares characters by their Unicode numbers, the ones you saw in [chapter 6](006-ask-a-glyph-its-name.md): `A` is 65 and `a` is 97, so `A` comes first, and so does `Z` at 90. For glyph names this is often what you want anyway. It keeps the capitals together. If Ines's checklist is sorted the way a dictionary is, tell her about the difference before the proofreader finds it.

`sorted` did not change `wide`. Print `wide` again and it's still in font order. To keep the sorted version, put it in a box:

```python
by_name = sorted(wide)
print(by_name[:3])
print(wide[:3])
```

```text
['AE', 'M', 'OE']
['AE', 'M', 'OE']
```

Same three here, because the capitals were already in order. Now you have both lists and can use whichever the chore needs.

Sorting works on numbers too, smallest first. Collect widths instead of names and you get the answer to a different question:

```python
from fly import fl

font = fl.CurrentFont()
widths = []
for glyph in font.glyphs:
    if glyph.width > 800:
        widths.append(glyph.width)

print(sorted(widths))
print(sorted(widths)[-3:])
```

```text
[824.0, 840.0, 848.0, 852.0, 859.0, 859.0, 859.0, 859.0, 859.0, 989.0, 1000.0]
[859.0, 989.0, 1000.0]
```

The last line sorts the widths and slices off the last three: the three largest. Sorting and slicing together answer most "top three" questions you'll ever have. What this list can't tell you is which glyph each number belongs to. The names are in one list and the widths in another. Keeping them side by side is a job for Part 2.

## Step 6: The whole script

Here's what Mira saves. It collects, counts, sorts and shows the start:

```python
from fly import fl

font = fl.CurrentFont()
wide = []
for glyph in font.glyphs:
    if glyph.width > 800:
        wide.append(glyph.name)

by_name = sorted(wide)
print(len(wide), "glyphs are wider than 800")
print("In font order:", wide)
print("By name:", by_name)
print("First three:", by_name[:3])
```

```text
11 glyphs are wider than 800
In font order: ['AE', 'M', 'OE', 'W', 'Wacute', 'Wcircumflex', 'Wdieresis', 'Wgrave', 'oe', 'emdash', 'at']
By name: ['AE', 'M', 'OE', 'W', 'Wacute', 'Wcircumflex', 'Wdieresis', 'Wgrave', 'at', 'emdash', 'oe']
First three: ['AE', 'M', 'OE']
```

Save it as `collect_and_sort.py` in your `scripting-book` folder.

To print the names one per line, without brackets and quotes, loop over your own list. You did this in chapter 7 with a list you typed by hand. A list the script built is no different:

```python
for name in by_name:
    print(name)
```

Look at the shape of the script, because most of the scripts in this book have it. First collect: a loop goes through the font and fills a list. Then work on the list: count, sort, slice, print. The two halves don't mix. When Ines asks for the widest three, or for the list backwards, you change the second half and leave the loop alone.

Mira sends the sorted list to the proofreader, with one line about capitals coming first. Then she starts the proof page with *AE*, *M* and *OE*.

??? info "Going deeper: `append` hands nothing back"
    Sooner or later you'll type `wide = wide.append("AE")`, by analogy with `count = count + 1`. Don't. `append` changes the list and hands back `None`. The line then puts that `None` into the box, your list is gone, and the next `append` fails with `AttributeError: 'NoneType' object has no attribute 'append'`. A bare `wide.append("AE")` is the whole instruction.

## What you learned

An empty list, `[]`, is a row you can fill, and `append` puts one more thing at its end. With the list made before the loop and the `append` inside the `if`, a loop collects what it finds instead of printing it and forgetting it. Once the names are in a list, `len` counts them, `sorted` hands back an ordered copy with capitals before lowercase, and a slice such as `[:3]` or `[-3:]` takes a stretch from either end.

## Try it yourself

1. Change `collect_and_sort.py` so it collects the glyphs narrower than 225 units. How many are there? In Plum as it came there are 14, and your three new glyphs may add to that. Print the last three in font order.
2. Collect every glyph name in the font, with no `if`, and print the first ten of the sorted list. Which name comes first, and why does it come before `A`? The Unicode number of the dot is 46.
3. Collect the names that contain `dieresis`, as in [chapter 9](009-strings-are-made-of-letters.md). Print the length of the list, then loop over the sorted list and print one name per line.

## Next

Chapter 11 looks at the numbers themselves. Every width so far has come with `.0` on the end, and nobody has said what a width of 596 is 596 of.
