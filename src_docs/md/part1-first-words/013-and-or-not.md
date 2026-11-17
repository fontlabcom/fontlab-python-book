---
this_file: src_docs/md/part1-first-words/013-and-or-not.md
---

# 13. And, or, not

Monday of the third week. The width table has reached the proofreader, and the proofreader has read it. Tomas passes on her question:

*She says some capitals look very wide next to the others. Can she have only the uppercase ones that are wider than 700?*

Mira reads it twice. She can list the glyphs wider than 700. That's the test from [chapter 8](008-only-the-ones-i-want.md) with 700 in it, and it gives her 22 names with an em dash and a percent sign among them. She could find the capitals too, somehow. What she can't do is ask both questions about the same glyph at the same time.

Last Wednesday the same wall came up with glyph names. A test that was too loose let an asterisk in among the versions of the letter *a*, and there was no way to add a second condition. Today you get three small words that join tests together, and two more that say what to do when a test fails.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open, with 208 glyphs.
- The f-string notes from [chapter 12](012-the-width-report.md), for the table at the end.

## Step 1: Two tests joined with `and`

Start with a plain number. The *O* in Plum is 708 units wide. Type this and run it:

```python
w = 708
print(w > 700)
print(w < 800)
print(w > 700 and w < 800)
print(w > 750 and w < 800)
```

```text
True
True
True
False
```

The first two lines are comparisons, as you know them. The third joins them with the word `and`. The joined question is `True` only when both parts are `True`. In the fourth line the first part fails, 708 isn't greater than 750, so the whole thing is `False`. One no is enough.

That's how the word works in a sentence, too. "Wider than 700 and narrower than 800" describes a glyph that passes both tests.

Now write it the way you'd say it aloud:

```python
w = 708
if w > 700 and < 800:
    print("wide")
```

```text
  File "<string>", line 2
    if w > 700 and < 800:
                   ^
SyntaxError: invalid syntax
```

The little arrow points at the `<`. In speech you say "wider than 700 and narrower than 800" and the listener knows that both halves are about the same glyph. Python doesn't fill in what you left out. On each side of `and` it wants a whole question, one that could stand alone after `if`. `< 800` can't stand alone: less than 800, but what is? Say `w` again, as in `w > 700 and w < 800`, and it runs.

## Step 2: Which glyphs are uppercase?

For the proofreader you need a second test: is this glyph a capital? A plain glyph has no drawer that says so. But its name is a string, and a string can say whether it's written in capitals:

```python
print("A".isupper())
print("a".isupper())
print("Aacute".isupper())
print("Aacute"[0].isupper())
```

```text
True
False
False
True
```

`isupper` is another question a string works out when asked, like `endswith` in [chapter 9](009-strings-are-made-of-letters.md), with nothing to pass through the slot. It says `True` when the letters in the string are all capitals. So `"A"` passes and `"Aacute"` doesn't, because five of its six letters are small.

That's the wrong test for glyph names. The glyph *Aacute* is a capital letter. What marks it as one is the first character of its name. The fourth line asks only that character. You know `[0]` from lists: the first thing in the row. A string is a row of characters, so `"Aacute"[0]` is `"A"`, and the question goes to that one letter.

This is a convention of glyph names, not a law. In Plum, 68 names start with a capital. Sixty-seven are capital letters, and one is `Euro`, the currency sign. A test on names finds what the names say. Later in the book, in Part 5, you'll ask FontLab what kind of character a glyph stands for, and that's the dependable way. For today's question the name is good enough, and you'll check the list by eye.

## Step 3: Both at once

Now put the two tests on one line, inside the loop:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.name[0].isupper() and glyph.width > 700:
        print(glyph.name)
```

```text
AE
M
O
Oacute
Ocircumflex
Odieresis
Ograve
Oslash
Otilde
OE
Q
W
Wacute
Wcircumflex
Wdieresis
Wgrave
```

Sixteen names, and every one a capital. The em dash, the percent sign, the at sign and the small *m* are gone. Each glyph had to pass two tests, and they failed the first. The `Euro` passed the first and failed the second: it's 490 units wide.

Read the `if` line aloud. "If the first character of the glyph's name is uppercase, and the glyph's width is greater than 700." It's long, but each side of the `and` is a question you could have asked alone.

## Step 4: Either one will do, with `or`

`and` wants both. The word `or` is content with one:

```python
w = 708
print(w < 200 or w > 700)
print(w < 200 or w > 900)
```

```text
True
False
```

In the first line, 708 isn't less than 200, but it is greater than 700, and one yes is enough. In the second line both parts fail. `or` is `False` only when everything it joins is `False`.

Use it to collect two families of glyphs in one pass:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.name.startswith("W") or glyph.name.startswith("M"):
        print(glyph.name)
```

```text
M
W
Wacute
Wcircumflex
Wdieresis
Wgrave
```

You can use `and` and `or` in the same line. When you do, put parentheses around the part that belongs together. Compare these two tests:

```python
(glyph.name.startswith("W") or glyph.name.startswith("M")) and glyph.width > 850
```

```python
glyph.name.startswith("W") or glyph.name.startswith("M") and glyph.width > 850
```

The first one says: a name that starts with W or M, and in either case a width over 850. The *M* is 840 units wide, so it drops out, and all five W glyphs stay. The second one has no parentheses, and Python reads `and` before `or`, the way it multiplies before it adds. So it means: starts with W, whatever the width, or else starts with M and is over 850. In Plum both versions happen to print the same five names. In a font with a narrow *W* they wouldn't. Don't make the reader work out which you meant. Write the parentheses.

## Step 5: Turn a test around with `not`

The third word goes in front of a test and flips its answer:

```python
w = 708
print(w > 700)
print(not w > 700)
```

```text
True
False
```

Here's the other half of this morning's list. The glyphs wider than 700 that aren't capitals:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.width > 700 and not glyph.name[0].isupper():
        print(glyph.name)
```

```text
ae
m
oe
emdash
percent
at
```

Six names. Sixteen and six make 22, the number Mira's first test found for all the glyphs wider than 700. Every wide glyph is on one list or the other, and none is on both. When two lists are supposed to split a group, add them up. It's the cheapest check there is.

`not` also narrows a test that lets too much in. Last Wednesday's too-loose test was `glyph.name.startswith("a")`, and it caught `asterisk`, `asciitilde` and `asciicircum`. Now you can shut them out:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.name.startswith("a") and not glyph.name.startswith("as"):
        print(glyph.name)
```

That leaves thirteen names. It still lets through `ampersand`, `at` and the `acute` accent, so the test is tighter and not yet tight. You could add more conditions. At some point a short list typed by hand is the better tool, and knowing when you've reached that point is part of the craft.

## Step 6: Otherwise: `else` and `elif`

So far an `if` either does something or stays silent. Often you want it to do one thing or another. Type this:

```python
from fly import fl

font = fl.CurrentFont()
for name in ["H", "O", "n", "m"]:
    glyph = font[name]
    if glyph.width > 700:
        print(name, "is wide")
    else:
        print(name, "is not wide")
```

```text
H is not wide
O is wide
n is not wide
m is wide
```

`else` means "otherwise". It sits at the same depth as the `if` it belongs to, it has no test of its own, and it ends in a colon. The lines indented under it run when the `if` test was `False`. Exactly one of the two blocks runs each time around. Never both, never neither.

Two choices aren't always enough. The proofreader's real question is how the capitals compare, so sort the 26 plain capital letters into three bins:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if len(glyph.name) == 1 and glyph.name.isupper():
        if glyph.width < 500:
            label = "narrow"
        elif glyph.width <= 700:
            label = "medium"
        else:
            label = "wide"
        print(f"{glyph.name:<4}{glyph.width:>6.0f}  {label}")
```

Here are the rows for five of the letters:

```text
A      596  medium
I      228  narrow
M      840  wide
Q      708  wide
W      859  wide
```

Over all 26 letters you get 8 narrow, 14 medium and 4 wide.

`elif` is short for "else if". It's an `else` with a test of its own. Python goes down the ladder from the top and stops at the first rung whose test is `True`. It runs that block and skips all the rest. That's why the second test doesn't need to say "500 or more". If a glyph arrives at the `elif`, the first test has already failed, so its width can't be under 500. You can have as many `elif` rungs as you like, and one `else` at the bottom to catch whatever is left.

Look at the outer `if` as well. It joins two tests with `and`: the name is one character long, and that character is uppercase. And it shows an `if` inside an `if`, each with its own depth of indentation. The `print` line is at the depth of the inner `if`, not inside any of its three blocks, so it runs once for every capital, whichever label was chosen.

## The proofreader's list

Here's what Mira saves, with the columns from chapter 12 and a count at the end:

```python
from fly import fl

font = fl.CurrentFont()

count = 0
for glyph in font.glyphs:
    if glyph.name[0].isupper() and glyph.width > 700:
        print(f"{glyph.name:<16}{glyph.width:>6.0f}")
        count = count + 1
print(f"{count} uppercase glyphs are wider than 700")
```

```text
AE                 852
M                  840
O                  708
Oacute             708
Ocircumflex        708
Odieresis          708
Ograve             708
Oslash             708
Otilde             708
OE                 989
Q                  708
W                  859
Wacute             859
Wcircumflex        859
Wdieresis          859
Wgrave             859
16 uppercase glyphs are wider than 700
```

Save it as `wide_caps.py` in your `scripting-book` folder.

Mira sends the list with a note: the *O* family and the *Q* are round, the *M* and the *W* have four strokes, and the two ligatures are two letters each. Wide is what they should be. The proofreader writes back that she'll stop worrying about the *W*.

??? info "Going deeper: the column for a missing value"
    Chapter 12 left a table that broke on `.notdef`, because `None` can't be given a note about room. With `else` you can mend it. Before the `print` line, write `if glyph.unicode is None:` and under it `shown = "none"`, then `else:` and under it `shown = glyph.unicode`. Print `{shown:>6}` in place of `{glyph.unicode:>6}`. Now the box `shown` always holds something that can be printed, a word or a number.

## What you learned

`and` joins two tests into one that passes only when both pass, `or` makes one that passes when either does, and `not` flips an answer. Each side of `and` and `or` has to be a whole question. When you mix them, parentheses say which parts belong together. `else` gives an `if` a second block for the times its test fails, and `elif` adds further tests in between, tried from the top until one is `True`.

## Try it yourself

1. Change `wide_caps.py` so it lists the uppercase glyphs narrower than 300. You should get seven: the *I*, five accented versions of it, and the *J*.
2. List the glyphs whose names start with `O` and whose width is not 708. Use `!=`, or use `not` with `==`. There's one.
3. In the three-bin script from step 6, add a fourth bin called `very wide` for widths over 850. Where in the ladder does the new rung have to go, and what happens if you put it last?

## Next

Chapter 14 is the first script that changes the font. Until now every script has looked and reported. The next one puts a red mark on the empty glyphs, so that Mira can see them in the Font window without reading a list.
